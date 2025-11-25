# 测试指南

本项目使用pytest作为测试框架，hypothesis用于属性测试。

## 测试结构

```
tests/
├── __init__.py
├── conftest.py                    # pytest配置和fixtures
├── test_models.py                 # 数据模型测试
├── property_tests/                # 属性测试目录
│   ├── __init__.py
│   └── test_property_example.py   # 属性测试示例
└── README.md                      # 本文件
```

## 测试类型

### 1. 单元测试 (Unit Tests)

单元测试验证单个组件或函数的行为。

**标记**: `@pytest.mark.unit`

**示例**:
```python
@pytest.mark.unit
def test_user_creation(db_session):
    user = User(username="test", email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### 2. 属性测试 (Property-Based Tests)

属性测试使用Hypothesis生成随机测试数据，验证通用属性。

**标记**: `@pytest.mark.property`

**要求**:
- 每个属性测试必须运行至少100次迭代
- 必须使用注释标注对应的设计文档属性
- 注释格式: `# Feature: text-archive-assistant, Property {number}: {property_text}`

**示例**:
```python
from hypothesis import given, strategies as st, settings

@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1))
def test_password_encryption_property(password):
    """
    Feature: text-archive-assistant, Property 28: 密码加密存储
    Validates: Requirements 10.1
    
    对于任意用户注册，系统应该使用加密算法存储密码，
    数据库中不应存在明文密码
    """
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
```

### 3. 集成测试 (Integration Tests)

集成测试验证多个组件协同工作。

**标记**: `@pytest.mark.integration`

## 运行测试

### 运行所有测试
```bash
pytest
# 或
python run_tests.py
```

### 运行特定类型的测试
```bash
# 只运行单元测试
pytest -m unit
# 或
python run_tests.py unit

# 只运行属性测试
pytest -m property
# 或
python run_tests.py property

# 只运行集成测试
pytest -m integration
# 或
python run_tests.py integration
```

### 运行特定文件
```bash
pytest tests/test_models.py
```

### 运行特定测试
```bash
pytest tests/test_models.py::test_user_model_creation
```

### 显示详细输出
```bash
pytest -v
```

### 显示打印输出
```bash
pytest -s
```

## Fixtures

### db_session
提供测试数据库会话，每个测试函数后自动清理。

```python
def test_example(db_session):
    user = User(username="test")
    db_session.add(user)
    db_session.commit()
```

### client
提供FastAPI测试客户端。

```python
def test_api(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 200
```

### sample_user_data
提供示例用户数据。

```python
def test_user(sample_user_data):
    assert sample_user_data["username"] == "testuser"
```

## 编写测试的最佳实践

1. **测试命名**: 使用描述性名称，清楚说明测试内容
   - ✅ `test_user_registration_with_valid_data`
   - ❌ `test_1`

2. **一个测试一个断言**: 尽量每个测试只验证一个行为

3. **使用fixtures**: 复用测试数据和设置

4. **属性测试策略**: 
   - 使用合适的策略生成测试数据
   - 考虑边界情况
   - 设置合理的约束条件

5. **测试隔离**: 每个测试应该独立，不依赖其他测试

6. **清晰的断言消息**: 使用有意义的断言消息
   ```python
   assert user.email == expected_email, f"Expected {expected_email}, got {user.email}"
   ```

## 测试覆盖率

查看测试覆盖率：
```bash
pytest --cov=app --cov-report=html
```

然后打开 `htmlcov/index.html` 查看详细报告。

## 持续集成

所有测试应该在提交代码前通过：
```bash
pytest
```

目标测试覆盖率: >80%

## 属性测试策略示例

### 文本策略
```python
from hypothesis import strategies as st

# 非空文本
st.text(min_size=1, max_size=100)

# 用户名（字母数字）
st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=3, max_size=20)

# 邮箱
st.emails()
```

### 日期时间策略
```python
from datetime import datetime, timedelta

# 日期范围
st.dates(min_value=datetime(2020, 1, 1).date(), max_value=datetime(2030, 12, 31).date())

# 时间
st.times()
```

### 列表策略
```python
# 标签列表
st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10)
```

## 调试测试

### 使用pdb调试
```python
def test_example():
    import pdb; pdb.set_trace()
    # 测试代码
```

### 查看失败的属性测试
Hypothesis会自动保存失败的测试用例，可以重现：
```bash
pytest --hypothesis-show-statistics
```

## 常见问题

### Q: 测试数据库如何清理？
A: 使用 `db_session` fixture，每个测试后自动清理。

### Q: 如何模拟外部服务（如OCR）？
A: 使用pytest的monkeypatch或unittest.mock。

### Q: 属性测试运行太慢怎么办？
A: 减少 `max_examples` 数量，或使用 `@settings(deadline=None)` 禁用超时。

## 参考资源

- [pytest文档](https://docs.pytest.org/)
- [Hypothesis文档](https://hypothesis.readthedocs.io/)
- [FastAPI测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
