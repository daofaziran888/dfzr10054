"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class PublishGateService(BaseModuleService):
    MODULE = "publish_gate"
    ENTITY = "闸口记录"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["闸口编号", "版本序号", "检查项数", "通过项数", "闸口结论", "闸口时间"]
    REQUIRED_FIELDS = ["闸口编号", "版本序号", "检查项数"]
    STATUS_ORDER = ["检查中", "待裁决", "已通过", "已拦截"]
    ACTION_RULES = {"提交裁决": "待裁决", "通过闸口": "已通过", "拦截版本": "已拦截"}
    NEGATIVE_ACTIONS = []
