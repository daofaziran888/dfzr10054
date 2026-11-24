"""发布闸口领域服务：检查项计分后产出闸口指标数据集，裁决版本对外可见性。"""
from __future__ import annotations

from typing import Any

from app.services.base import BaseModuleService
from app.store import store


class PublishGateService(BaseModuleService):
    MODULE = "publish_gate"
    ENTITY = "闸口记录"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["闸口编号", "版本序号", "检查项数", "通过项数", "闸口结论", "闸口时间"]
    REQUIRED_FIELDS = ["闸口编号", "版本序号", "检查项数"]
    STATUS_ORDER = ["检查中", "待裁决", "已通过", "已拦截"]
    ACTION_RULES = {"提交裁决": "待裁决", "通过闸口": "已通过", "拦截版本": "已拦截"}
    NEGATIVE_ACTIONS = ["拦截版本"]

    def run_checks(self, dataset_id: str, version: str) -> dict[str, Any]:
        """对版本执行三项检查并返回得分。"""
        checks_passed = 0

        # 检查1：版本链中有此版本的已校验链
        chain_ok = False
        for row in store.rows("version_chain"):
            if row.get("数据集标识") == dataset_id:
                if (str(row.get("前序版本")) == version
                        or str(row.get("后继版本")) == version):
                    if row.get("status") == "已校验":
                        chain_ok = True
                        break
        if chain_ok:
            checks_passed += 1

        # 检查2：一致性核查通过
        if self._consistency_ok(dataset_id, version):
            checks_passed += 1

        # 检查3：差异条数不超50
        diff_ok = True
        for row in store.rows("diff_summary"):
            if abs(int(str(row.get("净差异数", 0)))) > 50:
                diff_ok = False
        if diff_ok:
            checks_passed += 1

        score = checks_passed / 3.0
        passed = checks_passed == 3
        return {
            "version": version,
            "total_checks": 3,
            "passed_checks": checks_passed,
            "score": score,
            "passed": passed,
            "conclusion": "已通过" if passed else "已拦截",
        }

    def _consistency_ok(self, dataset_id: str, version: str) -> bool:
        for row in store.rows("consistency_check"):
            if row.get("数据集标识") == dataset_id:
                ver_pair = row.get("核查版本对", "")
                if version in str(ver_pair) or str(ver_pair).replace("v", "") == version:
                    if row.get("status") == "核查通过":
                        return True
        return False

    def intercepted_versions(self) -> list[str]:
        """返回全部被闸口拦截的版本。"""
        return [
            str(row.get("版本序号"))
            for row in store.rows(self.MODULE)
            if row.get("闸口结论") == "已拦截"
        ]

    def passed_versions(self) -> list[str]:
        """返回全部已通过闸口的版本。"""
        return [
            str(row.get("版本序号"))
            for row in store.rows(self.MODULE)
            if row.get("闸口结论") == "已通过"
        ]

    def visibility_status(self, version: str) -> str:
        """返回版本的可见性状态。"""
        for row in store.rows(self.MODULE):
            if str(row.get("版本序号")) == version:
                if row.get("闸口结论") == "已通过":
                    return "对外可见"
                return "仅内部可查"
        return "未检查"

    def gate_pass_rate(self) -> float:
        """返回闸口通过率。"""
        rows = store.rows(self.MODULE)
        decided = sum(1 for r in rows if r.get("闸口结论") in ("已通过", "已拦截"))
        passed = sum(1 for r in rows if r.get("闸口结论") == "已通过")
        return passed / decided if decided else 0.0