#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試關鍵字管理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_keyword_management():
    """測試關鍵字管理功能"""
    print("=== 測試關鍵字管理功能 ===")
    
    # 創建服務實例
    service = SalesAssistantService()
    
    # 1. 測試獲取當前關鍵字配置
    print("\n1. 當前關鍵字配置:")
    keywords = service.get_intent_keywords()
    for intent, config in keywords.items():
        print(f"  {intent}: {config['keywords']}")
    
    # 2. 測試查詢意圖解析
    print("\n2. 測試查詢意圖解析:")
    test_queries = [
        "比較 AG958 和 APX958 的螢幕規格",
        "AG958 的 CPU 性能如何？",
        "APX958 的電池續航力",
        "958 系列的重量比較",
        "AG958 的記憶體配置"
    ]
    
    for query in test_queries:
        intent = service._parse_query_intent(query)
        print(f"  查詢: '{query}'")
        print(f"    意圖: {intent['intent']}")
        print(f"    查詢類型: {intent['query_type']}")
        print(f"    模型名稱: {intent['modelnames']}")
        print()
    
    # 3. 測試添加關鍵字
    print("3. 測試添加關鍵字:")
    success = service.add_intent_keyword("cpu", "中央處理器")
    print(f"  添加 '中央處理器' 到 CPU 意圖: {'成功' if success else '失敗'}")
    
    # 4. 測試移除關鍵字
    print("\n4. 測試移除關鍵字:")
    success = service.remove_intent_keyword("cpu", "中央處理器")
    print(f"  從 CPU 意圖移除 '中央處理器': {'成功' if success else '失敗'}")
    
    # 5. 測試保存配置
    print("\n5. 測試保存配置:")
    success = service.save_intent_keywords()
    print(f"  保存關鍵字配置: {'成功' if success else '失敗'}")
    
    # 6. 測試重新載入配置
    print("\n6. 測試重新載入配置:")
    success = service.reload_intent_keywords()
    print(f"  重新載入關鍵字配置: {'成功' if success else '失敗'}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_keyword_management() 