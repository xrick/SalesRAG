import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_query_intent_parsing():
    """测试查询意图解析"""
    
    service = SalesAssistantService()
    
    test_queries = [
        "請問958系列螢幕規格有何不同",
        "AHP958的CPU是什麼型號",
        "958和AHP958的電池容量比較",
        "958系列的重量如何",
        "AB819-S: FP6的GPU性能",
        "比較839系列的記憶體規格"
    ]
    
    print("=== 测试查询意图解析 ===")
    for query in test_queries:
        intent = service._parse_query_intent(query)
        print(f"\n查询: {query}")
        print(f"解析结果: {intent}")

def test_data_retrieval():
    """测试数据获取"""
    
    service = SalesAssistantService()
    
    print("\n=== 测试数据获取 ===")
    
    # 测试具体型号查询
    print("\n1. 测试具体型号查询")
    query_intent_1 = {
        "query_type": "specific_model",
        "modelnames": ["AHP958"],
        "modeltypes": [],
        "intent": "cpu"
    }
    
    try:
        context_1, models_1 = service._get_data_by_query_type(query_intent_1)
        print(f"成功获取型号 {models_1} 的数据，记录数: {len(context_1)}")
        if context_1:
            print(f"第一个记录的modelname: {context_1[0].get('modelname', 'N/A')}")
    except Exception as e:
        print(f"具体型号查询失败: {e}")
    
    # 测试型号系列查询
    print("\n2. 测试型号系列查询")
    query_intent_2 = {
        "query_type": "model_type",
        "modelnames": [],
        "modeltypes": ["958"],
        "intent": "display"
    }
    
    try:
        context_2, models_2 = service._get_data_by_query_type(query_intent_2)
        print(f"成功获取系列 {query_intent_2['modeltypes'][0]} 的数据，型号数: {len(models_2)}")
        print(f"型号列表: {models_2}")
        if context_2:
            print(f"记录数: {len(context_2)}")
    except Exception as e:
        print(f"型号系列查询失败: {e}")

def test_full_flow():
    """测试完整流程"""
    
    service = SalesAssistantService()
    
    print("\n=== 测试完整流程 ===")
    
    # 测试查询1：具体型号
    print("\n1. 测试具体型号查询: AHP958的CPU是什麼型號")
    query_1 = "AHP958的CPU是什麼型號"
    
    try:
        intent_1 = service._parse_query_intent(query_1)
        print(f"查询意图: {intent_1}")
        
        if intent_1["query_type"] != "unknown":
            context_1, models_1 = service._get_data_by_query_type(intent_1)
            print(f"获取到 {len(context_1)} 条数据，型号: {models_1}")
            
            # 构建增强上下文
            enhanced_context_1 = {
                "data": context_1,
                "query_intent": intent_1,
                "target_modelnames": models_1
            }
            print(f"增强上下文构建成功，包含 {len(enhanced_context_1['data'])} 条数据")
        else:
            print("查询类型为unknown，无法获取数据")
    except Exception as e:
        print(f"完整流程测试1失败: {e}")
    
    # 测试查询2：型号系列
    print("\n2. 测试型号系列查询: 958系列的螢幕規格")
    query_2 = "958系列的螢幕規格"
    
    try:
        intent_2 = service._parse_query_intent(query_2)
        print(f"查询意图: {intent_2}")
        
        if intent_2["query_type"] != "unknown":
            context_2, models_2 = service._get_data_by_query_type(intent_2)
            print(f"获取到 {len(context_2)} 条数据，型号: {models_2}")
            
            # 构建增强上下文
            enhanced_context_2 = {
                "data": context_2,
                "query_intent": intent_2,
                "target_modelnames": models_2
            }
            print(f"增强上下文构建成功，包含 {len(enhanced_context_2['data'])} 条数据")
        else:
            print("查询类型为unknown，无法获取数据")
    except Exception as e:
        print(f"完整流程测试2失败: {e}")

if __name__ == "__main__":
    test_query_intent_parsing()
    test_data_retrieval()
    test_full_flow() 