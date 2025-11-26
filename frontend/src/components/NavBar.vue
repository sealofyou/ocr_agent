<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          📝 文本归档助手
        </router-link>
      </div>

      <!-- 移动端菜单按钮 -->
      <button class="mobile-menu-btn" @click="toggleMenu">
        <span v-if="!menuOpen">☰</span>
        <span v-else>✕</span>
      </button>

      <!-- 导航菜单 -->
      <div class="nav-menu" :class="{ 'menu-open': menuOpen }">
        <template v-if="authStore.isAuthenticated()">
          <router-link to="/memos" class="nav-link" @click="closeMenu">
            📝 备忘录
          </router-link>
          <router-link to="/schedules" class="nav-link" @click="closeMenu">
            📅 日程
          </router-link>
          <router-link to="/ocr" class="nav-link" @click="closeMenu">
            🔍 OCR识别
          </router-link>
          <button @click="handleLogout" class="nav-link logout-btn">
            🚪 登出
          </button>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-link" @click="closeMenu">
            🔐 登录
          </router-link>
          <router-link to="/register" class="nav-link" @click="closeMenu">
            📋 注册
          </router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { logout } from '../api/auth'

const router = useRouter()
const authStore = useAuthStore()
const menuOpen = ref(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const closeMenu = () => {
  menuOpen.value = false
}

const handleLogout = async () => {
  try {
    await logout()
    authStore.clearAuth()
    closeMenu()
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
  }
}
</script>

<style scoped>
.navbar {
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-brand {
  flex-shrink: 0;
}

.brand-link {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-link:hover {
  color: #3b82f6;
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  color: #374151;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  padding: 0.5rem 1rem;
  color: #374151;
  text-decoration: none;
  border-radius: 0.375rem;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.nav-link:hover {
  background: #f3f4f6;
  color: #3b82f6;
}

.nav-link.router-link-active {
  background: #dbeafe;
  color: #1e40af;
}

.logout-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
}

.logout-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
  }

  .nav-menu {
    position: absolute;
    top: 64px;
    left: 0;
    right: 0;
    background: white;
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: none;
  }

  .nav-menu.menu-open {
    display: flex;
  }

  .nav-link {
    padding: 0.75rem 1rem;
    text-align: left;
  }
}
</style>
