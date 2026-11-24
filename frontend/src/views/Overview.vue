<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标，先看总量再看异常。</p>
      </div>
    </header>
    <div class="stat-row">
      <article v-for="card in cards" :key="card.label" class="stat-card">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>业务模块</th><th>今日新增</th><th>待处理</th><th>异常量</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in moduleRows" :key="row.name">
          <td>{{ row.name }}</td>
          <td>{{ row.created }}</td>
          <td>{{ row.pending }}</td>
          <td>{{ row.abnormal }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchJson } from '@/api/client'

type Overview = {
  cards: { label: string; value: number }[]
  modules: { name: string; created: number; pending: number; abnormal: number }[]
}

const cards = ref<Overview['cards']>([])
const moduleRows = ref<Overview['modules']>([])

onMounted(async () => {
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    cards.value = payload.cards
    moduleRows.value = payload.modules
  } catch {
    cards.value = [{"label": "业务模块", "value": 0}, {"label": "今日新增", "value": 0}]
    moduleRows.value = [{"name": "快照编目", "created": 0, "pending": 0, "abnormal": 0}, {"name": "版本链", "created": 0, "pending": 0, "abnormal": 0}, {"name": "时点查询", "created": 0, "pending": 0, "abnormal": 0}, {"name": "重述单", "created": 0, "pending": 0, "abnormal": 0}, {"name": "重述波次", "created": 0, "pending": 0, "abnormal": 0}, {"name": "影响范围", "created": 0, "pending": 0, "abnormal": 0}, {"name": "差异摘要", "created": 0, "pending": 0, "abnormal": 0}, {"name": "保留策略", "created": 0, "pending": 0, "abnormal": 0}, {"name": "回收记录", "created": 0, "pending": 0, "abnormal": 0}, {"name": "发布闸口", "created": 0, "pending": 0, "abnormal": 0}, {"name": "下游通知", "created": 0, "pending": 0, "abnormal": 0}, {"name": "时点缓存", "created": 0, "pending": 0, "abnormal": 0}, {"name": "分支比对", "created": 0, "pending": 0, "abnormal": 0}, {"name": "审计轨迹", "created": 0, "pending": 0, "abnormal": 0}, {"name": "合并请求", "created": 0, "pending": 0, "abnormal": 0}, {"name": "配额台账", "created": 0, "pending": 0, "abnormal": 0}, {"name": "重述指标", "created": 0, "pending": 0, "abnormal": 0}, {"name": "冷藏层级", "created": 0, "pending": 0, "abnormal": 0}, {"name": "一致性核查", "created": 0, "pending": 0, "abnormal": 0}, {"name": "回滚点", "created": 0, "pending": 0, "abnormal": 0}, {"name": "模式演进", "created": 0, "pending": 0, "abnormal": 0}, {"name": "访问台账", "created": 0, "pending": 0, "abnormal": 0}]
  }
})
</script>
