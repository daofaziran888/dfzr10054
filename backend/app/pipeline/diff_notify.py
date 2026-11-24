"""影响范围→差异摘要→下游通知：重述后生成差异摘要并通知受影响下游。

核心行为：
- 对每个受影响的版本对计算重述前后差异（条数变化）
- 差异条数超阈值（默认50条）标记差异异常
- 为受影响的下游数据集逐条发送通知
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.store import store


@dataclass
class DiffEntry:
    """差异摘要条目。"""
    diff_id: str
    ticket_id: str
    before_count: int
    after_count: int
    net_diff: int
    is_abnormal: bool = False
    status: str = "已复核"

    def to_dict(self) -> dict[str, Any]:
        return {
            "diff_id": self.diff_id,
            "ticket_id": self.ticket_id,
            "before_count": self.before_count,
            "after_count": self.after_count,
            "net_diff": self.net_diff,
            "is_abnormal": self.is_abnormal,
            "status": self.status,
        }


@dataclass
class NotifyEntry:
    """下游通知条目。"""
    notice_id: str
    ticket_id: str
    downstream_dataset: str
    summary: str
    status: str = "已发送"

    def to_dict(self) -> dict[str, Any]:
        return {
            "notice_id": self.notice_id,
            "ticket_id": self.ticket_id,
            "downstream_dataset": self.downstream_dataset,
            "summary": self.summary,
            "status": self.status,
        }


class DiffNotifyEngine:
    """差异摘要与下游通知引擎。"""

    DIFF_ABNORMAL_THRESHOLD = 50

    def __init__(self) -> None:
        self._diffs: list[DiffEntry] = []
        self._notices: list[NotifyEntry] = []

    def generate_diff_summary(
        self, ticket_id: str,
        version_diffs: list[tuple[str, int, int]],
    ) -> list[DiffEntry]:
        """为重述单的各版本对生成差异摘要。"""
        diffs = []
        for seq, (version, before, after) in enumerate(version_diffs, 1):
            net_diff = after - before
            is_abnormal = abs(net_diff) > self.DIFF_ABNORMAL_THRESHOLD
            diff_id = f"DIFF-{seq:04d}"
            entry = DiffEntry(
                diff_id=diff_id,
                ticket_id=ticket_id,
                before_count=before,
                after_count=after,
                net_diff=net_diff,
                is_abnormal=is_abnormal,
                status="差异异常" if is_abnormal else "已复核",
            )
            self._write_diff(entry)
            diffs.append(entry)

        self._diffs.extend(diffs)
        return diffs

    def _write_diff(self, entry: DiffEntry) -> None:
        """写入差异摘要记录。"""
        max_id = max(
            (int(row.get("id", 0)) for row in store.rows("diff_summary")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": entry.status,
            "pending": entry.is_abnormal,
            "abnormal": entry.is_abnormal,
            "摘要编号": entry.diff_id,
            "单据编号": entry.ticket_id,
            "重述前条数": str(entry.before_count),
            "重述后条数": str(entry.after_count),
            "净差异数": str(entry.net_diff),
            "摘要时间": "",
        }
        store.rows("diff_summary").append(record)

    def notify_downstream(
        self, ticket_id: str,
    ) -> list[NotifyEntry]:
        """向受影响下游逐条发送通知。"""
        affected = [
            row for row in store.rows("impact_scope")
            if str(row.get("单据编号")) == ticket_id
            and row.get("status") == "已确认"
        ]
        notices = []
        for idx, scope in enumerate(affected):
            ds = str(scope.get("下游数据集", ""))
            ver_count = str(scope.get("影响版本数", ""))
            max_notice_id = max(
                (int(str(r.get("通知编号", "0")).replace("DOWN-", ""))
                 for r in store.rows("downstream_notice")),
                default=0,
            )
            notice_id = f"DOWN-{max_notice_id + idx + 1:04d}"
            entry = NotifyEntry(
                notice_id=notice_id,
                ticket_id=ticket_id,
                downstream_dataset=ds,
                summary=f"重述影响{ver_count}个版本，请核查下游数据",
            )
            self._write_notice(entry)
            notices.append(entry)

        self._notices.extend(notices)
        return notices

    def _write_notice(self, entry: NotifyEntry) -> None:
        """写入下游通知记录。"""
        max_id = max(
            (int(row.get("id", 0))
             for row in store.rows("downstream_notice")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": entry.status,
            "pending": True,
            "abnormal": False,
            "通知编号": entry.notice_id,
            "单据编号": entry.ticket_id,
            "下游数据集": entry.downstream_dataset,
            "通知摘要": entry.summary,
            "通知时间": "",
            "确认状态": "待确认",
        }
        store.rows("downstream_notice").append(record)

    def confirm_notice(self, notice_id: str) -> tuple[bool, str]:
        """下游确认收到通知。"""
        for row in store.rows("downstream_notice"):
            if str(row.get("通知编号")) == notice_id:
                row["确认状态"] = "已确认"
                row["status"] = "已确认"
                row["pending"] = False
                return True, f"通知 {notice_id} 已确认"
        return False, f"通知 {notice_id} 不存在"

    def get_outstanding_notices(self) -> list[dict[str, Any]]:
        """获取未确认通知列表。"""
        return [
            row for row in store.rows("downstream_notice")
            if row.get("confirm", row.get("确认状态")) == "待确认"
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "diffs": [d.to_dict() for d in self._diffs],
            "notices": [n.to_dict() for n in self._notices],
            "total_diffs": len(store.rows("diff_summary")),
            "total_notices": len(store.rows("downstream_notice")),
        }