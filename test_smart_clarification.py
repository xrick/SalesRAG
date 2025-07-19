#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能澄清機制測試程式
測試改進後的用戶意圖識別和智能澄清功能
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# 添加專案路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from sales_rag_app.libs.service_manager import ServiceManager
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SmartClarificationTester:
    """智能澄清機制測試器"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.sales_service = self.service_manager.get_service("sales_assistant")
        self.test_results = []
        
    def log_test_result(self, test_name: str, query: str, expected_type: str, actual_result: dict, success: bool):
        """記錄測試結果"""
        result = {
            "test_name": test_name,
            "query": query,
            "expected_type": expected_type,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "actual_result": actual_result
        }
        self.test_results.append(result)
        
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{status} {test_name}")
        print(f"   查詢: {query}")
        print(f"   預期: {expected_type}")
        print(f"   實際: {actual_result.get('message_type', 'unknown')}")
        if not success:
            print(f"   錯誤: {actual_result.get('answer_summary', 'N/A')[:100]}...")
        print()
    
    async def test_basic_queries(self):
        """測試基本查詢場景"""
        print("=== 測試基本查詢場景 ===")
        
        test_cases = [
            {
                "name": "模糊比較查詢",
                "query": "哪一款筆電比較省電？",
                "expected_type": "smart_clarification"
            },
            {
                "name": "遊戲相關查詢",
                "query": "哪一款筆電比較適合玩遊戲？",
                "expected_type": "smart_clarification"
            },
            {
                "name": "辦公相關查詢",
                "query": "推薦適合辦公的筆電",
                "expected_type": "smart_clarification"
            },
            {
                "name": "學習相關查詢",
                "query": "學生用筆電推薦",
                "expected_type": "smart_clarification"
            },
            {
                "name": "設計相關查詢",
                "query": "設計用筆電哪個好？",
                "expected_type": "smart_clarification"
            }
        ]
        
        for test_case in test_cases:
            try:
                # 模擬 chat_stream 的處理流程
                query_intent = self.sales_service._parse_query_intent(test_case["query"])
                
                if query_intent["query_type"] == "unknown":
                    # 測試智能澄清問題生成
                    smart_questions = self.sales_service._generate_smart_clarification_questions(
                        test_case["query"], query_intent
                    )
                    
                    if smart_questions:
                        result = {
                            "message_type": "smart_clarification",
                            "questions": smart_questions
                        }
                        success = True
                    else:
                        # 測試友善幫助信息
                        help_message = self.sales_service._generate_user_friendly_help(test_case["query"])
                        result = {
                            "message_type": "help_message",
                            "answer_summary": help_message
                        }
                        success = True
                else:
                    result = {
                        "message_type": "direct_response",
                        "query_intent": query_intent
                    }
                    success = False  # 預期是 unknown 類型
                
                self.log_test_result(
                    test_case["name"],
                    test_case["query"],
                    test_case["expected_type"],
                    result,
                    success
                )
                
            except Exception as e:
                result = {
                    "message_type": "error",
                    "error": str(e)
                }
                self.log_test_result(
                    test_case["name"],
                    test_case["query"],
                    test_case["expected_type"],
                    result,
                    False
                )
    
    async def test_smart_clarification_responses(self):
        """測試智能澄清回應處理"""
        print("=== 測試智能澄清回應處理 ===")
        
        test_cases = [
            {
                "name": "遊戲場景選擇",
                "original_query": "哪一款筆電比較好？",
                "question_id": "usage_scenario",
                "user_choice": "gaming",
                "expected_modeltypes": ["958"],
                "expected_intents": ["gpu", "cpu"]
            },
            {
                "name": "辦公場景選擇",
                "original_query": "推薦筆電",
                "question_id": "usage_scenario",
                "user_choice": "business",
                "expected_modeltypes": ["819"],
                "expected_intents": ["battery", "cpu"]
            },
            {
                "name": "學習場景選擇",
                "original_query": "學生用筆電",
                "question_id": "usage_scenario",
                "user_choice": "study",
                "expected_modeltypes": ["839"],
                "expected_intents": ["battery", "cpu"]
            },
            {
                "name": "性能優先級選擇",
                "original_query": "哪個比較快？",
                "question_id": "performance_priority",
                "user_choice": "cpu",
                "expected_intents": ["cpu"]
            },
            {
                "name": "便攜性選擇",
                "original_query": "輕便筆電",
                "question_id": "portability_priority",
                "user_choice": "ultralight",
                "expected_intents": ["portability"]
            },
            {
                "name": "預算選擇",
                "original_query": "便宜筆電",
                "question_id": "budget_range",
                "user_choice": "economy",
                "expected_modeltypes": ["839"],
                "expected_intents": ["budget"]
            }
        ]
        
        for test_case in test_cases:
            try:
                # 測試智能澄清回應處理
                enhanced_intent = self.sales_service._build_query_intent_from_smart_clarification(
                    test_case["original_query"],
                    test_case["question_id"],
                    test_case["user_choice"],
                    ""
                )
                
                # 驗證結果
                success = True
                if "expected_modeltypes" in test_case:
                    if set(enhanced_intent.get("modeltypes", [])) != set(test_case["expected_modeltypes"]):
                        success = False
                        print(f"   模型類型不匹配: 預期 {test_case['expected_modeltypes']}, 實際 {enhanced_intent.get('modeltypes', [])}")
                
                if "expected_intents" in test_case:
                    if set(enhanced_intent.get("intents", [])) != set(test_case["expected_intents"]):
                        success = False
                        print(f"   意圖不匹配: 預期 {test_case['expected_intents']}, 實際 {enhanced_intent.get('intents', [])}")
                
                result = {
                    "message_type": "enhanced_intent",
                    "enhanced_intent": enhanced_intent
                }
                
                self.log_test_result(
                    test_case["name"],
                    f"{test_case['original_query']} -> {test_case['user_choice']}",
                    "enhanced_intent",
                    result,
                    success
                )
                
            except Exception as e:
                result = {
                    "message_type": "error",
                    "error": str(e)
                }
                self.log_test_result(
                    test_case["name"],
                    f"{test_case['original_query']} -> {test_case['user_choice']}",
                    "enhanced_intent",
                    result,
                    False
                )
    
    async def test_user_friendly_help(self):
        """測試友善幫助信息生成"""
        print("=== 測試友善幫助信息生成 ===")
        
        test_cases = [
            {
                "name": "比較查詢幫助",
                "query": "比較筆電",
                "expected_keywords": ["比較", "差異", "推薦"]
            },
            {
                "name": "推薦查詢幫助",
                "query": "推薦筆電",
                "expected_keywords": ["推薦", "建議", "需求"]
            },
            {
                "name": "遊戲查詢幫助",
                "query": "遊戲筆電",
                "expected_keywords": ["遊戲", "電競", "性能"]
            },
            {
                "name": "辦公查詢幫助",
                "query": "辦公筆電",
                "expected_keywords": ["辦公", "商務", "續航"]
            },
            {
                "name": "通用查詢幫助",
                "query": "筆電",
                "expected_keywords": ["推薦", "比較", "適合"]
            }
        ]
        
        for test_case in test_cases:
            try:
                help_message = self.sales_service._generate_user_friendly_help(test_case["query"])
                
                # 檢查幫助信息是否包含預期的關鍵詞
                success = any(keyword in help_message for keyword in test_case["expected_keywords"])
                
                result = {
                    "message_type": "help_message",
                    "help_message": help_message[:200] + "..." if len(help_message) > 200 else help_message
                }
                
                self.log_test_result(
                    test_case["name"],
                    test_case["query"],
                    "help_message",
                    result,
                    success
                )
                
            except Exception as e:
                result = {
                    "message_type": "error",
                    "error": str(e)
                }
                self.log_test_result(
                    test_case["name"],
                    test_case["query"],
                    "help_message",
                    result,
                    False
                )
    
    async def test_intent_recognition(self):
        """測試意圖識別功能"""
        print("=== 測試意圖識別功能 ===")
        
        test_cases = [
            {
                "name": "日常用語識別",
                "query": "哪個比較快？",
                "expected_intents": ["cpu", "performance"]
            },
            {
                "name": "省電查詢識別",
                "query": "哪個比較省電？",
                "expected_intents": ["battery", "energy_efficient"]
            },
            {
                "name": "輕便查詢識別",
                "query": "哪個比較輕？",
                "expected_intents": ["portability", "weight"]
            },
            {
                "name": "遊戲查詢識別",
                "query": "哪個比較適合玩遊戲？",
                "expected_intents": ["gaming", "gpu"]
            },
            {
                "name": "便宜查詢識別",
                "query": "哪個比較便宜？",
                "expected_intents": ["budget", "economy"]
            }
        ]
        
        for test_case in test_cases:
            try:
                query_intent = self.sales_service._parse_query_intent(test_case["query"])
                detected_intents = [intent.get("name") for intent in query_intent.get("intents", [])]
                
                # 檢查是否檢測到預期的意圖
                success = any(expected in detected_intents for expected in test_case["expected_intents"])
                
                result = {
                    "message_type": "intent_recognition",
                    "detected_intents": detected_intents,
                    "confidence_score": query_intent.get("confidence_score", 0)
                }
                
                self.log_test_result(
                    test_case["name"],
                    test_case["query"],
                    "intent_recognition",
                    result,
                    success
                )
                
            except Exception as e:
                result = {
                    "message_type": "error",
                    "error": str(e)
                }
                self.log_test_result(
                    test_case["name"],
                    test_case["query"],
                    "intent_recognition",
                    result,
                    False
                )
    
    async def test_end_to_end_scenarios(self):
        """測試端到端場景"""
        print("=== 測試端到端場景 ===")
        
        scenarios = [
            {
                "name": "遊戲筆電推薦場景",
                "steps": [
                    {"query": "哪一款筆電比較適合玩遊戲？", "expected": "smart_clarification"},
                    {"choice": "gaming", "expected_modeltypes": ["958"], "expected_intents": ["gpu", "cpu"]}
                ]
            },
            {
                "name": "辦公筆電推薦場景",
                "steps": [
                    {"query": "推薦適合辦公的筆電", "expected": "smart_clarification"},
                    {"choice": "business", "expected_modeltypes": ["819"], "expected_intents": ["battery", "cpu"]}
                ]
            },
            {
                "name": "學生筆電推薦場景",
                "steps": [
                    {"query": "學生用筆電推薦", "expected": "smart_clarification"},
                    {"choice": "study", "expected_modeltypes": ["839"], "expected_intents": ["battery", "cpu"]}
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n--- {scenario['name']} ---")
            
            try:
                # 第一步：用戶查詢
                step1 = scenario["steps"][0]
                query_intent = self.sales_service._parse_query_intent(step1["query"])
                
                if query_intent["query_type"] == "unknown":
                    smart_questions = self.sales_service._generate_smart_clarification_questions(
                        step1["query"], query_intent
                    )
                    
                    if smart_questions:
                        print(f"✅ 生成智能問題: {len(smart_questions)} 個問題")
                        
                        # 第二步：用戶選擇
                        step2 = scenario["steps"][1]
                        enhanced_intent = self.sales_service._build_query_intent_from_smart_clarification(
                            step1["query"],
                            "usage_scenario",  # 假設是使用場景問題
                            step2["choice"],
                            ""
                        )
                        
                        # 驗證結果
                        success = True
                        if set(enhanced_intent.get("modeltypes", [])) != set(step2["expected_modeltypes"]):
                            success = False
                        if set(enhanced_intent.get("intents", [])) != set(step2["expected_intents"]):
                            success = False
                        
                        result = {
                            "message_type": "end_to_end",
                            "enhanced_intent": enhanced_intent
                        }
                        
                        self.log_test_result(
                            scenario["name"],
                            f"{step1['query']} -> {step2['choice']}",
                            "end_to_end",
                            result,
                            success
                        )
                    else:
                        print("❌ 未生成智能問題")
                        self.log_test_result(
                            scenario["name"],
                            step1["query"],
                            "end_to_end",
                            {"error": "未生成智能問題"},
                            False
                        )
                else:
                    print("❌ 查詢類型不是 unknown")
                    self.log_test_result(
                        scenario["name"],
                        step1["query"],
                        "end_to_end",
                        {"error": "查詢類型不是 unknown"},
                        False
                    )
                    
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
                self.log_test_result(
                    scenario["name"],
                    scenario["steps"][0]["query"],
                    "end_to_end",
                    {"error": str(e)},
                    False
                )
    
    def generate_test_report(self):
        """生成測試報告"""
        print("\n" + "="*60)
        print("智能澄清機制測試報告")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"總測試數: {total_tests}")
        print(f"通過測試: {passed_tests} ✅")
        print(f"失敗測試: {failed_tests} ❌")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失敗的測試:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['query']}")
        
        # 保存詳細報告
        report_file = f"smart_clarification_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n詳細報告已保存至: {report_file}")
        
        return passed_tests, total_tests

async def main():
    """主測試函數"""
    print("開始智能澄清機制測試...")
    print("="*60)
    
    tester = SmartClarificationTester()
    
    # 執行各種測試
    await tester.test_basic_queries()
    await tester.test_smart_clarification_responses()
    await tester.test_user_friendly_help()
    await tester.test_intent_recognition()
    await tester.test_end_to_end_scenarios()
    
    # 生成測試報告
    passed, total = tester.generate_test_report()
    
    # 返回測試結果
    if passed == total:
        print("\n🎉 所有測試通過！智能澄清機制運行正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗，請檢查相關功能。")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n測試執行失敗: {e}")
        sys.exit(1) 