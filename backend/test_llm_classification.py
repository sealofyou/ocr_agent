"""测试LLM分类功能"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.classification_service import ClassificationService


async def test_llm_classification():
    """测试LLM分类"""
    service = ClassificationService()
    
    test_cases = [
        "明天下午2点开会讨论项目进度",
        "今天学习了Python编程，感觉很有收获",
        "2024年1月15日下午3点项目评审会议",
        "记录一下今天的想法和心得体会",
        "下周一上午10点面试",
    ]
    
    print("=" * 60)
    print("测试LLM文本分类")
    print("=" * 60)
    print()
    
    for i, text in enumerate(test_cases, 1):
        print(f"测试 {i}: {text}")
        print("-" * 60)
        
        try:
            # 测试LLM分类
            result = await service.classify_text_with_llm(text)
            print(f"✓ LLM分类成功")
            print(f"  类型: {result['type']}")
            print(f"  置信度: {result['confidence']:.2f}")
            print(f"  提取数据: {result['extracted_data']}")
        except Exception as e:
            print(f"✗ LLM分类失败: {str(e)}")
            print(f"  使用规则方法作为后备...")
            result = service._fallback_classify(text)
            print(f"  类型: {result['type']}")
            print(f"  置信度: {result['confidence']:.2f}")
        
        print()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_llm_classification())
