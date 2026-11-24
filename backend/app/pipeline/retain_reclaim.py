"""保留策略→回收记录：超期快照回收必须满足保留策略约束。

核心行为：
- 读保留策略获取最少保留版本数与保留天数
- 筛选超期且可回收的快照（不在版本链被引用、已编目且超期）
- 回收前校验：剩余版本数 >= 最少保留版本、被引用快照不可回收
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.store import store


@dataclass
class ReclaimResult:
    """回收结果。"""
    reclaim_id: str
    snapshot_id: str
    released_capacity: int
    success: bool
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "reclaim_id": self.reclaim_id,
            "snapshot_id": self.snapshot_id,
            "released_capacity": self.released_capacity,
            "success": self.success,
            "reason": self.reason,
        }


class RetainReclaimEngine:
    """保留策略约束下的回收引擎。"""

    def __init__(self) -> None:
        self._results: list[ReclaimResult] = []

    def find_overdue_snapshots(
        self, dataset_id: str, reference_date: str,
    ) -> list[dict[str, Any]]:
        """查找超期快照：快照时间早于参考日期减去保留天数。"""
        policy = self._get_policy(dataset_id)
        retain_days = int(policy.get("保留天数", 365))
        min_versions = int(policy.get("最少保留版本", 3))

        all_snapshots = [
            row for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        ]
        all_snapshots.sort(key=lambda r: str(r.get("快照时间", "")))

        if len(all_snapshots) <= min_versions:
            return []

        # 计算参考日期往前推保留天数的日期
        ref_date_int = int(reference_date.replace("-", ""))
        overdue = []
        for snap in all_snapshots:
            snap_date_str = str(snap.get("快照时间", ""))
            snap_date_int = int(snap_date_str.replace("-", ""))
            if ref_date_int - snap_date_int > retain_days:
                overdue.append(snap)

        return overdue[:-min_versions] if len(overdue) > min_versions else []

    def reclaim_snapshot(
        self, snapshot_id: str,
    ) -> ReclaimResult:
        """回收单个快照，需满足保留策略约束。"""
        snapshot = None
        for row in store.rows("snapshot_catalog"):
            if str(row.get("快照编号")) == snapshot_id:
                snapshot = row
                break
        if snapshot is None:
            return ReclaimResult("", snapshot_id, 0, False, "快照不存在")

        dataset_id = str(snapshot.get("数据集标识", ""))
        policy = self._get_policy(dataset_id)
        min_versions = int(policy.get("最少保留版本", 3))

        # 检查是否有版本链引用
        version = str(snapshot.get("版本序号", ""))
        for row in store.rows("version_chain"):
            if (str(row.get("前序版本")) == version
                    or str(row.get("后继版本")) == version):
                return ReclaimResult(
                    "", snapshot_id, 0, False,
                    f"快照版本{version}被版本链引用，不可回收",
                )

        # 检查剩余版本数
        remaining = [
            row for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("id") != snapshot.get("id")
            and row.get("status") == "已编目"
        ]
        if len(remaining) < min_versions:
            return ReclaimResult(
                "", snapshot_id, 0, False,
                f"回收后剩余{len(remaining)}版本，不满足最少保留{min_versions}版本",
            )

        # 执行回收
        capacity = int(snapshot.get("记录条数", 100))
        max_reclaim_id = max(
            (int(str(r.get("回收编号", "0")).replace("RECL-", ""))
             for r in store.rows("reclaim_record")),
            default=0,
        )
        reclaim_id = f"RECL-{max_reclaim_id + 1:04d}"

        snapshot["status"] = "已作废"
        snapshot["pending"] = False

        max_id = max(
            (int(row.get("id", 0))
             for row in store.rows("reclaim_record")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": "已回收",
            "pending": False,
            "abnormal": False,
            "回收编号": reclaim_id,
            "快照编号": snapshot_id,
            "回收层级": "标准回收",
            "释放容量": str(capacity),
            "回收时间": "",
            "审计标记": "已审计",
        }
        store.rows("reclaim_record").append(record)

        result = ReclaimResult(reclaim_id, snapshot_id, capacity, True, "回收成功")
        self._results.append(result)
        return result

    def _get_policy(self, dataset_id: str) -> dict[str, Any]:
        """获取数据集对应的生效保留策略。"""
        for row in store.rows("retain_policy"):
            if (row.get("status") == "已生效"
                    and row.get("适用数据集") == dataset_id):
                return row
        return {"最少保留版本": "3", "保留天数": "365"}

    def validate_reclaim_constraint(
        self, dataset_id: str, candidate_snapshots: list[str],
    ) -> tuple[bool, str]:
        """校验回收候选快照是否满足保留策略。"""
        policy = self._get_policy(dataset_id)
        min_versions = int(policy.get("最少保留版本", 3))

        all_count = sum(
            1 for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        )
        remaining = all_count - len(candidate_snapshots)
        if remaining < min_versions:
            return False, (
                f"回收后剩余{remaining}版本，不满足最少保留{min_versions}版本"
            )
        return True, "满足保留策略约束"

    def snapshot(self) -> dict[str, Any]:
        return {
            "results": [r.to_dict() for r in self._results],
            "total_reclaims": len(store.rows("reclaim_record")),
        }