"""保留策略领域服务：回收约束校验、策略匹配、保留阈值判定，产出策略条目数据集。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class RetainPolicyService(BaseModuleService):
    MODULE = "retain_policy"
    ENTITY = "策略条目"
    OPERATION_TERM = "归档"
    LIST_FIELDS = ["策略编号", "策略名称", "最少保留版本", "保留天数", "适用数据集", "更新时间"]
    REQUIRED_FIELDS = ["策略编号", "策略名称", "适用数据集"]
    STATUS_ORDER = ["草稿", "待生效", "已生效", "已废止"]
    ACTION_RULES = {"提交生效": "待生效", "生效策略": "已生效", "废止策略": "已废止"}
    NEGATIVE_ACTIONS = ["废止策略"]

    def active_policy(self, dataset_id: str) -> dict[str, Any] | None:
        """获取数据集当前生效的保留策略。"""
        for row in store.rows(self.MODULE):
            if (row.get("status") == "已生效"
                    and row.get("适用数据集") == dataset_id):
                return row
        return None

    def check_reclaim_constraint(
        self, dataset_id: str, candidate_count: int,
    ) -> tuple[bool, str]:
        """检查回收候选项数是否满足保留策略的最少保留版本约束。"""
        policy = self.active_policy(dataset_id)
        min_versions = int(
            str(policy.get("最少保留版本", 3)) if policy else "3"
        )
        current = sum(
            1 for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        remaining = current - candidate_count
        if remaining < min_versions:
            return False, (
                f"回收{candidate_count}个后剩余{remaining}版本，"
                f"不满足最少保留{min_versions}"
            )
        return True, "满足保留策略约束"

    def retention_vs_versus_catalog(
        self, dataset_id: str,
    ) -> dict[str, Any]:
        """比较保留策略与快照编目实际版本数的差异。"""
        policy = self.active_policy(dataset_id)
        min_versions = int(
            str(policy.get("最少保留版本", 0)) if policy else "0"
        )
        actual = sum(
            1 for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        return {
            "dataset": dataset_id,
            "policy_min": min_versions,
            "actual": actual,
            "surplus": actual - min_versions,
            "can_reclaim": actual > min_versions,
        }

    def is_snapshot_retainable(
        self, dataset_id: str, version: int,
    ) -> bool:
        """判断指定版本是否在保留范围内。"""
        policy = self.active_policy(dataset_id)
        min_versions = int(
            str(policy.get("最少保留版本", 3)) if policy else "3"
        )
        versions = sorted(
            int(str(row.get("版本序号", 0)))
            for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        if len(versions) <= min_versions:
            return True
        # 最后min_versions个版本必须保留
        retained = set(versions[-min_versions:])
        return version in retained