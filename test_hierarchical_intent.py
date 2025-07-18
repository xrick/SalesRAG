#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試階層式意圖檢測和澄清對話系統
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from sales_rag_app.libs.services.sales_assistant.entity_recognition import EntityRecognitionSystem
from sales_rag_app.libs.services.sales_assistant.clarification_manager import ClarificationManager
import json
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_hierarchical_intent_detection():
    """測試階層式意圖檢測"""
    print("=== 測試階層式意圖檢測 ===")
    
    # 初始化系統
    entity_recognizer = EntityRecognitionSystem()
    
    # 測試查詢
    test_queries = [
        "我想要一台適合玩遊戲的筆電",  # 應該檢測到 gaming sub-intent
        "有沒有適合商務使用的輕薄筆電？",  # 應該檢測到 business + ultralight
        "比較 958 和 819 系列的 CPU 性能",  # 應該檢測到 comparison + cpu
        "最新的高階筆電有哪些？",  # 應該檢測到 latest + premium
        "我需要一台筆電",  # 一般查詢，信心度應該很低
        "筆電的記憶體容量",  # 應該檢測到 memory
        "顯卡效能好的機型"  # 應該檢測到 gpu
    ]
    
    for query in test_queries:
        print(f"\n查詢: {query}")
        print("-" * 50)
        
        # 進行階層式意圖檢測
        result = entity_recognizer.detect_hierarchical_intent(query)
        
        print(f"主要意圖: {result['primary_intent']}")
        print(f"意圖類型: {result['primary_intent_type']}")
        print(f"信心度: {result['confidence_score']:.3f}")
        print(f"匹配關鍵字: {result['matched_keywords']}")
        
        if result['high_confidence_intents']:
            print("高信心度意圖:")
            for intent in result['high_confidence_intents']:
                print(f"  - {intent['name']} ({intent['type']}): {intent['confidence']:.3f}")
        
        # 檢查是否有細分意圖
        if result['sub_intents']:
            print("檢測到的細分意圖:")
            for sub_intent, data in result['sub_intents'].items():
                print(f"  - {sub_intent}: {data['confidence']:.3f}")
                if 'priority_specs' in data:
                    print(f"    優先規格: {data['priority_specs']}")

def test_clarification_system():
    """測試澄清對話系統"""
    print("\n\n=== 測試澄清對話系統 ===")
    
    # 初始化系統
    entity_recognizer = EntityRecognitionSystem()
    clarification_manager = ClarificationManager()
    
    # 測試低信心度查詢
    low_confidence_queries = [
        "我想要一台筆電",  # 應該觸發澄清
        "有什麼推薦的嗎？",  # 應該觸發澄清
        "筆電規格"  # 應該觸發澄清
    ]
    
    for query in low_confidence_queries:
        print(f"\n測試查詢: {query}")
        print("-" * 50)
        
        # 檢測意圖
        intent_result = entity_recognizer.detect_hierarchical_intent(query)
        
        # 檢查是否需要澄清
        should_clarify = clarification_manager.should_clarify(intent_result)
        print(f"需要澄清: {should_clarify}")
        
        if should_clarify:
            # 開始澄清對話
            conversation_id, clarification_question = clarification_manager.start_clarification(
                query, intent_result
            )
            
            print(f"對話ID: {conversation_id}")
            print(f"澄清問題: {clarification_question.question}")
            print(f"問題類型: {clarification_question.question_type}")
            print(f"選項數量: {len(clarification_question.options)}")
            
            # 顯示選項
            print("可選選項:")
            for option in clarification_question.options:
                print(f"  {option['id']}: {option['label']} - {option['description']}")
            
            # 模擬用戶選擇第一個選項
            if clarification_question.options:
                test_choice = clarification_question.options[0]['id']
                print(f"\n模擬用戶選擇: {test_choice}")
                
                # 處理澄清回應
                response_result = clarification_manager.process_clarification_response(
                    conversation_id, test_choice, ""
                )
                
                print(f"處理結果動作: {response_result['action']}")
                
                if response_result['action'] == 'continue':
                    print("需要繼續澄清")
                    next_question = response_result['next_question']
                    print(f"下一個問題: {next_question.question}")
                
                elif response_result['action'] == 'complete':
                    print("澄清完成")
                    enhanced_intent = response_result['enhanced_intent']
                    summary = response_result['clarification_summary']
                    print(f"增強意圖: {enhanced_intent['primary_intent']}")
                    print(f"澄清總結: {summary}")

def test_entity_recognition():
    """測試實體識別"""
    print("\n\n=== 測試實體識別 ===")
    
    entity_recognizer = EntityRecognitionSystem()
    
    test_texts = [
        "比較 AB819-S: FP6 和 AG958 的 CPU 性能",
        "958 系列的顯卡怎麼樣？",
        "最新的 839 筆電有 16GB 記憶體嗎？",
        "哪個型號比較輕便？"
    ]
    
    for text in test_texts:
        print(f"\n文本: {text}")
        print("-" * 30)
        
        entities = entity_recognizer.recognize_entities(text)
        for entity in entities:
            print(f"實體: '{entity.text}' -> {entity.label} (信心度: {entity.confidence:.3f})")

if __name__ == "__main__":
    try:
        test_hierarchical_intent_detection()
        test_clarification_system()
        test_entity_recognition()
        print("\n=== 所有測試完成 ===")
        
    except Exception as e:
        logging.error(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()