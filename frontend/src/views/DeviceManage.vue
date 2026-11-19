<template>
  <div class="page-container">
    <div class="page-header">
      <div><div class="page-title">设备管理</div><div class="page-subtitle">抽油机设备台账的增删改查</div></div>
      <el-button type="primary" icon="Plus" @click="openDialog()">新增设备</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="devices" stripe>
        <el-table-column prop="device_code" label="设备编号" width="120" />
        <el-table-column prop="device_name" label="设备名称" />
        <el-table-column prop="well_location" label="井位" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === 'running' ? 'success' : row.status === 'fault' ? 'danger' : 'info'">
              {{ { running: '运行中', stopped: '已停止', fault: '故障' }[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="stroke_length" label="冲程(m)" width="100" />
        <el-table-column prop="stroke_rate" label="冲次" width="90" />
        <el-table-column prop="pump_depth" label="泵挂(m)" width="100" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑设备' : '新增设备'" width="500px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="设备编号"><el-input v-model="form.device_code" :disabled="!!editing" /></el-form-item>
        <el-form-item label="设备名称"><el-input v-model="form.device_name" /></el-form-item>
        <el-form-item label="井位"><el-input v-model="form.well_location" /></el-form-item>
        <el-form-item label="冲程(m)"><el-input-number v-model="form.stroke_length" :min="0.5" :max="6" :step="0.1" /></el-form-item>
        <el-form-item label="冲次"><el-input-number v-model="form.stroke_rate" :min="1" :max="20" :step="0.5" /></el-form-item>
        <el-form-item label="泵挂(m)"><el-input-number v-model="form.pump_depth" :min="100" :max="5000" :step="100" /></el-form-item>
        <el-form-item label="载荷上限"><el-input-number v-model="form.max_load_limit" :min="10" :max="200" /></el-form-item>
        <el-form-item label="电流上限"><el-input-number v-model="form.current_limit" :min="5" :max="100" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deviceApi } from '@/api'
import { useDeviceStore } from '@/stores'
import type { Device } from '@/types'

const store = useDeviceStore()
const devices = ref<Device[]>([])
const dialogVisible = ref(false)
const editing = ref<Device | null>(null)
const form = reactive<any>({})

async function load() {
  devices.value = await deviceApi.list()
  store.devices = devices.value
}

function openDialog(row?: Device) {
  editing.value = row || null
  Object.assign(form, row ? { ...row } : {
    device_code: '', device_name: '', well_location: '',
    stroke_length: 3, stroke_rate: 6, pump_depth: 1200,
    max_load_limit: 90, current_limit: 45,
  })
  if (!row) delete form.id
  dialogVisible.value = true
}

async function save() {
  if (editing.value) await deviceApi.update(editing.value.id, form)
  else await deviceApi.create(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(row: Device) {
  await ElMessageBox.confirm(`确认删除设备 ${row.device_name}？`, '提示', { type: 'warning' })
  await deviceApi.delete(row.id)
  ElMessage.success('删除成功')
  await load()
}

onMounted(load)
</script>
