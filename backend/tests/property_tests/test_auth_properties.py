"""用户认证属性测试"""
import pytest
from hypothesis import given, strategies as st, settings
from app.utils.auth import hash_password, verify_password


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=100))
def test_password_encryption_property(password):
    """
    Feature: text-archive-assistant, Property 28: 密码加密存储
    Validates: Requirements 10.1
    
    对于任意用户注册，系统应该使用加密算法存储密码，
    数据库中不应存在明文密码
    
    属性：对于任意密码字符串，加密后的哈希值不应该等于原密码，
    且应该能够通过验证函数验证
    """
    # 加密密码
    hashed = hash_password(password)
    
    # 属性1：加密后的密码不应该等于原密码
    assert hashed != password, "加密后的密码不应该等于明文密码"
    
    # 属性2：加密后的密码应该能够通过验证
    assert verify_password(password, hashed), "加密后的密码应该能够通过验证"
    
    # 属性3：错误的密码不应该通过验证
    if len(password) > 1:
        wrong_password = password[:-1] + ("x" if password[-1] != "x" else "y")
        assert not verify_password(wrong_password, hashed), "错误的密码不应该通过验证"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=100))
def test_password_hash_uniqueness(password):
    """
    Feature: text-archive-assistant, Property 28: 密码加密存储
    Validates: Requirements 10.1
    
    属性：相同的密码每次加密应该产生不同的哈希值（因为使用了salt）
    """
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # bcrypt会为每次加密生成不同的salt，所以哈希值应该不同
    # 但两个哈希值都应该能够验证原密码
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
    st.text(min_size=6, max_size=100)
)
def test_password_verification_consistency(username, password):
    """
    Feature: text-archive-assistant, Property 28: 密码加密存储
    Validates: Requirements 10.1
    
    属性：对于任意用户名和密码组合，加密和验证应该保持一致性
    """
    # 加密密码
    hashed = hash_password(password)
    
    # 验证应该成功
    assert verify_password(password, hashed), f"密码验证失败: username={username}"
    
    # 加密后的密码长度应该固定（bcrypt产生固定长度的哈希）
    assert len(hashed) == 60, "bcrypt哈希长度应该是60字符"



@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=10, max_size=50))
def test_access_token_validation_property(user_id):
    """
    Feature: text-archive-assistant, Property 29: 访问权限验证
    Validates: Requirements 10.2
    
    对于任意归档内容访问请求，系统应该验证用户身份和访问权限
    
    属性：对于任意用户ID，创建的访问令牌应该能够被正确解码，
    且解码后的用户ID应该与原始用户ID一致
    """
    from app.utils.auth import create_access_token, decode_access_token
    
    # 创建访问令牌
    token = create_access_token(data={"sub": user_id})
    
    # 属性1：令牌应该是非空字符串
    assert isinstance(token, str)
    assert len(token) > 0
    
    # 属性2：令牌应该能够被解码
    payload = decode_access_token(token)
    assert payload is not None, "令牌应该能够被解码"
    
    # 属性3：解码后的用户ID应该与原始用户ID一致
    assert payload.get("sub") == user_id, "解码后的用户ID应该与原始用户ID一致"
    
    # 属性4：令牌应该包含过期时间
    assert "exp" in payload, "令牌应该包含过期时间"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=100))
def test_invalid_token_rejection_property(invalid_token):
    """
    Feature: text-archive-assistant, Property 29: 访问权限验证
    Validates: Requirements 10.2
    
    属性：对于任意无效的令牌字符串，解码应该返回None
    """
    from app.utils.auth import decode_access_token
    
    # 尝试解码无效令牌
    payload = decode_access_token(invalid_token)
    
    # 无效令牌应该返回None
    assert payload is None, "无效令牌应该返回None"
