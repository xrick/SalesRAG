#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parent-Child Chunking 系統綜合測試程式

測試完整的 Parent-Child 檢索系統功能，包括：
1. 基礎功能測試
2. 邊界情況測試  
3. 性能基準測試
4. 對話記憶測試
5. 與舊系統對比測試
"""

import sys
import os
import json
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 導入 Parent-Child 系統組件
from sales_rag_app.libs.services.sales_assistant.parent_child_retriever import ParentChildRetriever
from sales_rag_app.libs.services.sales_assistant.laptop_spec_chunker import LaptopSpecChunker
from sales_rag_app.libs.services.sales_assistant.enhanced_vector_store import EnhancedVectorStore
from sales_rag_app.libs.services.sales_assistant.conversation_memory import ConversationMemoryManager


class MockDuckDBQuery:
    """模擬 DuckDB 查詢接口"""
    
    def __init__(self):
        self.data = self._create_comprehensive_test_data()
        
    def _create_comprehensive_test_data(self) -> List[Dict[str, Any]]:
        """創建更全面的測試數據"""
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
                'bluetooth': 'Bluetooth 5.2',
                'tpm': '',
                'version': '',
                'mainboard': '',
                'devtime': '',
                'pm': '',
                'structconfig': '',
                'touchpanel': '',
                'iointerface': '',
                'ledind': '',
                'powerbutton': '',
                'webcamera': '',
                'touchpad': '',
                'audio': '',
                'lcdconnector': '',
                'wifislot': '',
                'rtc': '',
                'lan': '',
                'softwareconfig': '',
                'ai': '',
                'accessory': '',
                'certfications': '',
                'otherfeatures': ''
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
                'wireless': 'WiFi 6',
                'bluetooth': '',
                'thermal': '',
                'version': '',
                'mainboard': '',
                'devtime': '',
                'pm': '',
                'structconfig': '',
                'touchpanel': '',
                'iointerface': '',
                'ledind': '',
                'powerbutton': '',
                'webcamera': '',
                'touchpad': '',
                'audio': '',
                'lcdconnector': '',
                'wifislot': '',
                'rtc': '',
                'lan': '',
                'softwareconfig': '',
                'ai': '',
                'accessory': '',
                'certfications': '',
                'otherfeatures': ''
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
                'wireless': 'WiFi 6',
                'bluetooth': '',
                'fingerprint': '',
                'thermal': '',
                'tpm': '',
                'version': '',
                'mainboard': '',
                'devtime': '',
                'pm': '',
                'structconfig': '',
                'touchpanel': '',
                'iointerface': '',
                'ledind': '',
                'powerbutton': '',
                'webcamera': '',
                'touchpad': '',
                'audio': '',
                'lcdconnector': '',
                'wifislot': '',
                'rtc': '',
                'lan': '',
                'softwareconfig': '',
                'ai': '',
                'accessory': '',
                'certfications': '',
                'otherfeatures': ''
            },
            {
                'modelname': 'AMD819-S: FT6',
                'modeltype': '819',
                'cpu': 'AMD Ryzen 5 7530U',
                'gpu': 'AMD Radeon Graphics',
                'memory': '16GB DDR4',
                'storage': '512GB SSD',
                'battery': '12-14 hours',
                'lcd': '14" FHD IPS',
                'keyboard': '舒適鍵盤',
                'wireless': 'WiFi 6',
                'bluetooth': 'Bluetooth 5.1',
                'fingerprint': '指紋辨識',
                'thermal': '智能散熱',
                'tpm': 'TPM 2.0',
                'structconfig': 'Weight: 1450g\nDimension: 324 × 210 × 19.5mm\nForm: Compact Business Laptop',
                'version': '',
                'mainboard': '',
                'devtime': '',
                'pm': '',
                'touchpanel': '',
                'iointerface': '',
                'ledind': '',
                'powerbutton': '',
                'webcamera': '',
                'touchpad': '',
                'audio': '',
                'lcdconnector': '',
                'wifislot': '',
                'rtc': '',
                'lan': '',
                'softwareconfig': '',
                'ai': '',
                'accessory': '',
                'certfications': '',
                'otherfeatures': ''
            },
            {
                'modelname': 'AMD819: FT6',
                'modeltype': '819',
                'cpu': 'AMD Ryzen 7 7730U',
                'gpu': 'AMD Radeon Graphics',
                'memory': '16GB DDR4',
                'storage': '1TB SSD',
                'battery': '13-15 hours',
                'lcd': '14" FHD IPS',
                'keyboard': '背光鍵盤',
                'wireless': 'WiFi 6',
                'bluetooth': 'Bluetooth 5.2',
                'fingerprint': '指紋辨識',
                'thermal': '高效散熱',
                'tpm': 'TPM 2.0',
                'structconfig': 'Weight: 1380g\nDimension: 320 × 208 × 18.8mm\nForm: Ultralight Business Laptop',
                'version': '',
                'mainboard': '',
                'devtime': '',
                'pm': '',
                'touchpanel': '',
                'iointerface': '',
                'ledind': '',
                'powerbutton': '',
                'webcamera': '',
                'touchpad': '',
                'audio': '',
                'lcdconnector': '',
                'wifislot': '',
                'rtc': '',
                'lan': '',
                'softwareconfig': '',
                'ai': '',
                'accessory': '',
                'certfications': '',
                'otherfeatures': ''
            }
        ]
        
    def query(self, sql: str):
        """模擬 DuckDB 查詢"""
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


class ParentChildTestSuite:
    """Parent-Child 檢索系統測試套件"""
    
    def __init__(self):
        self.mock_duckdb = MockDuckDBQuery()
        self.retriever = ParentChildRetriever(duckdb_query_instance=self.mock_duckdb)
        self.memory_manager = ConversationMemoryManager()
        self.test_results = {}
        
    def setup(self) -> bool:
        """設置測試環境"""
        print("🔧 設置測試環境...")
        
        # 初始化 Parent-Child 系統
        if not self.retriever.initialize_with_data(force_reload=True):
            print("❌ Parent-Child 系統初始化失敗")
            return False
            
        print("✅ Parent-Child 系統初始化成功")
        return True
    
    def test_basic_functionality(self) -> Dict[str, Any]:
        """測試基礎功能"""
        print("\n" + "="*60)
        print("📋 測試 1: 基礎功能測試")
        print("="*60)
        
        test_queries = [
            "哪款筆電比較省電？",
            "推薦適合遊戲的",
            "學生用什麼好？",
            "螢幕效果怎麼樣？",
            "筆電規格",
            "適合辦公的筆電",
            "請比較AMD819-S: FT6與AMD819: FT6何者更輕便？"  # Specific problematic query
        ]
        
        results = {}
        success_count = 0
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n測試 1.{i}: {query}")
            
            try:
                start_time = time.time()
                query_result = self.retriever.process_query(query)
                processing_time = time.time() - start_time
                
                needs_clarification = self.retriever.should_clarify(query_result)
                parent_child_data = query_result.get("parent_child_data", {})
                
                result = {
                    "success": not needs_clarification,
                    "processing_time": processing_time,
                    "primary_intent": query_result.get('primary_intent', 'unknown'),
                    "retrieval_confidence": parent_child_data.get('retrieval_confidence', 0.0),
                    "response_strategy": parent_child_data.get('response_strategy', 'unknown'),
                    "matched_models": len(parent_child_data.get('matched_parents', [])),
                    "matched_chunks": len(parent_child_data.get('top_chunks', [])),
                    "clarification_needed": needs_clarification
                }
                
                if result["success"]:
                    success_count += 1
                    print(f"   ✅ 成功 - 意圖: {result['primary_intent']}, 策略: {result['response_strategy']}")
                    print(f"   📊 信心度: {result['retrieval_confidence']:.3f}, 處理時間: {processing_time:.3f}s")
                else:
                    print(f"   ❌ 失敗 - 觸發澄清請求")
                
                results[query] = result
                
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
                results[query] = {"success": False, "error": str(e)}
        
        summary = {
            "total_queries": len(test_queries),
            "successful_queries": success_count,
            "success_rate": success_count / len(test_queries),
            "average_processing_time": sum(r.get("processing_time", 0) for r in results.values()) / len(results),
            "results": results
        }
        
        print(f"\n📊 基礎功能測試結果:")
        print(f"   成功率: {summary['success_rate']*100:.1f}% ({success_count}/{len(test_queries)})")
        print(f"   平均處理時間: {summary['average_processing_time']:.3f}s")
        
        return summary
    
    def test_edge_cases(self) -> Dict[str, Any]:
        """測試邊界情況"""
        print("\n" + "="*60)
        print("🔍 測試 2: 邊界情況測試")
        print("="*60)
        
        edge_cases = [
            ("空查詢", ""),
            ("單字查詢", "筆電"),
            ("英文查詢", "laptop gaming"),
            ("混合語言", "gaming 筆電 performance"),
            ("數字查詢", "958"),
            ("特殊符號", "筆電????"),
            ("超長查詢", "我想要一台非常適合遊戲的筆電而且電池續航力要很好螢幕要很大顯卡要很強處理器要很快記憶體要很多儲存空間要很大"),
            ("模糊查詢", "有什麼推薦的嗎"),
            ("比較查詢", "958和819哪個好"),
            ("否定查詢", "不要太貴的筆電")
        ]
        
        results = {}
        robust_count = 0
        
        for i, (case_name, query) in enumerate(edge_cases, 1):
            print(f"\n測試 2.{i}: {case_name} - '{query}'")
            
            try:
                start_time = time.time()
                query_result = self.retriever.process_query(query)
                processing_time = time.time() - start_time
                
                needs_clarification = self.retriever.should_clarify(query_result)
                parent_child_data = query_result.get("parent_child_data", {})
                
                # 評估系統健壯性
                is_robust = (
                    not needs_clarification and  # 不觸發澄清
                    processing_time < 2.0 and   # 處理時間合理
                    parent_child_data.get('retrieval_confidence', 0) >= 0  # 有效的信心度
                )
                
                if is_robust:
                    robust_count += 1
                    print(f"   ✅ 健壯處理")
                else:
                    print(f"   ⚠️ 邊界處理")
                
                results[case_name] = {
                    "query": query,
                    "robust": is_robust,
                    "processing_time": processing_time,
                    "clarification_needed": needs_clarification,
                    "confidence": parent_child_data.get('retrieval_confidence', 0.0)
                }
                
            except Exception as e:
                print(f"   ❌ 異常: {e}")
                results[case_name] = {
                    "query": query,
                    "robust": False,
                    "error": str(e)
                }
        
        summary = {
            "total_cases": len(edge_cases),
            "robust_cases": robust_count,
            "robustness_rate": robust_count / len(edge_cases),
            "results": results
        }
        
        print(f"\n📊 邊界情況測試結果:")
        print(f"   健壯性: {summary['robustness_rate']*100:.1f}% ({robust_count}/{len(edge_cases)})")
        
        return summary
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """測試性能基準"""
        print("\n" + "="*60)
        print("⚡ 測試 3: 性能基準測試")
        print("="*60)
        
        # 準備測試查詢
        benchmark_queries = [
            "哪款筆電比較省電？",
            "推薦適合遊戲的",
            "學生用什麼好？",
            "螢幕效果怎麼樣？",
            "適合辦公的筆電"
        ] * 10  # 重複10次進行壓力測試
        
        print(f"執行 {len(benchmark_queries)} 次查詢的性能測試...")
        
        processing_times = []
        memory_stats = []
        
        for i, query in enumerate(benchmark_queries):
            start_time = time.time()
            
            try:
                query_result = self.retriever.process_query(query)
                processing_time = time.time() - start_time
                processing_times.append(processing_time)
                
                # 記錄系統統計（每10次記錄一次）
                if i % 10 == 0:
                    stats = self.retriever.get_system_statistics()
                    memory_stats.append(stats)
                
            except Exception as e:
                print(f"查詢 {i+1} 失敗: {e}")
        
        # 計算性能指標
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
            
            # 計算 95th percentile
            sorted_times = sorted(processing_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index]
            
            summary = {
                "total_queries": len(processing_times),
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "p95_time": p95_time,
                "queries_per_second": 1.0 / avg_time if avg_time > 0 else 0,
                "memory_stats": memory_stats[-1] if memory_stats else {}
            }
            
            print(f"\n📊 性能基準測試結果:")
            print(f"   總查詢數: {summary['total_queries']}")
            print(f"   平均處理時間: {avg_time:.3f}s")
            print(f"   最快處理時間: {min_time:.3f}s")
            print(f"   最慢處理時間: {max_time:.3f}s")
            print(f"   95%處理時間: {p95_time:.3f}s")
            print(f"   每秒查詢數: {summary['queries_per_second']:.1f} QPS")
            
            return summary
        
        return {"error": "沒有成功的查詢用於性能分析"}
    
    def test_conversation_memory(self) -> Dict[str, Any]:
        """測試對話記憶功能"""
        print("\n" + "="*60)
        print("🧠 測試 4: 對話記憶測試")
        print("="*60)
        
        session_id = str(uuid.uuid4())
        print(f"測試會話 ID: {session_id}")
        
        # 模擬多輪對話
        conversation_flow = [
            "我想買筆電",
            "主要用來遊戲",
            "預算不要太高",
            "958系列怎麼樣？",
            "和819比較呢？"
        ]
        
        results = []
        
        for i, query in enumerate(conversation_flow, 1):
            print(f"\n對話輪次 {i}: {query}")
            
            try:
                # 使用對話記憶生成上下文感知查詢
                contextualized_query = self.memory_manager.create_contextualized_query(session_id, query)
                
                # 處理查詢
                query_result = self.retriever.process_query(contextualized_query)
                parent_child_data = query_result.get("parent_child_data", {})
                
                # 記錄對話輪次
                turn = self.memory_manager.add_conversation_turn(
                    session_id=session_id,
                    user_query=query,
                    system_response="模擬回應",
                    query_intent=query_result.get('primary_intent', 'unknown'),
                    retrieval_confidence=parent_child_data.get('retrieval_confidence', 0.0),
                    response_strategy=parent_child_data.get('response_strategy', 'unknown'),
                    matched_models=[p.get('model_name', '') for p in parent_child_data.get('matched_parents', [])]
                )
                
                result = {
                    "turn_id": turn.turn_id,
                    "original_query": query,
                    "contextualized_query": contextualized_query,
                    "intent": query_result.get('primary_intent'),
                    "strategy": parent_child_data.get('response_strategy'),
                    "confidence": parent_child_data.get('retrieval_confidence', 0.0)
                }
                
                results.append(result)
                
                print(f"   原始查詢: {query}")
                print(f"   上下文查詢: {contextualized_query}")
                print(f"   意圖: {result['intent']}, 策略: {result['strategy']}")
                
            except Exception as e:
                print(f"   ❌ 對話輪次失敗: {e}")
                results.append({"error": str(e)})
        
        # 獲取對話上下文
        final_context = self.memory_manager.get_conversation_context(session_id)
        
        summary = {
            "session_id": session_id,
            "total_turns": len(conversation_flow),
            "successful_turns": len([r for r in results if "error" not in r]),
            "final_context": final_context,
            "conversation_results": results
        }
        
        print(f"\n📊 對話記憶測試結果:")
        print(f"   對話輪次: {summary['total_turns']}")
        print(f"   成功輪次: {summary['successful_turns']}")
        print(f"   用戶偏好: {final_context.get('user_preferences', {})}")
        print(f"   對話模式: {final_context.get('conversation_flow', {}).get('pattern', 'unknown')}")
        
        return summary
    
    def test_system_comparison(self) -> Dict[str, Any]:
        """與舊系統的對比測試"""
        print("\n" + "="*60)
        print("📈 測試 5: 系統對比測試")
        print("="*60)
        
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
            "適合辦公的筆電",
            "請比較AMD819-S: FT6與AMD819: FT6何者更輕便？"  # New problematic query
        ]
        
        print("測試之前觸發澄清請求的查詢...")
        
        results = {}
        perfect_responses = 0
        
        for i, query in enumerate(problematic_queries, 1):
            print(f"\n對比測試 {i}: {query}")
            
            try:
                query_result = self.retriever.process_query(query)
                needs_clarification = self.retriever.should_clarify(query_result)
                parent_child_data = query_result.get("parent_child_data", {})
                
                result = {
                    "old_system": "觸發澄清請求",
                    "new_system": "即時回應" if not needs_clarification else "澄清請求",
                    "improvement": not needs_clarification,
                    "confidence": parent_child_data.get('retrieval_confidence', 0.0),
                    "strategy": parent_child_data.get('response_strategy', 'unknown')
                }
                
                if result["improvement"]:
                    perfect_responses += 1
                    print(f"   ✅ 改善成功 - 舊系統: 澄清請求 → 新系統: 即時回應")
                    print(f"   📊 策略: {result['strategy']}, 信心度: {result['confidence']:.3f}")
                else:
                    print(f"   ⚠️ 仍需澄清")
                
                results[query] = result
                
            except Exception as e:
                print(f"   ❌ 測試失敗: {e}")
                results[query] = {"error": str(e), "improvement": False}
        
        improvement_rate = perfect_responses / len(problematic_queries)
        
        summary = {
            "tested_queries": len(problematic_queries),
            "improved_queries": perfect_responses,
            "improvement_rate": improvement_rate,
            "old_system_clarification_rate": 1.0,  # 舊系統100%觸發澄清
            "new_system_clarification_rate": 1.0 - improvement_rate,
            "results": results
        }
        
        print(f"\n📊 系統對比結果:")
        print(f"   測試查詢數: {summary['tested_queries']}")
        print(f"   改善查詢數: {summary['improved_queries']}")
        print(f"   改善率: {improvement_rate*100:.1f}%")
        print(f"   舊系統澄清率: {summary['old_system_clarification_rate']*100:.1f}%")
        print(f"   新系統澄清率: {summary['new_system_clarification_rate']*100:.1f}%")
        
        return summary
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """執行綜合測試"""
        print("🚀 開始 Parent-Child Chunking 系統綜合測試")
        print("="*80)
        
        if not self.setup():
            return {"error": "測試環境設置失敗"}
        
        # 執行所有測試
        test_results = {}
        
        try:
            test_results["basic_functionality"] = self.test_basic_functionality()
            test_results["edge_cases"] = self.test_edge_cases()
            test_results["performance_benchmarks"] = self.test_performance_benchmarks()
            test_results["conversation_memory"] = self.test_conversation_memory()
            test_results["system_comparison"] = self.test_system_comparison()
            
            # 生成綜合評估
            overall_assessment = self._generate_overall_assessment(test_results)
            test_results["overall_assessment"] = overall_assessment
            
            # 保存測試結果
            self._save_test_results(test_results)
            
            return test_results
            
        except Exception as e:
            print(f"❌ 測試過程中發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _generate_overall_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成綜合評估"""
        print("\n" + "="*60)
        print("🎯 綜合評估")
        print("="*60)
        
        # 提取關鍵指標
        basic_success_rate = results.get("basic_functionality", {}).get("success_rate", 0)
        edge_robustness = results.get("edge_cases", {}).get("robustness_rate", 0)
        avg_processing_time = results.get("performance_benchmarks", {}).get("average_time", 999)
        improvement_rate = results.get("system_comparison", {}).get("improvement_rate", 0)
        
        # 計算綜合分數
        functionality_score = basic_success_rate * 25  # 25分
        robustness_score = edge_robustness * 20       # 20分
        performance_score = min(20, (1.0 / max(avg_processing_time, 0.001)) * 5)  # 20分，1秒=5分
        improvement_score = improvement_rate * 35      # 35分
        
        total_score = functionality_score + robustness_score + performance_score + improvement_score
        
        # 評級
        if total_score >= 90:
            grade = "A+ (優秀)"
        elif total_score >= 80:
            grade = "A (良好)"
        elif total_score >= 70:
            grade = "B+ (滿意)"
        elif total_score >= 60:
            grade = "B (及格)"
        else:
            grade = "C (需改善)"
        
        assessment = {
            "total_score": total_score,
            "grade": grade,
            "functionality_score": functionality_score,
            "robustness_score": robustness_score,
            "performance_score": performance_score,
            "improvement_score": improvement_score,
            "key_metrics": {
                "basic_success_rate": f"{basic_success_rate*100:.1f}%",
                "edge_robustness": f"{edge_robustness*100:.1f}%",
                "avg_processing_time": f"{avg_processing_time:.3f}s",
                "improvement_rate": f"{improvement_rate*100:.1f}%"
            },
            "recommendations": self._generate_recommendations(results)
        }
        
        print(f"📊 綜合評分: {total_score:.1f}/100 - {grade}")
        print(f"   功能性: {functionality_score:.1f}/25")
        print(f"   健壯性: {robustness_score:.1f}/20") 
        print(f"   性能: {performance_score:.1f}/20")
        print(f"   改善度: {improvement_score:.1f}/35")
        
        return assessment
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成改善建議"""
        recommendations = []
        
        basic_success = results.get("basic_functionality", {}).get("success_rate", 0)
        if basic_success < 0.9:
            recommendations.append("建議加強基礎功能的意圖識別準確性")
        
        edge_robustness = results.get("edge_cases", {}).get("robustness_rate", 0)
        if edge_robustness < 0.8:
            recommendations.append("建議改善邊界情況的處理機制")
        
        avg_time = results.get("performance_benchmarks", {}).get("average_time", 0)
        if avg_time > 0.5:
            recommendations.append("建議優化查詢處理性能，目標處理時間 < 0.5s")
        
        improvement = results.get("system_comparison", {}).get("improvement_rate", 0)
        if improvement < 1.0:
            recommendations.append("建議進一步減少澄清請求的觸發頻率")
        
        if not recommendations:
            recommendations.append("系統表現優秀，建議持續監控並定期優化")
        
        return recommendations
    
    def _save_test_results(self, results: Dict[str, Any]):
        """保存測試結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"parent_child_comprehensive_test_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_timestamp": datetime.now().isoformat(),
                "test_type": "comprehensive_parent_child_chunking",
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 測試結果已保存到: {result_file}")


def main():
    """主函式"""
    test_suite = ParentChildTestSuite()
    
    try:
        results = test_suite.run_comprehensive_test()
        
        print("\n" + "="*80)
        if "error" not in results:
            overall = results.get("overall_assessment", {})
            print(f"🎉 Parent-Child Chunking 系統綜合測試完成！")
            print(f"📊 總分: {overall.get('total_score', 0):.1f}/100")
            print(f"🏆 評級: {overall.get('grade', '未知')}")
            
            # 顯示關鍵指標
            metrics = overall.get("key_metrics", {})
            print(f"\n📈 關鍵指標:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
            
            # 顯示建議
            recommendations = overall.get("recommendations", [])
            if recommendations:
                print(f"\n💡 改善建議:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
        else:
            print(f"❌ 測試失敗: {results['error']}")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n⚠️ 測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試過程發生未預期錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()