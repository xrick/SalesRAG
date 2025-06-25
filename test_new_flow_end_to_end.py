import requests
import json
import time

def test_new_flow():
    """测试新流程的端到端效果"""
    
    print("等待服务器启动...")
    time.sleep(5)
    
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    
    test_cases = [
        {
            "name": "具体型号查询",
            "query": "AHP958的CPU是什麼型號"
        },
        {
            "name": "型号系列查询", 
            "query": "958系列的螢幕規格有何不同"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== 测试: {test_case['name']} ===")
        print(f"查询: {test_case['query']}")
        
        try:
            response = requests.post(url, headers=headers, json={"query": test_case['query']}, timeout=30)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        try:
                            json_data = json.loads(line[6:])
                            answer_summary = json_data.get('answer_summary', '')
                            comparison_table = json_data.get('comparison_table', [])
                            
                            print(f"✅ 成功")
                            print(f"answer_summary: {len(answer_summary)} 字符")
                            print(f"comparison_table: {len(comparison_table)} 行")
                            
                            if answer_summary and comparison_table:
                                print("✅ 数据完整")
                            else:
                                print("⚠️  数据不完整")
                            
                            break
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        time.sleep(2)

def test_performance_comparison():
    """测试性能对比"""
    
    print("\n" + "="*60)
    print("=== 性能对比测试 ===")
    
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    
    # 测试查询
    test_query = "958系列的螢幕規格有何不同"
    
    print(f"测试查询: {test_query}")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json={"query": test_query}, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ 响应时间: {end_time - start_time:.2f} 秒")
            
            # 解析响应
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        json_data = json.loads(line[6:])
                        answer_summary = json_data.get('answer_summary', '')
                        comparison_table = json_data.get('comparison_table', [])
                        
                        print(f"✅ 数据质量:")
                        print(f"   - answer_summary: {len(answer_summary)} 字符")
                        print(f"   - comparison_table: {len(comparison_table)} 行")
                        
                        # 检查是否包含958系列的所有型号
                        if all(model in answer_summary for model in ['AG958', 'AHP958', 'APX958']):
                            print("✅ 包含完整的958系列型号")
                        else:
                            print("⚠️  可能缺少部分型号")
                        
                        break
                    except json.JSONDecodeError:
                        continue
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("开始测试新的RAG流程...")
    test_new_flow()
    test_performance_comparison() 