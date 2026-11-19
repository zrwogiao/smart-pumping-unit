// 全局类型定义

export interface User {
  id: number
  username: string
  real_name: string
  role: string
}

export interface ApiResult<T = any> {
  code: number
  message: string
  data: T
}

export interface Device {
  id: number
  device_code: string
  device_name: string
  well_location: string
  status: 'running' | 'stopped' | 'fault'
  stroke_length: number
  stroke_rate: number
  pump_depth: number
  max_load_limit: number
  current_limit: number
  last_heartbeat: string
}

export interface RealtimeData {
  id?: number
  device_id: number
  timestamp: string
  max_load: number
  min_load: number
  displacement: number
  current: number
  voltage: number
  stroke_rate: number
  stroke_length: number
  power: number
}

export interface DynamoCard {
  id: number
  device_id: number
  timestamp: string
  source: string
  condition_hint: string
  displacement: string
  load: string
  max_load: number
  min_load: number
  area: number
}

export interface ConditionInfo {
  key: string
  label: string
  description: string
  color: string
}

export interface DiagnosisResult {
  id: number
  dynamo_id: number
  device_id: number
  condition: string
  condition_label: string
  confidence: number
  features_json: string
  method: string
  suggestion: string
  diagnosed_at: string
}

export interface Alarm {
  id: number
  device_id: number
  alarm_type: string
  level: 'info' | 'warning' | 'critical'
  message: string
  value: number | null
  status: 'active' | 'acknowledged' | 'cleared'
  triggered_at: string
}

export interface ControlLog {
  id: number
  device_id: number
  command: string
  params_json: string
  result: string
  executed_at: string
}

export interface WsPayload {
  type: string
  device_id: number
  data: RealtimeData
  diagnosis: { condition: string; label: string; confidence: number } | null
  dynamo: { displacement: number[]; load: number[] } | null
  alarms: Array<{ id: number; type: string; level: string; message: string }>
}
