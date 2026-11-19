<template>
  <div class="page-container">
    <div class="page-header">
      <div><div class="page-title">历史数据</div><div class="page-subtitle">多条件筛选历史监测数据，点击查看对应示功图</div></div>
    </div>

    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true" :model="filters">
        <el-form-item label="设备">
          <DeviceSelector v-model="filters.deviceId" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker v-model="dateRange" type="datetimerange" range-separator="至"
                          start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table :data="rows" stripe height="520" @row-click="viewDynamo" highlight-current-row>
        <el-table-column prop="timestamp" label="采集时间" width="180" />
        <el-table-column prop="device_id" label="设备ID" width="90" />
        <el-table-column prop="max_load" label="最大载荷(kN)" />
        <el-table-column prop="min_load" label="最小载荷(kN)" />
        <el-table-column prop="current" label="电流(A)" />
        <el-table-column prop="power" label="功率(kW)" />
        <el-table-column prop="stroke_rate" label="冲次" />
      </el-table>
      <div style="margin-top:12px; color:#909399; font-size:12px">共 {{ rows.length }} 条记录 · 点击行查看示功图</div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="对应示功图" width="600px">
      <DynamoChart v-if="dialogData" :displacement="dialogData.displacement" :load="dialogData.load" :height="'380px'" />
      <div v-else class="empty-tip">该时刻无示功图记录</div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import DeviceSelector from '@/components/DeviceSelector.vue'
import DynamoChart from '@/components/DynamoChart.vue'
import { historyApi, dynamoApi } from '@/api'
import { useDeviceStore } from '@/stores'

const deviceStore = useDeviceStore()
const filters = reactive({ deviceId: deviceStore.currentDeviceId || 1 })
const dateRange = ref<string[] | null>(null)
const rows = ref<any[]>([])
const dialogVisible = ref(false)
const dialogData = ref<{ displacement: number[]; load: number[] } | null>(null)

async function loadData() {
  const params: Record<string, any> = { device_id: filters.deviceId, limit: 300 }
  if (dateRange.value?.length === 2) {
    params.start = dateRange.value[0]
    params.end = dateRange.value[1]
  }
  rows.value = await historyApi.query(params)
}

function reset() {
  dateRange.value = null
  loadData()
}

async function viewDynamo(row: any) {
  dialogData.value = null
  dialogVisible.value = true
  try {
    const card = await dynamoApi.latest(row.device_id)
    if (card) dialogData.value = { displacement: JSON.parse(card.displacement), load: JSON.parse(card.load) }
  } catch { /* ignore */ }
}

onMounted(loadData)
</script>
