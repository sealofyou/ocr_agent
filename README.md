# 手写管理助手 (Text Archive Assistant)

一个智能的文本归档应用，使用OCR技术识别手写或图片文本，并通过AI模型自动分类和整理日程信息与备忘录。

## ✨ 项目概述

手写管理助手帮助用户智能整理和归档文本内容，核心功能包括：

- 📅 **日程管理** - 自动识别时间信息，智能创建日程安排
- 📝 **备忘录管理** - 标签分类，快速检索个人笔记
- 🔍 **OCR识别** - PaddleOCR引擎，高精度文字识别
- 🤖 **AI智能分类** - LLM + 规则双引擎，自动区分日程与备忘录
- 🔐 **用户认证** - JWT Token安全认证
- 🎨 **响应式设计** - 支持Web和移动端访问

## 🛠️ 技术栈

### 前端技术
- **框架**: Vue 3 (Composition API) + TypeScript
- **样式**: Tailwind CSS
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 后端技术
- **框架**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy
- **数据库**: SQLite (开发) / MySQL (生产)
- **OCR引擎**: PaddleOCR
- **AI分类**: LLM (Qwen2-VL) + 规则引擎
- **认证**: JWT Token
- **测试**: Pytest + Hypothesis (属性测试)

## 📁 项目结构

```
ocr_agent/
├── frontend/                    # 前端Vue项目
│   ├── src/
│   │   ├── api/                # API客户端
│   │   ├── components/         # 可复用组件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia状态管理
│   │   └── views/              # 页面组件
│   └── package.json
│
├── backend/                     # 后端FastAPI项目
│   ├── app/
│   │   ├── api/                # API路由层
│   │   │   ├── auth.py         # 认证API
│   │   │   ├── upload.py       # 文件上传API
│   │   │   ├── ocr.py          # OCR识别API
│   │   │   ├── classification.py # 分类API
│   │   │   ├── schedule.py     # 日程管理API
│   │   │   └── memo.py         # 备忘录管理API
│   │   ├── core/               # 核心配置
│   │   ├── db/                 # 数据库配置
│   │   ├── models/             # 数据模型
│   │   │   ├── user.py         # 用户模型
│   │   │   ├── upload.py       # 上传文件模型
│   │   │   ├── schedule.py     # 日程模型
│   │   │   └── memo.py         # 备忘录模型
│   │   ├── schemas/            # Pydantic模式
│   │   ├── services/           # 业务服务层
│   │   │   ├── ocr_service.py  # OCR服务
│   │   │   └── classification_service.py # 分类服务
│   │   ├── dependencies/       # 依赖注入
│   │   └── utils/              # 工具函数
│   ├── tests/                  # 测试代码
│   ├── uploads/                # 上传文件存储
│   ├── logs/                   # 日志文件
│   ├── main.py                 # 应用入口
│   └── requirements.txt        # Python依赖
│
├── .kiro/specs/                # 项目规范文档
│   └── text-archive-assistant/
│       ├── requirements.md     # 需求文档
│       ├── design.md           # 设计文档
│       └── tasks.md            # 任务列表
│
└── 项目流程图.md                # 项目流程图文档
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

## 🎯 功能特性

### 已实现功能

#### 🔐 用户认证系统
- ✅ 用户注册与登录
- ✅ JWT Token认证
- ✅ 密码加密存储
- ✅ 用户信息管理

#### 📤 文件上传
- ✅ 图片上传功能
- ✅ 文件格式验证
- ✅ 文件大小限制
- ✅ 上传记录管理

#### 🔍 OCR识别
- ✅ PaddleOCR文字识别
- ✅ 图片验证
- ✅ 识别结果预览
- ✅ 手动编辑功能

#### 🤖 AI智能分类
- ✅ LLM智能分类 (Qwen2-VL)
- ✅ 规则引擎后备方案
- ✅ 置信度评估
- ✅ 手动分类选择
- ✅ 时间信息提取
- ✅ 标签自动生成

#### 📅 日程管理
- ✅ 创建日程
- ✅ 查询日程列表
- ✅ 日期范围筛选
- ✅ 时间排序
- ✅ 更新日程
- ✅ 删除日程

#### 📝 备忘录管理
- ✅ 创建备忘录
- ✅ 查询备忘录列表
- ✅ 标签筛选
- ✅ 自动摘要生成
- ✅ 更新备忘录
- ✅ 删除备忘录

#### 🧪 测试覆盖
- ✅ 单元测试 (Pytest)
- ✅ 属性测试 (Hypothesis)
- ✅ API集成测试
- ✅ 分类服务测试

### 待实现功能
- ⏳ 全文搜索功能
- ⏳ 前端UI完善
- ⏳ 数据导出功能
- ⏳ 移动端优化

## 开发规范

详见各子项目的README：
- [前端开发规范](./frontend/README.md)
- [后端开发规范](./backend/README.md)

## 🔌 API端点

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 文件上传
- `POST /api/v1/upload` - 上传图片文件

### OCR识别
- `POST /api/v1/ocr/recognize` - 识别图片文字
- `POST /api/v1/ocr/edit` - 编辑识别结果

### AI分类
- `POST /api/v1/classify` - 自动分类文本
- `POST /api/v1/classify/manual` - 手动选择分类

### 日程管理
- `GET /api/v1/schedules` - 获取日程列表（支持日期筛选）
- `POST /api/v1/schedules` - 创建日程
- `GET /api/v1/schedules/{id}` - 获取日程详情
- `PUT /api/v1/schedules/{id}` - 更新日程
- `DELETE /api/v1/schedules/{id}` - 删除日程

### 备忘录管理
- `GET /api/v1/memos` - 获取备忘录列表（支持标签筛选）
- `POST /api/v1/memos` - 创建备忘录
- `GET /api/v1/memos/{id}` - 获取备忘录详情
- `PUT /api/v1/memos/{id}` - 更新备忘录
- `DELETE /api/v1/memos/{id}` - 删除备忘录

详细API文档：http://127.0.0.1:8000/docs

## 🧪 测试

### 运行所有测试
```bash
cd backend
pytest
```

### 运行特定类型测试
```bash
# 单元测试
pytest -m unit

# 属性测试
pytest -m property

# 集成测试
pytest -m integration
```

### 查看测试覆盖率
```bash
pytest --cov=app --cov-report=html
```

### 运行分类服务测试
```bash
# 测试LLM分类
python test_llm_classification.py

# 测试分类属性
pytest backend/tests/test_classification_properties.py -v
```

## 📊 项目流程

查看完整的项目流程图：[项目流程图.md](./项目流程图.md)

主要流程包括：
1. **用户认证流程** - 注册/登录 → JWT Token → 访问控制
2. **OCR识别流程** - 上传图片 → 文字识别 → 结果编辑
3. **AI分类流程** - LLM分类 → 置信度判断 → 自动/手动分类
4. **数据管理流程** - 创建 → 查询 → 更新 → 删除

## 📚 文档

- [项目流程图](./项目流程图.md) - 完整的业务流程和系统架构图
- [需求文档](./.kiro/specs/text-archive-assistant/requirements.md) - 功能需求和验收标准
- [设计文档](./.kiro/specs/text-archive-assistant/design.md) - 系统设计和技术方案
- [任务列表](./.kiro/specs/text-archive-assistant/tasks.md) - 开发任务和进度
- [快速开始](./QUICK_START.md) - 快速启动指南
- [后端文档](./backend/README.md) - 后端开发规范
- [前端文档](./frontend/README.md) - 前端开发规范
- [测试指南](./backend/TESTING.md) - 测试说明

## 🔧 配置说明

### 环境变量配置

后端 `.env` 文件配置项：

```env
# 应用配置
PROJECT_NAME=文本归档助手
HOST=127.0.0.1
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./text_archive.db

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM配置
LLM_API_URL=http://localhost:8000/v1/chat/completions
LLM_MODEL=Qwen/Qwen2-VL-7B-Instruct

# 文件上传配置
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp
```

### LLM服务配置

项目支持两种分类模式：
1. **LLM模式**（推荐）- 使用大语言模型进行智能分类
2. **规则模式**（后备）- 基于关键词和模式匹配

启动LLM服务（可选）：
```bash
# 使用Qwen模型
start_qwen_llm.bat

# 或使用Ollama
start_ollama_llm.bat
```

## 🚀 部署

### 开发环境
```bash
# 后端
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 前端
cd frontend
npm run dev
```

### 生产环境
```bash
# 后端
cd backend
python main.py

# 前端
cd frontend
npm run build
npm run preview
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献指南
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

## 👥 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 Issue
- 发送 Pull Request

---

**祝使用愉快！** 🎉
