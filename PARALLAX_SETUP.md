# Parallax LLM部署指南

本指南介绍如何使用Parallax部署Qwen2-VL-7B-Instruct模型用于文本分类。

## 前置要求

1. **Docker Desktop** (已安装 ✓)
   - 版本: 28.0.4
   - 确保Docker Desktop正在运行

2. **NVIDIA GPU** (可选，推荐)
   - 支持的架构: Blackwell, Ampere, Hopper
   - 如果没有GPU，可以使用CPU模式（速度较慢）

3. **足够的磁盘空间**
   - 模型大小: ~8GB
   - Docker镜像: ~5GB

## 快速启动

### 方法1: 使用批处理脚本（推荐）

```bash
# 启动Parallax服务器
start_parallax.bat

# 停止Parallax服务器
stop_parallax.bat
```

### 方法2: 手动Docker命令

#### 启动服务器（GPU模式）

```bash
docker run -d \
  --name parallax-server \
  --gpus all \
  -p 8000:8000 \
  gradientservice/parallax:latest \
  bash -c "parallax serve --model Qwen/Qwen2-VL-7B-Instruct --host 0.0.0.0 --port 8000"
```

#### 启动服务器（CPU模式）

如果没有GPU或遇到GPU相关错误，使用CPU模式：

```bash
docker run -d \
  --name parallax-server \
  -p 8000:8000 \
  gradientservice/parallax:latest \
  bash -c "parallax serve --model Qwen/Qwen2-VL-7B-Instruct --host 0.0.0.0 --port 8000 --device cpu"
```

## 验证安装

### 1. 检查容器状态

```bash
docker ps | findstr parallax-server
```

应该看到容器正在运行。

### 2. 查看日志

```bash
docker logs parallax-server
```

等待看到类似以下的消息：
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. 测试API

使用curl或PowerShell测试API：

```powershell
# PowerShell
$body = @{
    model = "Qwen/Qwen2-VL-7B-Instruct"
    messages = @(
        @{
            role = "user"
            content = "你好"
        }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/v1/chat/completions" -Method Post -Body $body -ContentType "application/json"
```

## 配置后端服务

### 1. 更新环境变量

编辑 `backend/.env` 文件（如果不存在，从 `.env.example` 复制）：

```env
# LLM配置
LLM_API_URL=http://localhost:8000/v1/chat/completions
LLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
LLM_ENABLED=true
```

### 2. 重启后端服务

```bash
# 停止当前运行的后端
# 然后重新启动
start_backend.bat
```

## 使用其他模型

Parallax支持多种模型。要使用不同的模型，修改启动命令中的 `--model` 参数：

### 推荐的中文模型

```bash
# Qwen2-VL-7B-Instruct (默认，推荐)
--model Qwen/Qwen2-VL-7B-Instruct

# Qwen2-7B-Instruct (纯文本，更快)
--model Qwen/Qwen2-7B-Instruct

# Qwen2-1.5B-Instruct (更小，更快)
--model Qwen/Qwen2-1.5B-Instruct
```

## 故障排除

### 问题1: 容器无法启动

**症状**: `docker ps` 没有显示容器

**解决方案**:
```bash
# 查看容器日志
docker logs parallax-server

# 检查所有容器（包括已停止的）
docker ps -a

# 删除旧容器并重新启动
docker rm parallax-server
start_parallax.bat
```

### 问题2: GPU不可用

**症状**: 错误消息提到GPU或CUDA

**解决方案**:
1. 确保安装了NVIDIA驱动
2. 安装NVIDIA Container Toolkit
3. 或使用CPU模式（见上文）

### 问题3: 端口8000已被占用

**症状**: 错误消息 "port is already allocated"

**解决方案**:
```bash
# 方法1: 停止占用端口的服务
# 查找占用端口的进程
netstat -ano | findstr :8000

# 方法2: 使用不同的端口
docker run -d \
  --name parallax-server \
  -p 8001:8000 \
  ...

# 然后更新 .env 中的 LLM_API_URL
LLM_API_URL=http://localhost:8001/v1/chat/completions
```

### 问题4: 模型下载缓慢

**症状**: 首次启动时下载模型很慢

**解决方案**:
1. 使用国内镜像源（如果可用）
2. 或者预先下载模型并挂载到容器

### 问题5: 内存不足

**症状**: 容器被杀死或OOM错误

**解决方案**:
1. 使用更小的模型（如Qwen2-1.5B）
2. 增加Docker Desktop的内存限制
3. 使用量化模型

## 性能优化

### 1. 使用GPU加速

确保使用 `--gpus all` 参数启动容器。

### 2. 调整批处理大小

```bash
parallax serve --model Qwen/Qwen2-VL-7B-Instruct --batch-size 4
```

### 3. 使用量化模型

量化模型可以减少内存使用并提高速度：

```bash
--model Qwen/Qwen2-VL-7B-Instruct-GPTQ-Int4
```

## 监控和日志

### 实时查看日志

```bash
docker logs -f parallax-server
```

### 检查资源使用

```bash
docker stats parallax-server
```

## 停止和清理

### 停止服务器

```bash
docker stop parallax-server
```

### 删除容器

```bash
docker rm parallax-server
```

### 删除镜像（释放空间）

```bash
docker rmi gradientservice/parallax:latest
```

## API文档

Parallax提供OpenAI兼容的API。访问：

```
http://localhost:8000/docs
```

## 参考资源

- Parallax GitHub: https://github.com/GradientHQ/parallax
- Qwen模型: https://huggingface.co/Qwen
- Docker文档: https://docs.docker.com/

## 下一步

1. 启动Parallax服务器
2. 验证API可用
3. 配置后端环境变量
4. 重启后端服务
5. 测试文本分类功能

现在您的系统将使用真正的LLM进行智能文本分类！
