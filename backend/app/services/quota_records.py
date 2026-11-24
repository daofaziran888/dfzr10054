"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class QuotaRecordsService(BaseModuleService):
    MODULE = "quota_records"
    ENTITY = "台账条目"
    OPERATION_TERM = "存储"
    LIST_FIELDS = ["台账编号", "数据集标识", "容量配额", "已用容量", "配额余量", "台账周期", "更新时间"]
    REQUIRED_FIELDS = ["台账编号", "数据集标识", "容量配额"]
    STATUS_ORDER = ["计量中", "待复核", "已确认", "已超支"]
    ACTION_RULES = {"提交复核": "待复核", "确认台账": "已确认", "登记超支": "已超支"}
    NEGATIVE_ACTIONS = []
