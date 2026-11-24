"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class ImpactScopeService(BaseModuleService):
    MODULE = "impact_scope"
    ENTITY = "范围清单"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["范围编号", "单据编号", "下游数据集", "影响版本数", "传播深度", "评估时间"]
    REQUIRED_FIELDS = ["范围编号", "单据编号", "下游数据集"]
    STATUS_ORDER = ["评估中", "待确认", "已确认", "范围存疑"]
    ACTION_RULES = {"提交确认": "待确认", "确认范围": "已确认", "登记存疑": "范围存疑"}
    NEGATIVE_ACTIONS = []
