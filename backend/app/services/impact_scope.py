"""影响范围领域服务：传播BFS、影响半径计算、传播深度统计。"""
from __future__ import annotations

from collections import deque
from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class ImpactScopeService(BaseModuleService):
    MODULE = "impact_scope"
    ENTITY = "范围清单"
    OPERATION_TERM = "关联"
    LIST_FIELDS = ["范围编号", "单据编号", "下游数据集", "影响版本数", "传播深度", "评估时间"]
    REQUIRED_FIELDS = ["范围编号", "单据编号", "下游数据集"]
    STATUS_ORDER = ["评估中", "待确认", "已确认", "范围存疑"]
    ACTION_RULES = {"提交确认": "待确认", "确认范围": "已确认", "登记存疑": "范围存疑"}
    NEGATIVE_ACTIONS = ["登记存疑"]

    def propagate_bfs(self, ticket_no: str) -> list[str]:
        """BFS传播重述单影响：从重述单数据集出发，沿分支比对引用图发现下游数据集。"""
        ticket = next(
            (r for r in store.rows("restate_ticket")
             if str(r.get("单据编号")) == ticket_no),
            None,
        )
        if ticket is None:
            return []

        source = str(ticket.get("数据集标识", ""))
        graph: dict[str, list[str]] = {}
        for row in store.rows("branch_compare"):
            ds = str(row.get("数据集标识", ""))
            v_a = str(row.get("版本甲", ""))
            v_b = str(row.get("版本乙", ""))
            if "DS-" in str(v_a) or "DS-" in str(v_b):
                referenced = v_a if v_a != "DS-" else v_b
                if referenced.startswith("DS-"):
                    graph.setdefault(ds, []).append(referenced)

        visited = {source}
        result = [source]
        q = deque([source])
        while q:
            current = q.popleft()
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    result.append(neighbor)
                    q.append(neighbor)
        return result

    def blast_radius(self, ticket_no: str) -> dict[str, Any]:
        """计算重述单的影响半径统计。"""
        scopes = [
            row for row in store.rows(self.MODULE)
            if str(row.get("单据编号")) == ticket_no
            and row.get("status") == "已确认"
        ]
        return {
            "downstream_count": len(scopes),
            "max_depth": max(
                (int(str(r.get("传播深度", 0))) for r in scopes),
                default=0,
            ),
            "total_affected": sum(
                int(str(r.get("影响版本数", 0))) for r in scopes
            ),
        }

    def questionable_scopes(self) -> list[dict[str, Any]]:
        """返回全部范围存疑的清单。"""
        return [
            row for row in store.rows(self.MODULE)
            if row.get("status") == "范围存疑"
        ]

    def confirm_all(self, ticket_no: str) -> int:
        """批量确认某重述单下全部待确认范围。返回确认数量。"""
        count = 0
        for row in store.rows(self.MODULE):
            if (str(row.get("单据编号")) == ticket_no
                    and row.get("status") == "待确认"):
                row["status"] = "已确认"
                row["pending"] = False
                count += 1
        return count