"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class RetainPolicyService(BaseModuleService):
    MODULE = "retain_policy"
    ENTITY = "策略条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["策略编号", "策略名称", "最少保留版本", "保留天数", "适用数据集", "更新时间"]
    REQUIRED_FIELDS = ["策略编号", "策略名称", "最少保留版本"]
    STATUS_ORDER = ["草稿", "待生效", "已生效", "已废止"]
    ACTION_RULES = {"提交生效": "待生效", "生效策略": "已生效", "废止策略": "已废止"}
    NEGATIVE_ACTIONS = []
