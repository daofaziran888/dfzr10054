"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class TravelCacheService(BaseModuleService):
    MODULE = "travel_cache"
    ENTITY = "缓存条目"
    OPERATION_TERM = "写入"
    LIST_FIELDS = ["缓存编号", "查询编号", "缓存版本", "命中次数", "过期时间", "缓存状态"]
    REQUIRED_FIELDS = ["缓存编号", "查询编号", "缓存版本"]
    STATUS_ORDER = ["已写入", "生效中", "已失效", "已驱逐"]
    ACTION_RULES = {"标记失效": "生效中", "驱逐缓存": "已失效", "刷新缓存": "已驱逐"}
    NEGATIVE_ACTIONS = []
