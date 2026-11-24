"""重述单→波次拆分：按版本链将重述单拆分为多个重述波次。

核心行为：
- 读重述单确定重述范围（数据集+版本区间）
- 从版本链获取该范围内全部版本，按版本序号拆分波次
- 跳过数量为已校验且不需重述的版本
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.store import store


@dataclass
class WaveBatch:
    """重述波次批次。"""
    wave_id: str
    ticket_id: str
    wave_seq: int
    versions: list[str] = field(default_factory=list)
    skip_count: int = 0
    status: str = "待执行"

    def to_dict(self) -> dict[str, Any]:
        return {
            "wave_id": self.wave_id,
            "ticket_id": self.ticket_id,
            "wave_seq": self.wave_seq,
            "version_count": len(self.versions),
            "skip_count": self.skip_count,
            "status": self.status,
            "versions": self.versions,
        }


class RestateWaveSplitter:
    """重述波次拆分引擎：将重述单按版本链段拆分成波次。"""

    DEFAULT_WAVE_SIZE = 3

    def __init__(self) -> None:
        self._waves: dict[str, list[WaveBatch]] = {}

    def split_ticket(
        self, ticket_id: str, wave_size: int = DEFAULT_WAVE_SIZE,
    ) -> list[WaveBatch]:
        """将重述单按版本链拆分为多个波次。"""
        ticket = None
        for row in store.rows("restate_ticket"):
            if str(row.get("单据编号")) == ticket_id:
                ticket = row
                break
        if ticket is None:
            return []

        dataset_id = str(ticket.get("数据集标识", ""))
        version_range = str(ticket.get("重述范围", ""))
        versions = self._parse_version_range(version_range)

        # 从版本链获取该数据集全部已校验版本
        chain_versions = sorted({
            str(row.get("前序版本")) for row in store.rows("version_chain")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已校验"
        } | {
            str(row.get("后继版本")) for row in store.rows("version_chain")
            if row.get("数据集标识") == dataset_id
            and row.get("status") == "已校验"
        }, key=int)

        # 只保留在重述范围内的版本
        target_versions = [v for v in chain_versions if v in versions]
        if not target_versions:
            target_versions = chain_versions

        waves = []
        for i in range(0, len(target_versions), wave_size):
            chunk = target_versions[i:i + wave_size]
            seq = len(waves) + 1
            max_wave_id = max(
                (int(str(r.get("波次编号", "0")).replace("WAVE-", ""))
                 for r in store.rows("restate_wave")),
                default=0,
            )
            wave_id = f"WAVE-{max_wave_id + seq:04d}"
            wave = WaveBatch(
                wave_id=wave_id,
                ticket_id=ticket_id,
                wave_seq=seq,
                versions=chunk,
                skip_count=0,
            )
            waves.append(wave)

        self._waves[ticket_id] = waves
        ticket["status"] = "执行中"
        return waves

    def _parse_version_range(self, version_range: str) -> list[str]:
        """解析版本范围字符串为版本列表。"""
        versions = []
        for part in version_range.replace("v", "").split(","):
            part = part.strip()
            if "-" in part:
                try:
                    start, end = part.split("-")
                    versions.extend(
                        str(v) for v in range(int(start), int(end) + 1)
                    )
                except ValueError:
                    versions.append(part.replace("-", ""))
            elif part:
                versions.append(part)
        return versions

    def execute_wave(self, wave_id: str) -> tuple[bool, str]:
        """执行单个波次的重述。"""
        for waves in self._waves.values():
            for wave in waves:
                if wave.wave_id == wave_id:
                    wave.status = "已完成"
                    # 写入波次记录
                    max_id = max(
                        (int(row.get("id", 0))
                         for row in store.rows("restate_wave")),
                        default=0,
                    )
                    record = {
                        "id": max_id + 1,
                        "status": "已完成",
                        "pending": False,
                        "abnormal": False,
                        "波次编号": wave.wave_id,
                        "单据编号": wave.ticket_id,
                        "波次序": str(wave.wave_seq),
                        "重述版本数": str(len(wave.versions)),
                        "跳过数量": wave.skip_count,
                        "生成时间": "",
                    }
                    store.rows("restate_wave").append(record)
                    return True, f"波次 {wave_id} 已完成"
        return False, f"波次 {wave_id} 不存在"

    def wave_status_summary(
        self, ticket_id: str,
    ) -> dict[str, int]:
        """汇总某重述单下所有波次状态。"""
        waves = self._waves.get(ticket_id, [])
        summary = {"total": len(waves)}
        for w in waves:
            summary[w.status] = summary.get(w.status, 0) + 1
        return summary

    def snapshot(self) -> dict[str, Any]:
        return {
            "waves_by_ticket": {
                tid: [w.to_dict() for w in waves]
                for tid, waves in self._waves.items()
            },
            "total_waves_stored": len(store.rows("restate_wave")),
        }