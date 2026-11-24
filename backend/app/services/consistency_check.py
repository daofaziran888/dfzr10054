"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class ConsistencyCheckService(BaseModuleService):
    MODULE = "consistency_check"
    ENTITY = "核查报告"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["核查编号", "数据集标识", "核查版本对", "差异条数", "核查结论", "核查时间"]
    REQUIRED_FIELDS = ["核查编号", "数据集标识", "核查版本对"]
    STATUS_ORDER = ["核查中", "待裁决", "核查通过", "链污染"]
    ACTION_RULES = {"提交裁决": "待裁决", "通过核查": "核查通过", "登记污染": "链污染"}
    NEGATIVE_ACTIONS = []
