"""访问台账领域服务：访问审计、敏感用途检查、访问统计，产出访问明细数据集。"
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class AccessRecordsService(BaseModuleService):
    MODULE = "access_records"
    ENTITY = "访问明细"
    OPERATION_TERM = "查询"
    LIST_FIELDS = ["访问编号", "查询编号", "访问者", "访问行数", "访问时间", "用途标记"]
    REQUIRED_FIELDS = ["访问编号", "查询编号", "访问者"]
    STATUS_ORDER = ["已记录", "待复核", "已复核", "存疑中"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记存疑": "存疑中"}
    NEGATIVE_ACTIONS = ["登记存疑"]

    def suspicious_accesses(self) -> list[dict[str, Any]]:
        """返回全部存疑访问记录。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "存疑中"
        ]

    def access_summary_by_user(self) -> dict[str, int]:
        """按访问者汇总访问行数。"""
        summary: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            user = str(row.get("访问者", ""))
            rows_count = int(str(row.get("访问行数", 0)))
            summary[user] = summary.get(user, 0) + rows_count
        return summary

    def usage_mark_stats(self) -> dict[str, int]:
        """用途标记分类统计。"""
        stats: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            mark = str(row.get("用途标记", ""))
            stats[mark] = stats.get(mark, 0) + 1
        return stats

    def verify_usage(
        self, access_no: str, is_legitimate: bool,
    ) -> tuple[bool, str]:
        """复核访问用途。"""
        for row in store.rows(self.MODULE):
            if str(row.get("访问编号")) == access_no:
                if is_legitimate:
                    row["status"] = "已复核"
                    row["pending"] = False
                    return True, f"访问{access_no}用途复核通过"
                else:
                    row["status"] = "存疑中"
                    row["pending"] = True
                    row["abnormal"] = True
                    return True, f"访问{access_no}标记存疑"
        return False, f"访问{access_no}不存在"

    def recent_accesses(
        self, query_no: str, limit: int = 10,
    ) -> list[dict[str, Any]]:
        """查询某查询单的最近访问记录。"""
        records = sorted(
            [
                row for row in store.rows(self.MODULE)
                if str(row.get("查询编号")) == query_no
            ],
            key=lambda r: str(r.get("访问时间", "")),
            reverse=True,
        )
        return records[:limit]