<template>
  <div class="register-page">
    <div class="register-card">
      <h2 class="card-title">注册</h2>
      
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>
      
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input 
            v-model="formData.username"
            type="text" 
            class="form-input" 
            placeholder="请输入用户名"
            required
            :disabled="loading"
            minlength="3"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input 
            v-model="formData.email"
            type="email" 
            class="form-input" 
            placeholder="请输入邮箱"
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
            placeholder="请输入密码（至少6位）"
            required
            :disabled="loading"
            minlength="6"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">确认密码</label>
          <input 
            v-model="formData.confirmPassword"
            type="password" 
            class="form-input" 
            placeholder="请再次输入密码"
            required
            :disabled="loading"
          />
        </div>
        
        <button 
          type="submit" 
          class="btn btn-primary btn-block"
          :disabled="loading"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="footer-links">
        <router-link to="/login" class="link">已有账号？立即登录</router-link>
        <router-link to="/" class="link">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { register } from '../api/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''
  
  // 验证表单
  if (!formData.value.username || !formData.value.email || !formData.value.password) {
    errorMessage.value = '请填写所有必填项'
    return
  }
  
  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  if (formData.value.password.length < 6) {
    errorMessage.value = '密码长度至少为6位'
    return
  }
  
  loading.value = true
  
  try {
    const response = await register({
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password
    })
    
    // 保存认证信息
    authStore.setAuth(response.access_token, response.user_id)
    
    successMessage.value = '注册成功！正在跳转...'
    
    // 延迟跳转以显示成功消息
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } catch (err: any) {
    console.error('Register error:', err)
    errorMessage.value = err.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.register-card {
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

.register-form {
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
