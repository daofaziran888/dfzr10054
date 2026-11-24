"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class RollbackPointService(BaseModuleService):
    MODULE = "rollback_point"
    ENTITY = "点位条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["点位编号", "版本序号", "点位标记", "创建时间", "已用次数", "点位状态"]
    REQUIRED_FIELDS = ["点位编号", "版本序号", "点位标记"]
    STATUS_ORDER = ["已设置", "可用", "已使用", "已失效"]
    ACTION_RULES = {"标记使用": "可用", "恢复点位": "已使用", "失效点位": "已失效"}
    NEGATIVE_ACTIONS = []
