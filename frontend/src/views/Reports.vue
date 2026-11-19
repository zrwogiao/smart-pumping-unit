<template>
  <div class="page-container">
    <div class="page-header">
      <div><div class="page-title">统计报表</div><div class="page-subtitle">运行统计、工况分布与数据导出</div></div>
      <div style="display:flex; gap:10px">
        <el-button type="success" @click="doExport('csv')">导出 CSV</el-button>
        <el-button type="primary" @click="doExport('excel')">导出 Excel</el-button>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :span="6" v-for="s in statCards" :key="s.label">
        <div class="stat-card">
          <div class="card-title">{{ s.label }}</div>
          <div style="font-size:28px; font-weight:bold; color:#409EFF">{{ s.value }}</div>
          <div style="font-size:12px; color:#909399; margin-top:4px">{{ s.unit }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never"><template #header>工况分布</template>
          <div ref="pieEl" style="height:360px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>载荷趋势</template>
          <TrendChart :points="trendPoints" :height="'360px'" title="" metric="kN" color="#67C23A" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import TrendChart from '@/components/TrendChart.vue'
import { historyApi } from '@/api'
import { useDeviceStore } from '@/stores'

const deviceStore = useDeviceStore()
const summary = ref<any>({})
const trendPoints = ref<any[]>([])
const pieEl = ref<HTMLElement | null>(null)
let pieChart: echarts.ECharts | null = null

const statCards = computed(() => [
  { label: '累计采集记录', value: summary.value.total_records ?? 0, unit: '条' },
  { label: '平均最大载荷', value: summary.value.avg_load ?? 0, unit: 'kN' },
  { label: '平均电流', value: summary.value.avg_current ?? 0, unit: 'A' },
  { label: '告警总数', value: summary.value.alarm_count ?? 0, unit: '条' },
])

function renderPie() {
  if (!pieEl.value) return
  if (!pieChart) pieChart = echarts.init(pieEl.value)
  const dist = summary.value.condition_distribution || []
  const colorMap: Record<string, string> = {
    '正常': '#67c23a', '泵漏失': '#e6a23c', '供液不足': '#f56c6c',
    '气体影响': '#909399', '结蜡': '#409eff', '抽油杆断脱': '#c45656',
  }
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 10, top: 'center' },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['60%', '50%'],
      data: dist.map((d: any) => ({ name: d.label, value: d.count, itemStyle: { color: colorMap[d.label] } })),
      label: { formatter: '{b}: {c}' },
    }],
  }, true)
}

function doExport(format: string) {
  const url = historyApi.exportUrl({ format, device_id: deviceStore.currentDeviceId || '' })
  window.open(url, '_blank')
}

onMounted(async () => {
  try {
    summary.value = await historyApi.summary()
    const trend = await historyApi.trend({ device_id: deviceStore.currentDeviceId || 1, metric: 'max_load' })
    trendPoints.value = trend.points
  } catch { /* ignore */ }
  nextTick(renderPie)
})
</script>
