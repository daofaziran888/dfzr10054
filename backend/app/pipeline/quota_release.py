"""回收记录→配额释放：回收完成后更新配额台账释放已用容量。

核心行为：
- 读回收记录获取释放容量总数
- 更新对应数据集的配额台账已用容量与余量
- 超支状态在配额恢复后自动消除
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.store import store


@dataclass
class QuotaUpdate:
    """配额更新结果。"""
    dataset_id: str
    released_capacity: int
    new_used: int
    new_remaining: int
    is_overdraft: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "released_capacity": self.released_capacity,
            "new_used": self.new_used,
            "new_remaining": self.new_remaining,
            "is_overdraft": self.is_overdraft,
        }


class QuotaReleaseEngine:
    """配额释放引擎：回收后更新配额台账。"""

    def __init__(self) -> None:
        self._updates: list[QuotaUpdate] = []

    def release_quota_from_reclaims(
        self, dataset_id: str,
    ) -> QuotaUpdate:
        """汇总该数据集所有已回收记录的释放容量，更新配额台账。"""
        total_released = 0
        for row in store.rows("reclaim_record"):
            if row.get("status") != "已回收":
                continue
            snapshot_id = str(row.get("快照编号", ""))
            for snap in store.rows("snapshot_catalog"):
                if (str(snap.get("快照编号")) == snapshot_id
                        and snap.get("数据集标识") == dataset_id):
                    total_released += int(row.get("释放容量", 0))
                    break

        quota = self._get_or_create_quota(dataset_id)
        current_used = int(quota.get("已用容量", 0))
        cap = int(quota.get("容量配额", 10000))
        new_used = max(0, current_used - total_released)
        new_remaining = cap - new_used

        quota["已用容量"] = str(new_used)
        quota["配额余量"] = str(new_remaining)
        quota["status"] = "已确认" if new_remaining >= 0 else "已超支"
        quota["pending"] = new_remaining < 0
        quota["abnormal"] = new_remaining < 0

        update = QuotaUpdate(
            dataset_id=dataset_id,
            released_capacity=total_released,
            new_used=new_used,
            new_remaining=new_remaining,
            is_overdraft=new_remaining < 0,
        )
        self._updates.append(update)
        return update

    def _get_or_create_quota(self, dataset_id: str) -> dict[str, Any]:
        """获取或创建数据集配额台账。"""
        for row in store.rows("quota_records"):
            if row.get("数据集标识") == dataset_id:
                return row
        max_id = max(
            (int(row.get("id", 0))
             for row in store.rows("quota_records")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": "已确认",
            "pending": False,
            "abnormal": False,
            "台账编号": f"QUOT-{max_id + 1:04d}",
            "数据集标识": dataset_id,
            "容量配额": "10000",
            "已用容量": "0",
            "配额余量": "10000",
            "台账周期": "2026Q4",
            "更新时间": "",
        }
        store.rows("quota_records").append(record)
        return record

    def check_quota_before_write(
        self, dataset_id: str, needed_capacity: int,
    ) -> tuple[bool, str]:
        """快照写入前检查配额余量是否足够。"""
        quota = self._get_or_create_quota(dataset_id)
        remaining = int(quota.get("配额余量", 0))
        if remaining < needed_capacity:
            return False, (
                f"配额余量{remaining}不足，需{needed_capacity}容量，"
                f"请先执行回收"
            )
        # 预占
        quota["已用容量"] = str(int(quota.get("已用容量", 0)) + needed_capacity)
        quota["配额余量"] = str(int(quota.get("容量配额", 10000))
                                - int(quota.get("已用容量", 0)))
        return True, f"配额余量充足，已预占{needed_capacity}容量"

    def snapshot(self) -> dict[str, Any]:
        return {
            "updates": [u.to_dict() for u in self._updates],
            "total_quotas": len(store.rows("quota_records")),
        }