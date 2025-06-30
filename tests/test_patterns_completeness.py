#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 patterns 和 keywords 的完整性
檢查是否有遺漏的簡體關鍵字
"""

import json
import re
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_file(file_path):
    """載入 JSON 檔案"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入檔案 {file_path} 失敗: {e}")
        return None

def extract_keywords_from_patterns(patterns_data):
    """從 patterns 中提取關鍵字"""
    keywords = {}
    
    for entity_type, config in patterns_data.get("entity_patterns", {}).items():
        keywords[entity_type] = []
        for pattern in config.get("patterns", []):
            # 提取正則表達式中的關鍵字
            # 移除轉義字符和正則表達式語法
            clean_pattern = pattern.replace("\\b", "").replace("\\s*", " ").replace("\\d+", "")
            # 提取括號內的關鍵字
            matches = re.findall(r'\([^)]*\)', clean_pattern)
            for match in matches:
                # 移除括號和管道符號
                keywords_str = match.strip("()")
                if "|" in keywords_str:
                    keywords_list = [k.strip() for k in keywords_str.split("|")]
                    keywords[entity_type].extend(keywords_list)
                else:
                    keywords[entity_type].append(keywords_str.strip())
    
    return keywords

def extract_keywords_from_intents(intents_data):
    """從 intents 中提取關鍵字"""
    keywords = {}
    
    for intent_name, config in intents_data.get("intent_keywords", {}).items():
        keywords[intent_name] = config.get("keywords", [])
    
    return keywords

def check_simplified_chinese_keywords():
    """檢查簡體中文關鍵字的完整性"""
    print("=== 檢查 patterns 和 keywords 的簡體中文關鍵字完整性 ===\n")
    
    # 載入檔案
    patterns_file = "sales_rag_app/libs/services/sales_assistant/prompts/entity_patterns.json"
    keywords_file = "sales_rag_app/libs/services/sales_assistant/prompts/query_keywords.json"
    
    patterns_data = load_json_file(patterns_file)
    keywords_data = load_json_file(keywords_file)
    
    if not patterns_data or not keywords_data:
        print("無法載入配置文件")
        return
    
    # 提取關鍵字
    patterns_keywords = extract_keywords_from_patterns(patterns_data)
    intents_keywords = extract_keywords_from_intents(keywords_data)
    
    print("1. 檢查 SPEC_TYPE 模式中的簡體關鍵字:")
    spec_keywords = patterns_keywords.get("SPEC_TYPE", [])
    simplified_spec_keywords = [k for k in spec_keywords if re.search(r'[\u4e00-\u9fff]', k)]
    print(f"   找到的簡體關鍵字: {simplified_spec_keywords}")
    
    # 檢查是否有對應的繁體版本
    traditional_pairs = {
        "处理器": "處理器",
        "显卡": "顯卡",
        "内存": "記憶體",
        "硬盘": "硬碟",
        "电池": "電池",
        "屏幕": "螢幕",
        "显示": "顯示",
        "存储": "儲存",
        "续航": "續航",
        "电量": "電量"
    }
    
    missing_traditional = []
    for simplified, traditional in traditional_pairs.items():
        if simplified in spec_keywords and traditional not in spec_keywords:
            missing_traditional.append(traditional)
    
    if missing_traditional:
        print(f"   缺少對應的繁體關鍵字: {missing_traditional}")
    else:
        print("   ✓ 所有簡體關鍵字都有對應的繁體版本")
    
    print("\n2. 檢查意圖關鍵字中的簡體關鍵字:")
    for intent_name, keywords in intents_keywords.items():
        simplified_keywords = [k for k in keywords if re.search(r'[\u4e00-\u9fff]', k)]
        if simplified_keywords:
            print(f"   {intent_name}: {simplified_keywords}")
    
    print("\n3. 檢查關鍵字一致性:")
    
    # 檢查 display 相關關鍵字
    display_keywords = intents_keywords.get("display", [])
    if "显示" in display_keywords and "顯示" in display_keywords:
        print("   ✓ display 意圖包含繁簡體關鍵字")
    else:
        print("   ✗ display 意圖缺少某些繁簡體關鍵字")
    
    # 檢查 portability 相關關鍵字
    portability_keywords = intents_keywords.get("portability", [])
    if "轻便" in portability_keywords and "輕便" in portability_keywords:
        print("   ✓ portability 意圖包含繁簡體關鍵字")
    else:
        print("   ✗ portability 意圖缺少某些繁簡體關鍵字")
    
    # 檢查 comparison 相關關鍵字
    comparison_keywords = intents_keywords.get("comparison", [])
    if "比较" in comparison_keywords and "比較" in comparison_keywords:
        print("   ✓ comparison 意圖包含繁簡體關鍵字")
    else:
        print("   ✗ comparison 意圖缺少某些繁簡體關鍵字")
    
    print("\n4. 建議的完整關鍵字對照表:")
    print("   繁體 -> 簡體")
    for traditional, simplified in traditional_pairs.items():
        print(f"   {traditional} -> {simplified}")
    
    print("\n=== 檢查完成 ===")

def test_keyword_recognition():
    """測試關鍵字識別功能"""
    print("\n=== 測試關鍵字識別功能 ===")
    
    # 載入檔案
    patterns_file = "sales_rag_app/libs/services/sales_assistant/prompts/entity_patterns.json"
    keywords_file = "sales_rag_app/libs/services/sales_assistant/prompts/query_keywords.json"
    
    patterns_data = load_json_file(patterns_file)
    keywords_data = load_json_file(keywords_file)
    
    if not patterns_data or not keywords_data:
        print("無法載入配置文件")
        return
    
    # 測試查詢
    test_queries = [
        "比較 AG958 和 APX958 的处理器性能",
        "AG958 的显卡配置如何",
        "958 系列的电池续航时间",
        "哪个型号的屏幕更好",
        "比较不同型号的存储容量",
        "AG958 的重量和便携性",
        "当前最新的型号有哪些"
    ]
    
    print("測試查詢識別:")
    for query in test_queries:
        print(f"\n查詢: {query}")
        
        # 檢查意圖關鍵字
        intents_keywords = keywords_data.get("intent_keywords", {})
        detected_intents = []
        
        for intent_name, config in intents_keywords.items():
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in query.lower():
                    detected_intents.append(intent_name)
                    break
        
        if detected_intents:
            print(f"  檢測到意圖: {detected_intents}")
        else:
            print("  未檢測到明確意圖")
        
        # 檢查實體模式
        entity_patterns = patterns_data.get("entity_patterns", {})
        detected_entities = []
        
        for entity_type, config in entity_patterns.items():
            patterns = config.get("patterns", [])
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    detected_entities.append(entity_type)
                    break
        
        if detected_entities:
            print(f"  檢測到實體: {detected_entities}")

if __name__ == "__main__":
    check_simplified_chinese_keywords()
    test_keyword_recognition() 