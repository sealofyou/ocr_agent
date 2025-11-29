"""最终LLM分类测试"""
import requests
import json
import time


def test_classification(text):
    """测试单个文本分类"""
    
    api_url = "http://localhost:3001/v1/chat/completions"
    
    prompt = f"""请分析以下文本，判断它是"日程"还是"备忘录"。

日程特征：包含时间、日期、会议、约会等
备忘录特征：记录想法、笔记、心得等

文本：{text}

请用JSON格式回复：
{{
    "type": "schedule" 或 "memo",
    "confidence": 0.8,
    "reason": "理由"
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
                "max_tokens": 150
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            choice = result['choices'][0]
            
            # 兼容不同格式
            if 'messages' in choice:
                content = choice['messages']['content']
            elif 'message' in choice:
                content = choice['message']['content']
            else:
                content = str(choice)
            
            return True, content
        else:
            return False, f"错误: {response.status_code}"
            
    except Exception as e:
        return False, f"异常: {str(e)}"


def main():
    """主测试函数"""
    
    test_cases = [
        ("明天下午2点开会讨论项目进度", "schedule"),
        ("今天学习了Python编程，感觉很有收获", "memo"),
        ("2024年1月15日下午3点项目评审会议", "schedule"),
        ("记录一下今天的想法和心得体会", "memo"),
        ("下周一上午10点面试", "schedule"),
    ]
    
    print("=" * 70)
    print("LLM文本分类测试")
    print("API: http://localhost:3001/v1/chat/completions")
    print("=" * 70)
    print()
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (text, expected) in enumerate(test_cases, 1):
        print(f"[{i}/{total_count}] 测试: {text}")
        print(f"      预期: {expected}")
        print("-" * 70)
        
        success, content = test_classification(text)
        
        if success:
            print(f"✓ LLM响应:")
            print(f"  {content}")
            
            # 尝试解析JSON
            try:
                # 提取JSON
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    json_str = content.split('```')[1].split('```')[0].strip()
                elif '{' in content and '}' in content:
                    start = content.index('{')
                    end = content.rindex('}') + 1
                    json_str = content[start:end]
                else:
                    json_str = content
                
                result = json.loads(json_str)
                result_type = result.get('type', 'unknown')
                confidence = result.get('confidence', 0)
                
                print(f"  解析结果: 类型={result_type}, 置信度={confidence}")
                
                if result_type == expected or (result_type == 'schedule' and expected == 'schedule') or (result_type == 'memo' and expected == 'memo'):
                    print(f"  ✓ 分类正确!")
                    success_count += 1
                else:
                    print(f"  ✗ 分类错误 (预期: {expected})")
                    
            except Exception as e:
                print(f"  ⚠ JSON解析失败: {e}")
        else:
            print(f"✗ 请求失败: {content}")
        
        print()
        time.sleep(1)  # 避免请求过快
    
    print("=" * 70)
    print(f"测试完成: {success_count}/{total_count} 成功")
    print("=" * 70)
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！LLM分类功能正常工作！")
        print("\n下一步:")
        print("1. 启动后端服务: start_backend.bat")
        print("2. 启动前端服务: start_frontend.bat")
        print("3. 访问应用测试完整流程")
    else:
        print(f"\n⚠ {total_count - success_count} 个测试失败")
        print("但LLM API基本可用，可以继续测试")


if __name__ == "__main__":
    main()
