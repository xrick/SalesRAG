# 測試文件說明

本目錄包含 SalesRAG 專案的各種測試文件，用於驗證系統功能和修復問題。

## 測試文件列表

### 核心功能測試
- `test_data_availability.py` - 測試數據可用性檢查功能
- `test_entity_recognition.py` - 測試實體識別模組功能
- `test_keyword_management.py` - 測試關鍵字管理功能
- `test_patterns_completeness.py` - 測試 patterns 和 keywords 的完整性，檢查簡體關鍵字

### 問題修復測試
- `test_dict_answer_summary.py` - 測試 LLM 返回字典格式 answer_summary 的處理
- `test_fix.py` - 測試修復後的系統功能
- `test_real_fix.py` - 測試真實場景的修復效果
- `test_service_fix.py` - 測試服務層修復

### 流程測試
- `test_full_flow.py` - 測試完整流程
- `test_full_flow_with_data_check.py` - 測試包含數據檢查的完整流程
- `test_new_flow.py` - 測試新的 RAG 流程
- `test_new_flow_end_to_end.py` - 端到端測試新流程

### 特定功能測試
- `test_table_generation.py` - 測試表格生成功能
- `test_two_step_strategy.py` - 測試兩步驟策略
- `test_llm_response.py` - 測試 LLM 回應處理
- `test_modelname_check.py` - 測試模型名稱檢查
- `test_modeltype_check.py` - 測試模型類型檢查
- `test_regex.py` - 測試正則表達式功能
- `test_final_table.py` - 測試最終表格生成

## 運行測試

### 運行所有測試
```bash
python run_tests.py
```

### 運行特定測試
```bash
# 運行核心功能測試
python tests/test_data_availability.py
python tests/test_entity_recognition.py
python tests/test_keyword_management.py

# 運行問題修復測試
python tests/test_dict_answer_summary.py
python tests/test_fix.py

# 運行流程測試
python tests/test_full_flow.py
python tests/test_new_flow.py
```

### 運行測試並生成報告
```bash
python run_tests.py --report
```

## 測試覆蓋範圍

### 功能測試
- ✅ 數據可用性檢查
- ✅ 實體識別和意圖檢測
- ✅ 關鍵字管理
- ✅ LLM 回應處理
- ✅ 表格生成和格式化
- ✅ 查詢意圖解析
- ✅ 模型名稱驗證

### 問題修復測試
- ✅ 字典格式 answer_summary 處理
- ✅ 簡體中文關鍵字支持
- ✅ 錯誤處理和備用回應
- ✅ 兩步驟策略處理

### 邊界情況測試
- ✅ 無效模型名稱處理
- ✅ 無效 GPU 型號處理
- ✅ 數據缺失情況
- ✅ 格式錯誤處理

## 測試結果解讀

### 成功指標
- 所有測試通過
- 無錯誤或警告
- 功能按預期工作

### 失敗指標
- 測試失敗
- 錯誤訊息
- 功能異常

## 維護說明

### 添加新測試
1. 創建新的測試文件
2. 遵循命名規範：`test_功能名稱.py`
3. 添加適當的測試用例
4. 更新本文件列表

### 更新測試
1. 修改現有測試文件
2. 確保測試覆蓋新功能
3. 驗證測試結果
4. 更新相關文檔

### 問題排查
1. 檢查測試環境
2. 驗證依賴項
3. 查看錯誤日誌
4. 修復問題並重新測試
