import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_two_step_strategy():
    """测试两步骤策略"""
    
    # 创建服务实例
    service = SalesAssistantService()
    
    # 测试用例1：LLM回答完全正确
    print("=== 测试用例1：LLM回答完全正确 ===")
    llm_response_1 = {
        "answer_summary": "958系列的两个型号（958和AHP958）在屏幕规格上完全相同，包括LCD连接器、存储类型和容量、无线支持等。唯一的区别是它们使用的处理器不同：958使用Ryzen 7 8845HS，而AHP958使用Ryzen 9 8945HS。",
        "comparison_table": [
            {
                "feature": "Display Size",
                "958": "15.6\" / 16.1\"",
                "AHP958": "15.6\" / 16.1\""
            },
            {
                "feature": "Resolution",
                "958": "FHD 1920×1080 / QHD 2560×1440",
                "AHP958": "FHD 1920×1080 / QHD 2560×1440"
            }
        ]
    }
    
    target_modelnames_1 = ["958", "AHP958"]
    context_data_1 = [
        {"modelname": "958", "lcd": "15.6\" FHD 1920×1080", "cpu": "Ryzen 7 8845HS"},
        {"modelname": "AHP958", "lcd": "15.6\" FHD 1920×1080", "cpu": "Ryzen 9 8945HS"}
    ]
    
    result_1 = service._process_llm_response_robust(llm_response_1, context_data_1, target_modelnames_1, "請問958系列螢幕規格有何不同")
    print(f"结果1 - answer_summary: {result_1.get('answer_summary', '')}")
    print(f"结果1 - comparison_table长度: {len(result_1.get('comparison_table', []))}")
    
    # 测试用例2：answer_summary正确，comparison_table有问题
    print("\n=== 测试用例2：answer_summary正确，comparison_table有问题 ===")
    llm_response_2 = {
        "answer_summary": "958系列的两个型号（958和AHP958）在屏幕规格上完全相同，包括LCD连接器、存储类型和容量、无线支持等。唯一的区别是它们使用的处理器不同：958使用Ryzen 7 8845HS，而AHP958使用Ryzen 9 8945HS。",
        "comparison_table": [
            {
                "feature": "Display Size",
                "InvalidModel": "15.6\" / 16.1\"",  # 错误的模型名称
                "AHP958": "15.6\" / 16.1\""
            }
        ]
    }
    
    result_2 = service._process_llm_response_robust(llm_response_2, context_data_1, target_modelnames_1, "請問958系列螢幕規格有何不同")
    print(f"结果2 - answer_summary: {result_2.get('answer_summary', '')}")
    print(f"结果2 - comparison_table长度: {len(result_2.get('comparison_table', []))}")
    
    # 测试用例3：answer_summary有问题，comparison_table正确
    print("\n=== 测试用例3：answer_summary有问题，comparison_table正确 ===")
    llm_response_3 = {
        "answer_summary": "HP品牌的两个型号在屏幕规格上完全相同。",  # 包含无效品牌
        "comparison_table": [
            {
                "feature": "Display Size",
                "958": "15.6\" / 16.1\"",
                "AHP958": "15.6\" / 16.1\""
            }
        ]
    }
    
    result_3 = service._process_llm_response_robust(llm_response_3, context_data_1, target_modelnames_1, "請問958系列螢幕規格有何不同")
    print(f"结果3 - answer_summary: {result_3.get('answer_summary', '')}")
    print(f"结果3 - comparison_table长度: {len(result_3.get('comparison_table', []))}")
    
    # 测试用例4：两者都有问题
    print("\n=== 测试用例4：两者都有问题 ===")
    llm_response_4 = {
        "answer_summary": "HP品牌的两个型号在屏幕规格上完全相同。",  # 包含无效品牌
        "comparison_table": [
            {
                "feature": "Display Size",
                "InvalidModel": "15.6\" / 16.1\"",  # 错误的模型名称
                "AHP958": "15.6\" / 16.1\""
            }
        ]
    }
    
    result_4 = service._process_llm_response_robust(llm_response_4, context_data_1, target_modelnames_1, "請問958系列螢幕規格有何不同")
    print(f"结果4 - answer_summary: {result_4.get('answer_summary', '')}")
    print(f"结果4 - comparison_table长度: {len(result_4.get('comparison_table', []))}")

def test_separated_validation():
    """测试分离验证方法"""
    
    service = SalesAssistantService()
    
    print("\n=== 测试分离验证方法 ===")
    
    # 测试分离验证
    llm_response = {
        "answer_summary": "958系列的两个型号（958和AHP958）在屏幕规格上完全相同。",
        "comparison_table": [
            {
                "feature": "Display Size",
                "958": "15.6\" / 16.1\"",
                "AHP958": "15.6\" / 16.1\""
            }
        ]
    }
    
    target_modelnames = ["958", "AHP958"]
    
    validation_result = service._validate_llm_response_separated(llm_response, target_modelnames)
    print(f"分离验证结果: {validation_result}")
    print(f"summary_valid: {validation_result['summary_valid']}")
    print(f"table_valid: {validation_result['table_valid']}")

if __name__ == "__main__":
    test_two_step_strategy()
    test_separated_validation() 