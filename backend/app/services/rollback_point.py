"""回滚点领域服务：在关键版本快照上设置点位，产出点位条目数据集供失败恢复校验。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class RollbackPointService(BaseModuleService):
    MODULE = "rollback_point"
    ENTITY = "点位条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["点位编号", "版本序号", "点位标记", "创建时间", "已用次数", "点位状态"]
    REQUIRED_FIELDS = ["点位编号", "版本序号", "点位标记"]
    STATUS_ORDER = ["已设置", "可用", "已使用", "已失效"]
    ACTION_RULES = {"标记使用": "可用", "恢复点位": "已使用", "失效点位": "已失效"}
    NEGATIVE_ACTIONS = ["失效点位"]

    def available_points(self, dataset_id: str) -> list[dict[str, Any]]:
        """返回数据集全部可用回滚点，按版本序号降序。"""
        points = []
        for row in store.rows(self.MODULE):
            if row.get("status") != "可用":
                continue
            version = str(row.get("版本序号", ""))
            for snap in store.rows("snapshot_catalog"):
                if (str(snap.get("版本序号")) == version
                        and snap.get("数据集标识") == dataset_id):
                    points.append(row)
                    break
        return sorted(
            points,
            key=lambda r: int(str(r.get("版本序号", 0))),
            reverse=True,
        )

    def nearest_point(self, dataset_id: str) -> dict[str, Any] | None:
        """返回最近可用回滚点（版本序号最大）。"""
        available = self.available_points(dataset_id)
        return available[0] if available else None

    def use_point(self, point_no: str) -> tuple[bool, str]:
        """使用回滚点（标记为已使用）。"""
        for row in store.rows(self.MODULE):
            if str(row.get("点位编号")) == point_no:
                if row.get("status") != "可用":
                    return False, f"回滚点{point_no}状态不是可用"
                row["status"] = "已使用"
                row["已用次数"] = str(int(str(row.get("已用次数", 0))) + 1)
                return True, f"回滚点{point_no}已使用"
        return False, f"回滚点{point_no}不存在"

    def expire_point(self, point_no: str) -> tuple[bool, str]:
        """废弃回滚点。"""
        for row in store.rows(self.MODULE):
            if str(row.get("点位编号")) == point_no:
                row["status"] = "已失效"
                row["abnormal"] = True
                return True, f"回滚点{point_no}已失效"
        return False, f"回滚点{point_no}不存在"

    def point_usage_summary(self) -> dict[str, Any]:
        """回滚点使用汇总。"""
        rows = store.rows(self.MODULE)
        return {
            "total": len(rows),
            "available": sum(1 for r in rows if r.get("status") == "可用"),
            "used": sum(1 for r in rows if r.get("status") == "已使用"),
            "expired": sum(1 for r in rows if r.get("status") == "已失效"),
            "total_usage": sum(int(str(r.get("已用次数", 0))) for r in rows),
        }