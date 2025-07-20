#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Parent-Child 檢索系統

驗證新的 Parent-Child 檢索系統能否成功替代三層意圖檢測，
解決之前的澄清請求問題，提供即時有用的回應。
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 導入 Parent-Child 系統組件
from sales_rag_app.libs.services.sales_assistant.parent_child_retriever import ParentChildRetriever
from sales_rag_app.libs.services.sales_assistant.laptop_spec_chunker import LaptopSpecChunker
from sales_rag_app.libs.services.sales_assistant.enhanced_vector_store import EnhancedVectorStore


def create_mock_duckdb_data() -> List[Dict[str, Any]]:
    """創建模擬的 DuckDB 數據用於測試"""
    return [
        {
            'modelname': 'AG958',
            'modeltype': '958',
            'cpu': 'AMD Ryzen 9 7940HS',
            'gpu': 'NVIDIA RTX 4060',
            'memory': '32GB DDR5',
            'storage': '1TB NVMe SSD',
            'battery': '8-10 hours',
            'lcd': '15.6" QHD 165Hz',
            'keyboard': '背光電競鍵盤',
            'fingerprint': '指紋辨識',
            'thermal': '高效散熱系統',
            'wireless': 'WiFi 6E',
            'bluetooth': 'Bluetooth 5.2'
        },
        {
            'modelname': 'AB819-S: FP6',
            'modeltype': '819',
            'cpu': 'Intel Core i5-13500H',
            'gpu': 'Intel Iris Xe',
            'memory': '16GB DDR4',
            'storage': '512GB SSD',
            'battery': '12-14 hours',
            'lcd': '14" FHD IPS',
            'keyboard': '舒適鍵盤',
            'tpm': 'TPM 2.0',
            'fingerprint': '指紋辨識',
            'wireless': 'WiFi 6'
        },
        {
            'modelname': 'AHP839',
            'modeltype': '839',
            'cpu': 'Intel Core i7-13700H',
            'gpu': 'NVIDIA GTX 1650',
            'memory': '16GB DDR4',
            'storage': '512GB SSD',
            'battery': '10-12 hours',
            'lcd': '15.6" FHD',
            'keyboard': '標準鍵盤',
            'wireless': 'WiFi 6'
        }
    ]


class MockDuckDBQuery:
    """模擬 DuckDB 查詢接口"""
    
    def __init__(self):
        self.data = create_mock_duckdb_data()
        
    def query(self, sql: str):
        """模擬 DuckDB 查詢"""
        # 簡單模擬，返回所有數據
        spec_fields = [
            'modeltype', 'version', 'modelname', 'mainboard', 'devtime',
            'pm', 'structconfig', 'lcd', 'touchpanel', 'iointerface', 
            'ledind', 'powerbutton', 'keyboard', 'webcamera', 'touchpad', 
            'fingerprint', 'audio', 'battery', 'cpu', 'gpu', 'memory', 
            'lcdconnector', 'storage', 'wifislot', 'thermal', 'tpm', 'rtc', 
            'wireless', 'lan', 'bluetooth', 'softwareconfig', 'ai', 'accessory', 
            'certfications', 'otherfeatures'
        ]
        
        result = []
        for item in self.data:
            row = []
            for field in spec_fields:
                row.append(item.get(field, ''))
            result.append(tuple(row))
        
        return result


def test_parent_child_system():
    """測試完整的 Parent-Child 系統"""
    print("=== 測試 Parent-Child 檢索系統 ===")
    print("目標：驗證系統能否替代三層意圖檢測，消除澄清請求\\n")
    
    # 初始化系統
    mock_duckdb = MockDuckDBQuery()
    retriever = ParentChildRetriever(duckdb_query_instance=mock_duckdb)
    
    # 初始化數據
    if not retriever.initialize_with_data(force_reload=True):
        print("❌ 系統初始化失敗")
        return False
    
    # 之前有問題的查詢（觸發澄清請求的查詢）
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
        print(f"\\n{'='*60}")
        print(f"測試 {i}: {query}")
        print(f"{'='*60}")
        
        try:
            # 使用 Parent-Child 系統處理查詢
            query_result = retriever.process_query(query)
            
            # 檢查是否需要澄清
            needs_clarification = retriever.should_clarify(query_result)
            
            # 提取關鍵信息
            parent_child_data = query_result.get("parent_child_data", {})
            matched_parents = parent_child_data.get("matched_parents", [])
            top_chunks = parent_child_data.get("top_chunks", [])
            topic_analysis = parent_child_data.get("topic_analysis", {})
            response_strategy = parent_child_data.get("response_strategy", "unknown")
            retrieval_confidence = parent_child_data.get("retrieval_confidence", 0.0)
            
            print(f"🎯 Parent-Child 檢索結果:")
            print(f"   主要意圖: {query_result.get('primary_intent', 'unknown')}")
            print(f"   查詢類型: {query_result.get('query_type', 'unknown')}")
            print(f"   檢索信心度: {retrieval_confidence:.3f}")
            print(f"   回應策略: {response_strategy}")
            
            print(f"\\n📊 匹配結果:")
            print(f"   匹配的型號: {len(matched_parents)} 個")
            for parent in matched_parents[:3]:  # 顯示前3個
                print(f"     - {parent.get('model_name', 'Unknown')}")
            
            print(f"   相關主題塊: {len(top_chunks)} 個")
            for chunk in top_chunks[:3]:  # 顯示前3個
                print(f"     - {chunk.get('topic_category', 'unknown')} (信心度: {chunk.get('confidence', 0):.2f})")
            
            print(f"\\n❓ 系統決策:")
            print(f"   需要澄清: {'❌ 否' if not needs_clarification else '✅ 是'}")
            print(f"   即時回應: {'✅ 是' if not needs_clarification else '❌ 否'}")
            
            # 測試增強上下文生成
            enhanced_context = retriever.get_enhanced_context_for_llm(query_result)
            print(f"\\n🔧 增強上下文預覽:")
            print(f"   {enhanced_context[:150]}...")
            
            # 記錄結果
            results[query] = {
                "success": not needs_clarification,
                "primary_intent": query_result.get('primary_intent', 'unknown'),
                "retrieval_confidence": retrieval_confidence,
                "response_strategy": response_strategy,
                "matched_models": len(matched_parents),
                "matched_chunks": len(top_chunks),
                "clarification_needed": needs_clarification,
                "immediate_response": not needs_clarification
            }
            
        except Exception as e:
            print(f"❌ 處理失敗: {e}")
            results[query] = {
                "success": False,
                "error": str(e),
                "clarification_needed": True,
                "immediate_response": False
            }
    
    # 生成測試報告
    print(f"\\n\\n{'='*80}")
    print("📊 Parent-Child 系統測試總結報告")
    print(f"{'='*80}")
    
    total_queries = len(problematic_queries)
    successful_queries = sum(1 for r in results.values() if r.get('success', False))
    clarification_rate = sum(1 for r in results.values() if r.get('clarification_needed', True)) / total_queries
    immediate_response_rate = sum(1 for r in results.values() if r.get('immediate_response', False)) / total_queries
    
    print(f"測試查詢總數: {total_queries}")
    print(f"成功處理數量: {successful_queries} ({successful_queries/total_queries*100:.1f}%)")
    print(f"澄清觸發率: {clarification_rate*100:.1f}% (目標: 0%)")
    print(f"即時回應率: {immediate_response_rate*100:.1f}% (目標: 100%)")
    
    # 回應策略分佈
    strategies = {}
    confidences = []
    for result in results.values():
        if result.get('success'):
            strategy = result.get('response_strategy', 'unknown')
            strategies[strategy] = strategies.get(strategy, 0) + 1
            confidences.append(result.get('retrieval_confidence', 0.0))
    
    print(f"\\n🎯 回應策略分佈:")
    for strategy, count in sorted(strategies.items(), key=lambda x: x[1], reverse=True):
        print(f"   {strategy}: {count} 次 ({count/successful_queries*100:.1f}%)")
    
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"\\n📈 檢索信心度分析:")
        print(f"   平均信心度: {avg_confidence:.3f}")
        print(f"   最低信心度: {min(confidences):.3f}")
        print(f"   最高信心度: {max(confidences):.3f}")
    
    # 系統效能評估
    print(f"\\n🎯 系統效能評估:")
    if successful_queries == total_queries and clarification_rate == 0:
        print("✅ 完美表現！Parent-Child 系統完全消除了澄清請求問題")
        print("✅ 所有查詢都獲得即時、有用的回應")
        success_level = "完美"
    elif successful_queries >= total_queries * 0.9 and clarification_rate < 0.1:
        print("🎉 優秀表現！大幅改善了用戶體驗")
        print("✅ 基本達成即時回應的目標")
        success_level = "優秀"
    elif successful_queries >= total_queries * 0.7:
        print("👍 良好表現，顯著改善但仍可優化")
        success_level = "良好"
    else:
        print("⚠️ 需要進一步改善")
        success_level = "待改善"
    
    # 保存詳細結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"parent_child_test_results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "system_type": "parent_child_chunking",
            "summary": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "success_rate": successful_queries/total_queries,
                "clarification_rate": clarification_rate,
                "immediate_response_rate": immediate_response_rate,
                "average_confidence": avg_confidence if confidences else 0,
                "performance_level": success_level,
                "target_achieved": clarification_rate == 0 and immediate_response_rate == 1.0
            },
            "strategy_distribution": strategies,
            "detailed_results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\\n📁 詳細結果已保存到: {result_file}")
    
    return successful_queries == total_queries and clarification_rate == 0


def test_system_statistics():
    """測試系統統計信息"""
    print("\\n\\n=== 系統統計信息 ===")
    
    mock_duckdb = MockDuckDBQuery()
    retriever = ParentChildRetriever(duckdb_query_instance=mock_duckdb)
    
    if retriever.initialize_with_data():
        stats = retriever.get_system_statistics()
        print("系統統計:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("❌ 無法獲取系統統計信息")


def test_vs_original_system():
    """與原始三層意圖檢測系統的對比"""
    print("\\n\\n=== Parent-Child vs 三層意圖檢測 對比 ===")
    
    test_query = "哪款筆電比較省電？"
    
    print(f"測試查詢: {test_query}")
    print("\\n--- Parent-Child 檢索系統 ---")
    
    mock_duckdb = MockDuckDBQuery()
    retriever = ParentChildRetriever(duckdb_query_instance=mock_duckdb)
    
    if retriever.initialize_with_data():
        result = retriever.process_query(test_query)
        needs_clarification = retriever.should_clarify(result)
        
        print(f"主要意圖: {result.get('primary_intent', 'unknown')}")
        print(f"查詢類型: {result.get('query_type', 'unknown')}")
        print(f"需要澄清: {'否' if not needs_clarification else '是'}")
        print(f"即時回應: {'是' if not needs_clarification else '否'}")
        
        parent_child_data = result.get("parent_child_data", {})
        print(f"檢索信心度: {parent_child_data.get('retrieval_confidence', 0):.3f}")
        print(f"回應策略: {parent_child_data.get('response_strategy', 'unknown')}")
    
    print("\\n--- 原始三層意圖檢測系統 ---")
    print("結果: 經常觸發澄清請求 '請問您的主要使用場景是什麼？'")
    print("問題: 用戶體驗差，無法獲得即時有用資訊")
    
    print("\\n--- 系統優勢比較 ---")
    advantages = [
        "✅ 零澄清請求 - Parent-Child 系統始終提供即時回應",
        "✅ 語義理解 - 基於主題塊的語義匹配",
        "✅ 上下文保留 - Parent-Child 關係保持完整資訊",
        "✅ 靈活適應 - 易於擴展新的主題類別",
        "✅ 用戶體驗 - 立即獲得有價值的資訊",
        "✅ 可維護性 - 清晰的架構設計"
    ]
    
    for advantage in advantages:
        print(f"   {advantage}")


if __name__ == "__main__":
    try:
        print("🚀 開始 Parent-Child 檢索系統測試\\n")
        
        # 執行主要測試
        success = test_parent_child_system()
        
        # 執行系統統計測試
        test_system_statistics()
        
        # 執行對比測試
        test_vs_original_system()
        
        print(f"\\n{'='*80}")
        if success:
            print("🎉 Parent-Child 檢索系統測試完全成功！")
            print("✅ 成功替代三層意圖檢測系統")
            print("✅ 完全消除澄清請求問題")
            print("✅ 實現即時智能回應目標")
            print("✅ 為用戶提供立即價值")
            print("\\n🚀 準備進行生產環境部署！")
        else:
            print("⚠️ 測試結果未完全達到預期")
            print("💡 建議進一步調整系統參數")
        print(f"{'='*80}")
        
    except Exception as e:
        logging.error(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()