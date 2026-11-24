"""重述失败→回滚点恢复：重述波次部分失败时按最近回滚点恢复数据集。

核心行为：
- 重述波次为部分失败时触发回滚恢复流程
- 查找最近可用回滚点（版本序号最大且状态为可用）
- 恢复数据集快照到回滚点版本，失效已使用的回滚点
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.store import store


@dataclass
class RollbackResult:
    """回滚恢复结果。"""
    rollback_id: str
    target_version: str
    wave_id: str
    recovered_snapshots: int
    success: bool
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollback_id": self.rollback_id,
            "target_version": self.target_version,
            "wave_id": self.wave_id,
            "recovered_snapshots": self.recovered_snapshots,
            "success": self.success,
            "reason": self.reason,
        }


class RollbackRecoverEngine:
    """回滚点恢复引擎：失败波次回退到最近可用回滚点。"""

    def __init__(self) -> None:
        self._results: list[RollbackResult] = []

    def find_nearest_rollback_point(
        self, dataset_id: str,
    ) -> tuple[str | None, str]:
        """查找最近可用回滚点（版本序号最大）。"""
        best_point = None
        best_version = 0
        for row in store.rows("rollback_point"):
            if row.get("status") != "可用":
                continue
            ver = int(row.get("版本序号", 0))
            if ver > best_version:
                # 检查该版本是否属于此数据集
                for snap in store.rows("snapshot_catalog"):
                    if (str(snap.get("版本序号")) == str(ver)
                            and snap.get("数据集标识") == dataset_id):
                        best_version = ver
                        best_point = row
                        break
        if best_point:
            return (
                str(best_point.get("点位编号")),
                f"找到回滚点位{best_point.get('点位编号')}版本{best_point.get('版本序号')}",
            )
        return None, f"数据集{dataset_id}无可用回滚点"

    def recover_from_wave_failure(
        self, wave_id: str, dataset_id: str,
    ) -> RollbackResult:
        """从重述波次失败中恢复数据集。"""
        # 验证波次是否失败
        wave_failed = False
        for row in store.rows("restate_wave"):
            if (str(row.get("波次编号")) == wave_id
                    and row.get("status") == "部分失败"):
                wave_failed = True
                break
        if not wave_failed:
            return RollbackResult(
                "", "", wave_id, 0, False,
                f"波次{wave_id}未处于部分失败状态",
            )

        point_id, msg = self.find_nearest_rollback_point(dataset_id)
        if point_id is None:
            return RollbackResult("", "", wave_id, 0, False, msg)

        # 获取回滚点版本
        point_row = None
        for row in store.rows("rollback_point"):
            if str(row.get("点位编号")) == point_id:
                point_row = row
                break
        if point_row is None:
            return RollbackResult(
                "", "", wave_id, 0, False, "回滚点不存在",
            )

        target_version = str(point_row.get("版本序号", ""))
        recovered = 0

        # 将回滚点之后的快照标记为已作废
        for snap in store.rows("snapshot_catalog"):
            if (snap.get("数据集标识") == dataset_id
                    and int(snap.get("版本序号", 0))
                    > int(target_version)):
                if snap.get("status") == "已编目":
                    snap["status"] = "已作废"
                    snap["abnormal"] = True
                    recovered += 1

        # 标记回滚点已使用
        point_row["status"] = "已使用"
        point_row["pending"] = False
        used_count = int(point_row.get("已用次数", 0)) + 1
        point_row["已用次数"] = str(used_count)

        # 更新波次状态
        for row in store.rows("restate_wave"):
            if str(row.get("波次编号")) == wave_id:
                row["status"] = "已完成"
                row["pending"] = False

        result = RollbackResult(
            rollback_id=point_id,
            target_version=target_version,
            wave_id=wave_id,
            recovered_snapshots=recovered,
            success=True,
            reason=f"恢复到回滚点{point_id}版本{target_version}，已恢复{recovered}个快照",
        )
        self._results.append(result)
        return result

    def set_rollback_point(
        self, dataset_id: str, version: str, label: str,
    ) -> tuple[bool, str]:
        """在指定版本上设置回滚点。"""
        # 确认版本存在且已编目
        version_exists = False
        for snap in store.rows("snapshot_catalog"):
            if (snap.get("数据集标识") == dataset_id
                    and str(snap.get("版本序号")) == version
                    and snap.get("status") in ("已编目",)):
                version_exists = True
                break
        if not version_exists:
            return False, f"版本{version}不存在或未编目"

        max_point_id = max(
            (int(str(r.get("点位编号", "0")).replace("ROLL-", ""))
             for r in store.rows("rollback_point")),
            default=0,
        )
        point_id = f"ROLL-{max_point_id + 1:04d}"
        max_id = max(
            (int(row.get("id", 0))
             for row in store.rows("rollback_point")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": "可用",
            "pending": False,
            "abnormal": False,
            "点位编号": point_id,
            "版本序号": str(version),
            "点位标记": label,
            "创建时间": "",
            "已用次数": "0",
            "点位状态": "可用",
        }
        store.rows("rollback_point").append(record)
        return True, f"已在版本{version}设置回滚点{point_id}"

    def snapshot(self) -> dict[str, Any]:
        return {
            "results": [r.to_dict() for r in self._results],
            "total_points": len(store.rows("rollback_point")),
        }