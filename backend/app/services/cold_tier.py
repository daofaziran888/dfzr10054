"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class ColdTierService(BaseModuleService):
    MODULE = "cold_tier"
    ENTITY = "层级条目"
    OPERATION_TERM = "查询"
    LIST_FIELDS = ["层级编号", "快照编号", "层级标记", "转层时间", "回取代价", "保留天数"]
    REQUIRED_FIELDS = ["层级编号", "快照编号", "层级标记"]
    STATUS_ORDER = ["待转层", "转层中", "已转层", "已销毁"]
    ACTION_RULES = {"发起转层": "转层中", "确认转层": "已转层", "销毁层级": "已销毁"}
    NEGATIVE_ACTIONS = []
