#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SalesRAG 快速啟動腳本
提供簡單的命令行介面來啟動和測試系統
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_banner():
    """顯示啟動橫幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                      SalesRAG 智能筆電推薦系統                    ║
║                                                              ║
║  🤖 階層式意圖檢測                                            ║
║  🔍 智能澄清對話                                              ║
║  📊 精準產品推薦                                              ║
║  ⚡ 實時流式回應                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_dependencies():
    """檢查依賴項目"""
    print("🔍 檢查系統依賴...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'python-multipart'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (未安裝)")
    
    if missing_packages:
        print(f"\n⚠️  缺少依賴項目: {', '.join(missing_packages)}")
        print("請運行: pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """檢查資料庫檔案"""
    print("📊 檢查資料庫檔案...")
    
    db_file = Path("sales_rag_app/db/sales_specs.db")
    if db_file.exists():
        print(f"  ✅ 資料庫檔案存在: {db_file}")
        return True
    else:
        print(f"  ⚠️  資料庫檔案不存在: {db_file}")
        print("     系統可能無法正常運作，但可以繼續測試基本功能")
        return False

def check_config_files():
    """檢查設定檔案"""
    print("⚙️  檢查設定檔案...")
    
    config_files = [
        "sales_rag_app/libs/services/sales_assistant/prompts/query_keywords.json",
        "sales_rag_app/libs/services/sales_assistant/prompts/clarification_templates.json",
        "sales_rag_app/libs/services/sales_assistant/prompts/entity_patterns.json"
    ]
    
    all_exist = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✅ {Path(config_file).name}")
        else:
            print(f"  ❌ {Path(config_file).name} (不存在)")
            all_exist = False
    
    return all_exist

def start_server(port=8000, auto_open=True):
    """啟動 FastAPI 伺服器"""
    print(f"🚀 啟動系統於 http://localhost:{port}")
    print("   按 Ctrl+C 停止服務")
    
    if auto_open:
        # 延遲開啟瀏覽器
        import threading
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{port}/test")
        
        thread = threading.Thread(target=open_browser)
        thread.daemon = True
        thread.start()
    
    try:
        # 啟動 uvicorn 伺服器
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "sales_rag_app.main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 系統已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

def run_quick_test():
    """運行快速測試"""
    print("🧪 運行快速功能測試...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_hierarchical_intent.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 快速測試通過")
            print("主要功能:")
            print("  - 階層式意圖檢測: 正常")
            print("  - 澄清對話系統: 正常")
            print("  - 實體識別: 正常")
        else:
            print("❌ 快速測試失敗")
            print("錯誤訊息:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ 測試逾時")
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")

def show_usage_info():
    """顯示使用資訊"""
    print("\n📖 使用指南:")
    print("1. 系統啟動後，瀏覽器會自動開啟測試介面")
    print("2. 測試介面位於: http://localhost:8000/test")
    print("3. 主要功能:")
    print("   - 基本查詢測試")
    print("   - 澄清對話測試")
    print("   - 系統狀態檢查")
    print("\n🔧 測試建議:")
    print("• 嘗試明確查詢: '比較 958 和 819 系列的 CPU 性能'")
    print("• 嘗試模糊查詢: '我想要一台筆電' (會觸發澄清對話)")
    print("• 檢查不同使用場景的推薦結果")

def main():
    """主函式"""
    print_banner()
    
    # 檢查當前目錄
    if not Path("sales_rag_app").exists():
        print("❌ 請在專案根目錄運行此腳本")
        print("   當前目錄應包含 sales_rag_app 資料夾")
        return
    
    # 系統檢查
    deps_ok = check_dependencies()
    db_ok = check_database()
    config_ok = check_config_files()
    
    if not deps_ok:
        print("\n❌ 系統檢查失敗，請先安裝依賴項目")
        return
    
    if not config_ok:
        print("\n⚠️  部分設定檔案缺失，系統可能無法正常運作")
        response = input("是否繼續啟動? (y/n): ")
        if response.lower() != 'y':
            return
    
    print("\n" + "="*60)
    print("選擇操作:")
    print("1. 啟動系統 (推薦)")
    print("2. 運行快速測試")
    print("3. 顯示使用資訊")
    print("4. 退出")
    print("="*60)
    
    while True:
        choice = input("\n請選擇 (1-4): ").strip()
        
        if choice == '1':
            port = 8000
            port_input = input(f"請輸入端口號 (預設 {port}): ").strip()
            if port_input:
                try:
                    port = int(port_input)
                except ValueError:
                    print("無效的端口號，使用預設值 8000")
                    port = 8000
            
            auto_open = input("是否自動開啟瀏覽器? (y/n, 預設 y): ").strip().lower()
            auto_open = auto_open != 'n'
            
            show_usage_info()
            input("\n按 Enter 繼續啟動...")
            start_server(port, auto_open)
            break
            
        elif choice == '2':
            run_quick_test()
            input("\n按 Enter 繼續...")
            
        elif choice == '3':
            show_usage_info()
            input("\n按 Enter 繼續...")
            
        elif choice == '4':
            print("👋 再見!")
            break
            
        else:
            print("無效選擇，請輸入 1-4")

if __name__ == "__main__":
    main()