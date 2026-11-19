<template>
  <span class="condition-tag" :style="{ backgroundColor: color + '20', color: color, borderColor: color }">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ label: string; color?: string }>()
const color = computed(() => props.color || '#409EFF')
</script>

<style scoped>
.condition-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  border: 1px solid;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
</style>
