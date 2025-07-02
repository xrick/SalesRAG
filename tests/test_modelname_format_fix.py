#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 modelname 格式修正
驗證 LLM 輸出的 modelname 格式能夠正確轉換為 list of dicts 格式
"""

import json
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_modelname_format_conversion():
    """測試 modelname 格式轉換"""
    print("=== 測試 modelname 格式轉換修正 ===")
    
    # 創建服務實例
    service = SalesAssistantService()
    
    # 模擬 LLM 輸出的 modelname 格式
    test_comparison_table = {
        'modelname': ['APX958', 'AHP958'],
        'cpu': ['Ryzen 7 5800HS (6C/12T, 4.3GHz/3.5GHz, TDP: 40W) - APX958', 'Ryzen 9 7945HS (8C/16T, 5.0GHz/3.5GHz, TDP: 45W) - AHP958'],
        'gpu': ['AMD Radeon™ RX 7720 XT (P1), 8GB GDDR6, 100W Smart Shift - APX958', 'AMD Radeon™ RX 7730 XT (P1), 8GB GDDR6, 120W Smart Shift - AHP958'],
        'ram': ['16GB', '32GB × 2'],
        'storage': ['2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD, up to 8TB (2 × 1TB) - APX958', '2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD, up to 8TB (2 × 1TB) - AHP958'],
        'battery': ['Type: Lithium-ion polymer battery - APX958', 'Type: Lithium-ion polymer battery - AHP958'],
        'os': ['Windows 11 SV2 (23H2), Support Modern Standby - APX958', 'Windows 11 SV2 (23H2), Support Modern Standby - AHP958'],
        'wifislot': ['1 × M.2 2230 WiFi 6E + BT5.2 - APX958', '1 × M.2 2230 WiFi 6E + BT5.2 - AHP958']
    }
    
    print(f"原始格式 (modelname):")
    print(json.dumps(test_comparison_table, ensure_ascii=False, indent=2))
    
    # 測試轉換
    converted_table = service._convert_dict_to_list_of_dicts(test_comparison_table)
    
    print(f"\n轉換後的格式 (list of dicts):")
    for row in converted_table:
        print(f"  {row}")
    
    # 驗證轉換結果
    expected_features = ['cpu', 'gpu', 'ram', 'storage', 'battery', 'os', 'wifislot']
    expected_models = ['APX958', 'AHP958']
    
    print(f"\n=== 驗證轉換結果 ===")
    
    # 檢查特徵數量
    if len(converted_table) == len(expected_features):
        print(f"✅ 特徵數量正確: {len(converted_table)}")
    else:
        print(f"❌ 特徵數量錯誤: 期望 {len(expected_features)}, 實際 {len(converted_table)}")
    
    # 檢查每個特徵
    for i, feature in enumerate(expected_features):
        if i < len(converted_table) and converted_table[i]['feature'] == feature:
            print(f"✅ 特徵 {feature} 正確")
        else:
            print(f"❌ 特徵 {feature} 錯誤")
    
    # 檢查模型名稱清理
    for row in converted_table:
        for model in expected_models:
            value = row.get(model, '')
            if f" - {model}" not in value:
                print(f"✅ 模型名稱 {model} 清理正確: {value}")
            else:
                print(f"❌ 模型名稱 {model} 清理失敗: {value}")
    
    # 測試表格格式化
    print(f"\n=== 測試表格格式化 ===")
    try:
        beautiful_table = service._create_beautiful_markdown_table(converted_table, expected_models)
        print("✅ 表格格式化成功")
        print(f"生成的表格:\n{beautiful_table}")
    except Exception as e:
        print(f"❌ 表格格式化失敗: {e}")
    
    # 測試完整流程
    print(f"\n=== 測試完整流程 ===")
    test_parsed_json = {
        'answer_summary': '根據比較，APX958 和 AHP958 在 CPU 和 GPU 方面有顯著差異。',
        'comparison_table': test_comparison_table
    }
    
    target_modelnames = ['APX958', 'AHP958']
    
    try:
        processed_response = service._process_llm_response_robust(
            test_parsed_json,
            [],  # 空的 context_list_of_dicts
            target_modelnames,
            '比較 APX958 和 AHP958 的規格'
        )
        
        print("✅ 完整流程處理成功")
        print(f"answer_summary: {processed_response.get('answer_summary', 'N/A')}")
        print(f"comparison_table 類型: {type(processed_response.get('comparison_table', 'N/A'))}")
        print(f"beautiful_table 長度: {len(processed_response.get('beautiful_table', ''))}")
        
    except Exception as e:
        print(f"❌ 完整流程處理失敗: {e}")
        import traceback
        traceback.print_exc()

def test_validation_with_modelname():
    """測試 modelname 格式的驗證"""
    print("\n=== 測試 modelname 格式驗證 ===")
    
    service = SalesAssistantService()
    
    # 測試驗證邏輯
    test_comparison_table = {
        'modelname': ['APX958', 'AHP958'],
        'cpu': ['Ryzen 7 5800HS - APX958', 'Ryzen 9 7945HS - AHP958']
    }
    
    target_modelnames = ['APX958', 'AHP958']
    
    # 測試分離驗證
    validation_result = service._validate_llm_response_separated(
        {'answer_summary': '測試', 'comparison_table': test_comparison_table},
        target_modelnames
    )
    
    print(f"驗證結果: {validation_result}")
    
    if validation_result['table_valid']:
        print("✅ modelname 格式驗證通過")
    else:
        print("❌ modelname 格式驗證失敗")

if __name__ == "__main__":
    test_modelname_format_conversion()
    test_validation_with_modelname()
    print("\n🎉 所有測試完成！") 