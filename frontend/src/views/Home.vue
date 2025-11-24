<template>
  <div class="home-page">
    <div class="container">
      <div class="header">
        <h1 class="page-title">文本归档助手</h1>
        <div v-if="authStore.isAuthenticated()" class="user-info">
          <span class="welcome">欢迎回来！</span>
          <button @click="handleLogout" class="btn-logout">登出</button>
        </div>
      </div>
      
      <p class="welcome-text">欢迎使用文本归档助手！</p>
      
      <div class="features">
        <div class="feature-card">
          <h3>📝 备忘录管理</h3>
          <p>创建、编辑和管理您的备忘录</p>
          <span class="coming-soon">即将推出</span>
        </div>
        
        <div class="feature-card">
          <h3>🔍 OCR识别</h3>
          <p>从图片中提取文字内容</p>
          <router-link 
            v-if="authStore.isAuthenticated()" 
            to="/ocr" 
            class="btn btn-primary"
          >
            开始使用
          </router-link>
          <router-link 
            v-else 
            to="/login" 
            class="btn btn-primary"
          >
            登录后使用
          </router-link>
        </div>
        
        <div class="feature-card">
          <h3>🔐 用户认证</h3>
          <p>安全的登录和注册系统</p>
          <router-link 
            v-if="!authStore.isAuthenticated()" 
            to="/login" 
            class="btn btn-secondary"
          >
            登录
          </router-link>
          <router-link 
            v-else 
            to="/register" 
            class="btn btn-secondary"
          >
            已登录
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { logout } from '../api/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await logout()
  authStore.clearAuth()
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f9fafb;
  padding: 2rem 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome {
  color: #6b7280;
  font-size: 0.875rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.btn-logout:hover {
  background: #dc2626;
}

.welcome-text {
  color: #6b7280;
  text-align: center;
  font-size: 1.125rem;
  margin-bottom: 3rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  font-size: 1.5rem;
  color: #111827;
  margin: 0 0 0.75rem 0;
}

.feature-card p {
  color: #6b7280;
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
}

.feature-card .btn {
  margin-top: 0.5rem;
}

.coming-soon {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
