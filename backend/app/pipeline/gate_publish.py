"""发布闸口→版本可见性：闸口检查项计分决定版本是否对外可见。

核心行为：
- 快照版本对外发布前须通过闸口检查（至少3项检查）
- 检查项：版本链完整性校验、一致性核查通过、差异条数不超阈值
- 全部通过才能标记为对外可见
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.store import store


@dataclass
class GateResult:
    """闸口检查结果。"""
    gate_id: str
    version: str
    total_checks: int
    passed_checks: int
    score: float
    passed: bool
    conclusion: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "version": self.version,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "score": float(self.score),
            "passed": self.passed,
            "conclusion": self.conclusion,
        }


class GatePublishEngine:
    """发布闸口引擎：检查项计分与发布判定。"""

    REQUIRED_CHECKS = [
        "chain_integrity",      # 版本链完整性
        "consistency_pass",     # 一致性核查通过
        "diff_threshold",       # 差异条数不超阈值
    ]

    def __init__(self) -> None:
        self._results: list[GateResult] = []

    def run_gate_check(
        self, dataset_id: str, version: str,
    ) -> GateResult:
        """对指定版本执行闸口三项检查并计分。"""
        checks_passed = 0

        # 检查1：版本链完整性
        has_chain = False
        for row in store.rows("version_chain"):
            if row.get("数据集标识") == dataset_id:
                if (str(row.get("前序版本")) == version
                        or str(row.get("后继版本")) == version):
                    if row.get("status") == "已校验":
                        has_chain = True
                        break
        if has_chain:
            checks_passed += 1

        # 检查2：一致性核查通过
        consist_ok = False
        for row in store.rows("consistency_check"):
            if row.get("数据集标识") == dataset_id:
                if version in str(row.get("核查版本对", "")):
                    if row.get("status") == "核查通过":
                        consist_ok = True
                        break
        if consist_ok:
            checks_passed += 1

        # 检查3：差异条数不超阈值（50条）
        diff_ok = False
        for row in store.rows("diff_summary"):
            net_diff = int(str(row.get("净差异数", 0)))
            if abs(net_diff) <= 50:
                diff_ok = True
        checks_passed += 1 if diff_ok else 0

        total = len(self.REQUIRED_CHECKS)
        score = checks_passed / total if total > 0 else 0.0
        passed = checks_passed == total

        max_gate_id = max(
            (int(str(r.get("闸口编号", "0")).replace("PUBL-", ""))
             for r in store.rows("publish_gate")),
            default=0,
        )
        gate_id = f"PUBL-{max_gate_id + 1:04d}"

        conclusion = "已通过" if passed else "已拦截"

        result = GateResult(
            gate_id=gate_id,
            version=version,
            total_checks=total,
            passed_checks=checks_passed,
            score=score,
            passed=passed,
            conclusion=conclusion,
        )

        self._write_gate(result)
        self._results.append(result)
        return result

    def _write_gate(self, result: GateResult) -> None:
        """写入闸口记录。"""
        max_id = max(
            (int(row.get("id", 0)) for row in store.rows("publish_gate")),
            default=0,
        )
        record = {
            "id": max_id + 1,
            "status": result.conclusion,
            "pending": not result.passed,
            "abnormal": not result.passed,
            "闸口编号": result.gate_id,
            "版本序号": result.version,
            "检查项数": str(result.total_checks),
            "通过项数": str(result.passed_checks),
            "闸口结论": result.conclusion,
            "闸口时间": "",
        }
        store.rows("publish_gate").append(record)

    def is_version_visible(self, version: str) -> tuple[bool, str]:
        """判定版本是否对外可见（已通过闸口）。"""
        for row in store.rows("publish_gate"):
            if (str(row.get("版本序号")) == version
                    and row.get("闸口结论") == "已通过"):
                return True, f"版本{version}已通过发布闸口，对外可见"
        return False, f"版本{version}未通过发布闸口，仅内部可查"

    def get_intercepted_versions(self) -> list[str]:
        """获取全部被闸口拦截的版本。"""
        return [
            str(row.get("版本序号"))
            for row in store.rows("publish_gate")
            if row.get("闸口结论") == "已拦截"
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "results": [r.to_dict() for r in self._results],
            "intercepted": self.get_intercepted_versions(),
            "total_gates": len(store.rows("publish_gate")),
        }