# 手写管理助手 - 前端

基于Vue 3 + TypeScript + Tailwind CSS开发的手写管理助手前端应用。

## 功能特性

- 用户注册和登录
- 图片上传和拍照
- OCR文字识别预览和编辑
- 日程管理和查看
- 备忘录管理和标签
- 全文搜索
- 响应式设计

## 技术栈

- Vue 3 (Composition API)
- TypeScript
- Tailwind CSS
- Vue Router
- Pinia (状态管理)
- Axios (HTTP客户端)
- Vite (构建工具)

## 项目结构

```
frontend/
├── src/
│   ├── api/                   # API客户端
│   │   └── client.ts          # Axios配置
│   ├── components/            # 可复用组件
│   ├── router/                # 路由配置
│   │   └── index.ts
│   ├── stores/                # Pinia状态管理
│   │   └── auth.ts            # 认证状态
│   ├── views/                 # 页面组件
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   └── Register.vue
│   ├── App.vue                # 根组件
│   ├── main.ts                # 应用入口
│   └── style.css              # 全局样式
├── public/                    # 静态资源
├── index.html                 # HTML模板
├── package.json               # 依赖配置
├── tailwind.config.js         # Tailwind配置
├── tsconfig.json              # TypeScript配置
└── vite.config.ts             # Vite配置
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产构建

```bash
npm run preview
```

## 开发规范

1. 使用Composition API编写组件
2. 使用TypeScript进行类型检查
3. 使用Tailwind CSS进行样式开发
4. 组件文件使用PascalCase命名
5. 工具函数使用camelCase命名

## API配置

API基础URL配置在 `src/api/client.ts`：
```typescript
baseURL: 'http://127.0.0.1:8000/api/v1'
```

## 状态管理

使用Pinia进行状态管理，stores位于 `src/stores/` 目录。

当前已实现的store：
- `auth.ts` - 用户认证状态

## 路由

路由配置在 `src/router/index.ts`。

当前路由：
- `/` - 首页
- `/login` - 登录页
- `/register` - 注册页

## 样式

使用Tailwind CSS进行样式开发。全局样式在 `src/style.css`。

## 环境变量

创建 `.env` 文件配置环境变量：
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```
