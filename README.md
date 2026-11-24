# 回溯工坊 · 数据快照回补与历史重述平台

面向快照编目、版本链管理、时点查询、重述波次传播、下游影响评估与回收策略的数据版本管理平台。

这是一个前后端分离的管理平台：前端 Vue 3 + Vite + TypeScript，后端 FastAPI（Python）。
两边各自独立启动，前端 dev server 已关掉自动打开页面，启动后按终端打印的地址手工打开。

## 目录结构

```text
.
├── frontend/                 Vue 3 + Vite + TypeScript 前端
│   ├── src/views/WorkbenchView.vue|tsx  全部模块共享工作台
│   ├── src/data/modules.ts              18个业务模块配置
│   ├── src/api/              统一请求封装
│   └── vite.config.ts        dev server 配置（open: false）
├── backend/                  FastAPI（Python） 后端
│   ├── app/routers/resource.py  通用查询/导出/登记/动作接口
│   ├── app/services/<key>.py    每个模块独立领域逻辑
│   ├── app/services/base.py     共享服务骨架
│   └── app/store.py          内存数据仓库与示例数据
├── .gitignore
└── docker-compose.yml
```

## 启动

### 后端

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./run.sh
```

健康检查：`curl http://127.0.0.1:8011/api/health`

### 前端

```bash
cd frontend
npm ci
npm run dev
```

前端默认监听 `http://127.0.0.1:5184/`，dev server 不会自动打开浏览器，
需要自己访问。`/api` 由 vite 代理到后端 `http://127.0.0.1:8011`。

## 业务模块

| 模块 | 目录 | 业务对象 | 主要字段 |
| --- | --- | --- | --- |
| 快照编目 | `snapshot_catalog` | 快照条目 | 快照编号、数据集标识、快照时间 |
| 版本链 | `version_chain` | 链条目 | 链编号、数据集标识、前序版本 |
| 时点查询 | `travel_query` | 查询单 | 查询编号、数据集标识、查询时点 |
| 重述单 | `restate_ticket` | 单据条目 | 单据编号、数据集标识、重述范围 |
| 重述波次 | `restate_wave` | 波次批次 | 波次编号、单据编号、波次序 |
| 影响范围 | `impact_scope` | 范围清单 | 范围编号、单据编号、下游数据集 |
| 差异摘要 | `diff_summary` | 摘要条目 | 摘要编号、单据编号、重述前条数 |
| 保留策略 | `retain_policy` | 策略条目 | 策略编号、策略名称、最少保留版本 |
| 回收记录 | `reclaim_record` | 回收明细 | 回收编号、快照编号、回收层级 |
| 发布闸口 | `publish_gate` | 闸口记录 | 闸口编号、版本序号、检查项数 |
| 下游通知 | `downstream_notice` | 通知记录 | 通知编号、单据编号、下游数据集 |
| 时点缓存 | `travel_cache` | 缓存条目 | 缓存编号、查询编号、缓存版本 |
| 分支比对 | `branch_compare` | 比对记录 | 比对编号、数据集标识、版本甲 |
| 审计轨迹 | `audit_trail` | 轨迹明细 | 轨迹编号、操作类型、操作对象 |
| 合并请求 | `merge_request` | 请求单 | 请求编号、源版本、目标版本 |
| 配额台账 | `quota_records` | 台账条目 | 台账编号、数据集标识、容量配额 |
| 重述指标 | `restate_metrics` | 指标快照 | 快照编号、统计日期、重述及时率 |
| 冷藏层级 | `cold_tier` | 层级条目 | 层级编号、快照编号、层级标记 |
| 一致性核查 | `consistency_check` | 核查报告 | 核查编号、数据集标识、核查版本对 |
| 回滚点 | `rollback_point` | 点位条目 | 点位编号、版本序号、点位标记 |
| 模式演进 | `schema_evolve` | 演进记录 | 演进编号、数据集标识、变更字段数 |
| 访问台账 | `access_records` | 访问明细 | 访问编号、查询编号、访问者 |

## 约定

- 全部模块共享`frontend/src/views/WorkbenchView.vue|tsx`和一套资源路由。
- 每个模块仍保留独立`backend/app/services/<模块>.py`；纯前端保留
  `frontend/src/domain/<模块>.ts`，用于承载真实业务差异并维持36题位容量。
- 列表接口统一返回 `{ items, total, page, size }`，动作接口统一返回 `{ ok, message }`。
- 状态流转只允许在 `app/services` 里改，路由层不做业务判断。

领域：数据工程
子方向：数仓与数据湖
