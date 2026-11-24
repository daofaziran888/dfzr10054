"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class AuditTrailService(BaseModuleService):
    MODULE = "audit_trail"
    ENTITY = "轨迹明细"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["轨迹编号", "操作类型", "操作对象", "操作者", "操作时间", "轨迹摘要"]
    REQUIRED_FIELDS = ["轨迹编号", "操作类型", "操作对象"]
    STATUS_ORDER = ["已记录", "待复核", "已复核", "存疑中"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记存疑": "存疑中"}
    NEGATIVE_ACTIONS = []
