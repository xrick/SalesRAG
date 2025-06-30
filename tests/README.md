# 測試文件說明

本資料夾包含 SalesRAG 專案的所有測試文件。

## 測試文件分類

### 核心功能測試

- `test_entity_recognition.py` - 實體識別系統測試
- `test_keyword_management.py` - 關鍵字管理功能測試

### 服務功能測試

- `test_data_availability.py` - 數據可用性檢查測試
- `test_full_flow.py` - 完整流程測試
- `test_full_flow_with_data_check.py` - 帶數據檢查的完整流程測試
- `test_new_flow.py` - 新流程測試
- `test_new_flow_end_to_end.py` - 端到端新流程測試
- `test_service_fix.py` - 服務修復測試

### 表格生成測試

- `test_final_table.py` - 最終表格生成測試
- `test_table_generation.py` - 表格生成功能測試
- `test_two_step_strategy.py` - 兩步驟策略測試

### LLM 回應測試

- `test_llm_response.py` - LLM 回應處理測試
- `test_real_fix.py` - 真實修復測試

### 模型驗證測試

- `test_modelname_check.py` - 模型名稱檢查測試
- `test_modeltype_check.py` - 模型類型檢查測試
- `test_regex.py` - 正則表達式測試

### 修復測試

- `test_fix.py` - 一般修復測試

## 運行測試

### 從專案根目錄運行

```bash
# 運行特定測試
python tests/test_entity_recognition.py
python tests/test_keyword_management.py

# 運行所有測試（需要創建測試腳本）
python -m pytest tests/
```

### 從測試資料夾運行

```bash
cd tests
python test_entity_recognition.py
python test_keyword_management.py
```

## 測試結果

測試結果通常會生成在專案根目錄中，例如：

- `entity_recognition_results.json` - 實體識別測試結果
- 其他測試輸出文件

## 注意事項

1. 所有測試文件都已經更新路徑，可以從 tests 資料夾或專案根目錄運行
2. 某些測試可能需要特定的數據庫連接或配置
3. 測試文件會自動處理路徑問題，無需手動調整
4. 建議在運行測試前確保所有依賴都已安裝

## 新增測試

當新增測試文件時，請：

1. 將文件放在 tests 資料夾中
2. 使用適當的命名規範（test_*.py）
3. 更新本 README 文件
4. 確保路徑設置正確
