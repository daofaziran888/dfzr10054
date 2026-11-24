"""分支比对领域服务：差异条数统计、差异阈值告警、版本对校验。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class BranchCompareService(BaseModuleService):
    MODULE = "branch_compare"
    ENTITY = "比对记录"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["比对编号", "数据集标识", "版本甲", "版本乙", "差异条数", "比对时间"]
    REQUIRED_FIELDS = ["比对编号", "数据集标识", "版本甲"]
    STATUS_ORDER = ["比对中", "待复核", "已复核", "差异待判"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记待判": "差异待判"}
    NEGATIVE_ACTIONS = ["登记待判"]

    DIFF_THRESHOLD = 1000

    def diff_stats(self, dataset_id: str) -> dict[str, Any]:
        """返回数据集的比对统计。"""
        records = [
            row for row in store.rows(self.MODULE)
            if row.get("数据集标识") == dataset_id
        ]
        diffs = [int(str(r.get("差异条数", 0))) for r in records
                 if r.get("差异条数")]
        return {
            "dataset": dataset_id,
            "count": len(records),
            "total_diff": sum(diffs),
            "max_diff": max(diffs) if diffs else 0,
            "above_threshold": sum(1 for d in diffs if d > self.DIFF_THRESHOLD),
        }

    def abnormal_diffs(self) -> list[dict[str, Any]]:
        """返回全部差异待判的比对记录。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "差异待判"
        ]

    def compare_two_versions(
        self, dataset_id: str, ver_a: str, ver_b: str,
    ) -> int:
        """返回两个版本的差异条数，无记录返回0。"""
        for row in store.rows(self.MODULE):
            if row.get("数据集标识") == dataset_id:
                stored_a = str(row.get("版本甲", ""))
                stored_b = str(row.get("版本乙", ""))
                if (stored_a == ver_a and stored_b == ver_b) or (
                    stored_a == ver_b and stored_b == ver_a
                ):
                    return int(str(row.get("差异条数", 0)))
        return 0

    def high_diff_versions(
        self, limit: int = 5,
    ) -> list[tuple[str, str, int]]:
        """返回差异条数最高的N对版本(数据集, 版本对, 差异数)。"""
        rows = sorted(
            [
                (str(r.get("数据集标识", "")),
                 f"{r.get('版本甲','')}vs{r.get('版本乙','')}",
                 int(str(r.get("差异条数", 0))))
                for r in store.rows(self.MODULE)
                if r.get("差异条数")
            ],
            key=lambda x: -x[2],
        )
        return rows[:limit]