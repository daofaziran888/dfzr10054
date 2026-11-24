"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class MergeRequestService(BaseModuleService):
    MODULE = "merge_request"
    ENTITY = "请求单"
    OPERATION_TERM = "合并"
    LIST_FIELDS = ["请求编号", "源版本", "目标版本", "合并策略", "提交时间"]
    REQUIRED_FIELDS = ["请求编号", "源版本", "目标版本"]
    STATUS_ORDER = ["待评审", "评审中", "已合并", "已拒绝"]
    ACTION_RULES = {"发起评审": "评审中", "确认合并": "已合并", "拒绝请求": "已拒绝"}
    NEGATIVE_ACTIONS = ["拒绝请求"]
