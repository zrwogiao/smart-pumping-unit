<template>
  <el-select :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)"
             placeholder="选择设备" style="width: 200px" filterable>
    <el-option v-for="d in store.devices" :key="d.id" :label="`${d.device_name} (${d.device_code})`" :value="d.id">
      <span>{{ d.device_name }}</span>
      <span style="float:right; color:#909399; font-size:12px">{{ d.device_code }}</span>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import { useDeviceStore } from '@/stores'
defineProps<{ modelValue: number }>()
defineEmits<{ 'update:modelValue': [value: number] }>()
const store = useDeviceStore()
</script>
