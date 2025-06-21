import asyncio
import sys
import os

# 添加路徑
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sales_rag_app'))

from libs.services.sales_assistant.service import SalesAssistantService

async def test_modelname_check():
    """測試modelname檢查功能"""
    service = SalesAssistantService()
    
    # 測試案例
    test_cases = [
        "比較 AB819-S: FP6 和 AG958 的 CPU 性能",
        "AG958P 的記憶體規格是什麼？",
        "哪個筆電比較好？",  # 沒有指定modelname
        "比較筆電性能",  # 沒有指定modelname
        "AB819-S: FP6 的電池續航力如何？",
        "AMD819: FT6 和 APX839 哪個更適合遊戲？"
    ]
    
    print("=== 測試 modelname 檢查功能 ===\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"測試案例 {i}: {query}")
        
        # 檢查是否包含modelname
        contains_modelname, found_modelnames = service._check_query_contains_modelname(query)
        
        print(f"  包含modelname: {contains_modelname}")
        print(f"  找到的modelname: {found_modelnames}")
        print()

if __name__ == "__main__":
    asyncio.run(test_modelname_check()) 