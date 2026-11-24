"""下游通知领域服务：通知状态追踪、催办、确认率统计。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class DownstreamNoticeService(BaseModuleService):
    MODULE = "downstream_notice"
    ENTITY = "通知记录"
    OPERATION_TERM = "调度"
    LIST_FIELDS = ["通知编号", "单据编号", "下游数据集", "通知摘要", "通知时间", "确认状态"]
    REQUIRED_FIELDS = ["通知编号", "单据编号", "下游数据集"]
    STATUS_ORDER = ["待发送", "已发送", "已确认", "催办中"]
    ACTION_RULES = {"发起发送": "已发送", "确认适配": "已确认", "发起催办": "催办中"}
    NEGATIVE_ACTIONS = ["发起催办"]

    def unconfirmed_notices(self) -> list[dict[str, Any]]:
        """返回全部未确认的通知。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("确认状态") != "已确认"
        ]

    def confirm_notice(self, notice_no: str) -> tuple[bool, str]:
        """确认通知适配完成。"""
        for row in store.rows(self.MODULE):
            if str(row.get("通知编号")) == notice_no:
                row["确认状态"] = "已确认"
                row["status"] = "已确认"
                row["pending"] = False
                return True, f"通知{notice_no}已确认"
        return False, f"通知{notice_no}不存在"

    def remind(self, notice_no: str) -> tuple[bool, str]:
        """催办未确认通知。"""
        for row in store.rows(self.MODULE):
            if str(row.get("通知编号")) == notice_no:
                if row.get("确认状态") == "已确认":
                    return False, f"通知{notice_no}已确认，无需催办"
                row["status"] = "催办中"
                row["pending"] = True
                row["abnormal"] = True
                return True, f"通知{notice_no}已发起催办"
        return False, f"通知{notice_no}不存在"

    def notice_summary_for_ticket(
        self, ticket_no: str,
    ) -> dict[str, Any]:
        """汇总某重述单的通知情况。"""
        notices = [
            row for row in store.rows(self.MODULE)
            if str(row.get("单据编号")) == ticket_no
        ]
        return {
            "ticket": ticket_no,
            "total": len(notices),
            "confirmed": sum(1 for n in notices if n.get("确认状态") == "已确认"),
            "pending": sum(1 for n in notices if n.get("确认状态") == "待确认"),
            "reminding": sum(1 for n in notices if n.get("status") == "催办中"),
        }

    def downstream_by_dataset(
        self, dataset_id: str,
    ) -> list[dict[str, Any]]:
        """返回指向某下游数据集的所有通知。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("下游数据集") == dataset_id
        ]