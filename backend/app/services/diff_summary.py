"""差异摘要领域服务：差异阈值告警、净差异聚合、异常摘要清单。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class DiffSummaryService(BaseModuleService):
    MODULE = "diff_summary"
    ENTITY = "摘要条目"
    OPERATION_TERM = "聚合"
    LIST_FIELDS = ["摘要编号", "单据编号", "重述前条数", "重述后条数", "净差异数", "摘要时间"]
    REQUIRED_FIELDS = ["摘要编号", "单据编号", "净差异数"]
    STATUS_ORDER = ["生成中", "待复核", "已复核", "差异异常"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记异常": "差异异常"}
    NEGATIVE_ACTIONS = ["登记异常"]

    THRESHOLD = 50

    def check_abnormal(self, diff_id: str) -> tuple[bool, str]:
        """检查差异是否异常：净差异数超过阈值50标记异常。"""
        entry = None
        for row in store.rows(self.MODULE):
            if str(row.get("摘要编号")) == diff_id:
                entry = row
                break
        if entry is None:
            return False, f"摘要{diff_id}不存在"

        net_diff = abs(int(str(entry.get("净差异数", 0))))
        if net_diff > self.THRESHOLD:
            entry["status"] = "差异异常"
            entry["pending"] = True
            entry["abnormal"] = True
            return True, f"差异超出阈值{net_diff}，标记异常"
        entry["status"] = "已复核"
        entry["pending"] = False
        return False, f"差异{net_diff}在阈值内"

    def net_diff_aggregation(self, ticket_no: str) -> int:
        """汇总某重述单全部摘要的净差异总和。"""
        return sum(
            int(str(row.get("净差异数", 0)))
            for row in store.rows(self.MODULE)
            if str(row.get("单据编号")) == ticket_no
        )

    def abnormal_summaries(self) -> list[dict[str, Any]]:
        """返回全部差异异常的摘要。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "差异异常"
        ]

    def compare_before_after(
        self, ticket_no: str,
    ) -> tuple[int, int]:
        """返回重述单全部版本重述前后总条数。"""
        before = 0
        after = 0
        for row in store.rows(self.MODULE):
            if str(row.get("单据编号")) == ticket_no:
                before += int(str(row.get("重述前条数", 0)))
                after += int(str(row.get("重述后条数", 0)))
        return before, after