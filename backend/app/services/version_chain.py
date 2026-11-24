"""版本链领域服务：前后继校验、断裂检测、链上版本遍历。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class VersionChainService(BaseModuleService):
    MODULE = "version_chain"
    ENTITY = "链条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["链编号", "数据集标识", "前序版本", "后继版本", "变更摘要", "链生成时间"]
    REQUIRED_FIELDS = ["链编号", "数据集标识", "前序版本"]
    STATUS_ORDER = ["已记录", "待校验", "已校验", "链断裂"]
    ACTION_RULES = {"提交校验": "待校验", "确认校验": "已校验", "登记断裂": "链断裂"}
    NEGATIVE_ACTIONS = ["登记断裂"]

    def validate_link(self, link_id: int) -> tuple[bool, str]:
        """校验链条目：后继必须等于前序+1，否则登记断裂。"""
        row = store.find(self.MODULE, link_id)
        if row is None:
            return False, f"链条目{link_id}不存在"
        prev = int(str(row.get("前序版本", 0)))
        nxt = int(str(row.get("后继版本", 0)))
        if nxt - prev == 1:
            row["status"] = "已校验"
            row["pending"] = False
            row["abnormal"] = False
            return True, f"链条目{link_id}校验通过：{prev}→{nxt}连续"
        row["status"] = "链断裂"
        row["pending"] = True
        row["abnormal"] = True
        return False, f"链条目{link_id}断裂：{prev}→{nxt}缺少中间版本"

    def detect_all_breaks(self, dataset_id: str) -> list[int]:
        """检测数据集全部断裂链条目并标记，返回断裂条目id列表。"""
        breaks = []
        for row in store.rows(self.MODULE):
            if row.get("数据集标识") != dataset_id:
                continue
            prev = int(str(row.get("前序版本", 0)))
            nxt = int(str(row.get("后继版本", 0)))
            if nxt - prev != 1:
                row["status"] = "链断裂"
                row["abnormal"] = True
                breaks.append(int(row.get("id", 0)))
        return breaks

    def chain_versions(self, dataset_id: str) -> list[int]:
        """沿已校验链遍历数据集全部版本序号（去重升序）。"""
        versions: set[int] = set()
        for row in store.rows(self.MODULE):
            if row.get("数据集标识") == dataset_id:
                versions.add(int(str(row.get("前序版本", 0))))
                versions.add(int(str(row.get("后继版本", 0))))
        return sorted(versions)

    def find_successor(self, dataset_id: str, version: int) -> int | None:
        """查找某版本的后继版本，无则返回None。"""
        for row in store.rows(self.MODULE):
            if (row.get("数据集标识") == dataset_id
                    and int(str(row.get("前序版本", -1))) == version):
                return int(str(row.get("后继版本")))
        return None

    def find_predecessor(self, dataset_id: str, version: int) -> int | None:
        """查找某版本的前序版本，无则返回None。"""
        for row in store.rows(self.MODULE):
            if (row.get("数据集标识") == dataset_id
                    and int(str(row.get("后继版本", -1))) == version):
                return int(str(row.get("前序版本")))
        return None

    def chain_stats(self, dataset_id: str) -> dict[str, Any]:
        """链统计：总条目、已校验、断裂数。"""
        rows = [
            row for row in store.rows(self.MODULE)
            if row.get("数据集标识") == dataset_id
        ]
        return {
            "total": len(rows),
            "validated": sum(1 for r in rows if r.get("status") == "已校验"),
            "broken": sum(1 for r in rows if r.get("status") == "链断裂"),
        }