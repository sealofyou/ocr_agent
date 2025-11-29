"""简单测试LLM API（使用requests）"""
import requests
import json


def test_llm():
    """测试LLM API"""
    
    api_url = "http://localhost:3001/v1/chat/completions"
    
    test_text = "明天下午2点开会讨论项目进度"
    
    print("=" * 60)
    print("测试LLM API")
    print(f"API: {api_url}")
    print(f"文本: {test_text}")
    print("=" * 60)
    print()
    
    prompt = f"""请分析以下文本，判断它是"日程安排"还是"备忘录"。

文本内容：{test_text}

请以JSON格式返回：
{{
    "type": "schedule" 或 "memo",
    "confidence": 0.0-1.0,
    "reasoning": "理由"
}}"""
    
    try:
        response = requests.post(
            api_url,
            json={
                "model": "Qwen/Qwen2-VL-7B-Instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 200
            },
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 成功!")
            print(f"\n完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('messages', [{}])[0].get('content', '')
                print(f"\nLLM回复:")
                print(content)
        else:
            print(f"✗ 错误: {response.text}")
            
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_llm()
