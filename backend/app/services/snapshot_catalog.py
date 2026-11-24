"""快照编目领域服务：编目状态推进、版本序号连续性检查、超期筛选。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class SnapshotCatalogService(BaseModuleService):
    MODULE = "snapshot_catalog"
    ENTITY = "快照条目"
    OPERATION_TERM = "存储"
    LIST_FIELDS = ["快照编号", "数据集标识", "快照时间", "版本序号", "记录条数", "存储分区", "编目状态"]
    REQUIRED_FIELDS = ["快照编号", "数据集标识", "快照时间"]
    STATUS_ORDER = ["写入中", "待编目", "已编目", "已作废"]
    ACTION_RULES = {"提交编目": "待编目", "确认编目": "已编目", "作废快照": "已作废"}
    NEGATIVE_ACTIONS = ["作废快照"]

    def catalog_confirm(self, snapshot_no: str) -> tuple[bool, str]:
        """确认编目：快照必须已完成写入且记录条数大于0。"""
        for row in store.rows(self.MODULE):
            if str(row.get("快照编号")) == snapshot_no:
                if row.get("status") == "写入中":
                    return False, f"快照{snapshot_no}仍在写入中，不能确认编目"
                if int(str(row.get("记录条数", 0))) <= 0:
                    return False, f"快照{snapshot_no}记录条数为0，不能确认编目"
                row["status"] = "已编目"
                row["编目状态"] = "已编目"
                row["pending"] = False
                return True, f"快照{snapshot_no}已确认编目"
        return False, f"快照{snapshot_no}不存在"

    def find_version_gaps(self, dataset_id: str) -> list[tuple[int, int]]:
        """检测数据集已编目版本序号的缺口：返回(前版本, 后版本)对。"""
        versions = sorted(
            int(str(row.get("版本序号", 0)))
            for row in store.rows(self.MODULE)
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        gaps = []
        for i in range(len(versions) - 1):
            if versions[i + 1] - versions[i] > 1:
                gaps.append((versions[i], versions[i + 1]))
        return gaps

    def latest_catalogued_version(self, dataset_id: str) -> int:
        """返回数据集最新已编目版本序号，无则返回0。"""
        return max(
            (
                int(str(row.get("版本序号", 0)))
                for row in store.rows(self.MODULE)
                if row.get("数据集标识") == dataset_id
                and row.get("status") == "已编目"
            ),
            default=0,
        )

    def is_referenced_by_chain(self, snapshot_no: str) -> bool:
        """判断快照的版本序号是否被版本链引用（被引用则不可回收）。"""
        snap = None
        for row in store.rows(self.MODULE):
            if str(row.get("快照编号")) == snapshot_no:
                snap = row
                break
        if snap is None:
            return False
        version = str(snap.get("版本序号"))
        for link in store.rows("version_chain"):
            if link.get("数据集标识") != snap.get("数据集标识"):
                continue
            if (str(link.get("前序版本")) == version
                    or str(link.get("后继版本")) == version):
                return True
        return False

    def dataset_snapshot_time_range(self, dataset_id: str) -> tuple[str, str]:
        """返回数据集已编目快照的最早与最晚时间。"""
        times = sorted(
            str(row.get("快照时间", ""))
            for row in store.rows(self.MODULE)
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        if not times:
            return "", ""
        return times[0], times[-1]

    def catalog_stats(self) -> dict[str, Any]:
        """编目统计：总数、已编目、待编目、写入中、版本缺口数据集数。"""
        rows = store.rows(self.MODULE)
        datasets = {str(row.get("数据集标识")) for row in rows}
        gap_datasets = sum(
            1 for ds in datasets if self.find_version_gaps(ds)
        )
        return {
            "total": len(rows),
            "catalogued": sum(1 for r in rows if r.get("status") == "已编目"),
            "pending_catalog": sum(1 for r in rows if r.get("status") == "待编目"),
            "writing": sum(1 for r in rows if r.get("status") == "写入中"),
            "datasets_with_gaps": gap_datasets,
        }