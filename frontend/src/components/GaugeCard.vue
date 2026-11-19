<template>
  <div ref="chartEl" :style="{ width: '100%', height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  value: number
  title: string
  max?: number
  unit?: string
  height?: string
  color?: string
}>(), { max: 100, unit: '', height: '180px', color: '#409EFF' })

const chartEl = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function render() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  const ratio = Math.min(1, Math.max(0, props.value / props.max))
  chart.setOption({
    series: [{
      type: 'gauge',
      startAngle: 210, endAngle: -30,
      min: 0, max: props.max,
      radius: '92%', center: ['50%', '58%'],
      progress: { show: true, width: 12, itemStyle: { color: props.color } },
      axisLine: { lineStyle: { width: 12, color: [[1, '#ebeef5']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: true, offsetCenter: [0, '35%'], color: '#606266', fontSize: 12 },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, '-5%'],
        formatter: `{value} ${props.unit}`,
        color: props.color, fontSize: 22, fontWeight: 'bold',
      },
      data: [{ value: props.value, name: props.title }],
    }],
  }, true)
}

function resize() { chart?.resize() }
onMounted(() => { nextTick(render); window.addEventListener('resize', resize) })
onUnmounted(() => { window.removeEventListener('resize', resize); chart?.dispose(); chart = null })
watch(() => props.value, render)
</script>
