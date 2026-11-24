"""领域服务注册表：通用资源路由按模块 key 分派到独立业务服务。"""
from __future__ import annotations

from app.services.base import BaseModuleService
from app.services.snapshot_catalog import SnapshotCatalogService
from app.services.version_chain import VersionChainService
from app.services.travel_query import TravelQueryService
from app.services.restate_ticket import RestateTicketService
from app.services.restate_wave import RestateWaveService
from app.services.impact_scope import ImpactScopeService
from app.services.diff_summary import DiffSummaryService
from app.services.retain_policy import RetainPolicyService
from app.services.reclaim_record import ReclaimRecordService
from app.services.publish_gate import PublishGateService
from app.services.downstream_notice import DownstreamNoticeService
from app.services.travel_cache import TravelCacheService
from app.services.branch_compare import BranchCompareService
from app.services.audit_trail import AuditTrailService
from app.services.merge_request import MergeRequestService
from app.services.quota_records import QuotaRecordsService
from app.services.restate_metrics import RestateMetricsService
from app.services.cold_tier import ColdTierService
from app.services.consistency_check import ConsistencyCheckService
from app.services.rollback_point import RollbackPointService
from app.services.schema_evolve import SchemaEvolveService
from app.services.access_records import AccessRecordsService

SERVICES: dict[str, BaseModuleService] = {
    "snapshot_catalog": SnapshotCatalogService(),
    "version_chain": VersionChainService(),
    "travel_query": TravelQueryService(),
    "restate_ticket": RestateTicketService(),
    "restate_wave": RestateWaveService(),
    "impact_scope": ImpactScopeService(),
    "diff_summary": DiffSummaryService(),
    "retain_policy": RetainPolicyService(),
    "reclaim_record": ReclaimRecordService(),
    "publish_gate": PublishGateService(),
    "downstream_notice": DownstreamNoticeService(),
    "travel_cache": TravelCacheService(),
    "branch_compare": BranchCompareService(),
    "audit_trail": AuditTrailService(),
    "merge_request": MergeRequestService(),
    "quota_records": QuotaRecordsService(),
    "restate_metrics": RestateMetricsService(),
    "cold_tier": ColdTierService(),
    "consistency_check": ConsistencyCheckService(),
    "rollback_point": RollbackPointService(),
    "schema_evolve": SchemaEvolveService(),
    "access_records": AccessRecordsService(),
}


def service_for(module: str) -> BaseModuleService | None:
    return SERVICES.get(module)
