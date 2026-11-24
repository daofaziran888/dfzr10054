"""合并请求领域服务：合并策略校验、版本冲突检测、合并统计。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class MergeRequestService(BaseModuleService):
    MODULE = "merge_request"
    ENTITY = "请求单"
    OPERATION_TERM = "合并"
    LIST_FIELDS = ["请求编号", "源版本", "目标版本", "合并策略", "提交时间"]
    REQUIRED_FIELDS = ["请求编号", "源版本", "目标版本"]
    STATUS_ORDER = ["待评审", "评审中", "已合并", "已拒绝"]
    ACTION_RULES = {"发起评审": "评审中", "确认合并": "已合并", "拒绝请求": "已拒绝"}
    NEGATIVE_ACTIONS = ["拒绝请求"]

    def conflict_check(
        self, source_ver: str, target_ver: str,
    ) -> tuple[bool, str]:
        """检查源版本与目标版本是否存在冲突。"""
        if source_ver == target_ver:
            return True, "源版本与目标版本相同，无法合并"
        source_int = int(source_ver) if source_ver.isdigit() else 0
        target_int = int(target_ver) if target_ver.isdigit() else 0
        if source_int > target_int:
            return True, (
                f"源版本{source_ver}高于目标{target_ver}，"
                f"可能丢失数据变更"
            )
        for row in store.rows("merge_request"):
            if (row.get("状态") == "评审中"
                    and str(row.get("目标版本")) == target_ver):
                return True, f"目标版本{target_ver}已有评审中的合并请求"
        return False, "无冲突"

    def pending_merges(self) -> list[dict[str, Any]]:
        """返回全部评审中合并请求。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "评审中"
        ]

    def merged_count(self) -> int:
        """统计已合并请求数。"""
        return sum(
            1 for row in store.rows(self.MODULE)
            if row.get("status") == "已合并"
        )

    def reject_rate(self) -> float:
        """拒绝率。"""
        rows = store.rows(self.MODULE)
        rejected = sum(1 for r in rows if r.get("status") == "已拒绝")
        return rejected / len(rows) if rows else 0.0

    def strategy_distribution(self) -> dict[str, int]:
        """合并策略分布统计。"""
        dist: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            strategy = str(row.get("合并策略", ""))
            dist[strategy] = dist.get(strategy, 0) + 1
        return dist