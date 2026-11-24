"""冷藏层级领域服务：转层判断、回取代价评估、层级分布统计，产出层级条目数据集。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class ColdTierService(BaseModuleService):
    MODULE = "cold_tier"
    ENTITY = "层级条目"
    OPERATION_TERM = "归档"
    LIST_FIELDS = ["层级编号", "快照编号", "层级标记", "转层时间", "回取代价", "保留天数"]
    REQUIRED_FIELDS = ["层级编号", "快照编号", "层级标记"]
    STATUS_ORDER = ["待转层", "转层中", "已转层", "已销毁"]
    ACTION_RULES = {"发起转层": "转层中", "确认转层": "已转层", "销毁层级": "已销毁"}
    NEGATIVE_ACTIONS = ["销毁层级"]

    def tier_distribution(self) -> dict[str, int]:
        """冷藏层级分布统计。"""
        dist: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            label = str(row.get("层级标记", "未知"))
            dist[label] = dist.get(label, 0) + 1
        return dist

    def high_cost_snapshots(self) -> list[dict[str, Any]]:
        """返回回取代价最高的快照。"""
        return sorted(
            [
                row for row in store.rows(self.MODULE)
                if row.get("回取代价") in ("high", "very_high")
            ],
            key=lambda r: {"very_high": 2, "high": 1}.get(
                str(r.get("回取代价", "")), 0,
            ),
            reverse=True,
        )

    def can_transition_to_cold(
        self, snapshot_no: str, days_since_last_access: int,
    ) -> tuple[bool, str]:
        """判断快照是否可以转入冷藏层级。"""
        # 检查是否被版本链引用
        version = None
        dataset_id = ""
        for row in store.rows("snapshot_catalog"):
            if str(row.get("快照编号")) == snapshot_no:
                version = str(row.get("版本序号"))
                dataset_id = str(row.get("数据集标识", ""))
                break
        if version is None:
            return False, f"快照{snapshot_no}不存在"

        for link in store.rows("version_chain"):
            if (link.get("数据集标识") == dataset_id
                    and (str(link.get("前序版本")) == version
                         or str(link.get("后继版本")) == version)):
                return False, f"快照{snapshot_no}被版本链引用，不能转层"

        # 检查保留策略
        policy = None
        for row in store.rows("retain_policy"):
            if (row.get("status") == "已生效"
                    and row.get("适用数据集") == dataset_id):
                policy = row
                break
        if policy:
            min_versions = int(str(policy.get("最少保留版本", 3)))
            retained_versions = sorted(
                int(str(r.get("版本序号", 0)))
                for r in store.rows("snapshot_catalog")
                if r.get("数据集标识") == dataset_id
                and r.get("status") == "已编目"
            )[-min_versions:]
            if int(version) in retained_versions:
                return False, f"版本{version}在保留策略内，不可转层"

        return True, f"快照{snapshot_no}满足转层条件"

    def refresh_retention(
        self, tier_id: str, new_days: int,
    ) -> tuple[bool, str]:
        """更新冷藏层级的保留天数。"""
        for row in store.rows(self.MODULE):
            if str(row.get("层级编号")) == tier_id:
                row["保留天数"] = str(new_days)
                return True, f"层级{tier_id}保留天数更新为{new_days}"
        return False, f"层级{tier_id}不存在"