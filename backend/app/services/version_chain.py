"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class VersionChainService(BaseModuleService):
    MODULE = "version_chain"
    ENTITY = "链条目"
    OPERATION_TERM = "校验"
    LIST_FIELDS = ["链编号", "数据集标识", "前序版本", "后继版本", "变更摘要", "链生成时间"]
    REQUIRED_FIELDS = ["链编号", "数据集标识", "前序版本"]
    STATUS_ORDER = ["已记录", "待校验", "已校验", "链断裂"]
    ACTION_RULES = {"提交校验": "待校验", "确认校验": "已校验", "登记断裂": "链断裂"}
    NEGATIVE_ACTIONS = []
