#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import sys
import os

# 添加專案路徑
sys.path.append(os.path.dirname(__file__))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

async def test_service():
    """測試修復後的服務"""
    try:
        service = SalesAssistantService()
        print("服務初始化成功")
        
        # 測試查詢
        query = "比較 AG958、APX839 和 AMD819 (FT6) 的電池續航力"
        print(f"測試查詢: {query}")
        
        # 執行查詢
        async for response in service.chat_stream(query):
            if response.startswith("data: "):
                json_str = response[6:]  # 移除 "data: " 前綴
                try:
                    data = json.loads(json_str)
                    print("\n=== 服務回應 ===")
                    print(f"摘要: {data.get('answer_summary', 'N/A')}")
                    print(f"比較表格: {data.get('comparison_table', 'N/A')}")
                    print(f"美化表格: {data.get('beautiful_table', 'N/A')}")
                    print("\n=== 測試成功 ===")
                    break
                except json.JSONDecodeError as e:
                    print(f"JSON 解析失敗: {e}")
                    print(f"原始回應: {json_str}")
            else:
                print(f"其他回應: {response}")
                
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service()) 