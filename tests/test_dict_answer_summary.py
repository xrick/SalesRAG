#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 LLM 返回字典格式 answer_summary 的情況
驗證修復是否有效
"""

import json
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_dict_answer_summary():
    """測試字典格式的 answer_summary 處理"""
    print("=== 測試字典格式 answer_summary 處理 ===")
    
    # 創建服務實例
    service = SalesAssistantService()
    
    # 模擬 LLM 返回的字典格式 answer_summary
    test_cases = [
        {
            "name": "遊戲推薦案例",
            "parsed_json": {
                "answer_summary": {
                    "best_model_for_gameing": "AG958P",
                    "reasoning": "AG958P has an RTX 4070 Ti GPU, which provides excellent performance for modern games. It also supports up to 1440p resolution and has four connected displays, making it ideal for gaming."
                },
                "comparison_table": [
                    {"feature": "CPU Model", "AG958P": "Ryzen™ 5 7535HS", "AG958V": "Ryzen™ 5 6600H"},
                    {"feature": "GPU Model", "AG958P": "AMD Radeon™ RX7600M", "AG958V": "AMD Radeon™ RX6500M"}
                ]
            },
            "target_modelnames": ["AG958P", "AG958V", "AHP958", "APX958", "AG958"]
        },
        {
            "name": "字符串格式案例",
            "parsed_json": {
                "answer_summary": "根據比較，AG958P 是最適合遊戲的型號，因為它配備了強大的 GPU 和高效能的 CPU。",
                "comparison_table": [
                    {"feature": "CPU Model", "AG958P": "Ryzen™ 5 7535HS", "AG958V": "Ryzen™ 5 6600H"}
                ]
            },
            "target_modelnames": ["AG958P", "AG958V"]
        },
        {
            "name": "包含無效 GPU 型號案例",
            "parsed_json": {
                "answer_summary": {
                    "best_model": "AG958P",
                    "reasoning": "AG958P has an RTX 3060 GPU, which is not available in our product line."
                },
                "comparison_table": []
            },
            "target_modelnames": ["AG958P", "AG958V"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 測試案例: {test_case['name']}")
        print(f"   輸入: {json.dumps(test_case['parsed_json'], ensure_ascii=False, indent=2)}")
        
        try:
            # 測試分離驗證
            validation_result = service._validate_llm_response_separated(
                test_case['parsed_json'], 
                test_case['target_modelnames']
            )
            
            print(f"   驗證結果:")
            print(f"   - summary_valid: {validation_result['summary_valid']}")
            print(f"   - table_valid: {validation_result['table_valid']}")
            print(f"   - answer_summary: {validation_result['answer_summary']}")
            print(f"   - comparison_table: {validation_result['comparison_table']}")
            
            # 測試兩步驟策略處理
            context_list_of_dicts = [
                {"modelname": "AG958P", "cpu": "Ryzen™ 5 7535HS", "gpu": "AMD Radeon™ RX7600M"},
                {"modelname": "AG958V", "cpu": "Ryzen™ 5 6600H", "gpu": "AMD Radeon™ RX6500M"}
            ]
            
            processed_response = service._process_llm_response_robust(
                test_case['parsed_json'],
                context_list_of_dicts,
                test_case['target_modelnames'],
                "測試查詢"
            )
            
            print(f"   處理結果:")
            print(f"   - answer_summary: {processed_response.get('answer_summary', 'N/A')}")
            print(f"   - comparison_table: {len(processed_response.get('comparison_table', []))} 行")
            print(f"   - beautiful_table: {'已生成' if processed_response.get('beautiful_table') else '未生成'}")
            
        except Exception as e:
            print(f"   錯誤: {e}")
            import traceback
            traceback.print_exc()

def test_real_scenario():
    """測試真實場景"""
    print("\n=== 測試真實場景 ===")
    
    # 模擬用戶查詢 "比較958系列哪款筆記型電腦更適合遊戲？"
    query = "比較958系列哪款筆記型電腦更適合遊戲？"
    
    # 模擬 LLM 返回的 JSON
    llm_response = {
        "answer_summary": {
            "best_model_for_gameing": "AG958P",
            "reasoning": "AG958P has an RTX 4070 Ti GPU, which provides excellent performance for modern games. It also supports up to 1440p resolution and has four connected displays, making it ideal for gaming."
        },
        "comparison_table": [
            {"feature": "CPU Model", "AG958P": "Ryzen™ 5 7535HS", "AG958V": "Ryzen™ 5 6600H", "AHP958": "Ryzen™ 5 8645HS", "APX958": "Ryzen™ 5 7640HS", "AG958": "Ryzen™ 5 6600H"},
            {"feature": "GPU Model", "AG958P": "AMD Radeon™ RX7600M", "AG958V": "AMD Radeon™ RX6500M", "AHP958": "AMD Radeon™ RX7600M", "APX958": "AMD Radeon™ RX7600M", "AG958": "AMD Radeon™ RX6550M"},
            {"feature": "Memory Type", "AG958P": "DDR5", "AG958V": "DDR5", "AHP958": "DDR5", "APX958": "DDR5", "AG958": "DDR5"},
            {"feature": "Storage Type", "AG958P": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "AG958V": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "AHP958": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "APX958": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "AG958": "M.2 2280 PCIe Gen4 (Lane 4) NVMe"},
            {"feature": "Battery Capacity", "AG958P": "80.08Wh", "AG958V": "80.08Wh", "AHP958": "80.08Wh", "APX958": "80.08Wh", "AG958": "80.08Wh"}
        ]
    }
    
    target_modelnames = ["AG958P", "AG958V", "AHP958", "APX958", "AG958"]
    
    # 模擬上下文數據
    context_list_of_dicts = [
        {"modelname": "AG958P", "cpu": "Ryzen™ 5 7535HS", "gpu": "AMD Radeon™ RX7600M", "memory": "DDR5", "storage": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "battery": "80.08Wh"},
        {"modelname": "AG958V", "cpu": "Ryzen™ 5 6600H", "gpu": "AMD Radeon™ RX6500M", "memory": "DDR5", "storage": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "battery": "80.08Wh"},
        {"modelname": "AHP958", "cpu": "Ryzen™ 5 8645HS", "gpu": "AMD Radeon™ RX7600M", "memory": "DDR5", "storage": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "battery": "80.08Wh"},
        {"modelname": "APX958", "cpu": "Ryzen™ 5 7640HS", "gpu": "AMD Radeon™ RX7600M", "memory": "DDR5", "storage": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "battery": "80.08Wh"},
        {"modelname": "AG958", "cpu": "Ryzen™ 5 6600H", "gpu": "AMD Radeon™ RX6550M", "memory": "DDR5", "storage": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "battery": "80.08Wh"}
    ]
    
    service = SalesAssistantService()
    
    try:
        print(f"查詢: {query}")
        print(f"目標型號: {target_modelnames}")
        
        # 測試分離驗證
        validation_result = service._validate_llm_response_separated(llm_response, target_modelnames)
        print(f"\n驗證結果:")
        print(f"- summary_valid: {validation_result['summary_valid']}")
        print(f"- table_valid: {validation_result['table_valid']}")
        
        # 測試兩步驟策略處理
        processed_response = service._process_llm_response_robust(
            llm_response,
            context_list_of_dicts,
            target_modelnames,
            query
        )
        
        print(f"\n處理結果:")
        print(f"- answer_summary: {processed_response.get('answer_summary', 'N/A')}")
        print(f"- comparison_table 行數: {len(processed_response.get('comparison_table', []))}")
        print(f"- beautiful_table 長度: {len(processed_response.get('beautiful_table', ''))}")
        
        # 檢查是否成功生成回應
        if processed_response.get('answer_summary') and processed_response.get('comparison_table'):
            print("✓ 成功生成回應")
        else:
            print("✗ 回應生成失敗")
            
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dict_answer_summary()
    test_real_scenario() 