<template>
  <div ref="chartEl" :style="{ width: '100%', height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  points: Array<{ timestamp: string; value: number }>
  title?: string
  metric?: string
  height?: string
  color?: string
}>(), { title: '趋势曲线', metric: '数值', height: '300px', color: '#409EFF' })

const chartEl = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function render() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  chart.setOption({
    title: { text: props.title, left: 'center', textStyle: { fontSize: 15, color: '#303133' } },
    tooltip: { trigger: 'axis' },
    grid: { left: 55, right: 25, top: 45, bottom: 40 },
    xAxis: {
      type: 'category',
      data: props.points.map((p) => p.timestamp.slice(11, 19) || p.timestamp),
      axisLine: { lineStyle: { color: '#909399' } },
      axisLabel: { color: '#909399', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: props.metric,
      axisLine: { lineStyle: { color: '#909399' } },
      splitLine: { lineStyle: { color: '#ebeef5' } },
    },
    series: [{
      type: 'line',
      data: props.points.map((p) => p.value),
      smooth: true,
      symbol: 'none',
      lineStyle: { color: props.color, width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: props.color + '55' },
          { offset: 1, color: props.color + '05' },
        ]),
      },
    }],
  }, true)
}

function resize() { chart?.resize() }
onMounted(() => { nextTick(render); window.addEventListener('resize', resize) })
onUnmounted(() => { window.removeEventListener('resize', resize); chart?.dispose(); chart = null })
watch(() => props.points, render, { deep: true })
</script>
