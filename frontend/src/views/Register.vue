<template>
  <div class="register-page">
    <div class="register-card">
      <h2 class="card-title">注册</h2>
      <p class="info-text">注册功能将在后续任务中实现</p>
      
      <form class="register-form">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input type="text" class="form-input" placeholder="请输入用户名" disabled />
        </div>
        
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input type="email" class="form-input" placeholder="请输入邮箱" disabled />
        </div>
        
        <div class="form-group">
          <label class="form-label">密码</label>
          <input type="password" class="form-input" placeholder="请输入密码" disabled />
        </div>
        
        <div class="form-group">
          <label class="form-label">确认密码</label>
          <input type="password" class="form-input" placeholder="请再次输入密码" disabled />
        </div>
        
        <button type="button" class="btn btn-primary btn-block" disabled>注册</button>
      </form>
      
      <div class="footer-links">
        <router-link to="/login" class="link">已有账号？立即登录</router-link>
        <router-link to="/" class="link">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 注册逻辑将在后续任务中实现
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
