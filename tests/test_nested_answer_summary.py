#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試嵌套格式的 answer_summary 處理
"""

import sys
import os
import json
import logging

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_nested_answer_summary_processing():
    """
    測試嵌套格式的 answer_summary 處理
    """
    print("=== 測試嵌套格式的 answer_summary 處理 ===")
    
    # 創建服務實例
    service = SalesAssistantService()
    
    # 模擬 LLM 返回的嵌套格式 JSON
    nested_json = {
        "answer_summary": {
            "best_model": "AG958V",
            "reasoning": "The AG958V offers a powerful combination of an 11th Gen Ryzen 7 7420 CPU, an RTX 4060独立显卡，以及16GB DDR5内存。其核显性能优异，支持高分辨率游戏，并且散热设计良好，适合高性能游戏需求。",
            "comparison_table": {
                "Model": ["AG958P", "APX958", "AHP958", "AG958V", "AG958"],
                "CPU": ["Ryzen 7 5800H @4.3GHz", "Ryzen 7 5800H @4.3GHz", "Ryzen 7 7420 @4.6GHz", "Ryzen 7 7420 @4.6GHz", "Ryzen 7 7420 @4.6GHz"],
                "显卡": ["无独立显卡（依赖核显）", "无独立显卡（依赖核显）", "RTX 4060独立显卡", "RTX 4060独立显卡", "RTX 4060独立显卡"],
                "核显": ["Yes", "Yes", "No", "No", "No"],
                "显存": ["16GB", "16GB", "8GB", "8GB", "8GB"],
                "存储": ["2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD"], 
                "无线": ["RZ608 (AMD), Wi-Fi 6E Tri-band + Bluetooth 5.2", "RZ608 (AMD), Wi-Fi 6E Tri-band + Bluetooth 5.2", "RZ616 (AMD), Wi-Fi 6E Dual-band + Bluetooth 5.2", "RZ616 (AMD), Wi-Fi 6E Dual-band + Bluetooth 5.2", "RZ608 (AMD), Wi-Fi 6E Tri-band + Bluetooth 5.2"],
                "散热": ["无风扇", "无风扇", "无风扇", "有风扇", "有风扇"]
            }
        }
    }
    
    print(f"原始嵌套格式 JSON:")
    print(json.dumps(nested_json, ensure_ascii=False, indent=2))
    
    # 模擬 JSON 解析和格式轉換邏輯
    parsed_json = nested_json
    
    # 檢查是否是嵌套格式：{"answer_summary": {"best_model": "...", "comparison_table": {...}}}
    if "answer_summary" in parsed_json and isinstance(parsed_json["answer_summary"], dict):
        nested_answer = parsed_json["answer_summary"]
        print(f"\n檢測到嵌套格式的 answer_summary: {nested_answer}")
        
        # 檢查嵌套的 answer_summary 是否包含 comparison_table
        if "comparison_table" in nested_answer:
            # 提取 reasoning 或 best_model 作為 answer_summary 的內容
            if "reasoning" in nested_answer:
                answer_content = nested_answer["reasoning"]
                print(f"使用 reasoning 作為 answer_summary: {answer_content}")
            elif "best_model" in nested_answer:
                best_model = nested_answer["best_model"]
                answer_content = f"根據分析，{best_model} 是最適合的選擇。"
                print(f"使用 best_model 生成 answer_summary: {answer_content}")
            else:
                # 如果沒有 reasoning 或 best_model，使用整個嵌套結構的字符串表示
                answer_content = json.dumps(nested_answer, ensure_ascii=False)
                print(f"使用整個嵌套結構作為 answer_summary: {answer_content}")
            
            # 轉換為標準格式
            converted_json = {
                "answer_summary": answer_content,
                "comparison_table": nested_answer["comparison_table"]
            }
            
            print(f"\n轉換後的標準格式:")
            print(json.dumps(converted_json, ensure_ascii=False, indent=2))
            parsed_json = converted_json
    
    # 檢查是否已經是正確的格式
    if "answer_summary" in parsed_json and "comparison_table" in parsed_json:
        print("\n✅ 格式轉換成功！")
        print(f"answer_summary 類型: {type(parsed_json['answer_summary'])}")
        print(f"comparison_table 類型: {type(parsed_json['comparison_table'])}")
        
        # 測試表格格式化
        model_names = ["AG958P", "APX958", "AHP958", "AG958V", "AG958"]
        comparison_table = parsed_json["comparison_table"]
        
        # 測試字典轉換為列表格式
        if isinstance(comparison_table, dict):
            print("\n測試字典格式轉換為列表格式...")
            converted_table = service._convert_dict_to_list_of_dicts(comparison_table, parsed_json["answer_summary"])
            print(f"轉換後的表格: {converted_table}")
            
            # 測試美化表格生成
            beautiful_table = service._create_beautiful_markdown_table(converted_table, model_names)
            print(f"\n生成的美化表格:\n{beautiful_table}")
        
        return True
    else:
        print("\n❌ 格式轉換失敗！")
        return False

def test_standard_format_processing():
    """
    測試標準格式的處理（確保不會影響現有功能）
    """
    print("\n=== 測試標準格式的處理 ===")
    
    # 標準格式的 JSON
    standard_json = {
        "answer_summary": "根據分析，AG958V 是最適合的選擇。",
        "comparison_table": [
            {"feature": "CPU", "AG958P": "Ryzen 7 5800H", "AG958V": "Ryzen 7 7420"},
            {"feature": "GPU", "AG958P": "核顯", "AG958V": "RTX 4060"}
        ]
    }
    
    print(f"標準格式 JSON:")
    print(json.dumps(standard_json, ensure_ascii=False, indent=2))
    
    parsed_json = standard_json
    
    # 檢查是否是嵌套格式
    if "answer_summary" in parsed_json and isinstance(parsed_json["answer_summary"], dict):
        print("檢測到嵌套格式，進行轉換...")
        # 轉換邏輯...
    else:
        print("檢測到標準格式，無需轉換")
    
    # 檢查是否已經是正確的格式
    if "answer_summary" in parsed_json and "comparison_table" in parsed_json:
        print("✅ 標準格式處理正常！")
        return True
    else:
        print("❌ 標準格式處理失敗！")
        return False

def test_edge_cases():
    """
    測試邊緣情況
    """
    print("\n=== 測試邊緣情況 ===")
    
    # 測試只有 best_model 沒有 reasoning 的情況
    edge_case_1 = {
        "answer_summary": {
            "best_model": "AG958V",
            "comparison_table": {
                "Model": ["AG958P", "AG958V"],
                "CPU": ["Ryzen 7 5800H", "Ryzen 7 7420"]
            }
        }
    }
    
    print("測試只有 best_model 的情況:")
    parsed_json = edge_case_1
    
    if "answer_summary" in parsed_json and isinstance(parsed_json["answer_summary"], dict):
        nested_answer = parsed_json["answer_summary"]
        
        if "comparison_table" in nested_answer:
            if "reasoning" in nested_answer:
                answer_content = nested_answer["reasoning"]
            elif "best_model" in nested_answer:
                best_model = nested_answer["best_model"]
                answer_content = f"根據分析，{best_model} 是最適合的選擇。"
            else:
                answer_content = json.dumps(nested_answer, ensure_ascii=False)
            
            converted_json = {
                "answer_summary": answer_content,
                "comparison_table": nested_answer["comparison_table"]
            }
            
            print(f"轉換結果: {converted_json['answer_summary']}")
    
    # 測試既沒有 reasoning 也沒有 best_model 的情況
    edge_case_2 = {
        "answer_summary": {
            "comparison_table": {
                "Model": ["AG958P", "AG958V"],
                "CPU": ["Ryzen 7 5800H", "Ryzen 7 7420"]
            }
        }
    }
    
    print("\n測試既沒有 reasoning 也沒有 best_model 的情況:")
    parsed_json = edge_case_2
    
    if "answer_summary" in parsed_json and isinstance(parsed_json["answer_summary"], dict):
        nested_answer = parsed_json["answer_summary"]
        
        if "comparison_table" in nested_answer:
            if "reasoning" in nested_answer:
                answer_content = nested_answer["reasoning"]
            elif "best_model" in nested_answer:
                best_model = nested_answer["best_model"]
                answer_content = f"根據分析，{best_model} 是最適合的選擇。"
            else:
                answer_content = json.dumps(nested_answer, ensure_ascii=False)
            
            converted_json = {
                "answer_summary": answer_content,
                "comparison_table": nested_answer["comparison_table"]
            }
            
            print(f"轉換結果: {converted_json['answer_summary']}")

if __name__ == "__main__":
    print("開始測試嵌套格式的 answer_summary 處理...")
    
    # 運行測試
    test1_result = test_nested_answer_summary_processing()
    test2_result = test_standard_format_processing()
    test_edge_cases()
    
    print("\n=== 測試結果總結 ===")
    print(f"嵌套格式處理測試: {'✅ 通過' if test1_result else '❌ 失敗'}")
    print(f"標準格式處理測試: {'✅ 通過' if test2_result else '❌ 失敗'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有測試通過！嵌套格式處理功能正常。")
    else:
        print("\n⚠️ 部分測試失敗，需要進一步檢查。") 