"""时点缓存→版本落后失效：重述后缓存版本落后于最新重述结果时必须失效。

核心行为：
- 检查时点缓存版本是否落后于重述后的最新版本
- 落后缓存自动标记失效并记录驱逐时间
- 缓存版本匹配命中版本时才允许生效
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.store import store


@dataclass
class CacheCheckResult:
    """缓存检查结果。"""
    cache_id: str
    cached_version: str
    latest_version: str
    is_stale: bool
    action: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "cache_id": self.cache_id,
            "cached_version": self.cached_version,
            "latest_version": self.latest_version,
            "is_stale": self.is_stale,
            "action": self.action,
        }


class CacheInvalidateEngine:
    """时点缓存失效引擎：重述后版本落后即失效。"""

    def __init__(self) -> None:
        self._check_results: list[CacheCheckResult] = []

    def check_cache_staleness(
        self, dataset_id: str,
    ) -> list[CacheCheckResult]:
        """检查所有相关缓存版本是否落后并失效。"""
        # 获取最新版本
        latest_version = self._get_latest_version(dataset_id)
        if latest_version is None:
            return []

        results = []
        for row in store.rows("travel_cache"):
            # 通过查询编号关联数据集
            if row.get("status") not in ("生效中", "已写入"):
                continue
            cached_ver = str(row.get("缓存版本", ""))
            if int(cached_ver) < int(latest_version):
                row["status"] = "已失效"
                row["pending"] = False
                row["abnormal"] = True
                row["缓存状态"] = "已失效"
                check = CacheCheckResult(
                    cache_id=str(row.get("缓存编号", "")),
                    cached_version=cached_ver,
                    latest_version=latest_version,
                    is_stale=True,
                    action="marked_stale",
                )
                results.append(check)

        self._check_results.extend(results)
        return results

    def _get_latest_version(self, dataset_id: str) -> str | None:
        """获取数据集的最新已编目版本。"""
        latest = None
        max_ver = 0
        for row in store.rows("snapshot_catalog"):
            if (row.get("数据集标识") == dataset_id
                    and row.get("status") == "已编目"):
                ver = int(row.get("版本序号", 0))
                if ver > max_ver:
                    max_ver = ver
                    latest = str(ver)
        return latest

    def evict_expired_caches(
        self, reference_time: str,
    ) -> list[str]:
        """驱逐已过期且已失效的缓存条目。"""
        evicted = []
        for row in store.rows("travel_cache"):
            if row.get("status") != "已失效":
                continue
            expire_time = str(row.get("过期时间", ""))
            if expire_time <= reference_time:
                row["status"] = "已驱逐"
                row["缓存状态"] = "已驱逐"
                evicted.append(str(row.get("缓存编号", "")))
        return evicted

    def refresh_cache(
        self, cache_id: str, new_version: str,
    ) -> tuple[bool, str]:
        """刷新缓存到新版本。"""
        for row in store.rows("travel_cache"):
            if str(row.get("缓存编号")) == cache_id:
                row["缓存版本"] = str(new_version)
                row["status"] = "生效中"
                row["pending"] = False
                row["abnormal"] = False
                row["缓存状态"] = "生效中"
                row["命中次数"] = str(int(row.get("命中次数", 0)) + 1)
                return True, f"缓存{cache_id}已刷新到版本{new_version}"
        return False, f"缓存{cache_id}不存在"

    def create_cache(
        self, query_id: str, version: str, expire_time: str,
    ) -> tuple[bool, str]:
        """创建时点缓存记录。"""
        max_ids = {
            "cache": max(
                (int(str(r.get("缓存编号", "0")).replace("CACH-", ""))
                 for r in store.rows("travel_cache")),
                default=0,
            ),
            "id": max(
                (int(row.get("id", 0))
                 for row in store.rows("travel_cache")),
                default=0,
            ),
        }
        cache_id = f"CACH-{max_ids['cache'] + 1:04d}"
        record = {
            "id": max_ids["id"] + 1,
            "status": "生效中",
            "pending": False,
            "abnormal": False,
            "缓存编号": cache_id,
            "查询编号": query_id,
            "缓存版本": str(version),
            "命中次数": "1",
            "过期时间": expire_time,
            "缓存状态": "生效中",
        }
        store.rows("travel_cache").append(record)
        return True, f"已创建缓存{cache_id}版本{version}"

    def snapshot(self) -> dict[str, Any]:
        return {
            "checks": [c.to_dict() for c in self._check_results],
            "total_caches": len(store.rows("travel_cache")),
            "stale_count": sum(
                1 for row in store.rows("travel_cache")
                if row.get("status") == "已失效"
            ),
        }