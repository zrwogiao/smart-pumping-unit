<template>
  <div ref="chartEl" :style="{ width: width, height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  displacement: number[]
  load: number[]
  height?: string
  width?: string
  title?: string
  conditionLabel?: string
  conditionColor?: string
  templateLoad?: number[]
  templateDisplacement?: number[]
}>(), {
  height: '360px',
  width: '100%',
  title: '示功图',
  conditionColor: '#409EFF',
})

const chartEl = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function buildOption() {
  const series: any[] = [
    {
      name: '示功图',
      type: 'line',
      data: props.displacement.map((s, i) => [s, props.load[i]]),
      smooth: 0.2,
      symbol: 'none',
      lineStyle: { width: 2.5, color: props.conditionColor || '#409EFF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: hexToRgba(props.conditionColor, 0.35) },
          { offset: 1, color: hexToRgba(props.conditionColor, 0.02) },
        ]),
      },
    },
  ]

  if (props.templateLoad?.length) {
    series.push({
      name: '标准模板',
      type: 'line',
      data: (props.templateDisplacement || props.displacement).map((s, i) => [s, props.templateLoad![i]]),
      smooth: 0.2,
      symbol: 'none',
      lineStyle: { width: 1.5, type: 'dashed', color: '#909399' },
    })
  }

  const maxLoad = Math.max(...props.load, 0)
  const minLoad = Math.min(...props.load, 0)

  return {
    title: {
      text: props.title,
      left: 'center',
      textStyle: { color: '#303133', fontSize: 15 },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        if (!p) return ''
        return `位移: ${p.value[0]}<br/>载荷: ${p.value[1]} kN`
      },
    },
    legend: {
      data: series.map((s) => s.name),
      bottom: 0,
      textStyle: { color: '#606266' },
    },
    grid: { left: 60, right: 30, top: 50, bottom: 50 },
    xAxis: {
      type: 'value',
      name: '位移 (归一化)',
      nameLocation: 'middle',
      nameGap: 28,
      min: 0, max: 1,
      axisLine: { lineStyle: { color: '#909399' } },
      splitLine: { lineStyle: { color: '#ebeef5' } },
    },
    yAxis: {
      type: 'value',
      name: '载荷 (kN)',
      min: (v: any) => Math.floor(v.min - 5),
      axisLine: { lineStyle: { color: '#909399' } },
      splitLine: { lineStyle: { color: '#ebeef5' } },
    },
    series,
    graphic: [
      {
        type: 'text',
        left: 'right', top: 30,
        style: {
          text: `Pmax: ${maxLoad.toFixed(1)} kN\nPmin: ${minLoad.toFixed(1)} kN`,
          fill: '#606266', fontSize: 12, lineHeight: 18,
        },
      },
      ...(props.conditionLabel ? [{
        type: 'text', left: 10, top: 30,
        style: { text: `诊断: ${props.conditionLabel}`, fill: props.conditionColor, fontSize: 14, fontWeight: 'bold' },
      }] : []),
    ],
  }
}

function hexToRgba(hex: string, alpha: number) {
  const h = hex.replace('#', '')
  const r = parseInt(h.substring(0, 2), 16) || 64
  const g = parseInt(h.substring(2, 4), 16) || 158
  const b = parseInt(h.substring(4, 6), 16) || 255
  return `rgba(${r},${g},${b},${alpha})`
}

function render() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  chart.setOption(buildOption(), true)
}

function resize() { chart?.resize() }

onMounted(() => { nextTick(render); window.addEventListener('resize', resize) })
onUnmounted(() => { window.removeEventListener('resize', resize); chart?.dispose(); chart = null })

watch(() => [props.displacement, props.load, props.conditionColor, props.templateLoad], render, { deep: true })
</script>
