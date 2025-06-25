import requests
import json

def test_answer_summary_display():
    """测试answer_summary是否正确显示"""
    
    # 测试URL
    url = "http://localhost:8000/chat"
    
    # 测试查询
    test_query = "請問958系列螢幕規格有何不同"
    
    # 发送请求
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "query": test_query
    }
    
    try:
        print(f"发送查询: {test_query}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            # 解析SSE响应
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        json_data = json.loads(line[6:])  # 移除 'data: ' 前缀
                        
                        # 检查answer_summary是否存在且不为空
                        answer_summary = json_data.get('answer_summary', '')
                        comparison_table = json_data.get('comparison_table', [])
                        
                        print(f"\n=== 响应分析 ===")
                        print(f"answer_summary: {answer_summary}")
                        print(f"answer_summary长度: {len(answer_summary) if answer_summary else 0}")
                        print(f"comparison_table长度: {len(comparison_table)}")
                        
                        # 检查是否是通用响应
                        if answer_summary and "根据提供的数据，比较了" in answer_summary:
                            print("❌ 问题仍然存在：使用了通用响应而不是LLM的原始answer_summary")
                        elif answer_summary and len(answer_summary) > 10:
                            print("✅ 修复成功：answer_summary正确显示")
                        else:
                            print("❌ answer_summary为空或太短")
                        
                        break
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}")
                        continue
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    test_answer_summary_display() 