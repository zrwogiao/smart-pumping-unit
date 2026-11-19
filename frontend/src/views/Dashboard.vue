<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>智能抽油机系统 · 监控大屏</h1>
      <div class="sub">SMART PUMPING UNIT MONITORING CENTER　|　实时数据驱动 · 智能工况诊断</div>
    </div>

    <div class="dash-grid">
      <!-- 顶部统计 -->
      <div class="dash-panel" style="grid-column: span 3">
        <div class="dash-stat"><div class="value" style="color:#5eb0ff">{{ devices.length }}</div><div class="label">设备总数</div></div>
      </div>
      <div class="dash-panel" style="grid-column: span 3">
        <div class="dash-stat"><div class="value" style="color:#67c23a">{{ runningCount }}</div><div class="label">运行中</div></div>
      </div>
      <div class="dash-panel" style="grid-column: span 3">
        <div class="dash-stat"><div class="value" style="color:#f56c6c">{{ activeAlarmCount }}</div><div class="label">活动告警</div></div>
      </div>
      <div class="dash-panel" style="grid-column: span 3">
        <div class="dash-stat"><div class="value" style="color:#e6a23c">{{ totalRecords }}</div><div class="label">累计采集</div></div>
      </div>

      <!-- 仪表盘区 -->
      <div class="dash-panel" style="grid-column: span 8">
        <div class="panel-title">实时运行参数 · {{ currentDevice?.device_name }}</div>
        <div style="display:flex; gap:10px">
          <div style="flex:1"><GaugeCard :value="rt?.max_load || 0" :max="deviceMaxLoad" title="最大载荷" unit="kN" color="#5eb0ff" /></div>
          <div style="flex:1"><GaugeCard :value="rt?.current || 0" :max="deviceCurrentLimit" title="电机电流" unit="A" color="#67c23a" /></div>
          <div style="flex:1"><GaugeCard :value="rt?.stroke_rate || 0" :max="12" title="冲次" unit="次/min" color="#e6a23c" /></div>
          <div style="flex:1"><GaugeCard :value="rt?.power || 0" :max="30" title="功率" unit="kW" color="#909399" /></div>
        </div>
      </div>

      <!-- 最新告警 -->
      <div class="dash-panel" style="grid-column: span 4">
        <div class="panel-title">最新告警</div>
        <div class="alarm-scroll" style="max-height:180px; color:#c8d6e5">
          <div v-for="a in recentAlarms" :key="a.id" class="alarm-item" style="border-color:rgba(255,255,255,0.08)">
            <el-tag :type="a.level==='critical'?'danger':a.level==='warning'?'warning':'info'" size="small">{{ levelLabel(a.level) }}</el-tag>
            <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap">{{ a.message }}</span>
          </div>
          <div v-if="!recentAlarms.length" class="empty-tip" style="color:#5a7fa8">暂无告警</div>
        </div>
      </div>

      <!-- 示功图 -->
      <div class="dash-panel" style="grid-column: span 6">
        <div class="panel-title">实时示功图 · 工况诊断</div>
        <DynamoChart v-if="dynamo" :displacement="dynamo.displacement" :load="dynamo.load"
                     :height="'320px'" :title="''" :condition-label="diagnosisLabel" :condition-color="diagnosisColor" />
        <div v-else class="empty-tip" style="color:#5a7fa8; height:320px; line-height:320px">等待示功图数据...</div>
      </div>

      <!-- 趋势曲线 -->
      <div class="dash-panel" style="grid-column: span 6">
        <div class="panel-title">载荷趋势曲线（实时）</div>
        <TrendChart :points="trendPoints" :height="'320px'" title="" metric="载荷(kN)" color="#5eb0ff" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import GaugeCard from '@/components/GaugeCard.vue'
import DynamoChart from '@/components/DynamoChart.vue'
import TrendChart from '@/components/TrendChart.vue'
import { useDeviceStore, useRealtimeStore } from '@/stores'
import { useRealtime } from '@/composables/useRealtime'
import { deviceApi, alarmApi, monitoringApi, historyApi, diagnosisApi } from '@/api'
import type { Alarm, WsPayload } from '@/types'

const deviceStore = useDeviceStore()
const realtimeStore = useRealtimeStore()
const selectedId = computed(() => deviceStore.currentDeviceId)
const devices = computed(() => deviceStore.devices)
const currentDevice = computed(() => deviceStore.currentDevice())

const rt = computed(() => realtimeStore.latest)
const dynamo = ref<{ displacement: number[]; load: number[] } | null>(null)
const diagnosisLabel = ref('')
const diagnosisColor = ref('#409EFF')
const recentAlarms = ref<Alarm[]>([])
const activeAlarmCount = ref(0)
const totalRecords = ref(0)
const deviceMaxLoad = computed(() => currentDevice.value?.max_load_limit || 90)
const deviceCurrentLimit = computed(() => currentDevice.value?.current_limit || 45)

const trendPoints = computed(() => realtimeStore.history.map((h) => ({
  timestamp: h.timestamp, value: h.max_load,
})))

const runningCount = computed(() => devices.value.filter((d) => d.status === 'running').length)

function levelLabel(level: string) {
  return { critical: '严重', warning: '警告', info: '提示' }[level] || level
}

function updateConditionColor() {
  const colorMap: Record<string, string> = {
    '正常': '#67c23a', '泵漏失': '#e6a23c', '供液不足': '#f56c6c',
    '气体影响': '#909399', '结蜡': '#409EFF', '抽油杆断脱': '#c45656',
  }
  diagnosisColor.value = colorMap[diagnosisLabel.value] || '#409EFF'
}

async function loadSummary() {
  try {
    const s = await historyApi.summary()
    totalRecords.value = s.total_records
  } catch { /* ignore */ }
}

onMounted(async () => {
  try {
    const ds = await deviceApi.list()
    deviceStore.devices = ds
    if (ds.length && !deviceStore.currentDevice()) deviceStore.currentDeviceId = ds[0].id
    const alarms = await alarmApi.list({ limit: 8 })
    recentAlarms.value = alarms
    activeAlarmCount.value = alarms.filter((a) => a.status === 'active').length
    const latest = await monitoringApi.latest(deviceStore.currentDeviceId)
    if (latest) realtimeStore.push(latest)
    await loadSummary()
  } catch { /* ignore */ }
})

useRealtime(() => selectedId.value, (payload: WsPayload) => {
  if (payload.dynamo) {
    dynamo.value = payload.dynamo
    diagnosisLabel.value = payload.diagnosis?.label || ''
    updateConditionColor()
  }
  if (payload.alarms?.length) {
    recentAlarms.value = payload.alarms.map((a) => ({
      id: a.id, device_id: payload.device_id, alarm_type: a.type, level: a.level as Alarm['level'],
      message: a.message, value: null, status: 'active', triggered_at: '',
    } as Alarm)).concat(recentAlarms.value).slice(0, 8)
    activeAlarmCount.value = recentAlarms.value.filter((a) => a.status === 'active').length
  }
})
</script>
