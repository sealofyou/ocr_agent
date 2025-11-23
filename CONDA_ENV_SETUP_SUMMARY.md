# Conda环境配置总结

## ✅ 已创建的文件

### 1. 环境配置文件

#### `backend/environment.yml`
- Conda环境配置文件
- 环境名称：`ocr_agent`
- Python版本：3.10
- 包含所有项目依赖
- 配置使用中科大镜像源

#### `backend/requirements.txt`
- pip依赖列表
- 包含所有Python包及版本号
- 可用于pip安装

### 2. 自动配置脚本

#### `backend/setup_conda_env.bat` (Windows)
自动化配置脚本，执行以下步骤：
1. 检查conda是否安装
2. 创建conda环境（ocr_agent, Python 3.10）
3. 激活环境
4. 安装依赖（使用中科大镜像源）
5. 验证安装

#### `backend/setup_conda_env.sh` (Linux/Mac)
Linux/Mac版本的自动化配置脚本
- 功能与Windows版本相同
- 需要添加执行权限：`chmod +x setup_conda_env.sh`

### 3. 文档

#### `backend/CONDA_SETUP.md`
详细的Conda环境配置指南，包含：
- 快速开始指南
- 手动配置步骤
- 依赖包列表和说明
- 常用命令
- 镜像源配置
- 项目初始化步骤
- 故障排除
- 开发建议

#### `QUICK_START.md`
项目快速启动指南，包含：
- 环境要求
- 后端快速启动步骤
- 前端快速启动步骤
- 验证安装方法
- API测试示例
- 常见问题解答
- 开发工作流

### 4. 更新的文档

#### `README.md`
- 添加了Conda环境配置说明
- 更新了后端启动步骤
- 添加了CONDA_SETUP.md的链接

#### `backend/README.md`
- 添加了Conda安装方式（推荐）
- 保留了其他安装方式
- 添加了详细文档链接

## 📦 依赖包列表

### 核心框架
- **fastapi** 0.103.1 - Web框架
- **uvicorn[standard]** 0.23.2 - ASGI服务器
- **pydantic-settings** 2.0.3 - 配置管理
- **python-dotenv** 1.0.0 - 环境变量

### 数据库
- **sqlalchemy** 2.0.21 - ORM
- **alembic** 1.12.0 - 数据库迁移
- **redis** 4.6.0 - 缓存（可选）

### 认证
- **passlib[bcrypt]** 1.7.4 - 密码加密
- **python-jose[cryptography]** 3.3.0 - JWT令牌

### OCR和AI
- **paddleocr** 2.7.0 - OCR引擎
- **paddlepaddle** 2.5.2 - PaddlePaddle框架

### 测试
- **pytest** 7.4.3 - 测试框架
- **pytest-asyncio** 0.21.1 - 异步测试
- **hypothesis** 6.92.1 - 属性测试
- **httpx** 0.25.1 - HTTP客户端
- **pytest-cov** 4.1.0 - 测试覆盖率

### 其他
- **python-multipart** 0.0.6 - 文件上传

## 🚀 使用方法

### 方法1：自动配置（推荐）

**Windows**:
```bash
cd backend
setup_conda_env.bat
```

**Linux/Mac**:
```bash
cd backend
chmod +x setup_conda_env.sh
./setup_conda_env.sh
```

### 方法2：使用environment.yml

```bash
cd backend
conda env create -f environment.yml
conda activate ocr_agent
```

### 方法3：手动配置

```bash
# 创建环境
conda create -n ocr_agent python=3.10 -y

# 激活环境
conda activate ocr_agent

# 安装依赖
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
```

## 🔧 配置说明

### 环境名称
- **名称**: `ocr_agent`
- **Python版本**: 3.10
- **原因**: 与PaddlePaddle兼容性最佳

### 镜像源
- **使用**: 中科大镜像源
- **URL**: https://pypi.mirrors.ustc.edu.cn/simple
- **原因**: 国内访问速度快，稳定可靠

### 其他可用镜像源
- 清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple
- 豆瓣：https://pypi.douban.com/simple

## 📝 初始化步骤

环境配置完成后：

### 1. 激活环境
```bash
conda activate ocr_agent
```

### 2. 配置环境变量
```bash
cd backend
cp .env.example .env
# 编辑.env文件（可选）
```

### 3. 初始化数据库
```bash
python init_db.py
```

### 4. 验证安装
```bash
python verify_setup.py
```

### 5. 运行测试
```bash
pytest
```

### 6. 启动服务
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## 🎯 验证清单

- [ ] Conda已安装
- [ ] 环境创建成功（ocr_agent）
- [ ] 环境可以激活
- [ ] 所有依赖安装成功
- [ ] verify_setup.py运行通过
- [ ] 数据库初始化成功
- [ ] 测试运行通过
- [ ] 服务可以启动
- [ ] API文档可以访问（http://127.0.0.1:8000/docs）

## 🐛 常见问题

### 1. conda命令未找到
**解决**: 安装Anaconda/Miniconda，重启终端

### 2. pip安装速度慢
**解决**: 使用镜像源
```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
```

### 3. PaddlePaddle安装失败
**解决**: 
- 确保Python版本为3.10
- 单独安装：`pip install paddlepaddle==2.5.2`

### 4. bcrypt安装失败（Windows）
**解决**: 安装Visual C++ Build Tools

### 5. 环境激活失败
**解决**: 
```bash
conda init
# 重启终端
conda activate ocr_agent
```

## 📚 相关文档

- [CONDA_SETUP.md](./backend/CONDA_SETUP.md) - 详细配置指南
- [QUICK_START.md](./QUICK_START.md) - 快速启动指南
- [README.md](./README.md) - 项目说明
- [backend/README.md](./backend/README.md) - 后端说明
- [backend/TESTING.md](./backend/TESTING.md) - 测试指南

## 🎉 完成状态

✅ **Conda环境配置已完成！**

现在可以：
1. 使用自动脚本快速配置环境
2. 使用中科大镜像源加速安装
3. 按照文档进行手动配置
4. 查看详细的故障排除指南

---

**下一步**: 运行 `setup_conda_env.bat` (Windows) 或 `./setup_conda_env.sh` (Linux/Mac) 开始配置！
