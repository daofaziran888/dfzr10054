"""重述单领域服务：重述范围解析、执行中版本统计、重述原因分类，产出单据条目数据集。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class RestateTicketService(BaseModuleService):
    MODULE = "restate_ticket"
    ENTITY = "单据条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["单据编号", "数据集标识", "重述范围", "重述原因", "影响版本数", "创建时间"]
    REQUIRED_FIELDS = ["单据编号", "数据集标识", "重述范围"]
    STATUS_ORDER = ["草拟中", "待审批", "执行中", "已完成"]
    ACTION_RULES = {"提交审批": "待审批", "启动重述": "执行中", "确认完成": "已完成"}
    NEGATIVE_ACTIONS = []

    def parse_version_range(self, ticket_no: str) -> list[int]:
        """解析重述单的版本范围字符串为版本列表。"""
        ticket = None
        for row in store.rows(self.MODULE):
            if str(row.get("单据编号")) == ticket_no:
                ticket = row
                break
        if ticket is None:
            return []
        range_str = str(ticket.get("重述范围", ""))
        versions = []
        for part in range_str.split(","):
            part = part.strip().replace("v", "")
            if "-" in part:
                try:
                    s, e = part.split("-")
                    versions.extend(range(int(s), int(e) + 1))
                except ValueError:
                    pass
            elif part:
                try:
                    versions.append(int(part))
                except ValueError:
                    pass
        return sorted(set(versions))

    def executing_tickets(self) -> list[dict[str, Any]]:
        """返回所有执行中重述单。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "执行中"
        ]

    def restate_reason_categories(self) -> dict[str, int]:
        """重述原因分类统计。"""
        counts: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            reason = str(row.get("重述原因", "未知"))
            counts[reason] = counts.get(reason, 0) + 1
        return counts

    def validate_approval(self, ticket_no: str) -> tuple[bool, str]:
        """审批校验：重述单必须已有影响范围评估且差异摘要已生成。"""
        ticket = None
        for row in store.rows(self.MODULE):
            if str(row.get("单据编号")) == ticket_no:
                ticket = row
                break
        if ticket is None:
            return False, f"重述单{ticket_no}不存在"

        has_scope = any(
            str(r.get("单据编号")) == ticket_no
            for r in store.rows("impact_scope")
        )
        has_diff = any(
            str(r.get("单据编号")) == ticket_no
            for r in store.rows("diff_summary")
        )
        if not has_scope or not has_diff:
            return False, f"重述单{ticket_no}缺少影响范围或差异摘要，不可审批"
        ticket["status"] = "待审批"
        return True, f"重述单{ticket_no}已提交审批"

    def ticket_statistics(self) -> dict[str, Any]:
        """重述单汇总统计。"""
        rows = store.rows(self.MODULE)
        return {
            "total": len(rows),
            "executing": sum(1 for r in rows if r.get("status") == "执行中"),
            "completed": sum(1 for r in rows if r.get("status") == "已完成"),
            "pending_approval": sum(1 for r in rows if r.get("status") == "待审批"),
        }