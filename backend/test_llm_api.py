"""简单测试LLM API连接"""
import httpx
import json
import asyncio


async def test_llm_api():
    """测试LLM API"""
    
    api_url = "http://localhost:3001/v1/chat/completions"
    
    test_cases = [
        "明天下午2点开会讨论项目进度",
        "今天学习了Python编程，感觉很有收获",
        "2024年1月15日下午3点项目评审会议",
        "记录一下今天的想法和心得体会",
        "下周一上午10点面试",
    ]
    
    print("=" * 60)
    print("测试LLM文本分类API")
    print(f"API地址: {api_url}")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, text in enumerate(test_cases, 1):
            print(f"测试 {i}: {text}")
            print("-" * 60)
            
            prompt = f"""请分析以下文本，判断它是"日程安排"还是"备忘录"。

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

请以JSON格式返回结果，包含以下字段：
{{
    "type": "schedule" 或 "memo",
    "confidence": 0.0-1.0之间的置信度,
    "reasoning": "分类理由"
}}

只返回JSON，不要其他内容。"""
            
            try:
                response = await client.post(
                    api_url,
                    json={
                        "model": "Qwen/Qwen2-VL-7B-Instruct",
                        "messages": [
                            {"role": "system", "content": "你是一个文本分类助手，擅长区分日程安排和备忘录。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 200
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['messages'][0]['content']
                    
                    print(f"✓ LLM响应成功")
                    print(f"  原始响应: {content[:200]}...")
                    
                    # 尝试解析JSON
                    try:
                        # 提取JSON（可能包含在markdown代码块中）
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0].strip()
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0].strip()
                        
                        classification = json.loads(content)
                        print(f"  类型: {classification.get('type', 'unknown')}")
                        print(f"  置信度: {classification.get('confidence', 0):.2f}")
                        print(f"  理由: {classification.get('reasoning', 'N/A')}")
                    except json.JSONDecodeError as e:
                        print(f"  ⚠ JSON解析失败: {e}")
                        print(f"  内容: {content}")
                else:
                    print(f"✗ API返回错误: {response.status_code}")
                    print(f"  {response.text}")
                    
            except Exception as e:
                print(f"✗ 请求失败: {str(e)}")
            
            print()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_llm_api())
