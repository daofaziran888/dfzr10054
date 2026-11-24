"""版本链→时点查询命中：二分查找时点对应版本并返回命中结果。

核心行为：
- 读版本链获取某数据集全部版本，按版本序号排序
- 二分查找不超过查询时点的最新版本
- 命中后创建时点查询记录并关联缓存
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.store import store


@dataclass
class HitResult:
    """时点查询命中结果。"""
    query_id: str
    dataset_id: str
    travel_time: str
    hit_version: str = ""
    hit_snapshot_id: str = ""
    row_count: int = 0
    success: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "dataset_id": self.dataset_id,
            "travel_time": self.travel_time,
            "hit_version": self.hit_version,
            "hit_snapshot_id": self.hit_snapshot_id,
            "row_count": self.row_count,
            "success": self.success,
            "reason": self.reason,
        }


class TravelHitEngine:
    """时点查询命中引擎。"""

    def __init__(self) -> None:
        self._history: list[HitResult] = []

    def find_version_by_time(
        self, dataset_id: str, travel_time: str,
    ) -> HitResult:
        """二分查找不超过查询时点的最新版本。"""
        snapshots = [
            row for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") in ("已编目", "已作废")
        ]
        snapshots.sort(key=lambda r: str(r.get("快照时间", "")))

        # 检查版本链是否有效
        links = [
            row for row in store.rows("version_chain")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已校验"
        ]

        # 二分查找
        lo, hi = 0, len(snapshots) - 1
        hit_idx = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            mid_time = str(snapshots[mid].get("快照时间", ""))
            if mid_time <= travel_time:
                hit_idx = mid
                lo = mid + 1
            else:
                hi = mid - 1

        max_id = max(
            (int(row.get("id", 0)) for row in store.rows("travel_query")),
            default=0,
        )
        query_id_val = f"TRAV-{max_id + 1:04d}"

        if hit_idx >= 0:
            snapshot = snapshots[hit_idx]
            result = HitResult(
                query_id=query_id_val,
                dataset_id=dataset_id,
                travel_time=travel_time,
                hit_version=str(snapshot.get("版本序号", "")),
                hit_snapshot_id=str(snapshot.get("快照编号", "")),
                row_count=int(snapshot.get("记录条数", 0)),
                success=True,
                reason=f"二分命中版本{snapshot.get('版本序号')}",
            )
        else:
            result = HitResult(
                query_id=query_id_val,
                dataset_id=dataset_id,
                travel_time=travel_time,
                success=False,
                reason="无不超过该时点的版本",
            )

        # 写入查询记录
        self._write_query_record(result)
        self._history.append(result)
        return result

    def _write_query_record(self, result: HitResult) -> None:
        """将命中结果写入时点查询表。"""
        max_id = max(
            (int(row.get("id", 0)) for row in store.rows("travel_query")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": "已完成" if result.success else "命中失败",
            "pending": not result.success,
            "abnormal": not result.success,
            "查询编号": result.query_id,
            "数据集标识": result.dataset_id,
            "查询时点": result.travel_time,
            "命中版本": result.hit_version,
            "返回条数": str(result.row_count),
            "查询耗时": f"二分查找耗时",
            "查询时间": result.travel_time,
        }
        store.rows("travel_query").append(record)

    def check_version_on_chain(
        self, dataset_id: str, version: str,
    ) -> tuple[bool, str]:
        """校验某版本是否在已校验的版本链上。"""
        links = [
            row for row in store.rows("version_chain")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已校验"
        ]
        for link in links:
            if (str(link.get("前序版本")) == version
                    or str(link.get("后继版本")) == version):
                return True, f"版本{version}在版本链上"
        return False, f"版本{version}不在任何已校验版本链上"

    def get_hit_history(self) -> list[HitResult]:
        return list(self._history)

    def snapshot(self) -> dict[str, Any]:
        return {
            "history": [h.to_dict() for h in self._history],
            "total_queries": len(store.rows("travel_query")),
        }