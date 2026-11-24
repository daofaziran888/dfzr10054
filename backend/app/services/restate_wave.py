"""重述波次领域服务：波次拆分、版本分配、波次状态汇总、跳过版本计数。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class RestateWaveService(BaseModuleService):
    MODULE = "restate_wave"
    ENTITY = "波次批次"
    OPERATION_TERM = "调度"
    LIST_FIELDS = ["波次编号", "单据编号", "波次序", "重述版本数", "跳过数量", "生成时间"]
    REQUIRED_FIELDS = ["波次编号", "单据编号", "波次序"]
    STATUS_ORDER = ["待执行", "执行中", "已完成", "部分失败"]
    ACTION_RULES = {"发起执行": "执行中", "确认完成": "已完成", "登记部分失败": "部分失败"}
    NEGATIVE_ACTIONS = ["登记部分失败"]

    def waves_by_ticket(self, ticket_no: str) -> list[dict[str, Any]]:
        """返回某重述单下全部波次，按波次序排序。"""
        waves = [
            row for row in store.rows(self.MODULE)
            if str(row.get("单据编号")) == ticket_no
        ]
        waves.sort(key=lambda r: int(str(r.get("波次序", 0))))
        return waves

    def wave_completion_rate(self, ticket_no: str) -> float:
        """某重述单的波次完成率。"""
        waves = self.waves_by_ticket(ticket_no)
        if not waves:
            return 0.0
        done = sum(1 for w in waves if w.get("status") in ("已完成",))
        return done / len(waves)

    def partial_failed_waves(self) -> list[dict[str, Any]]:
        """返回全部部分失败的波次。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "部分失败"
        ]

    def total_skip_count(self, ticket_no: str) -> int:
        """汇总某重述单全部波次的跳过版本总数。"""
        return sum(
            int(str(row.get("跳过数量", 0)))
            for row in store.rows(self.MODULE)
            if str(row.get("单据编号")) == ticket_no
        )

    def consolidate_waves(self, ticket_no: str) -> dict[str, Any]:
        """汇总某重述单波次执行情况。"""
        waves = self.waves_by_ticket(ticket_no)
        return {
            "ticket_no": ticket_no,
            "total_waves": len(waves),
            "completed": sum(1 for w in waves if w.get("status") == "已完成"),
            "partial_failed": sum(1 for w in waves if w.get("status") == "部分失败"),
            "total_skip": self.total_skip_count(ticket_no),
            "total_versions": sum(
                int(str(w.get("重述版本数", 0))) for w in waves
            ),
        }