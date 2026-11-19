import request from './request'
import type { Device, DynamoCard, DiagnosisResult, ConditionInfo, Alarm, ControlLog, RealtimeData } from '@/types'

export const authApi = {
  login: (username: string, password: string) =>
    request.post<any, any>('/auth/login', { username, password }),
  me: () => request.get<any, any>('/auth/me'),
}

export const deviceApi = {
  list: () => request.get<any, Device[]>('/devices'),
  create: (data: Partial<Device>) => request.post<any, Device>('/devices', data),
  update: (id: number, data: Partial<Device>) => request.put<any, Device>(`/devices/${id}`, data),
  delete: (id: number) => request.delete<any, any>(`/devices/${id}`),
}

export const monitoringApi = {
  latest: (deviceId: number) => request.get<any, RealtimeData>(`/monitoring/latest/${deviceId}`),
  series: (deviceId: number, limit = 100) => request.get<any, RealtimeData[]>(`/monitoring/series/${deviceId}?limit=${limit}`),
  simulateStart: () => request.post<any, any>('/monitoring/simulate/start'),
  simulateStop: () => request.post<any, any>('/monitoring/simulate/stop'),
  simulateStatus: () => request.get<any, { running: boolean }>('/monitoring/simulate/status'),
}

export const dynamoApi = {
  generate: (deviceId: number, condition: string) =>
    request.post<any, DynamoCard>('/dynamo/generate', { device_id: deviceId, condition }),
  latest: (deviceId: number) => request.get<any, DynamoCard>(`/dynamo/latest/${deviceId}`),
  conditions: () => request.get<any, ConditionInfo[]>('/dynamo/conditions/list'),
}

export const diagnosisApi = {
  analyze: (deviceId: number, method = 'rule', dynamoId?: number) =>
    request.post<any, any>('/diagnosis/analyze', { device_id: deviceId, method, dynamo_id: dynamoId }),
  results: (deviceId: number, limit = 50) =>
    request.get<any, DiagnosisResult[]>(`/diagnosis/results/${deviceId}?limit=${limit}`),
  conditions: () => request.get<any, ConditionInfo[]>('/diagnosis/conditions'),
}

export const historyApi = {
  query: (params: Record<string, any>) => request.get<any, any>('/history/query', { params }),
  trend: (params: Record<string, any>) => request.get<any, { metric: string; points: Array<{ timestamp: string; value: number }> }>('/history/trend', { params }),
  summary: () => request.get<any, any>('/history/reports/summary'),
  exportUrl: (params: Record<string, any>) => {
    const q = new URLSearchParams(params).toString()
    return `/api/v1/history/reports/export?${q}`
  },
}

export const controlApi = {
  start: (deviceId: number) => request.post<any, ControlLog>(`/control/${deviceId}/start`),
  stop: (deviceId: number) => request.post<any, ControlLog>(`/control/${deviceId}/stop`),
  setParams: (deviceId: number, data: Record<string, number>) => request.put<any, ControlLog>(`/control/${deviceId}/params`, data),
  logs: (deviceId: number) => request.get<any, ControlLog[]>(`/control/${deviceId}/logs`),
}

export const alarmApi = {
  list: (params?: Record<string, any>) => request.get<any, Alarm[]>('/alarms', { params }),
  ack: (id: number) => request.put<any, Alarm>(`/alarms/${id}/ack`),
  clear: (id: number) => request.put<any, Alarm>(`/alarms/${id}/clear`),
}
