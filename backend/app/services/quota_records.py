"""配额台账领域服务：容量分配、余量检查、超支告警。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class QuotaRecordsService(BaseModuleService):
    MODULE = "quota_records"
    ENTITY = "台账条目"
    OPERATION_TERM = "计算"
    LIST_FIELDS = ["台账编号", "数据集标识", "容量配额", "已用容量", "配额余量", "台账周期", "更新时间"]
    REQUIRED_FIELDS = ["台账编号", "数据集标识", "容量配额"]
    STATUS_ORDER = ["计量中", "待复核", "已确认", "已超支"]
    ACTION_RULES = {"提交复核": "待复核", "确认台账": "已确认", "登记超支": "已超支"}
    NEGATIVE_ACTIONS = ["登记超支"]

    def check_enough(self, dataset_id: str, needed: int) -> tuple[bool, str]:
        """检查配额余量是否足够。"""
        for row in store.rows(self.MODULE):
            if row.get("数据集标识") == dataset_id:
                remaining = int(str(row.get("配额余量", 0)))
                if remaining >= needed:
                    return True, f"配额充足：余量{remaining}>=需求{needed}"
                return False, f"配额不足：余量{remaining}<需求{needed}"
        return False, f"数据集{dataset_id}无台账记录"

    def reserve_capacity(
        self, dataset_id: str, amount: int,
    ) -> tuple[bool, str]:
        """预占容量配额。"""
        for row in store.rows(self.MODULE):
            if row.get("数据集标识") == dataset_id:
                used = int(str(row.get("已用容量", 0))) + amount
                cap = int(str(row.get("容量配额", 0)))
                row["已用容量"] = str(used)
                row["配额余量"] = str(cap - used)
                if cap - used < 0:
                    row["status"] = "已超支"
                    row["abnormal"] = True
                    return True, f"预占后超支：配额{cap}已用{used}"
                return True, f"预占成功：剩余{cap - used}"
        return False, f"数据集{dataset_id}无台账记录"

    def overdraft_quotas(self) -> list[dict[str, Any]]:
        """返回全部超支台账。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "已超支"
        ]

    def quota_by_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        """返回数据集配额详情。"""
        for row in store.rows(self.MODULE):
            if row.get("数据集标识") == dataset_id:
                return {
                    "dataset": dataset_id,
                    "total": int(str(row.get("容量配额", 0))),
                    "used": int(str(row.get("已用容量", 0))),
                    "remaining": int(str(row.get("配额余量", 0))),
                    "usage_rate": round(
                        int(str(row.get("已用容量", 0)))
                        / max(int(str(row.get("容量配额", 1))), 1),
                        3,
                    ),
                }
        return None

    def total_capacity_summary(self) -> dict[str, Any]:
        """全局容量汇总。"""
        rows = store.rows(self.MODULE)
        total_cap = sum(int(str(r.get("容量配额", 0))) for r in rows)
        total_used = sum(int(str(r.get("已用容量", 0))) for r in rows)
        return {
            "total_capacity": total_cap,
            "total_used": total_used,
            "remaining": total_cap - total_used,
            "datasets": len(rows),
        }