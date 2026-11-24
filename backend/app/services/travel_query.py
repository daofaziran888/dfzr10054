"""时点查询领域服务：命中版本二分查找、查询结果登记，产出查询单数据集并记录命中失败。"""
from __future__ import annotations

import bisect
from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class TravelQueryService(BaseModuleService):
    MODULE = "travel_query"
    ENTITY = "查询单"
    OPERATION_TERM = "查询"
    LIST_FIELDS = ["查询编号", "数据集标识", "查询时点", "命中版本", "返回条数", "查询耗时", "查询时间"]
    REQUIRED_FIELDS = ["查询编号", "数据集标识", "查询时点"]
    STATUS_ORDER = ["查询中", "待复核", "已完成", "命中失败"]
    ACTION_RULES = {"提交复核": "待复核", "确认完成": "已完成", "登记失败": "命中失败"}
    NEGATIVE_ACTIONS = ["登记失败"]

    def binary_hit(self, dataset_id: str, travel_time: str) -> int:
        """二分查找不超过查询时点的最新已编目版本序号，未命中返回0。"""
        pairs = sorted(
            (
                str(row.get("快照时间", "")),
                int(str(row.get("版本序号", 0))),
            )
            for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        times = [t for t, _ in pairs]
        idx = bisect.bisect_right(times, travel_time) - 1
        if idx < 0:
            return 0
        return pairs[idx][1]

    def execute_query(
        self, query_no: str, dataset_id: str, travel_time: str,
    ) -> tuple[dict[str, Any] | None, str]:
        """执行时点查询：命中则记录条数与耗时，未命中登记失败。"""
        hit_version = self.binary_hit(dataset_id, travel_time)
        query = None
        for row in store.rows(self.MODULE):
            if str(row.get("查询编号")) == query_no:
                query = row
                break
        if query is None:
            return None, f"查询单{query_no}不存在"

        query["数据集标识"] = dataset_id
        query["查询时点"] = travel_time
        if hit_version == 0:
            query["status"] = "命中失败"
            query["命中版本"] = ""
            query["返回条数"] = "0"
            query["pending"] = True
            query["abnormal"] = True
            return query, f"查询{query_no}命中失败：无不超过{travel_time}的版本"

        snapshot = next(
            (
                row for row in store.rows("snapshot_catalog")
                if row.get("数据集标识") == dataset_id
                and str(row.get("版本序号")) == str(hit_version)
                and row.get("status") == "已编目"
            ),
            None,
        )
        query["status"] = "已完成"
        query["命中版本"] = str(hit_version)
        query["返回条数"] = str(snapshot.get("记录条数", 0)) if snapshot else "0"
        query["pending"] = False
        query["abnormal"] = False
        return query, f"查询{query_no}命中版本{hit_version}"

    def failed_queries(self) -> list[dict[str, Any]]:
        """返回全部命中失败查询单。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "命中失败"
        ]

    def hit_rate(self) -> float:
        """查询命中率：已完成/（已完成+命中失败）。"""
        done = sum(1 for r in store.rows(self.MODULE) if r.get("status") == "已完成")
        failed = len(self.failed_queries())
        total = done + failed
        return done / total if total else 0.0