import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_data_availability_check():
    """测试数据可用性检查功能"""
    
    service = SalesAssistantService()
    
    print("=== 测试数据可用性检查 ===")
    
    # 测试用例1：有数据的情况
    print("\n1. 测试有数据的情况")
    context_data_1 = [
        {
            "modelname": "AHP958",
            "cpu": "Ryzen 9 8945HS",
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_intent_1 = {
        "intent": "cpu",
        "query": "AHP958的CPU是什麼型號"
    }
    
    has_data_1, missing_info_1 = service._check_data_availability(context_data_1, ["AHP958"], query_intent_1)
    print(f"有数据测试结果: has_data={has_data_1}, missing_info={missing_info_1}")
    
    # 测试用例2：CPU字段为空的情况
    print("\n2. 测试CPU字段为空的情况")
    context_data_2 = [
        {
            "modelname": "AHP958",
            "cpu": "",  # 空字段
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_intent_2 = {
        "intent": "cpu",
        "query": "AHP958的CPU是什麼型號"
    }
    
    has_data_2, missing_info_2 = service._check_data_availability(context_data_2, ["AHP958"], query_intent_2)
    print(f"CPU空字段测试结果: has_data={has_data_2}, missing_info={missing_info_2}")
    
    # 测试用例3：CPU字段为nodata的情况
    print("\n3. 测试CPU字段为nodata的情况")
    context_data_3 = [
        {
            "modelname": "AHP958",
            "cpu": "nodata",  # nodata字段
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_intent_3 = {
        "intent": "cpu",
        "query": "AHP958的CPU是什麼型號"
    }
    
    has_data_3, missing_info_3 = service._check_data_availability(context_data_3, ["AHP958"], query_intent_3)
    print(f"CPU nodata字段测试结果: has_data={has_data_3}, missing_info={missing_info_3}")
    
    # 测试用例4：屏幕查询但lcd字段为空
    print("\n4. 测试屏幕查询但lcd字段为空的情况")
    context_data_4 = [
        {
            "modelname": "AHP958",
            "cpu": "Ryzen 9 8945HS",
            "gpu": "AMD Radeon RX7600M",
            "lcd": "",  # 空字段
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_intent_4 = {
        "intent": "display",
        "query": "AHP958的螢幕規格"
    }
    
    has_data_4, missing_info_4 = service._check_data_availability(context_data_4, ["AHP958"], query_intent_4)
    print(f"屏幕空字段测试结果: has_data={has_data_4}, missing_info={missing_info_4}")
    
    # 测试用例5：多个型号，部分有数据部分没有
    print("\n5. 测试多个型号，部分有数据部分没有")
    context_data_5 = [
        {
            "modelname": "AHP958",
            "cpu": "Ryzen 9 8945HS",
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        },
        {
            "modelname": "AG958",
            "cpu": "",  # 空字段
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_intent_5 = {
        "intent": "cpu",
        "query": "958系列的CPU比較"
    }
    
    has_data_5, missing_info_5 = service._check_data_availability(context_data_5, ["AHP958", "AG958"], query_intent_5)
    print(f"多型号部分空字段测试结果: has_data={has_data_5}, missing_info={missing_info_5}")

def test_fallback_summary_with_data_check():
    """测试备用摘要生成时的数据检查"""
    
    service = SalesAssistantService()
    
    print("\n=== 测试备用摘要生成时的数据检查 ===")
    
    # 测试用例1：有数据的情况
    print("\n1. 测试有数据的情况")
    context_data_1 = [
        {
            "modelname": "AHP958",
            "cpu": "Ryzen 9 8945HS",
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_1 = "AHP958的CPU是什麼型號"
    summary_1 = service._generate_fallback_summary(query_1, context_data_1, ["AHP958"])
    print(f"有数据时的备用摘要: {summary_1}")
    
    # 测试用例2：没有数据的情况
    print("\n2. 测试没有数据的情况")
    context_data_2 = [
        {
            "modelname": "AHP958",
            "cpu": "nodata",
            "gpu": "AMD Radeon RX7600M",
            "lcd": "15.6\" FHD 1920×1080",
            "battery": "80.08Wh",
            "memory": "DDR5-4800"
        }
    ]
    
    query_2 = "AHP958的CPU是什麼型號"
    summary_2 = service._generate_fallback_summary(query_2, context_data_2, ["AHP958"])
    print(f"没有数据时的备用摘要: {summary_2}")

if __name__ == "__main__":
    test_data_availability_check()
    test_fallback_summary_with_data_check() 