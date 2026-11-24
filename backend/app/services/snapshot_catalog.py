"""__NAME__领域服务：字段、状态和动作来自业务配置，数据处理骨架由基类复用。"""
from __future__ import annotations

from app.services.base import BaseModuleService


class SnapshotCatalogService(BaseModuleService):
    MODULE = "snapshot_catalog"
    ENTITY = "快照条目"
    OPERATION_TERM = "存储"
    LIST_FIELDS = ["快照编号", "数据集标识", "快照时间", "版本序号", "记录条数", "存储分区", "编目状态"]
    REQUIRED_FIELDS = ["快照编号", "数据集标识", "快照时间"]
    STATUS_ORDER = ["写入中", "待编目", "已编目", "已作废"]
    ACTION_RULES = {"提交编目": "待编目", "确认编目": "已编目", "作废快照": "已作废"}
    NEGATIVE_ACTIONS = ["作废快照"]
