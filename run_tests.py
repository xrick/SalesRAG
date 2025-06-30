#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試運行腳本
可以運行所有測試或特定測試
"""

import os
import sys
import subprocess
import glob

def run_test_file(test_file):
    """運行單個測試文件"""
    print(f"\n{'='*50}")
    print(f"運行測試: {test_file}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ 測試通過")
            if result.stdout:
                print("輸出:")
                print(result.stdout)
        else:
            print("❌ 測試失敗")
            if result.stderr:
                print("錯誤:")
                print(result.stderr)
            if result.stdout:
                print("輸出:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 運行測試時發生錯誤: {e}")
        return False

def list_test_files():
    """列出所有測試文件"""
    test_files = glob.glob("tests/test_*.py")
    return sorted(test_files)

def show_menu():
    """顯示選單"""
    print("\n=== 測試運行器 ===")
    print("1. 運行所有測試")
    print("2. 運行核心功能測試")
    print("3. 運行實體識別測試")
    print("4. 運行關鍵字管理測試")
    print("5. 列出所有測試文件")
    print("6. 運行特定測試文件")
    print("7. 退出")
    print("==================")

def run_core_tests():
    """運行核心功能測試"""
    core_tests = [
        "tests/test_entity_recognition.py",
        "tests/test_keyword_management.py"
    ]
    
    print("\n運行核心功能測試...")
    success_count = 0
    total_count = len(core_tests)
    
    for test_file in core_tests:
        if os.path.exists(test_file):
            if run_test_file(test_file):
                success_count += 1
        else:
            print(f"⚠️  測試文件不存在: {test_file}")
    
    print(f"\n核心測試結果: {success_count}/{total_count} 通過")

def run_all_tests():
    """運行所有測試"""
    test_files = list_test_files()
    
    if not test_files:
        print("❌ 沒有找到測試文件")
        return
    
    print(f"\n找到 {len(test_files)} 個測試文件，開始運行...")
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        if run_test_file(test_file):
            success_count += 1
    
    print(f"\n總測試結果: {success_count}/{total_count} 通過")

def run_specific_test():
    """運行特定測試文件"""
    test_files = list_test_files()
    
    if not test_files:
        print("❌ 沒有找到測試文件")
        return
    
    print("\n可用的測試文件:")
    for i, test_file in enumerate(test_files, 1):
        print(f"{i}. {os.path.basename(test_file)}")
    
    try:
        choice = input(f"\n請選擇測試文件 (1-{len(test_files)}): ").strip()
        index = int(choice) - 1
        
        if 0 <= index < len(test_files):
            run_test_file(test_files[index])
        else:
            print("❌ 無效的選擇")
    except (ValueError, KeyboardInterrupt):
        print("❌ 輸入無效或取消操作")

def main():
    """主函數"""
    print("SalesRAG 測試運行器")
    print("確保您在專案根目錄中運行此腳本")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n請選擇操作 (1-7): ").strip()
            
            if choice == '1':
                run_all_tests()
            elif choice == '2':
                run_core_tests()
            elif choice == '3':
                run_test_file("tests/test_entity_recognition.py")
            elif choice == '4':
                run_test_file("tests/test_keyword_management.py")
            elif choice == '5':
                test_files = list_test_files()
                print(f"\n找到 {len(test_files)} 個測試文件:")
                for test_file in test_files:
                    print(f"  - {os.path.basename(test_file)}")
            elif choice == '6':
                run_specific_test()
            elif choice == '7':
                print("再見！")
                break
            else:
                print("❌ 無效的選擇，請重新輸入")
                
        except KeyboardInterrupt:
            print("\n\n再見！")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main() 