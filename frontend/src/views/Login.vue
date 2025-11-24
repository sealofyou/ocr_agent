<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="card-title">登录</h2>
      
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input 
            v-model="formData.username"
            type="text" 
            class="form-input" 
            placeholder="请输入用户名"
            required
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">密码</label>
          <input 
            v-model="formData.password"
            type="password" 
            class="form-input" 
            placeholder="请输入密码"
            required
            :disabled="loading"
          />
        </div>
        
        <button 
          type="submit" 
          class="btn btn-primary btn-block"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="footer-links">
        <router-link to="/register" class="link">还没有账号？立即注册</router-link>
        <router-link to="/" class="link">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { login } from '../api/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!formData.value.username || !formData.value.password) {
    errorMessage.value = '请填写用户名和密码'
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await login({
      username: formData.value.username,
      password: formData.value.password
    })
    
    // 保存认证信息
    authStore.setAuth(response.access_token, response.user_id)
    
    // 跳转到首页
    router.push('/')
  } catch (err: any) {
    console.error('Login error:', err)
    errorMessage.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.card-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 1.5rem 0;
  text-align: center;
}

.info-text {
  color: #6b7280;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.login-form {
  margin-bottom: 1.5rem;
}

.btn-block {
  width: 100%;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.link:hover {
  color: #2563eb;
  text-decoration: underline;
}
</style>
