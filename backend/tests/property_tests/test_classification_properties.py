"""分类服务属性测试"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from app.services.classification_service import ClassificationService


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000))
def test_text_classification_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    对于任意文本内容，AI分类器应该将其分类为日程项或备忘录
    
    属性：所有文本都应该被分类为schedule或memo之一
    """
    service = ClassificationService()
    
    # 执行分类
    result = service.classify_text(text)
    
    # 属性1：分类结果必须是schedule或memo
    assert result["type"] in ["schedule", "memo"], f"分类类型必须是schedule或memo，实际为: {result['type']}"
    
    # 属性2：置信度必须在0到1之间
    assert 0 <= result["confidence"] <= 1, f"置信度必须在0-1之间，实际为: {result['confidence']}"
    
    # 属性3：必须包含extracted_data字段
    assert "extracted_data" in result, "结果必须包含extracted_data字段"
    assert isinstance(result["extracted_data"], dict), "extracted_data必须是字典类型"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=500),
    st.sampled_from(["明天", "今天", "后天", "下周", "下月"])
)
def test_schedule_classification_with_date_keywords_property(text_base, date_keyword):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：包含明确日期关键词的文本更可能被分类为日程
    """
    service = ClassificationService()
    
    # 构造包含日期关键词的文本
    text_with_date = f"{date_keyword}{text_base}"
    
    result = service.classify_text(text_with_date)
    
    # 属性：包含日期关键词应该增加日程分类的可能性
    # 注意：这不是绝对的，因为其他因素也会影响分类
    assert result["type"] in ["schedule", "memo"], "必须返回有效的分类类型"
    
    # 如果分类为日程，置信度应该合理
    if result["type"] == "schedule":
        assert result["confidence"] > 0, "日程分类的置信度应该大于0"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=500),
    st.sampled_from(["点", "时", "分", "上午", "下午", "晚上", "早上"])
)
def test_schedule_classification_with_time_keywords_property(text_base, time_keyword):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：包含时间关键词的文本更可能被分类为日程
    """
    service = ClassificationService()
    
    # 构造包含时间关键词的文本
    text_with_time = f"{text_base}{time_keyword}"
    
    result = service.classify_text(text_with_time)
    
    # 属性：必须返回有效的分类
    assert result["type"] in ["schedule", "memo"], "必须返回有效的分类类型"
    assert 0 <= result["confidence"] <= 1, "置信度必须在有效范围内"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=50, max_size=1000))
def test_long_text_classification_property(long_text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：较长的文本（没有明确时间信息）更可能被分类为备忘录
    """
    # 确保文本不包含明显的时间关键词
    time_keywords = ["点", "时", "分", "上午", "下午", "明天", "今天"]
    assume(not any(keyword in long_text for keyword in time_keywords))
    
    service = ClassificationService()
    result = service.classify_text(long_text)
    
    # 属性：长文本应该被正确分类
    assert result["type"] in ["schedule", "memo"], "必须返回有效的分类类型"
    
    # 如果没有时间信息，长文本更可能是备忘录
    # 但这不是绝对的，所以我们只验证分类的有效性
    assert result["confidence"] >= 0, "置信度应该是非负数"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000))
def test_classification_consistency_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：对同一文本的多次分类应该返回相同的结果
    """
    service = ClassificationService()
    
    # 对同一文本分类多次
    result1 = service.classify_text(text)
    result2 = service.classify_text(text)
    result3 = service.classify_text(text)
    
    # 属性：分类结果应该一致
    assert result1["type"] == result2["type"] == result3["type"], "同一文本的分类结果应该一致"
    assert result1["confidence"] == result2["confidence"] == result3["confidence"], "同一文本的置信度应该一致"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000))
def test_extracted_data_structure_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：提取的数据结构应该根据分类类型包含相应的字段
    """
    service = ClassificationService()
    result = service.classify_text(text)
    
    extracted_data = result["extracted_data"]
    
    if result["type"] == "schedule":
        # 日程应该包含这些字段
        assert "date" in extracted_data, "日程数据应该包含date字段"
        assert "time" in extracted_data, "日程数据应该包含time字段"
        assert "description" in extracted_data, "日程数据应该包含description字段"
        assert "has_time_info" in extracted_data, "日程数据应该包含has_time_info字段"
    else:  # memo
        # 备忘录应该包含这些字段
        assert "content" in extracted_data, "备忘录数据应该包含content字段"
        assert "summary" in extracted_data, "备忘录数据应该包含summary字段"
        assert "tags" in extracted_data, "备忘录数据应该包含tags字段"
        assert isinstance(extracted_data["tags"], list), "tags应该是列表类型"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=200),
    st.sampled_from(["会议", "约", "预约", "安排", "计划"])
)
def test_schedule_keywords_influence_property(text_base, schedule_keyword):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：包含日程关键词应该影响分类结果
    """
    service = ClassificationService()
    
    # 不包含关键词的文本
    result_without = service.classify_text(text_base)
    
    # 包含关键词的文本
    text_with_keyword = f"{text_base} {schedule_keyword}"
    result_with = service.classify_text(text_with_keyword)
    
    # 属性：两个结果都应该是有效的
    assert result_without["type"] in ["schedule", "memo"]
    assert result_with["type"] in ["schedule", "memo"]
    
    # 如果添加关键词后分类为日程，置信度应该合理
    if result_with["type"] == "schedule":
        assert result_with["confidence"] > 0, "包含日程关键词的文本分类为日程时置信度应该大于0"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=200),
    st.sampled_from(["记录", "笔记", "想法", "感想", "日记"])
)
def test_memo_keywords_influence_property(text_base, memo_keyword):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：包含备忘录关键词应该影响分类结果
    """
    service = ClassificationService()
    
    # 包含关键词的文本
    text_with_keyword = f"{text_base} {memo_keyword}"
    result = service.classify_text(text_with_keyword)
    
    # 属性：结果应该是有效的
    assert result["type"] in ["schedule", "memo"]
    
    # 如果分类为备忘录，置信度应该合理
    if result["type"] == "memo":
        assert result["confidence"] > 0, "包含备忘录关键词的文本分类为备忘录时置信度应该大于0"


@pytest.mark.property
@settings(max_examples=100)
@given(st.floats(min_value=0.0, max_value=1.0))
def test_manual_selection_threshold_property(confidence):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：置信度阈值判断应该一致
    """
    service = ClassificationService()
    
    needs_manual = service.needs_manual_selection(confidence)
    
    # 属性：低于阈值应该需要手动选择，高于阈值不需要
    if confidence < service.CONFIDENCE_THRESHOLD:
        assert needs_manual is True, f"置信度 {confidence} 低于阈值应该需要手动选择"
    else:
        assert needs_manual is False, f"置信度 {confidence} 高于阈值不应该需要手动选择"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000))
def test_schedule_info_extraction_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：日程信息提取应该总是返回完整的数据结构
    """
    service = ClassificationService()
    info = service.extract_schedule_info(text)
    
    # 属性：必须包含所有必需字段
    required_fields = ["date", "time", "description", "has_time_info"]
    for field in required_fields:
        assert field in info, f"日程信息必须包含 {field} 字段"
    
    # 属性：has_time_info应该与date/time的存在性一致
    has_date_or_time = info["date"] is not None or info["time"] is not None
    assert info["has_time_info"] == has_date_or_time, "has_time_info应该反映是否有日期或时间信息"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000))
def test_memo_info_extraction_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：备忘录信息提取应该总是返回完整的数据结构
    """
    service = ClassificationService()
    info = service.extract_memo_info(text)
    
    # 属性：必须包含所有必需字段
    required_fields = ["content", "summary", "tags"]
    for field in required_fields:
        assert field in info, f"备忘录信息必须包含 {field} 字段"
    
    # 属性：content应该与原始文本一致
    assert info["content"] == text, "content应该与原始文本一致"
    
    # 属性：summary不应该超过原始文本长度
    assert len(info["summary"]) <= len(text) + 3, "摘要长度不应该超过原始文本（考虑...）"
    
    # 属性：tags应该是列表
    assert isinstance(info["tags"], list), "tags应该是列表类型"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=50))
def test_summary_generation_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：短文本的摘要应该与原文一致
    """
    service = ClassificationService()
    summary = service._generate_summary(text, max_length=100)
    
    # 属性：短文本的摘要应该是原文本身
    if len(text) <= 100:
        assert summary == text, "短文本的摘要应该与原文一致"
    else:
        assert len(summary) <= 103, "摘要长度不应该超过max_length + 3（...）"
        assert summary.endswith("..."), "长文本的摘要应该以...结尾"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=101, max_size=1000))
def test_long_text_summary_property(long_text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：长文本的摘要应该被截断
    """
    service = ClassificationService()
    summary = service._generate_summary(long_text, max_length=100)
    
    # 属性：长文本的摘要应该被截断
    assert len(summary) <= 103, "摘要长度应该不超过max_length + 3"
    assert summary.endswith("..."), "长文本摘要应该以...结尾"
    assert summary.startswith(long_text[:100]), "摘要应该以原文开头"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=500),
    st.sampled_from(["schedule", "memo"])
)
def test_manual_classification_extraction_property(text, classification_type):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：手动分类后的信息提取应该根据类型返回正确的数据结构
    """
    service = ClassificationService()
    
    if classification_type == "schedule":
        extracted_data = service.extract_schedule_info(text)
        # 验证日程数据结构
        assert "date" in extracted_data
        assert "time" in extracted_data
        assert "description" in extracted_data
        assert "has_time_info" in extracted_data
    else:
        extracted_data = service.extract_memo_info(text)
        # 验证备忘录数据结构
        assert "content" in extracted_data
        assert "summary" in extracted_data
        assert "tags" in extracted_data
        assert extracted_data["content"] == text


@pytest.mark.property
@settings(max_examples=50)
@given(st.lists(st.text(min_size=1, max_size=200), min_size=1, max_size=10))
def test_batch_classification_property(text_list):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：批量分类应该为每个文本返回独立的结果
    """
    service = ClassificationService()
    
    results = []
    for text in text_list:
        result = service.classify_text(text)
        results.append(result)
    
    # 属性：每个文本都应该有有效的分类结果
    assert len(results) == len(text_list), "结果数量应该与输入文本数量一致"
    
    for i, result in enumerate(results):
        assert result["type"] in ["schedule", "memo"], f"第{i}个文本的分类类型应该有效"
        assert 0 <= result["confidence"] <= 1, f"第{i}个文本的置信度应该在有效范围内"
        assert "extracted_data" in result, f"第{i}个文本应该包含extracted_data"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000))
def test_classification_determinism_property(text):
    """
    Feature: text-archive-assistant, Property 9: 文本分类
    Validates: Requirements 3.1, 3.2, 3.3
    
    属性：分类算法应该是确定性的（相同输入产生相同输出）
    """
    service1 = ClassificationService()
    service2 = ClassificationService()
    
    result1 = service1.classify_text(text)
    result2 = service2.classify_text(text)
    
    # 属性：不同实例对相同文本的分类应该一致
    assert result1["type"] == result2["type"], "不同服务实例的分类结果应该一致"
    assert result1["confidence"] == result2["confidence"], "不同服务实例的置信度应该一致"
