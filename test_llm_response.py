import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_llm_response_processing():
    """测试LLM回答处理流程"""
    
    # 模拟LLM回答
    llm_response = {
        "answer_summary": "Yes, the APX819 FP7R2 supports dual-channel RAM configuration. This is possible due to the presence of two SO-DIMM slots in the system, each capable of supporting a single channel of memory.",
        "comparison_table": []
    }
    
    # 模拟目标模型名称
    target_modelnames = ["APX819: FP7R2"]
    
    # 模拟上下文数据
    context_list_of_dicts = [
        {
            "modelname": "APX819: FP7R2",
            "cpu": "Ryzen™ 7 7735HS",
            "gpu": "AMD Radeon™ 680M",
            "memory": "DDR5-4800",
            "storage": "M.2 PCIe 4.0 NVMe SSD",
            "battery": "50Wh"
        }
    ]
    
    # 创建服务实例
    service = SalesAssistantService()
    
    print("=== 测试LLM回答验证 ===")
    # 测试验证逻辑
    is_valid = service._validate_llm_response(llm_response, target_modelnames)
    print(f"LLM回答验证结果: {is_valid}")
    
    print("\n=== 测试LLM回答处理 ===")
    if is_valid:
        # 测试处理逻辑
        processed_response = service._process_llm_response(llm_response, context_list_of_dicts, target_modelnames)
        print(f"处理后的answer_summary: {processed_response.get('answer_summary', '')}")
        print(f"处理后的comparison_table: {processed_response.get('comparison_table', '')}")
        print(f"处理后的beautiful_table: {processed_response.get('beautiful_table', '')}")
    else:
        print("LLM回答验证失败，使用备用响应")
        fallback_response = service._generate_fallback_response("APX819: FP7R2 dual channel RAM", context_list_of_dicts, target_modelnames)
        print(f"备用响应的answer_summary: {fallback_response.get('answer_summary', '')}")

def test_ahp_model_validation():
    """测试包含AHP模型名称的验证"""
    
    # 模拟包含AHP模型名称的LLM回答
    llm_response = {
        "answer_summary": "958系列的两个型号（958和AHP958）在屏幕规格上完全相同，包括LCD连接器、存储类型和容量、无线支持等。唯一的区别是它们使用的处理器不同：958使用Ryzen 7 8845HS，而AHP958使用Ryzen 9 8945HS。",
        "comparison_table": []
    }
    
    # 模拟目标模型名称
    target_modelnames = ["AHP958"]
    
    # 创建服务实例
    service = SalesAssistantService()
    
    print("\n=== 测试AHP模型名称验证 ===")
    # 测试验证逻辑
    is_valid = service._validate_llm_response(llm_response, target_modelnames)
    print(f"AHP模型名称验证结果: {is_valid}")
    
    if is_valid:
        print("✅ AHP模型名称验证通过，不会误认为HP品牌")
    else:
        print("❌ AHP模型名称验证失败，可能误认为HP品牌")

if __name__ == "__main__":
    test_llm_response_processing()
    test_ahp_model_validation() 