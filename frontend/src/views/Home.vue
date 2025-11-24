<template>
  <div class="home-page">
    <div class="container">
      <h1 class="page-title">文本归档助手</h1>
      <p class="welcome-text">欢迎使用文本归档助手！</p>
      
      <div class="features">
        <div class="feature-card">
          <h3>📝 备忘录管理</h3>
          <p>创建、编辑和管理您的备忘录</p>
        </div>
        
        <div class="feature-card">
          <h3>🔍 OCR识别</h3>
          <p>从图片中提取文字内容</p>
          <router-link to="/ocr" class="btn btn-primary">开始使用</router-link>
        </div>
        
        <div class="feature-card">
          <h3>🔐 用户认证</h3>
          <p>安全的登录和注册系统</p>
          <router-link to="/login" class="btn btn-secondary">登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑将在后续任务中实现
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f9fafb;
  padding: 2rem 1rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 1rem 0;
  text-align: center;
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

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
