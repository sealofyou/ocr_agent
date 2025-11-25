# 测试配置总结

## 已完成的测试基础设施

### 1. 测试框架配置

- ✅ pytest 配置 (`pytest.ini`)
- ✅ 测试依赖添加到 `pyproject.toml`
- ✅ 测试fixtures配置 (`tests/conftest.py`)
- ✅ 测试运行脚本 (`run_tests.py`)

### 2. 测试目录结构

```
backend/tests/
├── __init__.py
├── conftest.py                    # pytest配置和fixtures
├── test_models.py                 # 数据模型单元测试
├── property_tests/                # 属性测试目录
│   ├── __init__.py
│   └── test_property_example.py   # 属性测试示例
└── README.md                      # 测试指南
```

### 3. 已实现的Fixtures

- `db_session`: 测试数据库会话（自动清理）
- `client`: FastAPI测试客户端
- `sample_user_data`: 示例用户数据
- `sample_schedule_data`: 示例日程数据
- `sample_memo_data`: 示例备忘录数据

### 4. 测试标记

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.property`: 属性测试
- `@pytest.mark.integration`: 集成测试

### 5. 已创建的示例测试

#### 单元测试 (`test_models.py`)
- ✅ `test_user_model_creation`: 用户模型创建测试
- ✅ `test_schedule_model_creation`: 日程模型创建测试
- ✅ `test_memo_model_creation`: 备忘录模型创建测试

#### 属性测试 (`test_property_example.py`)
- ✅ `test_string_property_example`: 字符串属性示例
- ✅ `test_integer_property_example`: 整数属性示例

## 测试运行方式

### 基本命令

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m unit

# 运行属性测试
pytest -m property

# 使用测试脚本
python run_tests.py
python run_tests.py unit
python run_tests.py property
```

### 高级选项

```bash
# 详细输出
pytest -v

# 显示打印
pytest -s

# 测试覆盖率
pytest --cov=app --cov-report=html

# 运行特定文件
pytest tests/test_models.py

# 运行特定测试
pytest tests/test_models.py::test_user_model_creation
```

## 后续任务的测试要求

根据更新后的 `tasks.md`，每个主要功能任务现在都包含：

1. **功能实现任务** - 实现核心功能
2. **单元测试子任务** - 测试具体实现细节
3. **属性测试子任务** - 验证通用属性

### 示例：任务2（用户认证系统）

- [ ] 2. 实现用户认证系统
- [ ] 2.1 编写用户认证的单元测试
  - 测试用户注册API端点
  - 测试用户登录API端点
  - 测试JWT token生成和验证
  - 测试认证中间件功能
- [ ] 2.2 编写用户认证的属性测试
  - Property 28: 密码加密存储
- [ ] 2.3 编写访问权限验证的属性测试
  - Property 29: 访问权限验证

## 属性测试编写规范

每个属性测试必须：

1. **运行至少100次迭代**
   ```python
   @settings(max_examples=100)
   ```

2. **标注对应的设计文档属性**
   ```python
   """
   Feature: text-archive-assistant, Property 28: 密码加密存储
   Validates: Requirements 10.1
   """
   ```

3. **使用合适的Hypothesis策略**
   ```python
   @given(st.text(min_size=1, max_size=100))
   ```

## 测试数据生成策略

### 常用Hypothesis策略

```python
from hypothesis import strategies as st

# 文本
st.text(min_size=1, max_size=100)
st.emails()

# 数字
st.integers(min_value=1, max_value=1000)
st.floats(min_value=0.0, max_value=1.0)

# 日期时间
st.dates()
st.times()
st.datetimes()

# 集合
st.lists(st.text(), min_size=0, max_size=10)
st.dictionaries(keys=st.text(), values=st.integers())

# 自定义
st.builds(User, username=st.text(), email=st.emails())
```

## 测试覆盖率目标

- 总体覆盖率: >80%
- 核心业务逻辑: >90%
- API端点: 100%

## 持续集成

所有测试应该在以下情况下运行：
- 提交代码前
- Pull Request创建时
- 合并到主分支前

## 调试技巧

### 1. 使用pdb
```python
import pdb; pdb.set_trace()
```

### 2. 查看Hypothesis统计
```bash
pytest --hypothesis-show-statistics
```

### 3. 重现失败的属性测试
Hypothesis会自动保存失败的测试用例，可以直接重新运行。

## 参考文档

- [测试指南](./tests/README.md)
- [设计文档](../.kiro/specs/text-archive-assistant/design.md)
- [任务列表](../.kiro/specs/text-archive-assistant/tasks.md)

## 下一步

1. 开始实现任务2：用户认证系统
2. 为每个功能编写对应的单元测试和属性测试
3. 确保所有测试通过后再进行下一个任务
4. 定期检查测试覆盖率
