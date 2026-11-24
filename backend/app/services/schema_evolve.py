"""模式演进领域服务：兼容性判定、演出版本追踪、字段变更统计，产出演进记录数据集。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class SchemaEvolveService(BaseModuleService):
    MODULE = "schema_evolve"
    ENTITY = "演进记录"
    OPERATION_TERM = "迁移"
    LIST_FIELDS = ["演进编号", "数据集标识", "变更字段数", "兼容标记", "演出版本", "演进时间"]
    REQUIRED_FIELDS = ["演进编号", "数据集标识", "变更字段数"]
    STATUS_ORDER = ["草拟中", "待评审", "已合入", "已回退"]
    ACTION_RULES = {"提交评审": "待评审", "合入演进": "已合入", "回退演进": "已回退"}
    NEGATIVE_ACTIONS = ["回退演进"]

    def compatible_evolves(self, dataset_id: str) -> list[dict[str, Any]]:
        """返回数据集的向前兼容演进记录。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("数据集标识") == dataset_id
            and row.get("兼容标记") == "向前兼容"
        ]

    def incompatible_evolves(self) -> list[dict[str, Any]]:
        """返回全部不兼容演进记录。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("兼容标记") == "不兼容"
        ]

    def latest_evolve_version(self, dataset_id: str) -> str:
        """获取数据集最新演进版本。"""
        best = ""
        for row in store.rows(self.MODULE):
            if (row.get("数据集标识") == dataset_id
                    and row.get("status") == "已合入"):
                ver = str(row.get("演出版本", ""))
                if ver > best:
                    best = ver
        return best

    def can_read_old_snapshot(
        self, dataset_id: str, evolve_version: str,
    ) -> bool:
        """判断旧版本快照能否被新演进版本读取。"""
        for row in store.rows(self.MODULE):
            if (row.get("数据集标识") == dataset_id
                    and row.get("演出版本") == evolve_version):
                return str(row.get("兼容标记", "")) == "向前兼容"
        return True

    def field_change_summary(self) -> dict[str, int]:
        """各数据集字段变更总数。"""
        summary: dict[str, int] = {}
        for row in store.rows(self.MODULE):
            ds = str(row.get("数据集标识", ""))
            changes = int(str(row.get("变更字段数", 0)))
            summary[ds] = summary.get(ds, 0) + changes
        return summary