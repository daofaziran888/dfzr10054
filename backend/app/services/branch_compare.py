"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class BranchCompareService(BaseModuleService):
    MODULE = "branch_compare"
    ENTITY = "比对记录"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["比对编号", "数据集标识", "版本甲", "版本乙", "差异条数", "比对时间"]
    REQUIRED_FIELDS = ["比对编号", "数据集标识", "版本甲"]
    STATUS_ORDER = ["比对中", "待复核", "已复核", "差异待判"]
    ACTION_RULES = {"提交复核": "待复核", "确认复核": "已复核", "登记待判": "差异待判"}
    NEGATIVE_ACTIONS = []
