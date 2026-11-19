import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  {
    path: '/',
    component: AppLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '监控大屏' } },
      { path: 'realtime', name: 'Realtime', component: () => import('@/views/RealtimeMonitor.vue'), meta: { title: '实时监测' } },
      { path: 'dynamo', name: 'Dynamo', component: () => import('@/views/DynamoAnalysis.vue'), meta: { title: '示功图诊断' } },
      { path: 'history', name: 'History', component: () => import('@/views/HistoryData.vue'), meta: { title: '历史数据' } },
      { path: 'reports', name: 'Reports', component: () => import('@/views/Reports.vue'), meta: { title: '统计报表' } },
      { path: 'control', name: 'Control', component: () => import('@/views/Control.vue'), meta: { title: '远程控制' } },
      { path: 'devices', name: 'Devices', component: () => import('@/views/DeviceManage.vue'), meta: { title: '设备管理' } },
      { path: 'alarms', name: 'Alarms', component: () => import('@/views/Alarms.vue'), meta: { title: '告警中心' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
