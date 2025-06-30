#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互動式關鍵字管理腳本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def print_menu():
    """顯示選單"""
    print("\n=== 關鍵字管理系統 ===")
    print("1. 顯示所有關鍵字配置")
    print("2. 添加關鍵字")
    print("3. 移除關鍵字")
    print("4. 測試查詢意圖解析")
    print("5. 保存配置")
    print("6. 重新載入配置")
    print("7. 退出")
    print("=====================")

def display_keywords(service):
    """顯示所有關鍵字配置"""
    print("\n當前關鍵字配置:")
    keywords = service.get_intent_keywords()
    for intent, config in keywords.items():
        print(f"\n{intent} ({config.get('description', '無描述')}):")
        for keyword in config['keywords']:
            print(f"  - {keyword}")

def add_keyword(service):
    """添加關鍵字"""
    print("\n可用的意圖:")
    keywords = service.get_intent_keywords()
    for intent in keywords.keys():
        print(f"  - {intent}")
    
    intent_name = input("\n請輸入意圖名稱: ").strip()
    if intent_name not in keywords:
        print(f"錯誤: 意圖 '{intent_name}' 不存在")
        return
    
    keyword = input("請輸入要添加的關鍵字: ").strip()
    if not keyword:
        print("錯誤: 關鍵字不能為空")
        return
    
    success = service.add_intent_keyword(intent_name, keyword)
    if success:
        print(f"成功添加關鍵字 '{keyword}' 到意圖 '{intent_name}'")
    else:
        print("添加關鍵字失敗")

def remove_keyword(service):
    """移除關鍵字"""
    print("\n可用的意圖:")
    keywords = service.get_intent_keywords()
    for intent in keywords.keys():
        print(f"  - {intent}")
    
    intent_name = input("\n請輸入意圖名稱: ").strip()
    if intent_name not in keywords:
        print(f"錯誤: 意圖 '{intent_name}' 不存在")
        return
    
    print(f"\n意圖 '{intent_name}' 的關鍵字:")
    for keyword in keywords[intent_name]['keywords']:
        print(f"  - {keyword}")
    
    keyword = input("\n請輸入要移除的關鍵字: ").strip()
    if not keyword:
        print("錯誤: 關鍵字不能為空")
        return
    
    success = service.remove_intent_keyword(intent_name, keyword)
    if success:
        print(f"成功從意圖 '{intent_name}' 移除關鍵字 '{keyword}'")
    else:
        print("移除關鍵字失敗")

def test_query_parsing(service):
    """測試查詢意圖解析"""
    print("\n測試查詢意圖解析")
    print("輸入 'quit' 退出測試")
    
    while True:
        query = input("\n請輸入測試查詢: ").strip()
        if query.lower() == 'quit':
            break
        
        if not query:
            print("請輸入有效的查詢")
            continue
        
        intent = service._parse_query_intent(query)
        print(f"查詢: '{query}'")
        print(f"  意圖: {intent['intent']}")
        print(f"  查詢類型: {intent['query_type']}")
        print(f"  模型名稱: {intent['modelnames']}")
        print(f"  模型類型: {intent['modeltypes']}")

def main():
    """主函數"""
    print("正在初始化服務...")
    try:
        service = SalesAssistantService()
        print("服務初始化成功！")
    except Exception as e:
        print(f"服務初始化失敗: {e}")
        return
    
    while True:
        print_menu()
        choice = input("請選擇操作 (1-7): ").strip()
        
        if choice == '1':
            display_keywords(service)
        elif choice == '2':
            add_keyword(service)
        elif choice == '3':
            remove_keyword(service)
        elif choice == '4':
            test_query_parsing(service)
        elif choice == '5':
            success = service.save_intent_keywords()
            if success:
                print("配置保存成功！")
            else:
                print("配置保存失敗！")
        elif choice == '6':
            success = service.reload_intent_keywords()
            if success:
                print("配置重新載入成功！")
            else:
                print("配置重新載入失敗！")
        elif choice == '7':
            print("再見！")
            break
        else:
            print("無效的選擇，請重新輸入")

if __name__ == "__main__":
    main() 