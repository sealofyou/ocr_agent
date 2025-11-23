# 快速启动指南

## 环境要求

- **后端**：Python 3.10+, Conda（推荐）
- **前端**：Node.js 18+

## 后端快速启动

### 1. 配置Conda环境

```bash
cd backend

# Windows用户
setup_conda_env.bat

# Linux/Mac用户
chmod +x setup_conda_env.sh
./setup_conda_env.sh
```

### 2. 激活环境

```bash
conda activate ocr_agent
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件（可选，使用默认配置即可开始）
# 重要配置项：
# - SECRET_KEY: JWT密钥（生产环境必须修改）
# - DATABASE_URL: 数据库连接（默认使用SQLite）
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动后端服务

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

访问：
- **API文档**：http://127.0.0.1:8000/docs
- **根路径**：http://127.0.0.1:8000/

## 前端快速启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

## 验证安装

### 后端验证

```bash
cd backend
conda activate ocr_agent

# 运行验证脚本
python verify_setup.py

# 运行测试
pytest

# 查看测试覆盖率
pytest --cov=app --cov-report=html
```

### 前端验证

```bash
cd frontend

# 构建项目
npm run build

# 预览构建结果
npm run preview
```

## 测试API

### 1. 用户注册

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### 2. 用户登录

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

### 3. 获取当前用户信息

```bash
# 使用登录返回的token
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 常见问题

### Q1: conda命令未找到

**A**: 确保已安装Anaconda或Miniconda，并重启终端。

### Q2: pip安装速度慢

**A**: 使用国内镜像源：
```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
```

### Q3: 端口被占用

**A**: 修改端口号：
```bash
# 后端
uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# 前端会自动选择可用端口
```

### Q4: 数据库初始化失败

**A**: 
1. 检查是否有写入权限
2. 删除旧的数据库文件：`rm text_archive.db`
3. 重新运行：`python init_db.py`

### Q5: 测试失败

**A**:
1. 确保conda环境已激活
2. 检查所有依赖是否安装：`pip list`
3. 查看详细错误：`pytest -v`

## 开发工作流

### 1. 每次开始工作

```bash
# 激活conda环境
conda activate ocr_agent

# 启动后端
cd backend
uvicorn main:app --reload

# 新终端启动前端
cd frontend
npm run dev
```

### 2. 提交代码前

```bash
# 运行测试
cd backend
pytest

# 检查代码质量
python verify_setup.py
```

### 3. 更新依赖

```bash
# 后端
cd backend
pip install -i https://pypi.mirrors.ustc.edu.cn/simple --upgrade -r requirements.txt

# 前端
cd frontend
npm update
```

## 项目结构

```
ocr_agent/
├── backend/              # 后端FastAPI项目
│   ├── app/             # 应用代码
│   ├── tests/           # 测试代码
│   ├── main.py          # 应用入口
│   └── requirements.txt # Python依赖
├── frontend/            # 前端Vue项目
│   ├── src/            # 源代码
│   └── package.json    # Node依赖
└── README.md           # 项目说明
```

## 下一步

- 查看 [README.md](./README.md) 了解项目详情
- 查看 [backend/CONDA_SETUP.md](./backend/CONDA_SETUP.md) 了解环境配置
- 查看 [backend/TESTING.md](./backend/TESTING.md) 了解测试
- 查看 [.kiro/specs/text-archive-assistant/](./kiro/specs/text-archive-assistant/) 了解需求和设计

## 获取帮助

- 查看API文档：http://127.0.0.1:8000/docs
- 查看测试指南：[backend/tests/README.md](./backend/tests/README.md)
- 查看任务列表：[.kiro/specs/text-archive-assistant/tasks.md](./.kiro/specs/text-archive-assistant/tasks.md)

---

**祝开发愉快！** 🚀
