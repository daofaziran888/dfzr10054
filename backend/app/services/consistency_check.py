"""一致性核查领域服务：版本对校验、污染判定、差异阈值告警。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class ConsistencyCheckService(BaseModuleService):
    MODULE = "consistency_check"
    ENTITY = "核查报告"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["核查编号", "数据集标识", "核查版本对", "差异条数", "核查结论", "核查时间"]
    REQUIRED_FIELDS = ["核查编号", "数据集标识", "核查版本对"]
    STATUS_ORDER = ["核查中", "待裁决", "核查通过", "链污染"]
    ACTION_RULES = {"提交裁决": "待裁决", "通过核查": "核查通过", "登记污染": "链污染"}
    NEGATIVE_ACTIONS = ["登记污染"]

    POLLUTION_THRESHOLD = 3000

    def check_pollution(self, check_id: int) -> tuple[bool, str]:
        """检查版本对是否链污染：差异条数>3000则判定污染。"""
        row = store.find(self.MODULE, check_id)
        if row is None:
            return False, f"核查报告{check_id}不存在"
        diff = int(str(row.get("差异条数", 0)))
        if diff > self.POLLUTION_THRESHOLD:
            row["status"] = "链污染"
            row["核查结论"] = "污染"
            row["pending"] = True
            row["abnormal"] = True
            return True, f"差异条数{diff}>{self.POLLUTION_THRESHOLD}，判定链污染"
        row["status"] = "核查通过"
        row["核查结论"] = "通过"
        row["pending"] = False
        return False, f"差异条数{diff}在阈值内，通过核查"

    def pollution_reports(self) -> list[dict[str, Any]]:
        """返回全部链污染报告。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "链污染"
        ]

    def check_summary(self, dataset_id: str) -> dict[str, Any]:
        """数据集核查摘要。"""
        reports = [
            row for row in store.rows(self.MODULE)
            if row.get("数据集标识") == dataset_id
        ]
        return {
            "dataset": dataset_id,
            "total": len(reports),
            "passed": sum(1 for r in reports if r.get("status") == "核查通过"),
            "polluted": sum(1 for r in reports if r.get("status") == "链污染"),
            "avg_diff": (
                sum(int(str(r.get("差异条数", 0))) for r in reports) / len(reports)
                if reports else 0.0
            ),
        }

    def failed_checks(self) -> list[dict[str, Any]]:
        """返回全部未通过的核查报告。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") not in ("核查通过",)
        ]