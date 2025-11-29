# 手写管理助手 - 测试指南

## 快速开始

### 1. 后端测试

#### 启动后端服务器

```bash
cd backend
conda activate ocr_agent
python main.py
```

后端服务将在 `http://localhost:8000` 启动

#### 运行后端单元测试

```bash
cd backend
conda activate ocr_agent

# 运行所有测试
python -m pytest tests/ -v

# 运行特定模块的测试
python -m pytest tests/test_auth.py -v          # 认证测试
python -m pytest tests/test_upload.py -v        # 文件上传测试
python -m pytest tests/test_ocr.py -v           # OCR测试

# 运行属性测试
python -m pytest tests/property_tests/ -v -m property
```

### 2. 前端测试

#### 安装前端依赖

```bash
cd frontend
npm install
```

#### 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 3. 完整系统测试

#### 步骤1：启动后端

在终端1中：
```bash
cd backend
conda activate ocr_agent
python main.py
```

#### 步骤2：启动前端

在终端2中：
```bash
cd frontend
npm run dev
```

#### 步骤3：访问应用

打开浏览器访问：`http://localhost:5173`

## 功能测试流程

### 测试1：用户注册和登录

1. 访问 `http://localhost:5173/register`
2. 填写注册信息：
   - 用户名：testuser
   - 邮箱：test@example.com
   - 密码：Test123!
3. 点击注册
4. 注册成功后会自动跳转到登录页
5. 使用相同的用户名和密码登录

### 测试2：文件上传

1. 登录后访问 `http://localhost:5173/ocr`
2. 准备一张包含文字的图片（支持 JPG、PNG、BMP 格式）
3. 点击上传区域或拖拽图片到上传区域
4. 等待上传完成，会显示上传成功的提示

### 测试3：OCR文字识别

1. 上传图片后，点击"开始识别"按钮
2. 等待OCR识别完成（首次运行会下载模型，可能需要几分钟）
3. 识别完成后会显示识别的文字内容
4. 可以查看详细信息，包括每行文字的置信度

### 测试4：编辑识别结果

1. 在识别结果页面，点击"编辑"按钮
2. 在文本框中修改识别的文字
3. 点击"保存"按钮保存修改
4. 或点击"取消"放弃修改

## API测试

### 使用Swagger UI测试API

访问 `http://localhost:8000/docs` 查看和测试所有API端点

### 使用curl测试

#### 1. 用户注册
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

#### 2. 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }'
```

保存返回的 `access_token`

#### 3. 上传文件
```bash
curl -X POST "http://localhost:8000/api/v1/upload/file" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

保存返回的 `file_id`

#### 4. OCR识别
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/recognize" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "YOUR_FILE_ID"
  }'
```

## 测试数据准备

### 准备测试图片

建议准备以下类型的测试图片：

1. **中文文本图片**：包含中文文字的截图或照片
2. **英文文本图片**：包含英文文字的文档
3. **中英混合图片**：同时包含中英文的图片
4. **手写文字图片**：手写笔记的照片
5. **印刷文档**：书籍、报纸的照片

### 测试图片要求

- 格式：JPG、PNG 或 BMP
- 大小：不超过 10MB
- 分辨率：建议 100x100 到 4000x4000 像素
- 清晰度：文字清晰可见

## 常见问题排查

### 后端问题

#### 1. 端口被占用
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或修改端口
# 在 backend/app/core/config.py 中修改 PORT 配置
```

#### 2. 数据库错误
```bash
cd backend
python init_db.py  # 重新初始化数据库
```

#### 3. OCR模型下载失败
- 检查网络连接
- 首次运行OCR识别时会自动下载模型
- 模型会缓存在 `~/.paddleocr/` 目录

### 前端问题

#### 1. 依赖安装失败
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 2. API连接失败
- 检查后端是否正常运行
- 检查 `frontend/src/api/client.ts` 中的 baseURL 配置
- 确认CORS配置正确

#### 3. 上传失败
- 检查文件格式和大小
- 查看浏览器控制台的错误信息
- 确认已登录并有有效的token

## 性能测试

### 后端性能测试

```bash
cd backend
conda activate ocr_agent

# 运行性能测试
python -m pytest tests/ -v --durations=10
```

### 压力测试

使用 Apache Bench 进行压力测试：

```bash
# 测试登录接口
ab -n 100 -c 10 -p login.json -T application/json \
  http://localhost:8000/api/v1/auth/login
```

## 测试覆盖率

### 查看测试覆盖率

```bash
cd backend
conda activate ocr_agent

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=app --cov-report=html

# 查看报告
# 打开 htmlcov/index.html
```

## 自动化测试

### 运行所有测试

```bash
# 后端测试
cd backend
conda activate ocr_agent
python -m pytest tests/ -v --tb=short

# 前端测试（如果配置了）
cd frontend
npm test
```

## 测试检查清单

- [ ] 后端服务器正常启动
- [ ] 前端开发服务器正常启动
- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 文件上传功能正常
- [ ] OCR识别功能正常
- [ ] 识别结果显示正常
- [ ] 编辑功能正常
- [ ] 所有单元测试通过
- [ ] 所有属性测试通过
- [ ] API文档可访问
- [ ] 错误处理正常

## 下一步

测试完成后，你可以：

1. 继续开发其他功能（AI分类、日程管理等）
2. 优化OCR识别准确率
3. 添加更多的测试用例
4. 部署到生产环境

## 获取帮助

如果遇到问题：

1. 查看日志文件：`backend/logs/`
2. 检查浏览器控制台
3. 查看后端终端输出
4. 参考 `backend/TESTING.md` 和 `TEST_SETUP_SUMMARY.md`
