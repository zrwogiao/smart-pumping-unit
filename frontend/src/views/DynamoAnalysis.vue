<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <div class="page-title">示功图分析诊断</div>
        <div class="page-subtitle">生成典型工况示功图 · 特征提取 · 规则/模板/机器学习三法诊断对比</div>
      </div>
      <DeviceSelector v-model="deviceId" />
    </div>

    <el-card shadow="never" style="margin-bottom:16px">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between">
          <span>工况模拟器</span>
          <span class="page-subtitle">点击生成不同工况的示功图并自动诊断</span>
        </div>
      </template>
      <div style="display:flex; flex-wrap:wrap; gap:10px">
        <el-button v-for="c in conditions" :key="c.key"
                   :type="c.key === selectedCondition ? 'primary' : 'default'"
                   @click="generate(c.key)">
          {{ c.label }}
        </el-button>
        <el-button type="success" plain @click="analyzeAll" :disabled="!currentCard">三法对比诊断</el-button>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div style="display:flex; align-items:center; justify-content:space-between">
              <span>示功图（实线=实测，虚线=标准模板）</span>
              <ConditionTag v-if="diagnosis" :label="diagnosis.label" :color="conditionColor" />
            </div>
          </template>
          <DynamoChart v-if="cardData" :displacement="cardData.displacement" :load="cardData.load"
                       :height="'420px'" :condition-label="diagnosis?.label" :condition-color="conditionColor"
                       :template-displacement="templateData?.displacement" :template-load="templateData?.load" />
          <div v-else class="empty-tip">请选择工况生成示功图</div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never" style="margin-bottom:16px">
          <template #header>诊断结论</template>
          <template v-if="diagnosis">
            <div style="text-align:center; padding:10px 0">
              <div style="font-size:34px; font-weight:bold" :style="{color:conditionColor}">{{ diagnosis.label }}</div>
              <div style="font-size:13px; color:#909399; margin-top:6px">置信度 {{ (diagnosis.confidence*100).toFixed(0) }}%</div>
            </div>
            <el-alert :title="diagnosis.suggestion" type="info" :closable="false" show-icon />
            <div v-if="diagnosis.evidence" style="margin-top:12px; font-size:12px; color:#606266; background:#f8f9fb; padding:10px; border-radius:4px">
              判定依据：{{ diagnosis.evidence }}
            </div>
          </template>
          <div v-else class="empty-tip">尚未诊断</div>
        </el-card>

        <el-card shadow="never">
          <template #header>特征参数</template>
          <el-descriptions :column="2" border size="small" v-if="features">
            <el-descriptions-item label="Pmax">{{ features.pmax }} kN</el-descriptions-item>
            <el-descriptions-item label="Pmin">{{ features.pmin }} kN</el-descriptions-item>
            <el-descriptions-item label="载荷差span">{{ features.span }}</el-descriptions-item>
            <el-descriptions-item label="面积">{{ features.area }}</el-descriptions-item>
            <el-descriptions-item label="填充系数">{{ features.fill }}</el-descriptions-item>
            <el-descriptions-item label="载荷基线">{{ features.pbase }}</el-descriptions-item>
            <el-descriptions-item label="底部凹陷">{{ features.notch_depth }}</el-descriptions-item>
            <el-descriptions-item label="右上凸起">{{ features.bulge_height }}</el-descriptions-item>
          </el-descriptions>
          <div v-else class="empty-tip">暂无特征数据</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 三法对比 -->
    <el-card shadow="never" style="margin-top:16px" v-if="comparison">
      <template #header>三种诊断方法对比</template>
      <el-table :data="comparisonTable" stripe>
        <el-table-column prop="method" label="诊断方法" width="140" />
        <el-table-column prop="label" label="诊断工况" />
        <el-table-column prop="confidence" label="置信度" width="120">
          <template #default="{row}">{{ (row.confidence*100).toFixed(0) }}%</template>
        </el-table-column>
        <el-table-column prop="evidence" label="判定依据" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import DeviceSelector from '@/components/DeviceSelector.vue'
import DynamoChart from '@/components/DynamoChart.vue'
import ConditionTag from '@/components/ConditionTag.vue'
import { dynamoApi, diagnosisApi } from '@/api'
import { useDeviceStore } from '@/stores'
import type { ConditionInfo, DynamoCard } from '@/types'

const deviceStore = useDeviceStore()
const deviceId = ref(deviceStore.currentDeviceId || 1)
const conditions = ref<ConditionInfo[]>([])
const selectedCondition = ref('normal')
const currentCard = ref<DynamoCard | null>(null)
const cardData = ref<{ displacement: number[]; load: number[] } | null>(null)
const templateData = ref<{ displacement: number[]; load: number[] } | null>(null)
const diagnosis = ref<any>(null)
const features = ref<any>(null)
const comparison = ref<any>(null)

const conditionColor = computed(() => conditions.value.find((c) => c.label === diagnosis.value?.label)?.color || '#409EFF')

const comparisonTable = computed(() => {
  if (!comparison.value?.results) return []
  return Object.entries(comparison.value.results).map(([method, r]: [string, any]) => ({
    method: { rule: '规则决策树', template: '模板匹配(DTW)', ml: '机器学习(KNN)' }[method] || method,
    label: r.label, confidence: r.confidence, evidence: r.evidence,
  }))
})

async function generate(condition: string) {
  selectedCondition.value = condition
  const card = await dynamoApi.generate(deviceId.value, condition)
  currentCard.value = card
  cardData.value = { displacement: JSON.parse(card.displacement), load: JSON.parse(card.load) }
  diagnosis.value = null
  features.value = null
  comparison.value = null
  // 自动用规则诊断
  const res = await diagnosisApi.analyze(deviceId.value, 'rule', card.id)
  diagnosis.value = res
  features.value = typeof res.features_json === 'string' ? JSON.parse(res.features_json) : res.features_json
  // 生成标准模板用于对比
  try {
    const tmpl = await dynamoApi.generate(deviceId.value, condition)
    templateData.value = { displacement: JSON.parse(tmpl.displacement), load: JSON.parse(tmpl.load) }
  } catch { /* ignore */ }
}

async function analyzeAll() {
  if (!currentCard.value) return
  const res = await diagnosisApi.analyze(deviceId.value, 'all', currentCard.value.id)
  comparison.value = res
  features.value = res.features
}

onMounted(async () => {
  conditions.value = await diagnosisApi.conditions()
  if (conditions.value.length) generate('gas_affected')
})
</script>
