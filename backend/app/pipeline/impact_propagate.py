"""重述波次→影响范围传播：BFS沿版本链传播影响范围到下游数据集。

核心行为：
- 从重述单出发，读版本链受影响的版本集合
- BFS从源数据集出发沿引用关系传播到下游数据集
- 记录传播深度和影响版本数
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from app.store import store


@dataclass
class ImpactEntry:
    """影响范围条目。"""
    scope_id: str
    ticket_id: str
    downstream_dataset: str
    affected_versions: list[str] = field(default_factory=list)
    depth: int = 0
    status: str = "已确认"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "ticket_id": self.ticket_id,
            "downstream_dataset": self.downstream_dataset,
            "affected_versions": self.affected_versions,
            "depth": self.depth,
            "status": self.status,
        }


class ImpactPropagateEngine:
    """影响范围传播引擎：BFS发现下游受影响数据集。"""

    def __init__(self) -> None:
        self._scopes: list[ImpactEntry] = []

    def propagate(self, ticket_id: str) -> list[ImpactEntry]:
        """BFS传播重述单影响范围到下游数据集。"""
        ticket = None
        for row in store.rows("restate_ticket"):
            if str(row.get("单据编号")) == ticket_id:
                ticket = row
                break
        if ticket is None:
            return []

        source_dataset = str(ticket.get("数据集标识", ""))
        affected_versions = self._get_affected_versions(source_dataset)

        # 构建数据集引用图：从分支比对/时点查询中提取引用关系
        ref_graph = self._build_reference_graph()

        scopes = []
        visited = {source_dataset}
        q = deque([(source_dataset, 0)])
        scope_seq = 0

        while q:
            current, depth = q.popleft()
            for neighbor in ref_graph.get(current, []):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                scope_seq += 1
                scope_id = f"IMPA-{scope_seq:04d}"
                entry = ImpactEntry(
                    scope_id=scope_id,
                    ticket_id=ticket_id,
                    downstream_dataset=neighbor,
                    affected_versions=list(affected_versions),
                    depth=depth + 1,
                )
                scopes.append(entry)
                self._write_scope(entry)
                q.append((neighbor, depth + 1))

        self._scopes.extend(scopes)
        return scopes

    def _get_affected_versions(self, dataset_id: str) -> set[str]:
        """获取数据集在版本链上的全部版本。"""
        versions = set()
        for row in store.rows("version_chain"):
            if row.get("数据集标识") == dataset_id:
                versions.add(str(row.get("前序版本", "")))
                versions.add(str(row.get("后继版本", "")))
        return versions

    def _build_reference_graph(self) -> dict[str, list[str]]:
        """从分支比对数据构建数据集引用图。"""
        graph: dict[str, list[str]] = {}
        for row in store.rows("branch_compare"):
            ds = str(row.get("数据集标识", ""))
            v_a = str(row.get("版本甲", ""))
            v_b = str(row.get("版本乙", ""))
            # 如果版本引用自不同数据集则建立边
            if v_a.startswith("DS-") and ds:
                graph.setdefault(ds, []).append(v_a)
            if v_b.startswith("DS-") and ds:
                graph.setdefault(ds, []).append(v_b)
        return graph

    def _write_scope(self, entry: ImpactEntry) -> None:
        """写入影响范围记录。"""
        max_id = max(
            (int(row.get("id", 0)) for row in store.rows("impact_scope")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": entry.status,
            "pending": False,
            "abnormal": False,
            "范围编号": entry.scope_id,
            "单据编号": entry.ticket_id,
            "下游数据集": entry.downstream_dataset,
            "影响版本数": str(len(entry.affected_versions)),
            "传播深度": str(entry.depth),
            "评估时间": "",
        }
        store.rows("impact_scope").append(record)

    def calculate_blast_radius(
        self, ticket_id: str,
    ) -> dict[str, Any]:
        """计算重述的影响半径统计。"""
        scopes = [s for s in self._scopes if s.ticket_id == ticket_id]
        if not scopes:
            scopes = []
            for row in store.rows("impact_scope"):
                if str(row.get("单据编号")) == ticket_id:
                    scopes.append(ImpactEntry(
                        scope_id=str(row.get("范围编号")),
                        ticket_id=ticket_id,
                        downstream_dataset=str(row.get("下游数据集")),
                        depth=int(row.get("传播深度", 0)),
                    ))
        return {
            "downstream_count": len(scopes),
            "max_depth": max((s.depth for s in scopes), default=0),
            "total_affected_versions": sum(
                len(s.affected_versions) for s in scopes
            ),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "scopes": [s.to_dict() for s in self._scopes],
            "total_scopes_stored": len(store.rows("impact_scope")),
        }