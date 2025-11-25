# 🚀 LLM快速开始指南

## ⚠️ 重要提示

**Parallax不支持Windows直接安装**（依赖uvloop库）

**解决方案：使用Docker运行Parallax（推荐）**

---

## 📋 前置要求

- ✅ Docker Desktop已安装并运行
- ✅ 至少8GB可用磁盘空间
- ✅ （可选）NVIDIA GPU用于加速

---

## 🎯 三步启动

### 步骤1：启动LLM服务

```bash
start_qwen_llm.bat
```

**首次运行会下载8GB模型，请耐心等待！**

### 步骤2：验证服务

```bash
# 检查容器状态
docker ps | findstr parallax

# 查看日志（等待看到 "Application startup complete"）
docker logs -f parallax-server
```

### 步骤3：测试分类

```bash
cd backend
conda activate ocr_agent
python test_llm_classification.py
```

---

## ✅ 完整流程

```bash
# 1. 检查环境
check_llm_setup.bat

# 2. 启动LLM
start_qwen_llm.bat

# 3. 配置后端（如果还没有.env文件）
copy backend\.env.example backend\.env

# 4. 启动后端
start_backend.bat

# 5. 启动前端
start_frontend.bat

# 6. 访问应用
# http://localhost:5173
```

---

## 🔧 配置说明

确保 `backend/.env` 包含：

```env
LLM_API_URL=http://localhost:8000/v1/chat/completions
LLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
LLM_ENABLED=true
```

---

## 🐛 常见问题

### Q: Docker容器无法启动？

```bash
# 查看错误日志
docker logs parallax-server

# 重新启动
docker stop parallax-server
docker rm parallax-server
start_qwen_llm.bat
```

### Q: 没有GPU怎么办？

脚本会自动尝试GPU，失败后使用CPU模式（速度较慢但可用）

### Q: 端口8000被占用？

编辑 `start_qwen_llm.bat`，将 `-p 8000:8000` 改为 `-p 8001:8000`

然后更新 `backend/.env`：
```env
LLM_API_URL=http://localhost:8001/v1/chat/completions
```

### Q: 模型下载很慢？

首次启动需要下载8GB模型，请确保网络稳定。可以使用更小的模型：

编辑 `start_qwen_llm.bat`，将模型改为：
```bash
--model Qwen/Qwen2-1.5B-Instruct
```

---

## 📊 性能说明

| 配置 | 响应时间 | 准确率 |
|------|----------|--------|
| GPU模式 | 1-2秒 | 90%+ |
| CPU模式 | 5-10秒 | 90%+ |
| 规则模式（后备） | <100ms | 70% |

---

## 🛑 停止服务

```bash
# 停止LLM服务
stop_parallax.bat

# 或手动停止
docker stop parallax-server
docker rm parallax-server
```

---

## 📚 详细文档

- **WINDOWS_LLM_SETUP.md** - Windows系统完整指南
- **PARALLAX_SETUP.md** - Parallax详细配置
- **LLM_INTEGRATION_README.md** - 架构和集成说明
- **LLM_SETUP_SUMMARY.md** - 完整总结

---

## 🎉 就这么简单！

现在运行 `start_qwen_llm.bat` 开始使用LLM智能分类吧！
