import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Device, RealtimeData, User } from '@/types'

export const useDeviceStore = defineStore('device', () => {
  const devices = ref<Device[]>([])
  const currentDeviceId = ref<number>(1)

  const currentDevice = () => devices.value.find((d) => d.id === currentDeviceId.value)

  return { devices, currentDeviceId, currentDevice }
})

export const useRealtimeStore = defineStore('realtime', () => {
  const latest = ref<RealtimeData | null>(null)
  const connected = ref(false)
  const history = ref<RealtimeData[]>([])

  function push(data: RealtimeData) {
    latest.value = data
    history.value.push(data)
    if (history.value.length > 200) history.value.shift()
  }

  return { latest, connected, history, push }
})

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loggedIn = ref(!!token.value)

  function setLogin(tokenValue: string, userInfo: User) {
    token.value = tokenValue
    user.value = userInfo
    loggedIn.value = true
    localStorage.setItem('token', tokenValue)
  }

  function logout() {
    token.value = null
    user.value = null
    loggedIn.value = false
    localStorage.removeItem('token')
  }

  return { user, token, loggedIn, setLogin, logout }
})
