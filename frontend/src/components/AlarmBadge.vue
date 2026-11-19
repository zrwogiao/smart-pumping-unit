<template>
  <el-badge :value="count" :hidden="count === 0" :type="count > 0 ? 'danger' : 'info'">
    <slot />
  </el-badge>
</template>

<script setup lang="ts">
defineProps<{ count: number }>()
</script>
