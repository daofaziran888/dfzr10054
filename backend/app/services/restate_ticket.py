"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class RestateTicketService(BaseModuleService):
    MODULE = "restate_ticket"
    ENTITY = "单据条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["单据编号", "数据集标识", "重述范围", "重述原因", "影响版本数", "创建时间"]
    REQUIRED_FIELDS = ["单据编号", "数据集标识", "重述范围"]
    STATUS_ORDER = ["草拟中", "待审批", "执行中", "已完成"]
    ACTION_RULES = {"提交审批": "待审批", "启动重述": "执行中", "确认完成": "已完成"}
    NEGATIVE_ACTIONS = []
