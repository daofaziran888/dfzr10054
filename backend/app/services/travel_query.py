"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class TravelQueryService(BaseModuleService):
    MODULE = "travel_query"
    ENTITY = "查询单"
    OPERATION_TERM = "查询"
    LIST_FIELDS = ["查询编号", "数据集标识", "查询时点", "命中版本", "返回条数", "查询耗时", "查询时间"]
    REQUIRED_FIELDS = ["查询编号", "数据集标识", "查询时点"]
    STATUS_ORDER = ["查询中", "待复核", "已完成", "命中失败"]
    ACTION_RULES = {"提交复核": "待复核", "确认完成": "已完成", "登记失败": "命中失败"}
    NEGATIVE_ACTIONS = []
