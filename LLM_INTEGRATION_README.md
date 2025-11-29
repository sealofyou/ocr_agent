# LLM集成说明

本文档说明如何将LLM（Qwen2-VL-7B-Instruct）集成到手写管理助手的分类服务中。

## 概述

系统现在支持两种分类模式：

1. **LLM模式**（推荐）：使用Qwen2-VL-7B大语言模型进行智能分类
2. **规则模式**（后备）：基于关键词和模式匹配的规则分类

系统会优先尝试使用LLM，如果LLM不可用或失败，会自动降级到规则模式。

## 快速开始

### 1. 启动LLM服务

```bash
# 运行启动脚本
start_qwen_llm.bat
```

这将：
- 拉取Parallax Docker镜像
- 启动Qwen2-VL-7B-Instruct模型
- 在端口8000上提供API服务

**注意**：首次启动需要下载约8GB的模型文件，请耐心等待。

### 2. 配置后端

确保 `backend/.env` 文件包含以下配置：

```env
LLM_API_URL=http://localhost:8000/v1/chat/completions
LLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
LLM_ENABLED=true
```

### 3. 测试LLM分类

```bash
cd backend
conda activate ocr_agent
python test_llm_classification.py
```

### 4. 启动后端服务

```bash
start_backend.bat
```

## 架构说明

### 分类流程

```
用户输入文本
    ↓
API端点 (/api/v1/classify)
    ↓
ClassificationService.classify_text_with_llm()
    ↓
调用Parallax LLM API
    ↓
解析LLM响应
    ↓
提取结构化信息
    ↓
返回分类结果
```

### 降级策略

```
尝试LLM分类
    ↓
    ├─ 成功 → 返回LLM结果
    └─ 失败 → 使用规则方法
              ↓
              返回规则结果
```

## 代码修改说明

### 1. ClassificationService (`backend/app/services/classification_service.py`)

**新增方法**：
- `classify_text_with_llm()`: 异步LLM分类方法
- `_fallback_classify()`: 规则方法（原classify_text逻辑）

**修改**：
- `classify_text()`: 现在作为同步接口，调用规则方法
- 添加了httpx客户端用于HTTP请求

### 2. API端点 (`backend/app/api/classification.py`)

**修改**：
- `classify_text()`: 改为异步函数
- 优先调用LLM，失败时降级到规则方法

### 3. 配置 (`backend/app/core/config.py`)

**新增配置**：
```python
LLM_API_URL: str = "http://localhost:8000/v1/chat/completions"
LLM_MODEL: str = "Qwen/Qwen2-VL-7B-Instruct"
LLM_ENABLED: bool = True
```

## LLM Prompt设计

系统使用以下prompt进行分类：

```
请分析以下文本，判断它是"日程安排"还是"备忘录"。

日程安排的特征：
- 包含明确的时间信息（日期、时间）
- 描述未来要做的事情
- 通常包含会议、约会、活动等关键词

备忘录的特征：
- 记录想法、心得、笔记
- 没有明确的时间要求
- 通常是个人记录或总结

文本内容：
{text}

请以JSON格式返回结果...
```

## 性能对比

| 指标 | LLM模式 | 规则模式 |
|------|---------|----------|
| 准确率 | 高（~90%+） | 中（~70%） |
| 响应时间 | 慢（1-3秒） | 快（<100ms） |
| 资源消耗 | 高（需GPU） | 低 |
| 灵活性 | 高 | 低 |

## 测试

### 单元测试

现有的单元测试仍然有效，因为它们使用规则方法：

```bash
cd backend
python -m pytest tests/test_classification.py -v
```

### 属性测试

```bash
cd backend
python -m pytest tests/property_tests/test_classification_properties.py -v
```

### LLM集成测试

```bash
cd backend
python test_llm_classification.py
```

## 故障排除

### LLM服务无法启动

1. 检查Docker是否运行
2. 查看容器日志：`docker logs parallax-server`
3. 尝试CPU模式（见PARALLAX_SETUP.md）

### 分类请求超时

1. 增加超时时间（在ClassificationService中修改LLM_TIMEOUT）
2. 使用更小的模型（如Qwen2-1.5B）
3. 检查网络连接

### 分类结果不准确

1. 调整prompt（在classify_text_with_llm方法中）
2. 修改temperature参数（降低以获得更确定的结果）
3. 使用更大的模型

## 生产部署建议

1. **使用专用GPU服务器**
   - 推荐：NVIDIA A100, A10, RTX 4090

2. **负载均衡**
   - 部署多个Parallax实例
   - 使用Nginx或HAProxy进行负载均衡

3. **缓存策略**
   - 对相同文本的分类结果进行缓存
   - 使用Redis存储缓存

4. **监控和告警**
   - 监控LLM响应时间
   - 设置降级阈值
   - 记录降级事件

5. **模型优化**
   - 使用量化模型（GPTQ, AWQ）
   - 考虑模型蒸馏

## 未来改进

1. **批量分类**
   - 支持一次请求分类多个文本
   - 提高吞吐量

2. **流式响应**
   - 使用SSE返回实时分类进度
   - 改善用户体验

3. **模型微调**
   - 使用用户反馈数据微调模型
   - 提高特定场景的准确率

4. **多模型支持**
   - 支持切换不同的LLM
   - A/B测试不同模型

## 参考资源

- [Parallax文档](https://github.com/GradientHQ/parallax)
- [Qwen模型](https://huggingface.co/Qwen)
- [OpenAI API兼容性](https://platform.openai.com/docs/api-reference)

## 联系支持

如有问题，请查看：
1. PARALLAX_SETUP.md - 详细的安装和配置指南
2. 项目issue tracker
3. Parallax官方文档
