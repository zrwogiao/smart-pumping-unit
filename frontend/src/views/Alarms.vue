<template>
  <div class="page-container">
    <div class="page-header">
      <div><div class="page-title">告警中心</div><div class="page-subtitle">告警查看、确认与清除</div></div>
      <div style="display:flex; gap:10px">
        <el-select v-model="statusFilter" placeholder="状态筛选" style="width:140px" clearable>
          <el-option label="未处理" value="active" />
          <el-option label="已确认" value="acknowledged" />
          <el-option label="已清除" value="cleared" />
        </el-select>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="8"><div class="stat-card"><div class="card-title">未处理告警</div><div style="font-size:26px;font-weight:bold;color:#f56c6c">{{ activeCount }}</div></div></el-col>
      <el-col :span="8"><div class="stat-card"><div class="card-title">严重告警</div><div style="font-size:26px;font-weight:bold;color:#c45656">{{ criticalCount }}</div></div></el-col>
      <el-col :span="8"><div class="stat-card"><div class="card-title">告警总数</div><div style="font-size:26px;font-weight:bold;color:#409EFF">{{ alarms.length }}</div></div></el-col>
    </el-row>

    <el-card shadow="never">
      <el-table :data="filteredAlarms" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="device_id" label="设备ID" width="90" />
        <el-table-column prop="alarm_type" label="告警类型" width="130">
          <template #default="{row}">{{ typeLabel(row.alarm_type) }}</template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="90">
          <template #default="{row}">
            <el-tag :type="row.level === 'critical' ? 'danger' : row.level === 'warning' ? 'warning' : 'info'" size="small">
              {{ { critical: '严重', warning: '警告', info: '提示' }[row.level] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="告警内容" show-overflow-tooltip />
        <el-table-column prop="triggered_at" label="触发时间" width="170" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === 'active' ? 'danger' : row.status === 'acknowledged' ? 'warning' : 'success'" size="small">
              {{ { active: '未处理', acknowledged: '已确认', cleared: '已清除' }[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.status === 'active'" size="small" type="primary" @click="ack(row)">确认</el-button>
            <el-button v-if="row.status !== 'cleared'" size="small" @click="clear(row)">清除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { alarmApi } from '@/api'
import type { Alarm } from '@/types'

const alarms = ref<Alarm[]>([])
const statusFilter = ref('')

const filteredAlarms = computed(() => statusFilter.value ? alarms.value.filter((a) => a.status === statusFilter.value) : alarms.value)
const activeCount = computed(() => alarms.value.filter((a) => a.status === 'active').length)
const criticalCount = computed(() => alarms.value.filter((a) => a.level === 'critical' && a.status === 'active').length)

function typeLabel(t: string) {
  return { overload: '载荷超限', overcurrent: '电流超限', condition_fault: '工况异常', offline: '设备离线' }[t] || t
}

async function load() { alarms.value = await alarmApi.list({ limit: 200 }) }
async function ack(row: Alarm) { await alarmApi.ack(row.id); ElMessage.success('已确认'); await load() }
async function clear(row: Alarm) { await alarmApi.clear(row.id); ElMessage.success('已清除'); await load() }

onMounted(load)
</script>
