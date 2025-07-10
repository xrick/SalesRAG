# 生產環境 JSON 解析錯誤修正

## 問題描述

在生產環境中，當用戶查詢 "比較958系列哪款筆記型電腦更適合遊戲？" 時，系統出現以下錯誤：

```
2025-07-02 17:51:57,980 - root - ERROR - JSON解析失敗: Extra data: line 23 column 4 (char 739)
```

## 問題分析

### 1. **錯誤原因**
- LLM 返回的 JSON 格式不正確，在 JSON 結構後面還有額外的內容
- 錯誤訊息 `Extra data: line 23 column 4 (char 739)` 表示在 JSON 解析過程中發現了額外的數據
- 這通常發生在 LLM 在 JSON 後面添加了額外的文字說明或格式不完整

### 2. **影響範圍**
- 雖然 JSON 解析失敗，但系統仍然能夠正常處理並生成結果
- 這是因為系統有降級處理機制，會調用 `_generate_fallback_response()`
- 但會失去 LLM 生成的原始回答，只能使用備用的資料庫生成內容

## 解決方案

### 1. **改進的 JSON 解析機制**

在 `sales_rag_app/libs/services/sales_assistant/service.py` 中添加了兩個新方法：

#### `_fix_json_format(json_content: str) -> str`
修復常見的 JSON 格式問題：
- 移除 JSON 後面的額外內容
- 修復常見的引號問題
- 修復未轉義的引號
- 修復多餘的逗號
- 修復換行符和空格

#### `_extract_partial_json(json_content: str) -> dict`
從不完整的 JSON 中提取部分有效內容：
- 提取 answer_summary
- 提取 comparison_table
- 提供降級解析機制

### 2. **改進的錯誤處理流程**

在 `chat_stream` 方法中改進了 JSON 解析的錯誤處理：

```python
# 嘗試解析 JSON - 改進的錯誤處理
try:
    parsed_json = json.loads(json_content)
except json.JSONDecodeError as json_error:
    logging.warning(f"JSON 解析失敗: {json_error}")
    
    # 嘗試修復常見的 JSON 格式問題
    fixed_json_content = self._fix_json_format(json_content)
    logging.info(f"嘗試修復後的 JSON: {fixed_json_content}")
    
    try:
        parsed_json = json.loads(fixed_json_content)
        logging.info("JSON 修復成功")
    except json.JSONDecodeError as second_error:
        logging.error(f"JSON 修復後仍然失敗: {second_error}")
        # 如果修復失敗，嘗試提取部分 JSON
        parsed_json = self._extract_partial_json(json_content)
        if not parsed_json:
            raise json_error
```

## 測試驗證

### 1. **測試文件**
創建了 `tests/test_json_fix.py` 來驗證 JSON 修復功能：

- **測試案例 1**: 有多餘內容的 JSON
- **測試案例 2**: 有引號問題的 JSON  
- **測試案例 3**: 有多餘逗號的 JSON
- **測試案例 4**: 部分 JSON 提取功能
- **測試案例 5**: 生產環境錯誤場景

### 2. **測試結果**
所有測試案例都成功通過：

```
✅ 測試案例 1 成功：JSON 修復並解析成功
✅ 測試案例 2 成功：引號問題修復成功
✅ 測試案例 3 成功：多餘逗號修復成功
✅ 部分 JSON 提取成功
✅ 生產環境錯誤修復成功
✅ 表格格式化成功
```

### 3. **生產環境模擬測試**
模擬實際生產環境中的錯誤 JSON，驗證修復效果：

```
✅ JSON 修復成功！
answer_summary: 根据实际数据，AG958P 系列包含 5 个游戏笔记型电脑型号，各有不同的性能配置。
comparison_table 長度: 5
✅ 完整流程處理成功！
最終 answer_summary: 根据实际数据，AG958P 系列包含 5 个游戏笔记型电脑型号，各有不同的性能配置。
最終 comparison_table 類型: <class 'list'>
最終 beautiful_table 長度: 656
```

## 修正效果

### 1. **系統穩定性提升**
- 能夠處理 LLM 返回的不完整或格式不正確的 JSON
- 提供多層次的錯誤處理機制
- 確保系統在 JSON 解析失敗時仍能正常運作

### 2. **用戶體驗改善**
- 減少因 JSON 解析錯誤導致的系統故障
- 保持 LLM 生成的原始回答內容
- 提供更穩定和可靠的服務

### 3. **維護性提升**
- 詳細的日誌記錄，便於問題診斷
- 模組化的錯誤處理機制
- 完整的測試覆蓋

## 部署建議

1. **立即部署**: 建議立即部署此修正，以解決生產環境中的 JSON 解析錯誤
2. **監控日誌**: 部署後密切監控日誌，觀察 JSON 修復功能的運行情況
3. **性能監控**: 監控 JSON 修復功能對系統性能的影響
4. **用戶反饋**: 收集用戶反饋，確認問題是否得到解決

## 相關文件

- `sales_rag_app/libs/services/sales_assistant/service.py` - 主要修正文件
- `tests/test_json_fix.py` - 測試文件
- `tests/test_modelname_format_fix.py` - 相關的 modelname 格式修正測試

## 修正日期

2025-07-02 