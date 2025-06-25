import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

async def test_full_flow():
    """测试完整的RAG流程，包括数据可用性检查"""
    
    service = SalesAssistantService()
    
    print("=== 测试完整RAG流程（包含数据可用性检查）===")
    
    # 测试用例1：有数据的查询
    print("\n1. 测试有数据的查询: '比较AHP958和AG958的CPU性能'")
    query1 = "比较AHP958和AG958的CPU性能"
    
    async for response in service.chat_stream(query1):
        if response.startswith("data: "):
            data = response[6:]  # 移除 "data: " 前缀
            import json
            result = json.loads(data)
            print(f"Answer Summary: {result.get('answer_summary', 'N/A')}")
            print(f"Comparison Table: {len(result.get('comparison_table', []))} 行")
            for row in result.get('comparison_table', []):
                print(f"  {row}")
            break
    
    # 测试用例2：查询不存在的特性
    print("\n2. 测试查询不存在的特性: 'AHP958的重量是多少'")
    query2 = "AHP958的重量是多少"
    
    async for response in service.chat_stream(query2):
        if response.startswith("data: "):
            data = response[6:]  # 移除 "data: " 前缀
            import json
            result = json.loads(data)
            print(f"Answer Summary: {result.get('answer_summary', 'N/A')}")
            print(f"Comparison Table: {len(result.get('comparison_table', []))} 行")
            break
    
    # 测试用例3：查询nodata字段
    print("\n3. 测试查询nodata字段: 'AHP958的接口规格'")
    query3 = "AHP958的接口规格"
    
    async for response in service.chat_stream(query3):
        if response.startswith("data: "):
            data = response[6:]  # 移除 "data: " 前缀
            import json
            result = json.loads(data)
            print(f"Answer Summary: {result.get('answer_summary', 'N/A')}")
            print(f"Comparison Table: {len(result.get('comparison_table', []))} 行")
            break
    
    # 测试用例4：查询空字段
    print("\n4. 测试查询空字段: 'AHP958的无线网卡规格'")
    query4 = "AHP958的无线网卡规格"
    
    async for response in service.chat_stream(query4):
        if response.startswith("data: "):
            data = response[6:]  # 移除 "data: " 前缀
            import json
            result = json.loads(data)
            print(f"Answer Summary: {result.get('answer_summary', 'N/A')}")
            print(f"Comparison Table: {len(result.get('comparison_table', []))} 行")
            break

def test_data_availability_edge_cases():
    """测试数据可用性检查的边界情况"""
    
    service = SalesAssistantService()
    
    print("\n=== 测试数据可用性检查的边界情况 ===")
    
    # 测试用例1：所有字段都是nodata
    print("\n1. 测试所有字段都是nodata")
    context_data_1 = [
        {
            "modelname": "TEST958",
            "cpu": "nodata",
            "gpu": "nodata",
            "memory": "nodata",
            "storage": "nodata",
            "battery": "nodata"
        }
    ]
    
    query_intent_1 = {
        "intent": "cpu",
        "query": "TEST958的CPU是什麼型號"
    }
    
    has_data_1, missing_info_1 = service._check_data_availability(context_data_1, ["TEST958"], query_intent_1)
    print(f"结果: has_data={has_data_1}, missing_info={missing_info_1}")
    
    # 测试用例2：部分字段为空，部分有数据
    print("\n2. 测试部分字段为空，部分有数据")
    context_data_2 = [
        {
            "modelname": "TEST958",
            "cpu": "",  # 空字段
            "gpu": "AMD Radeon™ RX7600M",  # 有数据
            "memory": "DDR5",  # 有数据
            "storage": "",  # 空字段
            "battery": "80.08Wh"  # 有数据
        }
    ]
    
    query_intent_2 = {
        "intent": "cpu",
        "query": "TEST958的CPU是什麼型號"
    }
    
    has_data_2, missing_info_2 = service._check_data_availability(context_data_2, ["TEST958"], query_intent_2)
    print(f"CPU查询结果: has_data={has_data_2}, missing_info={missing_info_2}")
    
    query_intent_2_gpu = {
        "intent": "gpu",
        "query": "TEST958的GPU是什麼型號"
    }
    
    has_data_2_gpu, missing_info_2_gpu = service._check_data_availability(context_data_2, ["TEST958"], query_intent_2_gpu)
    print(f"GPU查询结果: has_data={has_data_2_gpu}, missing_info={missing_info_2_gpu}")
    
    # 测试用例3：多个型号，部分有数据
    print("\n3. 测试多个型号，部分有数据")
    context_data_3 = [
        {
            "modelname": "AHP958",
            "cpu": "Ryzen™ 9 8945HS",
            "gpu": "AMD Radeon™ RX7600M",
            "memory": "DDR5",
            "storage": "M.2 2280 PCIe Gen4",
            "battery": "80.08Wh"
        },
        {
            "modelname": "AG958",
            "cpu": "nodata",  # 没有数据
            "gpu": "AMD Radeon™ RX6550M",
            "memory": "DDR5",
            "storage": "M.2 2280 PCIe Gen4",
            "battery": "80.08Wh"
        }
    ]
    
    query_intent_3 = {
        "intent": "cpu",
        "query": "958系列的CPU比較"
    }
    
    has_data_3, missing_info_3 = service._check_data_availability(context_data_3, ["AHP958", "AG958"], query_intent_3)
    print(f"结果: has_data={has_data_3}, missing_info={missing_info_3}")

if __name__ == "__main__":
    # 运行边界情况测试
    test_data_availability_edge_cases()
    
    # 运行完整流程测试
    asyncio.run(test_full_flow()) 