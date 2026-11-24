"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class RestateMetricsService(BaseModuleService):
    MODULE = "restate_metrics"
    ENTITY = "指标快照"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["快照编号", "统计日期", "重述及时率", "平均重述耗时", "通知确认率", "快照时间"]
    REQUIRED_FIELDS = ["快照编号", "统计日期", "重述及时率"]
    STATUS_ORDER = ["已生成", "待复核", "已复核", "已发布"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "发布快照": "已发布"}
    NEGATIVE_ACTIONS = []
