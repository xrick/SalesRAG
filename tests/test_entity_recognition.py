#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
實體識別系統測試腳本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_rag_app.libs.services.sales_assistant.entity_recognition import EntityRecognitionSystem

def test_entity_recognition():
    """測試實體識別功能"""
    print("=== 實體識別系統測試 ===")
    
    # 創建系統實例
    nlp_system = EntityRecognitionSystem()
    
    # 測試用例
    test_cases = [
        "比較 AG958 和 APX958 的 CPU 性能",
        "AG958 的電池續航力如何？",
        "958 系列的螢幕規格比較",
        "APX958 的記憶體配置是 16GB DDR4",
        "哪個型號比較輕便？AG958 還是 APX958？",
        "現在最新的 839 系列有哪些型號？",
        "AG958 的價格是多少？",
        "APX958 使用 AMD Ryzen 7 處理器",
        "比較兩個型號的儲存容量：AG958 有 512GB SSD，APX958 有 1TB NVMe"
    ]
    
    results = []
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n--- 測試案例 {i} ---")
        print(f"輸入文本: {text}")
        
        # 處理文本
        result = nlp_system.process_text(text)
        results.append(result)
        
        # 顯示結果
        print(f"檢測到的意圖: {result['intent']['name']} (信心度: {result['intent']['confidence']:.2f})")
        print(f"匹配的關鍵字: {result['intent']['keywords']}")
        
        print("識別到的實體:")
        for entity in result['entities']:
            print(f"  - {entity['text']} ({entity['label']}, 信心度: {entity['confidence']:.2f})")
        
        print("實體與意圖關係:")
        for relation in result['relations']:
            print(f"  - {relation['entity_text']} -> {relation['intent_name']} ({relation['relation_type']}, 信心度: {relation['confidence']:.2f})")
    
    # 保存結果到JSON
    success = nlp_system.save_to_json(results, 'entity_recognition_results.json')
    if success:
        print(f"\n結果已保存到: entity_recognition_results.json")
    else:
        print(f"\n保存結果失敗")
    
    print("\n=== 測試完成 ===")

def test_individual_components():
    """測試個別組件"""
    print("\n=== 個別組件測試 ===")
    
    nlp_system = EntityRecognitionSystem()
    
    # 測試實體識別
    print("\n1. 實體識別測試:")
    text = "AG958 的 CPU 性能比 APX958 好"
    entities = nlp_system.recognize_entities(text)
    for entity in entities:
        print(f"  - {entity.text} ({entity.label}, 信心度: {entity.confidence:.2f})")
    
    # 測試意圖檢測
    print("\n2. 意圖檢測測試:")
    intent = nlp_system.detect_intent(text)
    print(f"  - 意圖: {intent.name} (信心度: {intent.confidence:.2f})")
    print(f"  - 關鍵字: {intent.keywords}")
    
    # 測試關係識別
    print("\n3. 關係識別測試:")
    relations = nlp_system.identify_relations(text, entities, intent)
    for relation in relations:
        print(f"  - {relation.entity_text} -> {relation.intent_name} ({relation.relation_type}, 信心度: {relation.confidence:.2f})")

def interactive_test():
    """互動式測試"""
    print("\n=== 互動式測試 ===")
    print("輸入 'quit' 退出測試")
    
    nlp_system = EntityRecognitionSystem()
    
    while True:
        text = input("\n請輸入測試文本: ").strip()
        if text.lower() == 'quit':
            break
        
        if not text:
            print("請輸入有效的文本")
            continue
        
        # 處理文本
        result = nlp_system.process_text(text)
        
        # 顯示結果
        print(f"\n分析結果:")
        print(f"  意圖: {result['intent']['name']} (信心度: {result['intent']['confidence']:.2f})")
        print(f"  關鍵字: {result['intent']['keywords']}")
        
        if result['entities']:
            print(f"  實體:")
            for entity in result['entities']:
                print(f"    - {entity['text']} ({entity['label']}, 信心度: {entity['confidence']:.2f})")
        else:
            print(f"  實體: 無")
        
        if result['relations']:
            print(f"  關係:")
            for relation in result['relations']:
                print(f"    - {relation['entity_text']} -> {relation['intent_name']} ({relation['relation_type']}, 信心度: {relation['confidence']:.2f})")
        else:
            print(f"  關係: 無")

def main():
    """主函數"""
    print("實體識別系統測試")
    print("1. 自動測試")
    print("2. 個別組件測試")
    print("3. 互動式測試")
    print("4. 全部測試")
    
    choice = input("\n請選擇測試模式 (1-4): ").strip()
    
    if choice == '1':
        test_entity_recognition()
    elif choice == '2':
        test_individual_components()
    elif choice == '3':
        interactive_test()
    elif choice == '4':
        test_entity_recognition()
        test_individual_components()
        interactive_test()
    else:
        print("無效的選擇")

if __name__ == "__main__":
    main() 