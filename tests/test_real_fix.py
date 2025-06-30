import requests
import json
import time

def test_real_query():
    """测试实际的查询问题是否已修复"""
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(5)
    
    # 测试URL
    url = "http://localhost:8000/chat"
    
    # 测试查询 - 这是之前出现问题的查询
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
                        beautiful_table = json_data.get('beautiful_table', '')
                        
                        print(f"\n=== 响应结果 ===")
                        print(f"answer_summary: {answer_summary}")
                        print(f"comparison_table长度: {len(comparison_table)}")
                        print(f"beautiful_table长度: {len(beautiful_table)}")
                        
                        # 检查是否包含LLM的原始摘要（而不是通用摘要）
                        if "958系列的两个型号" in answer_summary or "AHP958" in answer_summary:
                            print("✅ SUCCESS: 成功显示LLM的原始answer_summary")
                        elif "根據提供的数据" in answer_summary:
                            print("⚠️  WARNING: 显示的是备用摘要，可能LLM回答验证失败")
                        else:
                            print("❌ ERROR: answer_summary格式异常")
                        
                        # 检查表格是否正确
                        if comparison_table and len(comparison_table) > 0:
                            print("✅ SUCCESS: comparison_table存在且不为空")
                        else:
                            print("❌ ERROR: comparison_table为空")
                        
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

def test_multiple_queries():
    """测试多个查询"""
    
    queries = [
        "請問958系列螢幕規格有何不同",
        "AHP958的CPU是什麼型號",
        "958和AHP958的電池容量比較",
        "958系列的重量如何"
    ]
    
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    
    for i, query in enumerate(queries, 1):
        print(f"\n=== 测试查询 {i}: {query} ===")
        
        try:
            response = requests.post(url, headers=headers, json={"query": query}, timeout=30)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        try:
                            json_data = json.loads(line[6:])
                            answer_summary = json_data.get('answer_summary', '')
                            
                            # 检查是否包含模型名称
                            if any(model in answer_summary for model in ["958", "AHP958"]):
                                print(f"✅ 查询 {i} 成功: 包含正确的模型名称")
                            else:
                                print(f"⚠️  查询 {i} 警告: 使用备用摘要")
                            
                            break
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"❌ 查询 {i} 失败: 状态码 {response.status_code}")
                
        except Exception as e:
            print(f"❌ 查询 {i} 异常: {e}")
        
        time.sleep(1)  # 避免请求过快

if __name__ == "__main__":
    print("开始测试两步骤策略的实际效果...")
    test_real_query()
    print("\n" + "="*50)
    test_multiple_queries() 