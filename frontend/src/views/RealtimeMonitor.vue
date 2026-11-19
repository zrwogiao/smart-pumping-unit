<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <div class="page-title">实时监测</div>
        <div class="page-subtitle">WebSocket 实时推送 · 载荷 / 位移 / 电流 / 冲次 动态刷新</div>
      </div>
      <div style="display:flex; gap:10px; align-items:center">
        <DeviceSelector v-model="selectedId" @update:model-value="onDeviceChange" />
        <el-tag :type="realtimeStore.connected ? 'success' : 'info'">
          {{ realtimeStore.connected ? '实时连接中' : '连接断开' }}
        </el-tag>
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric-box"><div class="label">最大载荷</div><div class="value">{{ fmt(rt?.max_load) }}<span class="unit"> kN</span></div></div>
      <div class="metric-box"><div class="label">最小载荷</div><div class="value">{{ fmt(rt?.min_load) }}<span class="unit"> kN</span></div></div>
      <div class="metric-box"><div class="label">当前位移</div><div class="value">{{ fmt(rt?.displacement) }}<span class="unit"> m</span></div></div>
      <div class="metric-box"><div class="label">电机电流</div><div class="value">{{ fmt(rt?.current) }}<span class="unit"> A</span></div></div>
      <div class="metric-box"><div class="label">电压</div><div class="value">{{ fmt(rt?.voltage) }}<span class="unit"> V</span></div></div>
      <div class="metric-box"><div class="label">冲次</div><div class="value">{{ fmt(rt?.stroke_rate) }}<span class="unit"> 次/min</span></div></div>
      <div class="metric-box"><div class="label">冲程</div><div class="value">{{ fmt(rt?.stroke_length) }}<span class="unit"> m</span></div></div>
      <div class="metric-box"><div class="label">功率</div><div class="value">{{ fmt(rt?.power) }}<span class="unit"> kW</span></div></div>
      <div class="metric-box"><div class="label">更新时间</div><div class="value" style="font-size:15px">{{ rt?.timestamp?.slice(11,19) || '--:--:--' }}</div></div>
    </div>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never"><template #header>实时示功图</template>
          <DynamoChart v-if="dynamo" :displacement="dynamo.displacement" :load="dynamo.load" :height="'340px'" />
          <div v-else class="empty-tip">等待示功图数据...</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never"><template #header>最大载荷趋势</template>
          <TrendChart :points="points" :height="'340px'" title="" metric="kN" color="#409EFF" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DeviceSelector from '@/components/DeviceSelector.vue'
import DynamoChart from '@/components/DynamoChart.vue'
import TrendChart from '@/components/TrendChart.vue'
import { useDeviceStore, useRealtimeStore } from '@/stores'
import { useRealtime } from '@/composables/useRealtime'
import type { WsPayload } from '@/types'

const deviceStore = useDeviceStore()
const realtimeStore = useRealtimeStore()
const selectedId = ref(deviceStore.currentDeviceId)
const dynamo = ref<{ displacement: number[]; load: number[] } | null>(null)

const rt = computed(() => realtimeStore.latest)
const points = computed(() => realtimeStore.history.map((h) => ({ timestamp: h.timestamp, value: h.max_load })))

function fmt(v: number | undefined) { return v != null ? v.toFixed(2) : '--' }
function switchDevice(v: number) {
  selectedId.value = v
  deviceStore.currentDeviceId = v
  realtimeStore.history = []
  dynamo.value = null
}

const { switchDevice: wsSwitch } = useRealtime(() => selectedId.value, (payload: WsPayload) => {
  if (payload.dynamo) dynamo.value = payload.dynamo
})
// 覆盖以触发WS重连
function onDeviceChange(v: number) { switchDevice(v); wsSwitch() }
</script>
