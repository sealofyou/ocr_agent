# 快速测试指南

## 🚀 5分钟快速测试

### 第一步：启动后端（终端1）

```bash
# 双击运行
start_backend.bat

# 或手动运行
cd backend
conda activate ocr_agent
python main.py
```

**等待看到**：`Application startup complete`

**访问**：http://localhost:8000/docs （查看API文档）

---

### 第二步：启动前端（终端2）

```bash
# 双击运行
start_frontend.bat

# 或手动运行
cd frontend
npm run dev
```

**等待看到**：`Local: http://localhost:5173/`

**访问**：http://localhost:5173

---

### 第三步：测试功能

#### 1. 注册用户
- 访问：http://localhost:5173/register
- 填写信息并注册

#### 2. 登录
- 使用刚注册的账号登录

#### 3. 测试OCR
- 访问：http://localhost:5173/ocr
- 上传一张包含文字的图片
- 点击"开始识别"
- 查看识别结果
- 尝试编辑结果

---

## 🧪 运行自动化测试

```bash
# 双击运行
run_tests.bat

# 或手动运行
cd backend
conda activate ocr_agent
python -m pytest tests/ -v
```

**预期结果**：所有测试通过 ✅

---

## ⚠️ 常见问题

### 问题1：前端启动失败
**解决**：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 问题2：后端端口被占用
**解决**：
- 关闭占用8000端口的程序
- 或修改 `backend/app/core/config.py` 中的 PORT

### 问题3：OCR识别很慢
**原因**：首次运行会下载OCR模型（约200MB）
**解决**：耐心等待，模型会缓存到本地

### 问题4：上传失败
**检查**：
- 图片格式是否为 JPG/PNG/BMP
- 图片大小是否小于 10MB
- 是否已登录

---

## 📊 测试结果

当前测试状态：
- ✅ 用户认证：8个测试通过
- ✅ 文件上传：12个单元测试 + 18个属性测试通过
- ✅ OCR识别：8个测试通过
- ✅ **总计：46个测试全部通过**

---

## 🎯 下一步

测试通过后，你可以：

1. **继续开发**：实现AI分类、日程管理等功能
2. **优化性能**：提升OCR识别速度和准确率
3. **部署上线**：准备生产环境部署
4. **添加功能**：根据需求添加新特性

---

## 📞 需要帮助？

查看详细文档：
- `TESTING_GUIDE.md` - 完整测试指南
- `backend/TESTING.md` - 后端测试文档
- `backend/README.md` - 后端使用说明
- `frontend/README.md` - 前端使用说明
