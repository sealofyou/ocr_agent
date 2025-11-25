# Conda环境配置指南

本项目使用conda管理Python环境，环境名称为 `ocr_agent`。

## 前置要求

- Anaconda 或 Miniconda
- Python 3.10

## 快速开始

### Windows

```bash
# 运行自动配置脚本
setup_conda_env.bat
```

### Linux/Mac

```bash
# 添加执行权限
chmod +x setup_conda_env.sh

# 运行自动配置脚本
./setup_conda_env.sh
```

## 手动配置

### 1. 创建conda环境

```bash
conda create -n ocr_agent python=3.10 -y
```

### 2. 激活环境

```bash
conda activate ocr_agent
```

### 3. 安装依赖

使用中科大镜像源安装：

```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
```

或使用environment.yml：

```bash
conda env create -f environment.yml
```

### 4. 验证安装

```bash
python verify_setup.py
```

## 依赖包列表

### 核心框架
- fastapi==0.103.1 - Web框架
- uvicorn[standard]==0.23.2 - ASGI服务器
- pydantic-settings==2.0.3 - 配置管理
- python-dotenv==1.0.0 - 环境变量管理

### 数据库
- sqlalchemy==2.0.21 - ORM
- alembic==1.12.0 - 数据库迁移
- redis==4.6.0 - 缓存（可选）

### 认证
- passlib[bcrypt]==1.7.4 - 密码加密
- python-jose[cryptography]==3.3.0 - JWT令牌

### OCR和AI
- paddleocr==2.7.0 - OCR引擎
- paddlepaddle==2.5.2 - PaddlePaddle框架

### 测试
- pytest==7.4.3 - 测试框架
- pytest-asyncio==0.21.1 - 异步测试支持
- hypothesis==6.92.1 - 属性测试
- httpx==0.25.1 - HTTP客户端
- pytest-cov==4.1.0 - 测试覆盖率

### 其他
- python-multipart==0.0.6 - 文件上传支持

## 常用命令

### 激活环境
```bash
conda activate ocr_agent
```

### 停用环境
```bash
conda deactivate
```

### 查看已安装的包
```bash
conda list
```

### 更新依赖
```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple --upgrade -r requirements.txt
```

### 删除环境
```bash
conda env remove -n ocr_agent
```

## 镜像源配置

### 使用中科大镜像源（推荐）

临时使用：
```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple package_name
```

永久配置：
```bash
pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
```

### 其他国内镜像源

- 清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple
- 豆瓣：https://pypi.douban.com/simple

## 初始化项目

环境配置完成后，按以下步骤初始化项目：

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，设置必要的配置
```

### 2. 初始化数据库

```bash
python init_db.py
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m unit

# 运行属性测试
pytest -m property

# 查看测试覆盖率
pytest --cov=app --cov-report=html
```

### 4. 启动开发服务器

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

访问：
- API文档：http://127.0.0.1:8000/docs
- 根路径：http://127.0.0.1:8000/

## 故障排除

### 问题1：conda命令未找到

**解决方案**：
1. 确保已安装Anaconda或Miniconda
2. 重启终端或命令提示符
3. 检查环境变量PATH中是否包含conda路径

### 问题2：pip安装速度慢

**解决方案**：
使用国内镜像源：
```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
```

### 问题3：PaddlePaddle安装失败

**解决方案**：
1. 确保Python版本为3.10
2. 尝试单独安装：
```bash
pip install -i https://pypi.mirrors.ustc.edu.cn/simple paddlepaddle==2.5.2
```

### 问题4：bcrypt安装失败（Windows）

**解决方案**：
1. 安装Visual C++ Build Tools
2. 或使用预编译的wheel文件

### 问题5：环境激活失败

**解决方案**：
```bash
# 初始化conda
conda init

# 重启终端后再次尝试
conda activate ocr_agent
```

## 开发建议

1. **始终在激活的conda环境中工作**
   ```bash
   conda activate ocr_agent
   ```

2. **定期更新依赖**
   ```bash
   pip list --outdated
   ```

3. **使用虚拟环境隔离项目**
   - 避免全局安装包
   - 每个项目使用独立的conda环境

4. **提交前运行测试**
   ```bash
   pytest
   ```

## 参考资源

- [Conda文档](https://docs.conda.io/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [PaddleOCR文档](https://github.com/PaddlePaddle/PaddleOCR)
- [pytest文档](https://docs.pytest.org/)

## 联系支持

如果遇到问题，请：
1. 查看本文档的故障排除部分
2. 运行 `python verify_setup.py` 检查配置
3. 查看项目README.md
