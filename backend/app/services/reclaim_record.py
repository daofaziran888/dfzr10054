"""回收记录领域服务：回收可执行性校验、回收统计、释放容量汇总，产出回收明细数据集。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class ReclaimRecordService(BaseModuleService):
    MODULE = "reclaim_record"
    ENTITY = "回收明细"
    OPERATION_TERM = "存储"
    LIST_FIELDS = ["回收编号", "快照编号", "回收层级", "释放容量", "回收时间", "审计标记"]
    REQUIRED_FIELDS = ["回收编号", "快照编号", "回收层级"]
    STATUS_ORDER = ["待回收", "回收中", "已回收", "回收失败"]
    ACTION_RULES = {"发起回收": "回收中", "确认回收": "已回收", "登记失败": "回收失败"}
    NEGATIVE_ACTIONS = ["登记失败"]

    def is_referenced_by_chain(self, snapshot_id: str) -> bool:
        """检查快照是否被版本链引用，被引用则不可回收。"""
        for row in store.rows("snapshot_catalog"):
            if str(row.get("快照编号")) == snapshot_id:
                version = str(row.get("版本序号", ""))
                for link in store.rows("version_chain"):
                    if (str(link.get("前序版本")) == version
                            or str(link.get("后继版本")) == version):
                        return True
        return False

    def reclaimable_snapshots(
        self, dataset_id: str, reference_date: str,
    ) -> list[str]:
        """返回数据集中可回收的快照编号列表。"""
        policy = None
        for row in store.rows("retain_policy"):
            if (row.get("status") == "已生效"
                    and row.get("适用数据集") == dataset_id):
                policy = row
                break
        retain_days = int(str(policy.get("保留天数", 365))) if policy else 365

        result = []
        for row in store.rows("snapshot_catalog"):
            if (row.get("数据集标识") != dataset_id
                    or row.get("status") != "已编目"):
                continue
            snap_time = str(row.get("快照时间", ""))
            if snap_time < reference_date:
                days_old = self._days_between(snap_time, reference_date)
                if days_old > retain_days:
                    if not self.is_referenced_by_chain(
                        str(row.get("快照编号", ""))
                    ):
                        result.append(str(row.get("快照编号")))
        return result

    @staticmethod
    def _days_between(d1: str, d2: str) -> int:
        """简单日期差值（仅用于示例）。"""
        try:
            i1 = int(d1.replace("-", ""))
            i2 = int(d2.replace("-", ""))
            return i2 - i1
        except ValueError:
            return 0

    def released_capacity_total(
        self, dataset_id: str,
    ) -> int:
        """汇总数据集已回收的总释放容量。"""
        total = 0
        for row in store.rows(self.MODULE):
            if row.get("status") != "已回收":
                continue
            snap_id = str(row.get("快照编号", ""))
            for snap in store.rows("snapshot_catalog"):
                if (str(snap.get("快照编号")) == snap_id
                        and snap.get("数据集标识") == dataset_id):
                    total += int(str(row.get("释放容量", 0)))
                    break
        return total

    def reclaim_statistics(self) -> dict[str, Any]:
        """回收统计汇总。"""
        rows = store.rows(self.MODULE)
        return {
            "total": len(rows),
            "completed": sum(1 for r in rows if r.get("status") == "已回收"),
            "failed": sum(1 for r in rows if r.get("status") == "回收失败"),
            "total_released": sum(
                int(str(r.get("释放容量", 0))) for r in rows
                if r.get("status") == "已回收"
            ),
        }