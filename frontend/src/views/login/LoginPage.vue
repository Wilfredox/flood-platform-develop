<script setup lang="ts">
/**
 * M10 用户认证 · 登录页面
 * [DEMO-ONLY] 使用 Mock 用户数据验证
 * 内置账号：admin/admin123, province/p123, city/c123, county/co123, viewer/v123
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const formRef = ref()

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true

  // [DEMO-ONLY] 模拟网络延迟
  await new Promise(r => setTimeout(r, 600))

  const success = authStore.login(loginForm.username, loginForm.password)
  loading.value = false

  if (success) {
    ElMessage.success(`欢迎回来，${authStore.user?.name}`)
    router.push('/dashboard')
  } else {
    ElMessage.error('用户名或密码错误')
  }
}
</script>

<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <img src="@/assets/logo.svg" alt="logo" class="login-logo" />
        <h1>澜镜数字孪生洪水预警监管平台</h1>
        <p>LanJing Digital Twin Flood Warning Platform</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Demo 账号提示 -->
      <div class="demo-hint">
        <el-divider>Demo 测试账号</el-divider>
        <div class="account-list">
          <span class="account-item"><b>超管</b> admin / admin123</span>
          <span class="account-item"><b>省级</b> province / p123</span>
          <span class="account-item"><b>市级</b> city / c123</span>
          <span class="account-item"><b>县级</b> county / co123</span>
          <span class="account-item"><b>观察员</b> viewer / v123</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 50%, #0a1628 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
}

.c1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #1890FF, transparent);
  top: -200px;
  right: -100px;
}

.c2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #00D4FF, transparent);
  bottom: -150px;
  left: -100px;
}

.c3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #52C41A, transparent);
  top: 50%;
  left: 10%;
}

.login-card {
  width: 420px;
  padding: 48px 40px 36px;
  background: rgba(27, 40, 56, 0.9);
  border: 1px solid rgba(42, 63, 85, 0.6);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 12px;
  border-radius: 16px;
}

.login-header h1 {
  font-size: 22px;
  color: #E8F0FE;
  margin-bottom: 6px;
  font-weight: 600;
}

.login-header p {
  font-size: 12px;
  color: #5A7A9E;
  letter-spacing: 0.5px;
}

.login-form {
  margin-top: 24px;
}

.login-form :deep(.el-input__wrapper) {
  background: rgba(13, 27, 42, 0.8);
  border: 1px solid #2A3F55;
  border-radius: 8px;
  box-shadow: none;
}

.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #1890FF;
}

.login-form :deep(.el-input__inner) {
  color: #E8F0FE;
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: #5A7A9E;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1890FF, #00D4FF);
  border: none;
}

.login-btn:hover {
  opacity: 0.9;
}

.demo-hint {
  margin-top: 16px;
}

.demo-hint :deep(.el-divider__text) {
  background: transparent;
  color: #5A7A9E;
  font-size: 12px;
}

.demo-hint :deep(.el-divider) {
  border-color: #2A3F55;
}

.account-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.account-item {
  font-size: 11px;
  color: #5A7A9E;
  background: rgba(13, 27, 42, 0.6);
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #2A3F55;
}

.account-item b {
  color: #8BA3C7;
  margin-right: 4px;
}
</style>
