"""时点缓存领域服务：版本落后检测、缓存刷新、过期驱逐。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class TravelCacheService(BaseModuleService):
    MODULE = "travel_cache"
    ENTITY = "缓存条目"
    OPERATION_TERM = "存储"
    LIST_FIELDS = ["缓存编号", "查询编号", "缓存版本", "命中次数", "过期时间", "缓存状态"]
    REQUIRED_FIELDS = ["缓存编号", "查询编号", "缓存版本"]
    STATUS_ORDER = ["已写入", "生效中", "已失效", "已驱逐"]
    ACTION_RULES = {"标记失效": "已失效", "驱逐缓存": "已驱逐", "刷新缓存": "生效中"}
    NEGATIVE_ACTIONS = ["标记失效", "驱逐缓存"]

    def check_staleness(
        self, dataset_id: str, current_version: int,
    ) -> list[str]:
        """检查所有缓存是否落后于最新版本，落后则标记失效并返回失效编号列表。"""
        stale = []
        for row in store.rows(self.MODULE):
            if row.get("status") not in ("生效中", "已写入"):
                continue
            cached_ver = int(str(row.get("缓存版本", "0")))
            if cached_ver < current_version:
                row["status"] = "已失效"
                row["abnormal"] = True
                row["缓存状态"] = "已失效"
                stale.append(str(row.get("缓存编号")))
        return stale

    def active_caches(self) -> list[dict[str, Any]]:
        """返回全部生效中缓存。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "生效中"
        ]

    def evict_expired(self, reference_time: str) -> list[str]:
        """驱逐已过期且已失效的缓存。"""
        evicted = []
        for row in store.rows(self.MODULE):
            if row.get("status") != "已失效":
                continue
            if str(row.get("过期时间", "")) <= reference_time:
                row["status"] = "已驱逐"
                row["缓存状态"] = "已驱逐"
                evicted.append(str(row.get("缓存编号")))
        return evicted

    def cache_hit_rate(self) -> float:
        """缓存命中率（生效中/总数）。"""
        rows = store.rows(self.MODULE)
        if not rows:
            return 0.0
        active = sum(1 for r in rows if r.get("status") == "生效中")
        return active / len(rows)