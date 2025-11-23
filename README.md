# 文本归档助手 (Text Archive Assistant)

一个跨端的文本归档应用，使用OCR技术识别文本内容，并通过AI模型自动分类和整理日程信息和日记/备忘录。

## 项目概述

文本归档助手帮助用户整理和归档文本内容，包括：
- 📅 日程安排管理
- 📝 日记和备忘录管理
- 🔍 智能文本识别（OCR）
- 🤖 AI自动分类
- 🔄 跨端数据同步
- 🔎 全文搜索

## 技术栈

### 前端
- Vue 3 + TypeScript
- Tailwind CSS
- Vue Router + Pinia
- Axios
- Vite

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy + SQLite/MySQL
- PaddleOCR
- JWT认证

## 项目结构

```
ocr_agent/
├── frontend/              # 前端Vue项目
│   ├── src/
│   │   ├── api/          # API客户端
│   │   ├── components/   # 组件
│   │   ├── router/       # 路由
│   │   ├── stores/       # 状态管理
│   │   └── views/        # 页面
│   └── package.json
├── backend/              # 后端FastAPI项目
│   ├── app/
│   │   ├── core/        # 核心配置
│   │   ├── db/          # 数据库
│   │   ├── models/      # 数据模型
│   │   ├── modules/     # 功能模块
│   │   └── utils/       # 工具函数
│   ├── main.py          # 应用入口
│   └── pyproject.toml
└── .kiro/
    └── specs/           # 项目规范文档
        └── text-archive-assistant/
            ├── requirements.md  # 需求文档
            ├── design.md        # 设计文档
            └── tasks.md         # 任务列表
```

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.10+
- uv (Python包管理器，推荐) 或 pip

### 1. 启动后端

#### 使用Conda（推荐）

```bash
cd backend

# 自动配置conda环境（Windows）
setup_conda_env.bat

# 或手动配置
conda create -n ocr_agent python=3.10 -y
conda activate ocr_agent
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置

# 初始化数据库
python init_db.py

# 启动服务
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

详细的conda配置说明请查看：[backend/CONDA_SETUP.md](./backend/CONDA_SETUP.md)

#### 使用其他包管理器

```bash
cd backend

# 使用uv
uv sync

# 或使用pip
pip install -r requirements.txt

# 后续步骤相同...
```

后端服务将运行在 http://127.0.0.1:8000

API文档: http://127.0.0.1:8000/docs

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将运行在 http://localhost:5173

## 开发进度

当前已完成：
- ✅ 项目基础架构搭建
- ✅ 前端Vue项目初始化
- ✅ 后端FastAPI项目初始化
- ✅ 数据库模型设计
- ✅ Tailwind CSS配置
- ✅ 路由和状态管理配置

待实现功能（按任务列表顺序）：
- ⏳ 用户认证系统
- ⏳ 文件上传和输入功能
- ⏳ OCR引擎集成
- ⏳ AI分类服务
- ⏳ 日程管理
- ⏳ 备忘录管理
- ⏳ 搜索功能
- ⏳ 模型注册中心

## 开发规范

详见各子项目的README：
- [前端开发规范](./frontend/README.md)
- [后端开发规范](./backend/README.md)

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm run test
```

## 文档

- [需求文档](./.kiro/specs/text-archive-assistant/requirements.md)
- [设计文档](./.kiro/specs/text-archive-assistant/design.md)
- [任务列表](./.kiro/specs/text-archive-assistant/tasks.md)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
