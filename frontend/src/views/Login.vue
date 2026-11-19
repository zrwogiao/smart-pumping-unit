<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-brand">
        <div class="brand-icon">⛽</div>
        <h1>智能抽油机系统</h1>
        <p>智慧油气田应用开发 · 课程小组项目</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button type="primary" size="large" style="width:100%" :loading="loading" @click="handleLogin">登录</el-button>
      </el-form>
      <div class="demo-tip">演示账号：admin / admin123　或　operator / 123456</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { useUserStore } from '@/stores'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: 'admin', password: 'admin123' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res = await authApi.login(form.username, form.password)
    userStore.setLogin(res.access_token, res.user)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: radial-gradient(ellipse at top, #12345c 0%, #0a1a30 60%, #050d18 100%);
}
.login-box { width: 400px; background: rgba(255,255,255,0.98); border-radius: 12px; padding: 36px; box-shadow: 0 12px 40px rgba(0,0,0,0.3); }
.login-brand { text-align: center; margin-bottom: 28px; }
.brand-icon { font-size: 44px; }
.login-brand h1 { font-size: 22px; color: #1a3a5c; margin: 10px 0 4px; }
.login-brand p { font-size: 12px; color: #909399; }
.demo-tip { text-align: center; font-size: 12px; color: #a0a8b5; margin-top: 18px; }
</style>
