"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class SchemaEvolveService(BaseModuleService):
    MODULE = "schema_evolve"
    ENTITY = "演进记录"
    OPERATION_TERM = "读取"
    LIST_FIELDS = ["演进编号", "数据集标识", "变更字段数", "兼容标记", "演出版本", "演进时间"]
    REQUIRED_FIELDS = ["演进编号", "数据集标识", "变更字段数"]
    STATUS_ORDER = ["草拟中", "待评审", "已合入", "已回退"]
    ACTION_RULES = {"提交评审": "待评审", "合入演进": "已合入", "回退演进": "已回退"}
    NEGATIVE_ACTIONS = []
