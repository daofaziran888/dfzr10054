"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class DiffSummaryService(BaseModuleService):
    MODULE = "diff_summary"
    ENTITY = "摘要条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["摘要编号", "单据编号", "重述前条数", "重述后条数", "净差异数", "摘要时间"]
    REQUIRED_FIELDS = ["摘要编号", "单据编号", "重述前条数"]
    STATUS_ORDER = ["生成中", "待复核", "已复核", "差异异常"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记异常": "差异异常"}
    NEGATIVE_ACTIONS = []
