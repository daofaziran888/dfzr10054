<template>
  <div class="app-shell">
    <aside class="app-side">
      <h1 class="app-title">回溯工坊 · 数据快照回补与历史重述平台</h1>
      <nav class="nav-list">
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item">
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>
    <main class="app-main">
      <header class="app-head">
        <span class="head-desc">面向快照编目、版本链管理、时点查询、重述波次传播、下游影响评估与回收策略的数据版本管理平台。</span>
        <span class="head-user">当前值班：数据工程组</span>
      </header>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
const navItems = [{ label: "运营概览", path: "/" }, { label: "快照编目", path: "/snapshot_catalog" }, { label: "版本链", path: "/version_chain" }, { label: "时点查询", path: "/travel_query" }, { label: "重述单", path: "/restate_ticket" }, { label: "重述波次", path: "/restate_wave" }, { label: "影响范围", path: "/impact_scope" }, { label: "差异摘要", path: "/diff_summary" }, { label: "保留策略", path: "/retain_policy" }, { label: "回收记录", path: "/reclaim_record" }, { label: "发布闸口", path: "/publish_gate" }, { label: "下游通知", path: "/downstream_notice" }, { label: "时点缓存", path: "/travel_cache" }, { label: "分支比对", path: "/branch_compare" }, { label: "审计轨迹", path: "/audit_trail" }, { label: "合并请求", path: "/merge_request" }, { label: "配额台账", path: "/quota_records" }, { label: "重述指标", path: "/restate_metrics" }, { label: "冷藏层级", path: "/cold_tier" }, { label: "一致性核查", path: "/consistency_check" }, { label: "回滚点", path: "/rollback_point" }, { label: "模式演进", path: "/schema_evolve" }, { label: "访问台账", path: "/access_records" }]
</script>
