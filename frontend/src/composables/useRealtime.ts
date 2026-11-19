import { onMounted, onUnmounted, ref } from 'vue'
import { useRealtimeStore } from '@/stores'
import type { WsPayload } from '@/types'

/** WebSocket 实时数据订阅：自动连接、断线重连、供多页面复用。 */
export function useRealtime(deviceId: () => number, onMessage?: (payload: WsPayload) => void) {
  const store = useRealtimeStore()
  const ws = ref<WebSocket | null>(null)
  const reconnectTimer = ref<any>(null)
  let manualClose = false

  function connect() {
    if (manualClose) return
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${location.host}/ws/monitoring/${deviceId()}`
    const socket = new WebSocket(url)
    ws.value = socket

    socket.onopen = () => { store.connected = true }
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as WsPayload
        if (payload.type === 'realtime') {
          store.push(payload.data)
          onMessage?.(payload)
        }
      } catch { /* ignore */ }
    }
    socket.onclose = () => {
      store.connected = false
      if (!manualClose) reconnectTimer.value = setTimeout(connect, 3000)
    }
    socket.onerror = () => socket.close()
  }

  function switchDevice() {
    manualClose = true
    if (reconnectTimer.value) clearTimeout(reconnectTimer.value)
    ws.value?.close()
    manualClose = false
    connect()
  }

  onMounted(connect)
  onUnmounted(() => {
    manualClose = true
    if (reconnectTimer.value) clearTimeout(reconnectTimer.value)
    ws.value?.close()
  })

  return { store, ws, switchDevice }
}
