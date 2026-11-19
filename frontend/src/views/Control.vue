<template>
  <div class="page-container">
    <div class="page-header">
      <div><div class="page-title">远程控制</div><div class="page-subtitle">设备启停、参数调节与操作日志</div></div>
      <DeviceSelector v-model="deviceId" />
    </div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>设备控制 · {{ currentDevice?.device_name }}</template>
          <div style="text-align:center; padding:20px 0">
            <div style="font-size:14px; color:#606266; margin-bottom:16px">
              当前状态：
              <el-tag :type="currentDevice?.status === 'running' ? 'success' : 'info'" size="large">
                {{ currentDevice?.status === 'running' ? '运行中' : '已停止' }}
              </el-tag>
            </div>
            <div style="display:flex; gap:20px; justify-content:center">
              <el-button type="success" size="large" icon="VideoPlay" @click="doCommand('start')">远程启动</el-button>
              <el-button type="danger" size="large" icon="VideoPause" @click="doCommand('stop')">远程停止</el-button>
            </div>
          </div>
          <el-divider />
          <div style="font-weight:600; margin-bottom:12px">参数调节</div>
          <el-form :model="params" label-width="120px">
            <el-form-item label="冲次(次/min)"><el-input-number v-model="params.stroke_rate" :min="1" :max="20" :step="0.5" /></el-form-item>
            <el-form-item label="冲程(m)"><el-input-number v-model="params.stroke_length" :min="0.5" :max="6" :step="0.1" /></el-form-item>
            <el-form-item label="载荷上限(kN)"><el-input-number v-model="params.max_load_limit" :min="10" :max="200" :step="1" /></el-form-item>
            <el-form-item label="电流上限(A)"><el-input-number v-model="params.current_limit" :min="5" :max="100" :step="1" /></el-form-item>
            <el-form-item><el-button type="primary" @click="saveParams">保存参数</el-button></el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never">
          <template #header>控制操作日志</template>
          <el-table :data="logs" stripe height="520">
            <el-table-column prop="executed_at" label="时间" width="170" />
            <el-table-column prop="command" label="指令" width="110">
              <template #default="{row}">
                {{ { start: '启动', stop: '停止', set_params: '参数调节' }[row.command] || row.command }}
              </template>
            </el-table-column>
            <el-table-column prop="params_json" label="参数" show-overflow-tooltip />
            <el-table-column prop="result" label="结果" width="90">
              <template #default="{row}">
                <el-tag :type="row.result === 'success' ? 'success' : 'danger'" size="small">{{ row.result === 'success' ? '成功' : '失败' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DeviceSelector from '@/components/DeviceSelector.vue'
import { controlApi, deviceApi } from '@/api'
import { useDeviceStore } from '@/stores'

const deviceStore = useDeviceStore()
const deviceId = ref(deviceStore.currentDeviceId || 1)
const logs = ref<any[]>([])
const params = reactive({ stroke_rate: 6, stroke_length: 3, max_load_limit: 90, current_limit: 45 })
const currentDevice = computed(() => deviceStore.devices.find((d) => d.id === deviceId.value))

async function loadLogs() { logs.value = await controlApi.logs(deviceId.value) }

async function doCommand(cmd: 'start' | 'stop') {
  await ElMessageBox.confirm(`确认${cmd === 'start' ? '启动' : '停止'}该设备？`, '操作确认', { type: 'warning' })
  const fn = cmd === 'start' ? controlApi.start : controlApi.stop
  await fn(deviceId.value)
  ElMessage.success(`${cmd === 'start' ? '启动' : '停止'}指令已执行`)
  deviceStore.devices = await deviceApi.list()
  await loadLogs()
}

async function saveParams() {
  await controlApi.setParams(deviceId.value, { ...params })
  ElMessage.success('参数已更新')
  deviceStore.devices = await deviceApi.list()
  await loadLogs()
}

watch(deviceId, () => {
  const d = currentDevice.value
  if (d) {
    params.stroke_rate = d.stroke_rate
    params.stroke_length = d.stroke_length
    params.max_load_limit = d.max_load_limit
    params.current_limit = d.current_limit
  }
  loadLogs()
}, { immediate: true })

onMounted(loadLogs)
</script>
