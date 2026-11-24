"""审计轨迹领域服务：轨迹追加查询、操作类型统计、存疑轨迹筛选。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class AuditTrailService(BaseModuleService):
    MODULE = "audit_trail"
    ENTITY = "轨迹明细"
    OPERATION_TERM = "写入"
    LIST_FIELDS = ["轨迹编号", "操作类型", "操作对象", "操作者", "操作时间", "轨迹摘要"]
    REQUIRED_FIELDS = ["轨迹编号", "操作类型", "操作对象"]
    STATUS_ORDER = ["已记录", "待复核", "已复核", "存疑中"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记存疑": "存疑中"}
    NEGATIVE_ACTIONS = ["登记存疑"]

    def trail_for_object(self, obj_id: str) -> list[dict[str, Any]]:
        """查询某操作对象（重述单/快照/闸口）的全部轨迹。"""
        return [
            row for row in store.rows(self.MODULE)
            if str(row.get("操作对象")) == obj_id
        ]

    def operation_type_stats(self) -> dict[str, int]:
        """操作类型频次统计。"""
        stats: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            op_type = str(row.get("操作类型", ""))
            stats[op_type] = stats.get(op_type, 0) + 1
        return stats

    def suspicious_trails(self) -> list[dict[str, Any]]:
        """返回全部存疑轨迹。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "存疑中"
        ]

    def recent_operations(
        self, operator: str, limit: int = 10,
    ) -> list[dict[str, Any]]:
        """查询某操作者的最近操作轨迹。"""
        trails = [
            row for row in store.rows(self.MODULE)
            if row.get("操作者") == operator
        ]
        trails.sort(key=lambda r: str(r.get("操作时间", "")), reverse=True)
        return trails[:limit]

    def mark_suspicious(self, trail_no: str, reason: str) -> tuple[bool, str]:
        """标记轨迹为存疑。"""
        for row in store.rows(self.MODULE):
            if str(row.get("轨迹编号")) == trail_no:
                row["status"] = "存疑中"
                row["轨迹摘要"] = f"{row.get('轨迹摘要', '')} | 存疑原因：{reason}"
                row["pending"] = True
                row["abnormal"] = True
                return True, f"轨迹{trail_no}已标记存疑"
        return False, f"轨迹{trail_no}不存在"