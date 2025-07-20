#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試增強版意圖檢測系統
驗證系統能否解決之前的"請提供更多資訊"問題
"""

import sys
import os
import json
import logging
from datetime import datetime

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from sales_rag_app.libs.services.sales_assistant.entity_recognition_enhanced import EnhancedEntityRecognitionSystem
from sales_rag_app.libs.services.sales_assistant.clarification_manager_enhanced import EnhancedClarificationManager

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_problematic_queries():
    """測試之前有問題的查詢"""
    print("=== 測試增強版意圖檢測系統 ===")
    print("目標：消除'請提供更多資訊'問題，提供即時有用回應\n")
    
    # 初始化增強版系統
    enhanced_recognizer = EnhancedEntityRecognitionSystem()
    enhanced_clarification = EnhancedClarificationManager()
    
    # 之前有問題的查詢
    problematic_queries = [
        "哪款筆電比較省電？",
        "推薦適合遊戲的",  
        "958和819哪個好？",
        "學生用什麼好？",
        "螢幕效果怎麼樣？",
        "有什麼推薦的嗎？",
        "筆電規格",
        "比較一下",
        "哪個性價比高？",
        "適合辦公的筆電"
    ]
    
    results = {}
    
    for i, query in enumerate(problematic_queries, 1):
        print(f"\n{'='*60}")
        print(f"測試 {i}: {query}")
        print(f"{'='*60}")
        
        try:
            # 使用增強版處理
            analysis_result = enhanced_recognizer.process_text_enhanced(query)
            
            # 提取關鍵信息
            intent_analysis = analysis_result['intent_analysis']
            smart_context = analysis_result['smart_context']
            entities = analysis_result['entities']
            
            print(f"📍 檢測到的實體: {len(entities)} 個")
            for entity in entities:
                print(f"   - {entity['text']} ({entity['label']}) [信心度: {entity['confidence']:.3f}, 類型: {entity['match_type']}]")
            
            print(f"\n🎯 意圖分析:")
            print(f"   主要意圖: {intent_analysis['primary_intent']}")
            print(f"   信心度: {intent_analysis['confidence_score']:.3f}")
            print(f"   匹配關鍵字: {intent_analysis.get('matched_keywords', [])[:5]}")  # 只顯示前5個
            
            print(f"\n🧠 智能回應策略:")
            print(f"   回應策略: {smart_context['response_strategy']}")
            print(f"   推薦型號: {smart_context['recommended_models']}")
            print(f"   優先規格: {smart_context['priority_specs']}")
            
            # 檢查是否需要澄清
            should_clarify = enhanced_clarification.should_clarify_enhanced(
                intent_analysis, smart_context
            )
            
            print(f"\n❓ 需要澄清: {'❌ 否' if not should_clarify else '✅ 是'}")
            
            if not should_clarify:
                # 生成智能後備回應
                smart_response = enhanced_clarification.generate_smart_fallback_response(
                    query, intent_analysis, smart_context
                )
                
                print(f"\n💡 智能回應:")
                print(f"   類型: {smart_response['response_type']}")
                print(f"   摘要: {smart_response['answer_summary']}")
                print(f"   建議動作: {smart_response['recommended_action']}")
                print(f"   額外建議: {len(smart_response.get('additional_suggestions', []))} 項")
                
                # 顯示部分建議
                suggestions = smart_response.get('additional_suggestions', [])
                if suggestions:
                    print("   建議內容:")
                    for suggestion in suggestions[:3]:  # 只顯示前3個
                        print(f"     {suggestion}")
            else:
                print(f"\n⚠️  此查詢觸發澄清（這應該很少發生）")
            
            # 記錄結果
            results[query] = {
                "success": not should_clarify,
                "confidence": intent_analysis['confidence_score'],
                "intent": intent_analysis['primary_intent'],
                "strategy": smart_context['response_strategy'],
                "models": smart_context['recommended_models'],
                "clarification_needed": should_clarify
            }
            
        except Exception as e:
            print(f"❌ 處理失敗: {e}")
            results[query] = {
                "success": False,
                "error": str(e),
                "clarification_needed": True
            }
    
    # 總結報告
    print(f"\n\n{'='*80}")
    print("📊 測試總結報告")
    print(f"{'='*80}")
    
    total_queries = len(problematic_queries)
    successful_queries = sum(1 for r in results.values() if r.get('success', False))
    clarification_rate = sum(1 for r in results.values() if r.get('clarification_needed', True)) / total_queries
    
    print(f"總查詢數: {total_queries}")
    print(f"成功處理: {successful_queries} ({successful_queries/total_queries*100:.1f}%)")
    print(f"澄清觸發率: {clarification_rate*100:.1f}% (目標: <15%)")
    
    if successful_queries >= total_queries * 0.85:
        print("✅ 測試通過！大幅改善了意圖檢測和回應生成")
    else:
        print("⚠️ 仍需改進，部分查詢未達到預期效果")
    
    # 保存詳細結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"enhanced_intent_test_results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "success_rate": successful_queries/total_queries,
                "clarification_rate": clarification_rate,
                "target_achieved": successful_queries >= total_queries * 0.85
            },
            "detailed_results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 詳細結果已保存到: {result_file}")
    
    return successful_queries >= total_queries * 0.85

def test_enhancement_comparison():
    """比較增強前後的效果"""
    print("\n\n=== 增強前後效果比較 ===")
    
    # 使用原始系統
    try:
        from sales_rag_app.libs.services.sales_assistant.entity_recognition import EntityRecognitionSystem
        from sales_rag_app.libs.services.sales_assistant.clarification_manager import ClarificationManager
        
        original_recognizer = EntityRecognitionSystem()
        original_clarification = ClarificationManager()
        
        # 增強版系統
        enhanced_recognizer = EnhancedEntityRecognitionSystem()
        enhanced_clarification = EnhancedClarificationManager()
        
        test_query = "哪款筆電比較省電？"
        
        print(f"測試查詢: {test_query}")
        print("\n--- 原始系統 ---")
        
        # 原始系統處理
        original_intent = original_recognizer.detect_hierarchical_intent(test_query)
        original_clarify = original_clarification.should_clarify(original_intent)
        
        print(f"主要意圖: {original_intent.get('primary_intent', 'unknown')}")
        print(f"信心度: {original_intent.get('confidence_score', 0.0):.3f}")
        print(f"需要澄清: {'是' if original_clarify else '否'}")
        
        print("\n--- 增強版系統 ---")
        
        # 增強版系統處理
        enhanced_analysis = enhanced_recognizer.process_text_enhanced(test_query)
        enhanced_intent = enhanced_analysis['intent_analysis']
        enhanced_smart_context = enhanced_analysis['smart_context']
        enhanced_clarify = enhanced_clarification.should_clarify_enhanced(enhanced_intent, enhanced_smart_context)
        
        print(f"主要意圖: {enhanced_intent.get('primary_intent', 'unknown')}")
        print(f"信心度: {enhanced_intent.get('confidence_score', 0.0):.3f}")
        print(f"回應策略: {enhanced_smart_context.get('response_strategy', 'unknown')}")
        print(f"推薦型號: {enhanced_smart_context.get('recommended_models', [])}")
        print(f"需要澄清: {'是' if enhanced_clarify else '否'}")
        
        if not enhanced_clarify:
            smart_response = enhanced_clarification.generate_smart_fallback_response(
                test_query, enhanced_intent, enhanced_smart_context
            )
            print(f"智能回應: {smart_response.get('answer_summary', 'N/A')}")
        
        improvement = not enhanced_clarify and original_clarify
        print(f"\n改善效果: {'✅ 顯著改善' if improvement else '⚖️ 需要更多測試'}")
        
    except ImportError as e:
        print(f"無法載入原始系統進行比較: {e}")
        print("這是正常的，表示我們正在使用增強版系統")

if __name__ == "__main__":
    try:
        # 執行主要測試
        success = test_problematic_queries()
        
        # 執行比較測試
        test_enhancement_comparison()
        
        print(f"\n{'='*80}")
        if success:
            print("🎉 增強版意圖檢測系統測試成功！")
            print("✅ 大幅減少了澄清需求")
            print("✅ 提供了即時有用的回應")
            print("✅ 改善了用戶體驗")
        else:
            print("⚠️ 測試結果未完全達到預期")
            print("💡 建議進一步調整配置參數")
        print(f"{'='*80}")
        
    except Exception as e:
        logging.error(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()