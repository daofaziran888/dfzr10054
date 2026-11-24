"""重述指标领域服务：及时率计算、平均耗时、通知确认率追踪，产出指标快照数据集。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class RestateMetricsService(BaseModuleService):
    MODULE = "restate_metrics"
    ENTITY = "指标快照"
    OPERATION_TERM = "计算"
    LIST_FIELDS = ["快照编号", "统计日期", "重述及时率", "平均重述耗时", "通知确认率", "快照时间"]
    REQUIRED_FIELDS = ["快照编号", "统计日期"]
    STATUS_ORDER = ["已生成", "待复核", "已复核", "已发布"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "发布快照": "已发布"}
    NEGATIVE_ACTIONS = []

    def latest_timeliness(self) -> float:
        """最新重述及时率。"""
        rows = store.rows(self.MODULE)
        if not rows:
            return 0.0
        latest = max(rows, key=lambda r: str(r.get("快照时间", "")))
        return float(str(latest.get("重述及时率", 0)))

    def avg_restate_duration_min(self) -> float:
        """平均重述耗时（分钟）。"""
        rows = store.rows(self.MODULE)
        if not rows:
            return 0.0
        durations = []
        for r in rows:
            val = str(r.get("平均重述耗时", "0"))
            try:
                durations.append(float(val.replace("min", "")))
            except ValueError:
                durations.append(0.0)
        return sum(durations) / len(durations) if durations else 0.0

    def notification_confirm_rate(self) -> float:
        """最新通知确认率。"""
        rows = store.rows(self.MODULE)
        if not rows:
            return 0.0
        latest = max(rows, key=lambda r: str(r.get("快照时间", "")))
        return float(str(latest.get("通知确认率", 0)))

    def metrics_trend(self) -> list[dict[str, Any]]:
        """按日期排序的指标趋势数据。"""
        rows = sorted(
            store.rows(self.MODULE),
            key=lambda r: str(r.get("统计日期", "")),
        )
        return [
            {
                "date": r.get("统计日期"),
                "timeliness": float(str(r.get("重述及时率", 0))),
                "duration": str(r.get("平均重述耗时", "")),
                "confirm_rate": float(str(r.get("通知确认率", 0))),
            }
            for r in rows
        ]