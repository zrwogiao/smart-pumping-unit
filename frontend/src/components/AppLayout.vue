<template>
  <el-container class="app-layout">
    <el-aside width="230px" class="sidebar">
      <div class="logo">
        <div class="logo-icon">⛽</div>
        <div>
          <div class="logo-title">智能抽油机系统</div>
          <div class="logo-sub">智慧油气田 · 教学演示</div>
        </div>
      </div>
      <el-menu :default-active="route.path" router class="side-menu" background-color="#0d1b2a" text-color="#a0b0c0" active-text-color="#409EFF">
        <el-menu-item index="/dashboard"><el-icon><DataBoard /></el-icon><span>监控大屏</span></el-menu-item>
        <el-menu-item index="/realtime"><el-icon><Odometer /></el-icon><span>实时监测</span></el-menu-item>
        <el-menu-item index="/dynamo"><el-icon><TrendCharts /></el-icon><span>示功图诊断</span></el-menu-item>
        <el-menu-item index="/history"><el-icon><Clock /></el-icon><span>历史数据</span></el-menu-item>
        <el-menu-item index="/reports"><el-icon><Document /></el-icon><span>统计报表</span></el-menu-item>
        <el-menu-item index="/control"><el-icon><Setting /></el-icon><span>远程控制</span></el-menu-item>
        <el-menu-item index="/devices"><el-icon><Monitor /></el-icon><span>设备管理</span></el-menu-item>
        <el-menu-item index="/alarms">
          <el-icon><Bell /></el-icon><span>告警中心</span>
          <el-badge v-if="activeAlarmCount > 0" :value="activeAlarmCount" class="menu-badge" />
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">课程小组项目 · v1.0</div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          <span>{{ route.meta.title || '首页' }}</span>
        </div>
        <div class="header-right">
          <span class="status-dot" :class="realtimeStore.connected ? 'online' : 'offline'"></span>
          <span class="status-text">{{ realtimeStore.connected ? '数据连接正常' : '连接中...' }}</span>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="30" icon="User" />
              <span>{{ userStore.user?.real_name || '演示用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataBoard, Odometer, TrendCharts, Clock, Document, Setting, Monitor, Bell,
} from '@element-plus/icons-vue'
import { useUserStore, useRealtimeStore } from '@/stores'
import { deviceApi, alarmApi } from '@/api'
import { useDeviceStore } from '@/stores'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const realtimeStore = useRealtimeStore()
const deviceStore = useDeviceStore()
const activeAlarmCount = ref(0)
let globalWs: WebSocket | null = null
let wsTimer: any = null
let wsManualClose = false

function handleCommand(cmd: string) {
  if (cmd === 'logout') { userStore.logout(); router.push('/login') }
}

function connectGlobalWs() {
  if (wsManualClose) return
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const socket = new WebSocket(`${protocol}//${location.host}/ws/monitoring/0`)
  globalWs = socket
  socket.onopen = () => { realtimeStore.connected = true }
  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === 'realtime' && payload.alarms?.length) {
        activeAlarmCount.value += payload.alarms.length
      }
    } catch { /* ignore */ }
  }
  socket.onclose = () => {
    realtimeStore.connected = false
    if (!wsManualClose) wsTimer = setTimeout(connectGlobalWs, 3000)
  }
  socket.onerror = () => socket.close()
}

onMounted(async () => {
  try {
    const devices = await deviceApi.list()
    deviceStore.devices = devices
  } catch { /* ignore */ }
  try {
    const alarms = await alarmApi.list({ status: 'active' })
    activeAlarmCount.value = alarms.length
  } catch { /* ignore */ }
  connectGlobalWs()
})

onUnmounted(() => {
  wsManualClose = true
  if (wsTimer) clearTimeout(wsTimer)
  globalWs?.close()
})
</script>

<style scoped>
.app-layout { height: 100vh; }
.sidebar { background: #0d1b2a; display: flex; flex-direction: column; }
.logo { display: flex; align-items: center; gap: 10px; padding: 20px 16px; border-bottom: 1px solid #1e3044; color: #fff; }
.logo-icon { font-size: 28px; }
.logo-title { font-size: 15px; font-weight: bold; }
.logo-sub { font-size: 10px; color: #6b8299; margin-top: 2px; }
.side-menu { border-right: none; flex: 1; }
.menu-badge { margin-left: 6px; }
.sidebar-footer { padding: 12px; text-align: center; font-size: 11px; color: #4a6180; border-top: 1px solid #1e3044; }
.header { background: #fff; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e4e7ed; }
.breadcrumb { font-size: 16px; font-weight: 600; color: #303133; }
.header-right { display: flex; align-items: center; gap: 12px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.status-dot.online { background: #67c23a; box-shadow: 0 0 6px #67c23a; }
.status-dot.offline { background: #c0c4cc; }
.status-text { font-size: 12px; color: #909399; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; }
.main { background: #f0f2f5; padding: 20px; overflow-y: auto; }
</style>
