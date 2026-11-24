"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class ReclaimRecordService(BaseModuleService):
    MODULE = "reclaim_record"
    ENTITY = "回收明细"
    OPERATION_TERM = "存储"
    LIST_FIELDS = ["回收编号", "快照编号", "回收层级", "释放容量", "回收时间", "审计标记"]
    REQUIRED_FIELDS = ["回收编号", "快照编号", "回收层级"]
    STATUS_ORDER = ["待回收", "回收中", "已回收", "回收失败"]
    ACTION_RULES = {"发起回收": "回收中", "确认回收": "已回收", "登记失败": "回收失败"}
    NEGATIVE_ACTIONS = []
