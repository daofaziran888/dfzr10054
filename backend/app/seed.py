"""示例数据：每模块至少3行语义真实数据，字段值能驱动链路分支。"""
from __future__ import annotations

from typing import Any

SEED_ROWS: dict[str, list[dict[str, Any]]] = {
    # ── 1. 快照编目 ──
    "snapshot_catalog": [
        {
            "id": 1, "status": "已编目", "pending": False, "abnormal": False,
            "快照编号": "SNAP-0001", "数据集标识": "core_trade_detail",
            "快照时间": "2026-09-01", "版本序号": "1",
            "记录条数": "12500", "存储分区": "dt=20260901",
            "编目状态": "已编目",
        },
        {
            "id": 2, "status": "已编目", "pending": False, "abnormal": False,
            "快照编号": "SNAP-0002", "数据集标识": "core_trade_detail",
            "快照时间": "2026-09-02", "版本序号": "2",
            "记录条数": "13100", "存储分区": "dt=20260902",
            "编目状态": "已编目",
        },
        {
            "id": 3, "status": "已编目", "pending": False, "abnormal": False,
            "快照编号": "SNAP-0003", "数据集标识": "core_trade_detail",
            "快照时间": "2026-09-05", "版本序号": "4",
            "记录条数": "13450", "存储分区": "dt=20260905",
            "编目状态": "已编目",
        },
        {
            "id": 4, "status": "写入中", "pending": True, "abnormal": False,
            "快照编号": "SNAP-0004", "数据集标识": "core_trade_detail",
            "快照时间": "2026-09-06", "版本序号": "5",
            "记录条数": "0", "存储分区": "dt=20260906",
            "编目状态": "写入中",
        },
        {
            "id": 5, "status": "已编目", "pending": False, "abnormal": False,
            "快照编号": "SNAP-0005", "数据集标识": "downstream_agg",
            "快照时间": "2026-08-20", "版本序号": "1",
            "记录条数": "8500", "存储分区": "dt=20260820",
            "编目状态": "已编目",
        },
        {
            "id": 6, "status": "已编目", "pending": False, "abnormal": False,
            "快照编号": "SNAP-0006", "数据集标识": "downstream_agg",
            "快照时间": "2025-09-20", "版本序号": "2",
            "记录条数": "9200", "存储分区": "dt=20250920",
            "编目状态": "已编目",
        },
    ],
    # ── 2. 版本链 ──
    "version_chain": [
        {
            "id": 1, "status": "已校验", "pending": False, "abnormal": False,
            "链编号": "CHAIN-0001", "数据集标识": "core_trade_detail",
            "前序版本": "1", "后继版本": "2",
            "变更摘要": "新增交易记录", "链生成时间": "2026-09-02",
        },
        {
            "id": 2, "status": "链断裂", "pending": True, "abnormal": True,
            "链编号": "CHAIN-0002", "数据集标识": "core_trade_detail",
            "前序版本": "2", "后继版本": "4",
            "变更摘要": "链断裂-缺少版本3", "链生成时间": "2026-09-05",
        },
        {
            "id": 3, "status": "已校验", "pending": False, "abnormal": False,
            "链编号": "CHAIN-0003", "数据集标识": "downstream_agg",
            "前序版本": "1", "后继版本": "2",
            "变更摘要": "聚合口径调整", "链生成时间": "2025-09-20",
        },
    ],
    # ── 3. 时点查询 ──
    "travel_query": [
        {
            "id": 1, "status": "已完成", "pending": False, "abnormal": False,
            "查询编号": "TRAV-0001", "数据集标识": "core_trade_detail",
            "查询时点": "2026-09-01", "命中版本": "1",
            "返回条数": "12500", "查询耗时": "12ms",
            "查询时间": "2026-09-01",
        },
        {
            "id": 2, "status": "已完成", "pending": False, "abnormal": False,
            "查询编号": "TRAV-0002", "数据集标识": "core_trade_detail",
            "查询时点": "2026-09-03", "命中版本": "2",
            "返回条数": "13100", "查询耗时": "8ms",
            "查询时间": "2026-09-03",
        },
        {
            "id": 3, "status": "命中失败", "pending": True, "abnormal": True,
            "查询编号": "TRAV-0003", "数据集标识": "core_trade_detail",
            "查询时点": "2026-08-01", "命中版本": "",
            "返回条数": "0", "查询耗时": "2ms",
            "查询时间": "2026-09-06",
        },
    ],
    # ── 4. 重述单 ──
    "restate_ticket": [
        {
            "id": 1, "status": "已完成", "pending": False, "abnormal": False,
            "单据编号": "REST-0001", "数据集标识": "core_trade_detail",
            "重述范围": "1-4", "重述原因": "交易记录口径更正",
            "影响版本数": "3", "创建时间": "2026-09-05",
        },
        {
            "id": 2, "status": "执行中", "pending": True, "abnormal": False,
            "单据编号": "REST-0002", "数据集标识": "core_trade_detail",
            "重述范围": "2-4", "重述原因": "数据延迟补报重算",
            "影响版本数": "2", "创建时间": "2026-09-06",
        },
        {
            "id": 3, "status": "草拟中", "pending": True, "abnormal": False,
            "单据编号": "REST-0003", "数据集标识": "downstream_agg",
            "重述范围": "1-2", "重述原因": "聚合规则更新",
            "影响版本数": "2", "创建时间": "2026-09-07",
        },
    ],
    # ── 5. 重述波次 ──
    "restate_wave": [
        {
            "id": 1, "status": "已完成", "pending": False, "abnormal": False,
            "波次编号": "WAVE-0001", "单据编号": "REST-0001",
            "波次序": "1", "重述版本数": "2",
            "跳过数量": 0, "生成时间": "2026-09-05",
        },
        {
            "id": 2, "status": "部分失败", "pending": True, "abnormal": True,
            "波次编号": "WAVE-0002", "单据编号": "REST-0002",
            "波次序": "2", "重述版本数": "1",
            "跳过数量": 3, "生成时间": "2026-09-06",
        },
        {
            "id": 3, "status": "待执行", "pending": True, "abnormal": False,
            "波次编号": "WAVE-0003", "单据编号": "REST-0003",
            "波次序": "1", "重述版本数": "2",
            "跳过数量": 0, "生成时间": "2026-09-07",
        },
    ],
    # ── 6. 影响范围 ──
    "impact_scope": [
        {
            "id": 1, "status": "已确认", "pending": False, "abnormal": False,
            "范围编号": "IMPA-0001", "单据编号": "REST-0001",
            "下游数据集": "downstream_agg",
            "影响版本数": "2", "传播深度": "1",
            "评估时间": "2026-09-05",
        },
        {
            "id": 2, "status": "已确认", "pending": False, "abnormal": False,
            "范围编号": "IMPA-0002", "单据编号": "REST-0002",
            "下游数据集": "downstream_report",
            "影响版本数": "1", "传播深度": "2",
            "评估时间": "2026-09-06",
        },
        {
            "id": 3, "status": "范围存疑", "pending": True, "abnormal": True,
            "范围编号": "IMPA-0003", "单据编号": "REST-0003",
            "下游数据集": "downstream_agg",
            "影响版本数": "2", "传播深度": "1",
            "评估时间": "2026-09-07",
        },
    ],
    # ── 7. 差异摘要 ──
    "diff_summary": [
        {
            "id": 1, "status": "已复核", "pending": False, "abnormal": False,
            "摘要编号": "DIFF-0001", "单据编号": "REST-0001",
            "重述前条数": "12500", "重述后条数": "12750",
            "净差异数": "250", "摘要时间": "2026-09-05",
        },
        {
            "id": 2, "status": "差异异常", "pending": True, "abnormal": True,
            "摘要编号": "DIFF-0002", "单据编号": "REST-0002",
            "重述前条数": "13100", "重述后条数": "13250",
            "净差异数": "150", "摘要时间": "2026-09-06",
        },
        {
            "id": 3, "status": "生成中", "pending": True, "abnormal": False,
            "摘要编号": "DIFF-0003", "单据编号": "REST-0003",
            "重述前条数": "0", "重述后条数": "0",
            "净差异数": "0", "摘要时间": "2026-09-07",
        },
    ],
    # ── 8. 保留策略 ──
    "retain_policy": [
        {
            "id": 1, "status": "已生效", "pending": False, "abnormal": False,
            "策略编号": "RETA-0001", "策略名称": "核心交易保留策略",
            "最少保留版本": "3", "保留天数": "90",
            "适用数据集": "core_trade_detail", "更新时间": "2026-01-15",
        },
        {
            "id": 2, "status": "已生效", "pending": False, "abnormal": False,
            "策略编号": "RETA-0002", "策略名称": "下游聚合保留策略",
            "最少保留版本": "2", "保留天数": "365",
            "适用数据集": "downstream_agg", "更新时间": "2026-03-20",
        },
        {
            "id": 3, "status": "待生效", "pending": True, "abnormal": False,
            "策略编号": "RETA-0003", "策略名称": "时点缓存回收策略",
            "最少保留版本": "1", "保留天数": "30",
            "适用数据集": "cache_dataset", "更新时间": "2026-09-01",
        },
    ],
    # ── 9. 回收记录 ──
    "reclaim_record": [
        {
            "id": 1, "status": "已回收", "pending": False, "abnormal": False,
            "回收编号": "RECL-0001", "快照编号": "SNAP-0005",
            "回收层级": "标准回收",
            "释放容量": "8500", "回收时间": "2026-09-10",
            "审计标记": "已审计",
        },
        {
            "id": 2, "status": "回收失败", "pending": True, "abnormal": True,
            "回收编号": "RECL-0002", "快照编号": "SNAP-0003",
            "回收层级": "强制回收",
            "释放容量": "0", "回收时间": "2026-09-11",
            "审计标记": "未审计",
        },
        {
            "id": 3, "status": "待回收", "pending": True, "abnormal": False,
            "回收编号": "RECL-0003", "快照编号": "SNAP-0006",
            "回收层级": "深层回收",
            "释放容量": "9200", "回收时间": "",
            "审计标记": "待审计",
        },
    ],
    # ── 10. 发布闸口 ──
    "publish_gate": [
        {
            "id": 1, "status": "已通过", "pending": False, "abnormal": False,
            "闸口编号": "PUBL-0001", "版本序号": "1",
            "检查项数": "3", "通过项数": "3",
            "闸口结论": "已通过", "闸口时间": "2026-09-01",
        },
        {
            "id": 2, "status": "已拦截", "pending": True, "abnormal": True,
            "闸口编号": "PUBL-0002", "版本序号": "2",
            "检查项数": "3", "通过项数": "1",
            "闸口结论": "已拦截", "闸口时间": "2026-09-02",
        },
        {
            "id": 3, "status": "检查中", "pending": True, "abnormal": False,
            "闸口编号": "PUBL-0003", "版本序号": "4",
            "检查项数": "3", "通过项数": "0",
            "闸口结论": "", "闸口时间": "2026-09-05",
        },
    ],
    # ── 11. 下游通知 ──
    "downstream_notice": [
        {
            "id": 1, "status": "已确认", "pending": False, "abnormal": False,
            "通知编号": "DOWN-0001", "单据编号": "REST-0001",
            "下游数据集": "downstream_agg",
            "通知摘要": "重述影响核心交易明细，请核查聚合结果",
            "通知时间": "2026-09-05", "确认状态": "已确认",
        },
        {
            "id": 2, "status": "已发送", "pending": True, "abnormal": False,
            "通知编号": "DOWN-0002", "单据编号": "REST-0002",
            "下游数据集": "downstream_report",
            "通知摘要": "重述持续进行中，预计影响10个下游",
            "通知时间": "2026-09-06", "确认状态": "待确认",
        },
        {
            "id": 3, "status": "催办中", "pending": True, "abnormal": True,
            "通知编号": "DOWN-0003", "单据编号": "REST-0001",
            "下游数据集": "downstream_weekly_job",
            "通知摘要": "重述已发布3天仍未确认，请尽快核查",
            "通知时间": "2026-09-08", "确认状态": "待确认",
        },
    ],
    # ── 12. 时点缓存 ──
    "travel_cache": [
        {
            "id": 1, "status": "生效中", "pending": False, "abnormal": False,
            "缓存编号": "CACH-0001", "查询编号": "TRAV-0001",
            "缓存版本": "1", "命中次数": "5",
            "过期时间": "2026-09-02", "缓存状态": "生效中",
        },
        {
            "id": 2, "status": "已失效", "pending": False, "abnormal": True,
            "缓存编号": "CACH-0002", "查询编号": "TRAV-0002",
            "缓存版本": "2", "命中次数": "3",
            "过期时间": "2026-09-03", "缓存状态": "已失效",
        },
        {
            "id": 3, "status": "已写入", "pending": True, "abnormal": False,
            "缓存编号": "CACH-0003", "查询编号": "TRAV-0003",
            "缓存版本": "0", "命中次数": "0",
            "过期时间": "2026-09-07", "缓存状态": "待激活",
        },
    ],
    # ── 13. 分支比对 ──
    "branch_compare": [
        {
            "id": 1, "status": "已复核", "pending": False, "abnormal": False,
            "比对编号": "BRAN-0001", "数据集标识": "core_trade_detail",
            "版本甲": "v1", "版本乙": "v2",
            "差异条数": "600", "比对时间": "2026-09-02",
        },
        {
            "id": 2, "status": "差异待判", "pending": True, "abnormal": True,
            "比对编号": "BRAN-0002", "数据集标识": "downstream_agg",
            "版本甲": "v1", "版本乙": "v2",
            "差异条数": "700", "比对时间": "2025-09-20",
        },
        {
            "id": 3, "status": "比对中", "pending": True, "abnormal": False,
            "比对编号": "BRAN-0003", "数据集标识": "core_trade_detail",
            "版本甲": "v2", "版本乙": "v4",
            "差异条数": "0", "比对时间": "2026-09-05",
        },
    ],
    # ── 14. 审计轨迹 ──
    "audit_trail": [
        {
            "id": 1, "status": "已复核", "pending": False, "abnormal": False,
            "轨迹编号": "AUDI-0001", "操作类型": "重述执行",
            "操作对象": "REST-0001", "操作者": "data_ops",
            "操作时间": "2026-09-05", "轨迹摘要": "执行重述单REST-0001，波及3个版本",
        },
        {
            "id": 2, "status": "已记录", "pending": True, "abnormal": False,
            "轨迹编号": "AUDI-0002", "操作类型": "快照回收",
            "操作对象": "SNAP-0005", "操作者": "admin",
            "操作时间": "2026-09-10", "轨迹摘要": "回收快照SNAP-0005，释放容量8500条",
        },
        {
            "id": 3, "status": "存疑中", "pending": True, "abnormal": True,
            "轨迹编号": "AUDI-0003", "操作类型": "闸口裁决",
            "操作对象": "PUBL-0002", "操作者": "reviewer",
            "操作时间": "2026-09-02", "轨迹摘要": "版本2闸口检查未通过，拦截标记可疑",
        },
    ],
    # ── 15. 合并请求 ──
    "merge_request": [
        {
            "id": 1, "status": "已合并", "pending": False, "abnormal": False,
            "请求编号": "MERG-0001", "源版本": "2",
            "目标版本": "4", "合并策略": "源优先",
            "提交时间": "2026-09-05",
        },
        {
            "id": 2, "status": "评审中", "pending": True, "abnormal": False,
            "请求编号": "MERG-0002", "源版本": "3",
            "目标版本": "2", "合并策略": "目标优先",
            "提交时间": "2026-09-06",
        },
        {
            "id": 3, "status": "已拒绝", "pending": False, "abnormal": True,
            "请求编号": "MERG-0003", "源版本": "5",
            "目标版本": "4", "合并策略": "源优先",
            "提交时间": "2026-09-07",
        },
    ],
    # ── 16. 配额台账 ──
    "quota_records": [
        {
            "id": 1, "status": "已确认", "pending": False, "abnormal": False,
            "台账编号": "QUOT-0001", "数据集标识": "core_trade_detail",
            "容量配额": "100000", "已用容量": "40000",
            "配额余量": "60000", "台账周期": "2026Q4",
            "更新时间": "2026-09-01",
        },
        {
            "id": 2, "status": "已超支", "pending": True, "abnormal": True,
            "台账编号": "QUOT-0002", "数据集标识": "downstream_agg",
            "容量配额": "20000", "已用容量": "22000",
            "配额余量": "-2000", "台账周期": "2026Q3",
            "更新时间": "2026-08-15",
        },
        {
            "id": 3, "status": "计量中", "pending": True, "abnormal": False,
            "台账编号": "QUOT-0003", "数据集标识": "downstream_report",
            "容量配额": "50000", "已用容量": "0",
            "配额余量": "50000", "台账周期": "2026Q4",
            "更新时间": "2026-09-01",
        },
    ],
    # ── 17. 重述指标 ──
    "restate_metrics": [
        {
            "id": 1, "status": "已发布", "pending": False, "abnormal": False,
            "快照编号": "RMET-0001", "统计日期": "2026-09-05",
            "重述及时率": "0.92", "平均重述耗时": "45min",
            "通知确认率": "0.67", "快照时间": "2026-09-05",
        },
        {
            "id": 2, "status": "待复核", "pending": True, "abnormal": False,
            "快照编号": "RMET-0002", "统计日期": "2026-09-06",
            "重述及时率": "0.78", "平均重述耗时": "120min",
            "通知确认率": "0.33", "快照时间": "2026-09-06",
        },
        {
            "id": 3, "status": "已生成", "pending": True, "abnormal": False,
            "快照编号": "RMET-0003", "统计日期": "2026-09-07",
            "重述及时率": "0.95", "平均重述耗时": "30min",
            "通知确认率": "0.85", "快照时间": "2026-09-07",
        },
    ],
    # ── 18. 冷藏层级 ──
    "cold_tier": [
        {
            "id": 1, "status": "已转层", "pending": False, "abnormal": False,
            "层级编号": "COLD-0001", "快照编号": "SNAP-0005",
            "层级标记": "低频存储", "转层时间": "2026-09-15",
            "回取代价": "high", "保留天数": "730",
        },
        {
            "id": 2, "status": "转层中", "pending": True, "abnormal": False,
            "层级编号": "COLD-0002", "快照编号": "SNAP-0006",
            "层级标记": "归档存储", "转层时间": "",
            "回取代价": "very_high", "保留天数": "365",
        },
        {
            "id": 3, "status": "待转层", "pending": True, "abnormal": False,
            "层级编号": "COLD-0003", "快照编号": "SNAP-0001",
            "层级标记": "温存储", "转层时间": "",
            "回取代价": "medium", "保留天数": "180",
        },
    ],
    # ── 19. 一致性核查 ──
    "consistency_check": [
        {
            "id": 1, "status": "核查通过", "pending": False, "abnormal": False,
            "核查编号": "CONS-0001", "数据集标识": "core_trade_detail",
            "核查版本对": "v1-v2", "差异条数": "600",
            "核查结论": "通过", "核查时间": "2026-09-03",
        },
        {
            "id": 2, "status": "链污染", "pending": True, "abnormal": True,
            "核查编号": "CONS-0002", "数据集标识": "core_trade_detail",
            "核查版本对": "v2-v4", "差异条数": "4500",
            "核查结论": "污染", "核查时间": "2026-09-06",
        },
        {
            "id": 3, "status": "核查中", "pending": True, "abnormal": False,
            "核查编号": "CONS-0003", "数据集标识": "downstream_agg",
            "核查版本对": "v1-v2", "差异条数": "700",
            "核查结论": "", "核查时间": "2025-09-21",
        },
    ],
    # ── 20. 回滚点 ──
    "rollback_point": [
        {
            "id": 1, "status": "可用", "pending": False, "abnormal": False,
            "点位编号": "ROLL-0001", "版本序号": "1",
            "点位标记": "初始版本", "创建时间": "2026-09-01",
            "已用次数": "0", "点位状态": "可用",
        },
        {
            "id": 2, "status": "可用", "pending": False, "abnormal": False,
            "点位编号": "ROLL-0002", "版本序号": "2",
            "点位标记": "修订前版本", "创建时间": "2026-09-02",
            "已用次数": "1", "点位状态": "可用",
        },
        {
            "id": 3, "status": "已失效", "pending": False, "abnormal": True,
            "点位编号": "ROLL-0003", "版本序号": "3",
            "点位标记": "废弃点位", "创建时间": "2026-09-04",
            "已用次数": "2", "点位状态": "已失效",
        },
    ],
    # ── 21. 模式演进 ──
    "schema_evolve": [
        {
            "id": 1, "status": "已合入", "pending": False, "abnormal": False,
            "演进编号": "SCHE-0001", "数据集标识": "core_trade_detail",
            "变更字段数": "3", "兼容标记": "向前兼容",
            "演出版本": "v2", "演进时间": "2026-08-15",
        },
        {
            "id": 2, "status": "待评审", "pending": True, "abnormal": False,
            "演进编号": "SCHE-0002", "数据集标识": "downstream_agg",
            "变更字段数": "5", "兼容标记": "不兼容",
            "演出版本": "v3", "演进时间": "2026-09-01",
        },
        {
            "id": 3, "status": "已回退", "pending": False, "abnormal": True,
            "演进编号": "SCHE-0003", "数据集标识": "core_trade_detail",
            "变更字段数": "2", "兼容标记": "向前兼容",
            "演出版本": "v2.1", "演进时间": "2026-09-05",
        },
    ],
    # ── 22. 访问台账 ──
    "access_records": [
        {
            "id": 1, "status": "已复核", "pending": False, "abnormal": False,
            "访问编号": "ACCE-0001", "查询编号": "TRAV-0001",
            "访问者": "analyst_team", "访问行数": "12500",
            "访问时间": "2026-09-01", "用途标记": "日度统计",
        },
        {
            "id": 2, "status": "待复核", "pending": True, "abnormal": False,
            "访问编号": "ACCE-0002", "查询编号": "TRAV-0002",
            "访问者": "audit_user", "访问行数": "13100",
            "访问时间": "2026-09-03", "用途标记": "合规复核",
        },
        {
            "id": 3, "status": "存疑中", "pending": True, "abnormal": True,
            "访问编号": "ACCE-0003", "查询编号": "TRAV-0003",
            "访问者": "external_viewer", "访问行数": "0",
            "访问时间": "2026-09-06", "用途标记": "外部访问",
        },
    ],
}