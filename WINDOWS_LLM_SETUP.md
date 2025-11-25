# Windows系统LLM部署指南

## 问题说明

Parallax依赖的uvloop库**不支持Windows系统**，因此无法直接在Windows上安装Parallax。

错误信息：
```
RuntimeError: uvloop does not support Windows at the moment
```

## 解决方案

Windows用户有两个选择：

---

## 方案1：使用Docker运行Parallax（推荐）✅

### 优点
- ✅ 完整的Parallax功能
- ✅ 支持多种模型
- ✅ 性能最佳
- ✅ 与Linux环境一致

### 步骤

1. **确保Docker Desktop已安装并运行**
   ```bash
   docker --version
   ```

2. **运行启动脚本**
   ```bash
   start_qwen_llm.bat
   ```

3. **等待模型下载**（首次运行需要下载8GB模型）

4. **验证服务**
   ```bash
   docker ps | findstr parallax
   docker logs parallax-server
   ```

5. **测试API**
   ```powershell
   curl http://localhost:8000/v1/models
   ```

### 配置后端

在 `backend/.env` 中：
```env
LLM_API_URL=http://localhost:8000/v1/chat/completions
LLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
LLM_ENABLED=true
```

---

## 方案2：使用Ollama（Windows原生）

### 优点
- ✅ Windows原生支持
- ✅ 安装简单
- ✅ 自动管理模型
- ✅ 轻量级

### 缺点
- ⚠️ API格式不同（需要适配代码）
- ⚠️ 模型选择较少

### 步骤

#### 1. 安装Ollama

访问 https://ollama.com/download/windows 下载并安装

或运行：
```bash
setup_ollama.bat
```

#### 2. 下载模型

```bash
# 下载Qwen2 7B模型
ollama pull qwen2:7b

# 或下载更小的模型
ollama pull qwen2:1.5b
```

#### 3. 启动服务

```bash
start_ollama_llm.bat
```

Ollama会自动在后台运行，监听端口11434。

#### 4. 测试API

```bash
curl http://localhost:11434/api/generate -d "{\"model\":\"qwen2:7b\",\"prompt\":\"你好\"}"
```

#### 5. 更新后端代码

需要修改 `backend/app/services/classification_service.py` 以支持Ollama API格式。

在 `backend/.env` 中：
```env
LLM_API_URL=http://localhost:11434/api/chat
LLM_MODEL=qwen2:7b
LLM_ENABLED=true
LLM_PROVIDER=ollama
```

---

## 推荐方案对比

| 特性 | Docker + Parallax | Ollama |
|------|-------------------|--------|
| Windows支持 | ✅ (通过Docker) | ✅ (原生) |
| 安装难度 | 中 | 简单 |
| 性能 | 最佳 | 良好 |
| 模型选择 | 丰富 | 中等 |
| GPU支持 | ✅ | ✅ |
| 内存占用 | 高 | 中 |
| 推荐场景 | 生产环境 | 开发测试 |

---

## 推荐：使用Docker方案

对于本项目，**强烈推荐使用Docker方案**，原因：

1. ✅ 已经创建好所有脚本（`start_qwen_llm.bat`）
2. ✅ 代码已经适配Parallax API
3. ✅ 性能更好
4. ✅ 与生产环境一致

### 快速开始（Docker方案）

```bash
# 1. 启动LLM服务
start_qwen_llm.bat

# 2. 等待服务就绪（查看日志）
docker logs -f parallax-server

# 3. 测试分类
cd backend
conda activate ocr_agent
python test_llm_classification.py

# 4. 启动后端
start_backend.bat
```

---

## 常见问题

### Q: Docker Desktop需要WSL2吗？
A: 是的，Docker Desktop for Windows需要WSL2。如果未安装，Docker会提示安装。

### Q: 没有GPU可以运行吗？
A: 可以，但速度会慢很多。Docker方案会自动尝试GPU，失败后降级到CPU。

### Q: 模型下载很慢怎么办？
A: 
- 使用国内镜像源
- 或预先下载模型文件
- 或使用更小的模型

### Q: 可以同时使用Docker和Ollama吗？
A: 可以，但需要使用不同的端口。

### Q: 如何切换模型？
A: 修改启动脚本中的 `--model` 参数，或在Ollama中使用 `ollama pull` 下载其他模型。

---

## 故障排除

### Docker方案

**问题：容器无法启动**
```bash
# 查看详细日志
docker logs parallax-server

# 检查Docker是否运行
docker ps

# 重新启动
docker stop parallax-server
docker rm parallax-server
start_qwen_llm.bat
```

**问题：GPU不可用**
```bash
# 使用CPU模式
# 编辑 start_qwen_llm.bat，添加 --device cpu 参数
```

### Ollama方案

**问题：Ollama命令未找到**
```bash
# 重新安装Ollama
# 或将Ollama添加到PATH环境变量
```

**问题：模型下载失败**
```bash
# 重试下载
ollama pull qwen2:7b

# 或使用更小的模型
ollama pull qwen2:1.5b
```

---

## 下一步

1. ✅ 选择方案（推荐Docker）
2. ✅ 运行启动脚本
3. ✅ 验证服务运行
4. ✅ 测试分类功能
5. ✅ 启动完整应用

---

## 参考资源

- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- [Ollama官网](https://ollama.com/)
- [Parallax GitHub](https://github.com/GradientHQ/parallax)
- [WSL2安装指南](https://docs.microsoft.com/en-us/windows/wsl/install)

---

**建议：立即运行 `start_qwen_llm.bat` 使用Docker方案！**
