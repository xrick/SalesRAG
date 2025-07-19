#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試智能澄清機制
簡化版本，用於快速驗證核心功能
"""

import sys
import os

# 添加專案路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from sales_rag_app.libs.service_manager import ServiceManager

def test_smart_clarification():
    """測試智能澄清機制"""
    print("🚀 開始快速測試智能澄清機制...")
    print("="*50)
    
    try:
        # 初始化服務
        service_manager = ServiceManager()
        sales_service = service_manager.get_service("sales_assistant")
        
        # 測試案例
        test_cases = [
            "哪一款筆電比較省電？",
            "哪一款筆電比較適合玩遊戲？",
            "推薦適合辦公的筆電",
            "學生用筆電推薦",
            "設計用筆電哪個好？",
            "哪個比較快？",
            "哪個比較輕？",
            "哪個比較便宜？"
        ]
        
        print("📝 測試基本查詢場景:")
        for i, query in enumerate(test_cases, 1):
            print(f"\n{i}. 查詢: {query}")
            
            try:
                # 解析查詢意圖
                query_intent = sales_service._parse_query_intent(query)
                print(f"   查詢類型: {query_intent['query_type']}")
                print(f"   主要意圖: {query_intent['primary_intent']}")
                print(f"   信心度: {query_intent['confidence_score']:.2f}")
                
                if query_intent["query_type"] == "unknown":
                    # 生成智能澄清問題
                    smart_questions = sales_service._generate_smart_clarification_questions(query, query_intent)
                    
                    if smart_questions:
                        print(f"   ✅ 生成智能問題: {len(smart_questions)} 個")
                        for j, question in enumerate(smart_questions, 1):
                            print(f"      {j}. {question['question']}")
                            for option in question['options']:
                                print(f"         - {option['label']}")
                    else:
                        # 生成友善幫助信息
                        help_message = sales_service._generate_user_friendly_help(query)
                        print(f"   ✅ 生成友善幫助信息")
                        print(f"      {help_message[:100]}...")
                else:
                    print(f"   ⚠️  查詢類型不是 unknown，直接處理")
                    
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
        
        print("\n" + "="*50)
        print("🧪 測試智能澄清回應處理:")
        
        # 測試澄清回應處理
        test_responses = [
            {
                "query": "哪一款筆電比較好？",
                "question_id": "usage_scenario",
                "choice": "gaming",
                "expected_modeltypes": ["958"],
                "expected_intents": ["gpu", "cpu"]
            },
            {
                "query": "推薦筆電",
                "question_id": "usage_scenario", 
                "choice": "business",
                "expected_modeltypes": ["819"],
                "expected_intents": ["battery", "cpu"]
            },
            {
                "query": "學生用筆電",
                "question_id": "usage_scenario",
                "choice": "study", 
                "expected_modeltypes": ["839"],
                "expected_intents": ["battery", "cpu"]
            }
        ]
        
        for i, test_case in enumerate(test_responses, 1):
            print(f"\n{i}. 測試: {test_case['query']} -> {test_case['choice']}")
            
            try:
                enhanced_intent = sales_service._build_query_intent_from_smart_clarification(
                    test_case["query"],
                    test_case["question_id"],
                    test_case["choice"],
                    ""
                )
                
                print(f"   模型類型: {enhanced_intent.get('modeltypes', [])}")
                print(f"   意圖: {enhanced_intent.get('intents', [])}")
                print(f"   查詢類型: {enhanced_intent.get('query_type', 'unknown')}")
                
                # 驗證結果
                success = True
                if set(enhanced_intent.get("modeltypes", [])) != set(test_case["expected_modeltypes"]):
                    success = False
                    print(f"   ❌ 模型類型不匹配")
                if set(enhanced_intent.get("intents", [])) != set(test_case["expected_intents"]):
                    success = False
                    print(f"   ❌ 意圖不匹配")
                
                if success:
                    print(f"   ✅ 測試通過")
                else:
                    print(f"   ❌ 測試失敗")
                    
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
        
        print("\n" + "="*50)
        print("🎯 測試意圖識別:")
        
        # 測試意圖識別
        intent_tests = [
            ("哪個比較快？", ["cpu", "performance"]),
            ("哪個比較省電？", ["battery", "energy_efficient"]),
            ("哪個比較輕？", ["portability", "weight"]),
            ("哪個比較適合玩遊戲？", ["gaming", "gpu"]),
            ("哪個比較便宜？", ["budget", "economy"])
        ]
        
        for query, expected_intents in intent_tests:
            print(f"\n查詢: {query}")
            try:
                query_intent = sales_service._parse_query_intent(query)
                detected_intents = [intent.get("name") for intent in query_intent.get("intents", [])]
                
                print(f"   檢測到意圖: {detected_intents}")
                print(f"   信心度: {query_intent.get('confidence_score', 0):.2f}")
                
                # 檢查是否檢測到預期意圖
                matched = any(expected in detected_intents for expected in expected_intents)
                if matched:
                    print(f"   ✅ 意圖識別成功")
                else:
                    print(f"   ⚠️  未檢測到預期意圖")
                    
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
        
        print("\n" + "="*50)
        print("✅ 快速測試完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
        return False

def test_specific_scenario():
    """測試特定場景"""
    print("\n🎬 測試特定場景:")
    print("="*30)
    
    try:
        service_manager = ServiceManager()
        sales_service = service_manager.get_service("sales_assistant")
        
        # 模擬完整的用戶交互流程
        print("用戶查詢: 哪一款筆電比較適合玩遊戲？")
        
        # 1. 解析查詢意圖
        query_intent = sales_service._parse_query_intent("哪一款筆電比較適合玩遊戲？")
        print(f"查詢類型: {query_intent['query_type']}")
        print(f"主要意圖: {query_intent['primary_intent']}")
        
        if query_intent["query_type"] == "unknown":
            # 2. 生成智能澄清問題
            smart_questions = sales_service._generate_smart_clarification_questions(
                "哪一款筆電比較適合玩遊戲？", query_intent
            )
            
            if smart_questions:
                print(f"系統回應: 我理解您的需求，讓我幫您找到最適合的筆電。")
                print(f"問題: {smart_questions[0]['question']}")
                for option in smart_questions[0]['options']:
                    print(f"  - {option['label']}")
                
                # 3. 模擬用戶選擇
                user_choice = "gaming"
                print(f"\n用戶選擇: {user_choice}")
                
                # 4. 處理用戶選擇
                enhanced_intent = sales_service._build_query_intent_from_smart_clarification(
                    "哪一款筆電比較適合玩遊戲？",
                    "usage_scenario",
                    user_choice,
                    ""
                )
                
                print(f"增強意圖:")
                print(f"  - 模型類型: {enhanced_intent.get('modeltypes', [])}")
                print(f"  - 意圖: {enhanced_intent.get('intents', [])}")
                print(f"  - 查詢類型: {enhanced_intent.get('query_type', 'unknown')}")
                
                # 5. 模擬數據查詢
                try:
                    context_list_of_dicts, target_modelnames = sales_service._get_data_by_query_type(enhanced_intent)
                    print(f"查詢到 {len(target_modelnames)} 個型號: {target_modelnames}")
                    print("✅ 場景測試成功！")
                except Exception as e:
                    print(f"❌ 數據查詢失敗: {e}")
            else:
                print("❌ 未生成智能澄清問題")
        else:
            print("❌ 查詢類型不是 unknown")
            
    except Exception as e:
        print(f"❌ 場景測試失敗: {e}")

if __name__ == "__main__":
    print("智能澄清機制快速測試")
    print("="*50)
    
    # 執行快速測試
    success = test_smart_clarification()
    
    if success:
        # 執行特定場景測試
        test_specific_scenario()
        print("\n🎉 所有測試完成！")
    else:
        print("\n❌ 測試失敗，請檢查系統配置。") 