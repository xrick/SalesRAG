import asyncio
import sys
import os

# 添加路徑
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sales_rag_app'))

from libs.services.sales_assistant.service import SalesAssistantService

async def test_modeltype_check():
    """測試modeltype檢查功能"""
    service = SalesAssistantService()
    
    # 測試案例
    test_cases = [
        "比較 958 系列的 CPU 性能",  # 只有modeltype
        "比較 819 和 839 系列的記憶體",  # 兩個modeltype，應該只取第一個
        "比較 AB819-S: FP6 和 AG958 的 CPU 性能",  # 只有modelname
        "比較 958 系列和 AB819-S: FP6 的電池續航力",  # 同時有modeltype和modelname，應該以modeltype為主
        "哪個筆電比較好？",  # 沒有指定任何型號
        "比較筆電性能",  # 沒有指定任何型號
        "839 系列的散熱設計如何？",  # 只有modeltype
        "AMD819: FT6 和 APX839 哪個更適合遊戲？"  # 只有modelname
    ]
    
    print("=== 測試 modeltype 和 modelname 檢查功能 ===\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"測試案例 {i}: {query}")
        
        # 檢查是否包含modeltype
        contains_modeltype, found_modeltypes = service._check_query_contains_modeltype(query)
        
        # 檢查是否包含modelname
        contains_modelname, found_modelnames = service._check_query_contains_modelname(query)
        
        print(f"  包含modeltype: {contains_modeltype}")
        print(f"  找到的modeltype: {found_modeltypes}")
        print(f"  包含modelname: {contains_modelname}")
        print(f"  找到的modelname: {found_modelnames}")
        
        # 判斷處理邏輯
        if contains_modeltype and contains_modelname:
            print(f"  處理邏輯: 同時包含modeltype和modelname，以modeltype為主")
        elif contains_modeltype:
            print(f"  處理邏輯: 只有modeltype")
        elif contains_modelname:
            print(f"  處理邏輯: 只有modelname")
        else:
            print(f"  處理邏輯: 既沒有modeltype也沒有modelname")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_modeltype_check()) 