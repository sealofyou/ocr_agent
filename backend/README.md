# 手写管理助手 - 后端

基于FastAPI开发的手写管理助手后端服务。

## 功能特性

- 用户认证和授权（JWT）
- OCR文字识别（PaddleOCR）
- AI智能分类（日程/备忘录）
- 日程管理
- 备忘录管理
- 全文搜索
- 跨端数据同步

## 技术栈

- FastAPI
- SQLAlchemy (ORM)
- SQLite (开发环境) / MySQL (生产环境可选)
- PaddleOCR
- JWT认证
- Python 3.10+

## 项目结构

```
backend/
├── app/                       # 主应用目录
│   ├── core/                  # 核心配置
│   │   ├── config.py          # 项目配置
│   │   ├── cors.py            # CORS配置
│   │   └── __init__.py
│   ├── db/                    # 数据库相关
│   │   ├── base.py            # 数据库基础配置
│   │   └── __init__.py
│   ├── models/                # 数据模型
│   │   ├── user.py            # 用户模型
│   │   ├── schedule.py        # 日程模型
│   │   ├── memo.py            # 备忘录模型
│   │   └── __init__.py
│   ├── modules/               # 功能模块
│   │   └── __init__.py
│   ├── utils/                 # 工具函数
│   │   ├── logger.py
│   │   └── __init__.py
│   └── __init__.py
├── logs/                      # 日志文件目录
├── uploads/                   # 上传文件目录
├── main.py                    # 应用入口
├── init_db.py                 # 数据库初始化脚本
├── pyproject.toml             # 项目配置和依赖
├── .env.example               # 环境变量示例
└── README.md                  # 项目说明
```

## 快速开始

### 1. 安装依赖

#### 使用Conda（推荐）

**自动配置**：
```bash
# Windows
setup_conda_env.bat

# Linux/Mac
chmod +x setup_conda_env.sh
./setup_conda_env.sh
```

**手动配置**：
```bash
# 创建conda环境
conda create -n ocr_agent python=3.10 -y

# 激活环境
conda activate ocr_agent

# 安装依赖（使用中科大镜像源）
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
```

详细说明请查看：[CONDA_SETUP.md](./CONDA_SETUP.md)

#### 使用其他包管理器

使用uv：
```bash
uv sync
```

使用pip：
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：
```bash
cp .env.example .env
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 运行服务

开发模式（支持热重载）：
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

生产模式：
```bash
python main.py
```

### 5. 访问API文档

启动服务后，访问：
- Swagger UI: http://127.0.0.1:8000/docs
- 根路径: http://127.0.0.1:8000/

## 开发规范

1. 新功能模块放在 `app/modules/` 目录下
2. 数据模型放在 `app/models/` 目录下
3. API接口需要详细注释，包括：
   - 装饰器中的 `summary`、`tags`、`response_model`
   - 函数文档字符串
4. 使用logger记录日志：
```python
from app.utils.logger import logging
logging.info("日志信息")
```

## 数据库

默认使用SQLite，数据库文件：`text_archive.db`

如需切换到MySQL，修改 `.env` 中的 `DATABASE_URL`：
```
DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
```

## API端点

### 认证
- POST `/api/v1/auth/register` - 用户注册
- POST `/api/v1/auth/login` - 用户登录
- POST `/api/v1/auth/logout` - 用户登出

### OCR
- POST `/api/v1/ocr/recognize` - 图片文字识别

### 分类
- POST `/api/v1/classify` - 文本分类

### 日程
- GET `/api/v1/schedules` - 获取日程列表
- POST `/api/v1/schedules` - 创建日程
- PUT `/api/v1/schedules/{id}` - 更新日程
- DELETE `/api/v1/schedules/{id}` - 删除日程

### 备忘录
- GET `/api/v1/memos` - 获取备忘录列表
- POST `/api/v1/memos` - 创建备忘录
- PUT `/api/v1/memos/{id}` - 更新备忘录
- DELETE `/api/v1/memos/{id}` - 删除备忘录

### 搜索
- GET `/api/v1/search` - 全文搜索

## 测试

### 测试框架

- pytest: 单元测试和集成测试
- hypothesis: 属性测试（Property-Based Testing）
- httpx: API测试客户端

### 运行测试

运行所有测试：
```bash
pytest
# 或
python run_tests.py
```

运行特定类型的测试：
```bash
# 单元测试
pytest -m unit
python run_tests.py unit

# 属性测试
pytest -m property
python run_tests.py property

# 集成测试
pytest -m integration
python run_tests.py integration
```

查看测试覆盖率：
```bash
pytest --cov=app --cov-report=html
```

详细测试指南请查看: [tests/README.md](./tests/README.md)
