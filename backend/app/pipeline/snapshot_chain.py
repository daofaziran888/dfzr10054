"""快照编目→版本链构建：入编快照后自动登记前后继关系并校验链完整性。

核心行为：
- 从快照编目读取已编目快照，按数据集分组按版本序号排序
- 为相邻版本对创建版本链条目，填充前序版本与后继版本
- 校验版本链是否有断裂（两快照版本序号不连续）
- 断裂条目标记链断裂状态
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.store import store


@dataclass
class ChainBuildResult:
    """版本链构建结果。"""
    dataset_id: str
    new_links: int = 0
    chain_breaks: int = 0
    link_ids: list[int] = None

    def __post_init__(self):
        if self.link_ids is None:
            self.link_ids = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "new_links": self.new_links,
            "chain_breaks": self.chain_breaks,
            "link_ids": self.link_ids,
        }


class SnapshotChainEngine:
    """快照编目到版本链的构建引擎。"""

    def __init__(self) -> None:
        self._results: list[ChainBuildResult] = []

    def build_chain_for_dataset(self, dataset_id: str) -> ChainBuildResult:
        """为指定数据集的已编目快照构建版本链。"""
        snapshots = [
            row for row in store.rows("snapshot_catalog")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已编目"
        ]
        snapshots.sort(key=lambda r: int(r.get("版本序号", 0)))

        result = ChainBuildResult(dataset_id=dataset_id)
        if len(snapshots) < 2:
            self._results.append(result)
            return result

        existing_links = {}
        for row in store.rows("version_chain"):
            if row.get("数据集标识") == dataset_id:
                existing_links[(row.get("前序版本"), row.get("后继版本"))] = row

        max_id = max(
            (int(row.get("id", 0)) for row in store.rows("version_chain")),
            default=0,
        )

        for i in range(len(snapshots) - 1):
            prev_ver = str(snapshots[i].get("版本序号"))
            next_ver = str(snapshots[i + 1].get("版本序号"))
            if (prev_ver, next_ver) in existing_links:
                continue

            max_id += 1
            chain_time = str(snapshots[i + 1].get("快照时间", ""))
            link = {
                "id": max_id,
                "status": "已记录",
                "pending": True,
                "abnormal": False,
                "链编号": f"CHAIN-{max_id:04d}",
                "数据集标识": dataset_id,
                "前序版本": prev_ver,
                "后继版本": next_ver,
                "变更摘要": f"版本{prev_ver}→{next_ver}数据变更",
                "链生成时间": chain_time,
            }
            store.rows("version_chain").append(link)
            result.new_links += 1
            result.link_ids.append(max_id)

        self._results.append(result)
        return result

    def check_chain_integrity(self, dataset_id: str) -> tuple[int, list[int]]:
        """校验版本链完整性：检测断裂并标记。"""
        links = sorted(
            [
                row for row in store.rows("version_chain")
                if row.get("数据集标识") == dataset_id
            ],
            key=lambda r: int(r.get("前序版本", 0)),
        )
        breaks = 0
        break_ids = []
        for i in range(len(links)):
            prev = int(links[i].get("前序版本", 0))
            next_v = int(links[i].get("后继版本", 0))
            if next_v - prev != 1:
                links[i]["status"] = "链断裂"
                links[i]["abnormal"] = True
                breaks += 1
                break_ids.append(int(links[i].get("id", 0)))
        return breaks, break_ids

    def validate_successor(
        self, link_id: int, expected_successor: str,
    ) -> tuple[bool, str]:
        """校验单条链的后继版本是否正确。"""
        for row in store.rows("version_chain"):
            if int(row.get("id", 0)) == link_id:
                actual = str(row.get("后继版本", ""))
                if actual == expected_successor:
                    row["status"] = "已校验"
                    row["pending"] = False
                    return True, f"版本链 {link_id} 后继校验通过"
                else:
                    row["status"] = "链断裂"
                    row["abnormal"] = True
                    return False, f"版本链 {link_id} 后继预期{expected_successor}实际{actual}"
        return False, f"版本链 {link_id} 不存在"

    def snapshot(self) -> dict[str, Any]:
        return {
            "results": [r.to_dict() for r in self._results],
            "total_links": len(store.rows("version_chain")),
        }