#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試擴展後的備用答案生成功能
驗證所有新增的筆電特性欄位是否正確提取和顯示
"""

import asyncio
import json
import sys
import os

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from libs.services.sales_assistant.service import SalesAssistantService

async def test_extended_fallback_features():
    """測試擴展後的備用答案生成功能"""
    
    print("🔧 初始化 SalesAssistantService...")
    service = SalesAssistantService()
    
    # 模擬數據庫內容
    mock_context_data = [
        {
            "modelname": "AHP958",
            "cpu": "AMD Ryzen™ 7 7735HS, 8 cores, 16 threads, up to 4.7 GHz, 16 MB cache, TDP: 35W",
            "gpu": "AMD Radeon™ RX 7600S, 8GB GDDR6, RDNA 3, 2048 cores, up to 2200 MHz, Ray Tracing support, FSR 3.0",
            "memory": "DDR5 4800MHz, 16GB, Dual Channel, 2 slots, up to 64GB",
            "storage": "1TB NVMe SSD, PCIe 4.0, up to 7000 MB/s, 2 slots",
            "battery": "76Wh, up to 8 hours, Fast Charging, 230W adapter",
            "lcd": "15.6\" FHD 1920×1080, 144Hz, IPS, sRGB 100%, 300 nits, Touch support",
            "structconfig": "Weight: 1850g, Dimension: 359×259×19.9mm, Form: Clamshell, Material: Aluminum, Build Quality: Premium",
            "thermal": "Dual Fan cooling system, 45W TDP, Excellent thermal performance, Quiet operation",
            "iointerface": "2 USB 3.2, 1 USB-C, 1 HDMI 2.1, 1 DisplayPort, 1 Audio jack, SD card reader, Ethernet port, WiFi 6E + Bluetooth 5.2",
            "audio": "Harman Kardon dual speakers, Premium audio quality, Array microphone, Realtek audio codec",
            "keyboard": "Membrane keyboard, RGB backlight, 1.5mm key travel, Numpad, Function keys",
            "trackpad": "5.5\" precision touchpad, Gesture support, High precision tracking"
        },
        {
            "modelname": "AHP819",
            "cpu": "AMD Ryzen™ 5 7535U, 6 cores, 12 threads, up to 4.5 GHz, 16 MB cache, TDP: 28W",
            "gpu": "AMD Radeon™ 660M, 4GB GDDR6, RDNA 2, 1024 cores, up to 1900 MHz",
            "memory": "DDR5 4800MHz, 8GB, Single Channel, 1 slot, up to 32GB",
            "storage": "512GB NVMe SSD, PCIe 4.0, up to 5000 MB/s, 1 slot",
            "battery": "52Wh, up to 6 hours, Standard charging, 135W adapter",
            "lcd": "14\" FHD 1920×1080, 60Hz, IPS, sRGB 100%, 250 nits",
            "structconfig": "Weight: 1450g, Dimension: 324×220×17.9mm, Form: Clamshell, Material: Aluminum, Build Quality: Good",
            "thermal": "Single Fan cooling system, 28W TDP, Good thermal performance, Moderate noise",
            "iointerface": "2 USB 3.2, 1 USB-C, 1 HDMI 2.0, 1 Audio jack, WiFi 6 + Bluetooth 5.1",
            "audio": "Standard dual speakers, High audio quality, Standard microphone, Realtek audio codec",
            "keyboard": "Membrane keyboard, White backlight, 1.2mm key travel, Function keys",
            "trackpad": "4.5\" precision touchpad, Gesture support, Standard precision"
        }
    ]
    
    target_models = ["AHP958", "AHP819"]
    
    # 測試不同類型的查詢
    test_queries = [
        "比較螢幕規格",
        "電池續航能力比較",
        "CPU性能對比",
        "GPU顯卡比較",
        "記憶體規格",
        "硬碟儲存比較",
        "重量便攜性",
        "散熱系統比較",
        "接口連接性",
        "音效系統",
        "鍵盤體驗",
        "觸控板功能",
        "遊戲性能比較",
        "商務辦公特性",
        "設計創作功能",
        "綜合規格比較"
    ]
    
    print(f"\n📊 開始測試 {len(test_queries)} 種查詢類型的備用答案生成...")
    
    results = {}
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 測試 {i}/{len(test_queries)}: {query}")
        
        try:
            # 生成備用表格
            fallback_table = service._generate_fallback_table(mock_context_data, target_models, query)
            
            # 生成備用摘要
            fallback_summary = service._generate_fallback_summary(query, mock_context_data, target_models)
            
            # 格式化回應
            formatted_response = service._format_response_with_beautiful_table(
                fallback_summary, fallback_table, target_models
            )
            
            results[query] = {
                "summary": fallback_summary,
                "table_features": len(fallback_table),
                "table_content": fallback_table,
                "formatted_response": formatted_response
            }
            
            print(f"✅ 成功生成備用答案")
            print(f"   📝 摘要: {fallback_summary[:100]}...")
            print(f"   📊 特性數量: {len(fallback_table)}")
            
            # 顯示表格內容
            if fallback_table:
                print(f"   📋 特性列表:")
                for row in fallback_table[:3]:  # 只顯示前3個特性
                    feature = row.get("feature", "Unknown")
                    print(f"      - {feature}")
                if len(fallback_table) > 3:
                    print(f"      ... 還有 {len(fallback_table) - 3} 個特性")
            
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            results[query] = {"error": str(e)}
    
    # 生成詳細報告
    print(f"\n📈 測試結果統計:")
    
    successful_tests = sum(1 for result in results.values() if "error" not in result)
    total_tests = len(results)
    
    print(f"✅ 成功測試: {successful_tests}/{total_tests}")
    print(f"📊 成功率: {successful_tests/total_tests*100:.1f}%")
    
    # 分析特性覆蓋情況
    feature_coverage = {}
    for query, result in results.items():
        if "error" not in result:
            table = result["table_content"]
            for row in table:
                feature = row.get("feature", "Unknown")
                if feature not in feature_coverage:
                    feature_coverage[feature] = 0
                feature_coverage[feature] += 1
    
    print(f"\n🎯 特性覆蓋統計:")
    for feature, count in sorted(feature_coverage.items(), key=lambda x: x[1], reverse=True):
        print(f"   {feature}: {count} 次")
    
    # 保存詳細結果
    output_file = "extended_fallback_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果已保存到: {output_file}")
    
    # 顯示最佳和最差測試案例
    print(f"\n🏆 最佳測試案例:")
    best_query = max(results.items(), key=lambda x: len(x[1].get("table_content", [])) if "error" not in x[1] else 0)
    print(f"   查詢: {best_query[0]}")
    print(f"   特性數量: {len(best_query[1].get('table_content', []))}")
    
    print(f"\n⚠️ 需要改進的測試案例:")
    failed_tests = [query for query, result in results.items() if "error" in result]
    if failed_tests:
        for query in failed_tests[:3]:
            print(f"   - {query}: {results[query]['error']}")
    else:
        print("   所有測試都成功完成！")
    
    return results

def test_specific_features():
    """測試特定特性的提取邏輯"""
    
    print("\n🔬 測試特定特性提取邏輯...")
    
    service = SalesAssistantService()
    
    # 測試數據
    test_data = {
        "cpu": "AMD Ryzen™ 7 7735HS, 8 cores, 16 threads, up to 4.7 GHz, 16 MB cache, TDP: 35W",
        "gpu": "AMD Radeon™ RX 7600S, 8GB GDDR6, RDNA 3, 2048 cores, up to 2200 MHz, Ray Tracing support, FSR 3.0",
        "memory": "DDR5 4800MHz, 16GB, Dual Channel, 2 slots, up to 64GB",
        "storage": "1TB NVMe SSD, PCIe 4.0, up to 7000 MB/s, 2 slots",
        "battery": "76Wh, up to 8 hours, Fast Charging, 230W adapter",
        "lcd": "15.6\" FHD 1920×1080, 144Hz, IPS, sRGB 100%, 300 nits, Touch support"
    }
    
    # 測試 CPU 特性提取
    print("\n💻 CPU 特性提取測試:")
    cpu_features = [
        "CPU Model", "CPU Architecture", "CPU TDP", "CPU Cores", 
        "CPU Threads", "CPU Base Speed", "CPU Boost Speed", "CPU Cache"
    ]
    
    for feature in cpu_features:
        row = {"feature": feature}
        # 模擬提取邏輯
        if feature == "CPU Model":
            cpu_match = re.search(r"Ryzen™\s+\d+\s+\d+[A-Z]*[HS]*", test_data["cpu"])
            result = cpu_match.group(0) if cpu_match else "N/A"
        elif feature == "CPU Cores":
            cores_match = re.search(r"(\d+)\s*cores", test_data["cpu"])
            result = f"{cores_match.group(1)} Cores" if cores_match else "N/A"
        elif feature == "CPU Threads":
            threads_match = re.search(r"(\d+)\s*threads", test_data["cpu"])
            result = f"{threads_match.group(1)} Threads" if threads_match else "N/A"
        elif feature == "CPU Boost Speed":
            boost_match = re.search(r"up to\s*(\d+\.?\d*)\s*GHz", test_data["cpu"])
            result = f"Up to {boost_match.group(1)} GHz" if boost_match else "N/A"
        else:
            result = "N/A"
        
        print(f"   {feature}: {result}")
    
    # 測試 GPU 特性提取
    print("\n🎮 GPU 特性提取測試:")
    gpu_features = [
        "GPU Model", "GPU Memory", "GPU Power", "GPU Architecture",
        "GPU Cores", "GPU Boost Clock", "Ray Tracing", "DLSS/FSR Support"
    ]
    
    for feature in gpu_features:
        if feature == "GPU Model":
            gpu_match = re.search(r"AMD Radeon™\s+[A-Z0-9]+[A-Z]*", test_data["gpu"])
            result = gpu_match.group(0) if gpu_match else "N/A"
        elif feature == "GPU Memory":
            memory_match = re.search(r"(\d+GB)\s+GDDR\d+", test_data["gpu"])
            result = memory_match.group(1) if memory_match else "N/A"
        elif feature == "Ray Tracing":
            result = "Yes" if "ray tracing" in test_data["gpu"].lower() else "No"
        elif feature == "DLSS/FSR Support":
            features = []
            if "fsr" in test_data["gpu"].lower():
                features.append("FSR")
            if "dlss" in test_data["gpu"].lower():
                features.append("DLSS")
            result = ", ".join(features) if features else "N/A"
        else:
            result = "N/A"
        
        print(f"   {feature}: {result}")

if __name__ == "__main__":
    import re
    
    print("🚀 開始測試擴展後的備用答案生成功能")
    print("=" * 60)
    
    # 運行主要測試
    results = asyncio.run(test_extended_fallback_features())
    
    # 運行特定特性測試
    test_specific_features()
    
    print("\n🎉 測試完成！")
    print("=" * 60) 