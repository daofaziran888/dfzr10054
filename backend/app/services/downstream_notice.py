"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class DownstreamNoticeService(BaseModuleService):
    MODULE = "downstream_notice"
    ENTITY = "通知记录"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["通知编号", "单据编号", "下游数据集", "通知摘要", "通知时间", "确认状态"]
    REQUIRED_FIELDS = ["通知编号", "单据编号", "下游数据集"]
    STATUS_ORDER = ["待发送", "已发送", "已确认", "催办中"]
    ACTION_RULES = {"发起发送": "已发送", "确认适配": "已确认", "发起催办": "催办中"}
    NEGATIVE_ACTIONS = []
