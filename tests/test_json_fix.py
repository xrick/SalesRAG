#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 JSON 修復功能
驗證系統能夠正確處理 LLM 返回的不完整或格式不正確的 JSON
"""

import sys
import os
import json

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_json_fix_functions():
    """測試 JSON 修復功能"""
    print("=== 測試 JSON 修復功能 ===")
    
    # 創建服務實例
    service = SalesAssistantService()
    
    # 測試案例 1: 有多餘內容的 JSON
    test_json_1 = '''
    {
        "answer_summary": "根據比較，APX958 和 AHP958 在 CPU 和 GPU 方面有顯著差異。",
        "comparison_table": [
            {"feature": "CPU", "APX958": "Ryzen 7 5800HS", "AHP958": "Ryzen 9 7945HS"},
            {"feature": "GPU", "APX958": "AMD Radeon RX 7720 XT", "AHP958": "AMD Radeon RX 7730 XT"}
        ]
    }
    }
    這裡是額外的內容，不應該被包含在 JSON 中。
    '''
    
    print(f"測試案例 1 - 原始 JSON (有多餘內容):")
    print(test_json_1)
    
    fixed_json_1 = service._fix_json_format(test_json_1)
    print(f"\n修復後的 JSON:")
    print(fixed_json_1)
    
    try:
        parsed_1 = json.loads(fixed_json_1)
        print("✅ 測試案例 1 成功：JSON 修復並解析成功")
        print(f"answer_summary: {parsed_1.get('answer_summary', 'N/A')}")
        print(f"comparison_table 長度: {len(parsed_1.get('comparison_table', []))}")
    except Exception as e:
        print(f"❌ 測試案例 1 失敗：{e}")
    
    # 測試案例 2: 有引號問題的 JSON
    test_json_2 = '''
    {
        "answer_summary": "根據比較，APX958 和 AHP958 在 CPU 和 GPU 方面有顯著差異。例如："APX958 適合一般使用，AHP958 適合遊戲。"",
        "comparison_table": [
            {"feature": "CPU", "APX958": "Ryzen 7 5800HS", "AHP958": "Ryzen 9 7945HS"}
        ]
    }
    '''
    
    print(f"\n測試案例 2 - 原始 JSON (有引號問題):")
    print(test_json_2)
    
    fixed_json_2 = service._fix_json_format(test_json_2)
    print(f"\n修復後的 JSON:")
    print(fixed_json_2)
    
    try:
        parsed_2 = json.loads(fixed_json_2)
        print("✅ 測試案例 2 成功：引號問題修復成功")
        print(f"answer_summary: {parsed_2.get('answer_summary', 'N/A')}")
    except Exception as e:
        print(f"❌ 測試案例 2 失敗：{e}")
    
    # 測試案例 3: 有多餘逗號的 JSON
    test_json_3 = '''
    {
        "answer_summary": "測試內容",
        "comparison_table": [
            {"feature": "CPU", "APX958": "Ryzen 7", "AHP958": "Ryzen 9"},
        ],
    }
    '''
    
    print(f"\n測試案例 3 - 原始 JSON (有多餘逗號):")
    print(test_json_3)
    
    fixed_json_3 = service._fix_json_format(test_json_3)
    print(f"\n修復後的 JSON:")
    print(fixed_json_3)
    
    try:
        parsed_3 = json.loads(fixed_json_3)
        print("✅ 測試案例 3 成功：多餘逗號修復成功")
    except Exception as e:
        print(f"❌ 測試案例 3 失敗：{e}")

def test_partial_json_extraction():
    """測試部分 JSON 提取功能"""
    print(f"\n=== 測試部分 JSON 提取功能 ===")
    
    service = SalesAssistantService()
    
    # 測試案例：不完整的 JSON
    incomplete_json = '''
    {
        "answer_summary": "根據比較，APX958 和 AHP958 在 CPU 和 GPU 方面有顯著差異。",
        "comparison_table": [
            {"feature": "CPU", "APX958": "Ryzen 7 5800HS", "AHP958": "Ryzen 9 7945HS"},
            {"feature": "GPU", "APX958": "AMD Radeon RX 7720 XT", "AHP958": "AMD Radeon RX 7730 XT"}
        ]
    }
    "extra_field": "這個欄位沒有正確的格式"
    '''
    
    print(f"測試案例 - 不完整的 JSON:")
    print(incomplete_json)
    
    extracted = service._extract_partial_json(incomplete_json)
    
    if extracted:
        print("✅ 部分 JSON 提取成功")
        print(f"提取的內容: {extracted}")
        print(f"answer_summary: {extracted.get('answer_summary', 'N/A')}")
        print(f"comparison_table 長度: {len(extracted.get('comparison_table', []))}")
    else:
        print("❌ 部分 JSON 提取失敗")

def test_production_error_scenario():
    """測試生產環境錯誤場景"""
    print(f"\n=== 測試生產環境錯誤場景 ===")
    
    service = SalesAssistantService()
    
    # 模擬生產環境中的錯誤 JSON
    production_json = '''
    {
        "answer_summary": "根据实际数据，AG958P 系列包含 5 个游戏笔记型电脑型号，各有不同的性能配置。",
        "comparison_table": [
            {"feature": "CPU Model", "AG958P": "Ryzen™ 5 7535HS", "APX958": "Ryzen™ 5 7640HS", "AG958": "Ryzen™ 5 6600H", "AHP958": "Ryzen™ 5 8645HS", "AG958V": "Ryzen™ 5 6600H"},
            {"feature": "GPU Model", "AG958P": "AMD Radeon™ RX7600M", "APX958": "AMD Radeon™ RX7600M", "AG958": "AMD Radeon™ RX6550M", "AHP958": "AMD Radeon™ RX7600M", "AG958V": "AMD Radeon™ RX6500M"},
            {"feature": "Thermal Design", "AG958P": "150W", "APX958": "150W", "AG958": "110W", "AHP958": "150W", "AG958V": "70W"},
            {"feature": "Memory Type", "AG958P": "DDR5", "APX958": "DDR5", "AG958": "DDR5", "AHP958": "DDR5", "AG958V": "DDR5"},
            {"feature": "Storage Type", "AG958P": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "APX958": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "AG958": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "AHP958": "M.2 2280 PCIe Gen4 (Lane 4) NVMe", "AG958V": "M.2 2280 PCIe Gen4 (Lane 4) NVMe"}
        ]
    }
    }
    這裡是額外的內容，導致 JSON 解析失敗
    '''
    
    print(f"生產環境錯誤 JSON:")
    print(production_json)
    
    # 測試修復
    fixed_json = service._fix_json_format(production_json)
    print(f"\n修復後的 JSON:")
    print(fixed_json)
    
    try:
        parsed = json.loads(fixed_json)
        print("✅ 生產環境錯誤修復成功")
        print(f"answer_summary: {parsed.get('answer_summary', 'N/A')}")
        print(f"comparison_table 長度: {len(parsed.get('comparison_table', []))}")
        
        # 測試表格格式化
        comparison_table = parsed.get('comparison_table', [])
        if comparison_table:
            model_names = []
            for row in comparison_table:
                for key in row.keys():
                    if key != 'feature' and key not in model_names:
                        model_names.append(key)
            
            beautiful_table = service._create_beautiful_markdown_table(comparison_table, model_names)
            print(f"\n生成的表格長度: {len(beautiful_table)}")
            print("✅ 表格格式化成功")
        
    except Exception as e:
        print(f"❌ 生產環境錯誤修復失敗：{e}")
        
        # 嘗試部分提取
        extracted = service._extract_partial_json(production_json)
        if extracted:
            print("✅ 部分提取成功")
            print(f"提取的內容: {extracted}")
        else:
            print("❌ 部分提取也失敗")

if __name__ == "__main__":
    test_json_fix_functions()
    test_partial_json_extraction()
    test_production_error_scenario()
    print("\n🎉 所有 JSON 修復測試完成！") 