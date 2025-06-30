# 關鍵字管理系統說明

## 概述

本系統將原本硬編碼在程式碼中的查詢意圖關鍵字重構為可配置的 JSON 檔案，提供了更靈活和易於維護的關鍵字管理方式。

## 檔案結構

```
sales_rag_app/
├── libs/services/sales_assistant/
│   ├── prompts/
│   │   ├── sales_prompt4.txt          # 原有的提示模板
│   │   └── query_keywords.json        # 新增的關鍵字配置文件
│   └── service.py                     # 修改後的服務類別
├── test_keyword_management.py         # 測試腳本
├── manage_keywords.py                 # 互動式管理腳本
└── KEYWORD_MANAGEMENT_README.md       # 本說明文件
```

## 關鍵字配置文件格式

`query_keywords.json` 的結構如下：

```json
{
  "intent_keywords": {
    "display": {
      "keywords": ["螢幕", "顯示", "屏幕", "显示", "screen", "lcd", "面板"],
      "description": "螢幕相關查詢"
    },
    "cpu": {
      "keywords": ["cpu", "處理器", "处理器", "processor", "ryzen"],
      "description": "CPU相關查詢"
    },
    // ... 其他意圖
  }
}
```

## 支援的查詢意圖

| 意圖名稱 | 描述 | 關鍵字範例 |
|---------|------|-----------|
| `display` | 螢幕相關查詢 | 螢幕、顯示、屏幕、显示、screen、lcd、面板 |
| `cpu` | CPU相關查詢 | cpu、處理器、处理器、processor、ryzen |
| `gpu` | GPU相關查詢 | gpu、顯卡、显卡、graphics、radeon |
| `memory` | 記憶體相關查詢 | 記憶體、內存、内存、memory、ram、ddr |
| `storage` | 儲存相關查詢 | 硬碟、硬盤、硬盘、storage、ssd、nvme |
| `battery` | 電池相關查詢 | 電池、电池、續航、续航、battery、電量、电量 |
| `portability` | 重量和便攜性相關查詢 | 重量、輕便、轻便、weight、portable、尺寸、便携 |
| `connectivity` | 接口相關查詢 | 接口、port、usb、hdmi、lan |
| `comparison` | 比較相關查詢 | 比較、比较、compare、差異、差异、difference、不同 |
| `specifications` | 規格查詢 | 規格、规格、spec、配置、configuration |

## 使用方法

### 1. 自動載入

系統會在初始化時自動載入關鍵字配置：

```python
service = SalesAssistantService()
# 關鍵字配置已自動載入
```

### 2. 程式化管理

```python
# 獲取當前配置
keywords = service.get_intent_keywords()

# 添加關鍵字
service.add_intent_keyword("cpu", "中央處理器")

# 移除關鍵字
service.remove_intent_keyword("cpu", "中央處理器")

# 保存配置
service.save_intent_keywords()

# 重新載入配置
service.reload_intent_keywords()
```

### 3. 互動式管理

使用提供的管理腳本：

```bash
python manage_keywords.py
```

這會啟動一個互動式介面，提供以下功能：
- 顯示所有關鍵字配置
- 添加關鍵字
- 移除關鍵字
- 測試查詢意圖解析
- 保存配置
- 重新載入配置

### 4. 測試

運行測試腳本驗證功能：

```bash
python test_keyword_management.py
```

## 優勢

### 1. 靈活性
- 無需修改程式碼即可調整關鍵字
- 支援動態添加和移除關鍵字
- 可以為不同語言環境配置不同的關鍵字

### 2. 可維護性
- 關鍵字集中管理，易於維護
- 配置檔案格式清晰，易於理解
- 支援版本控制

### 3. 可擴展性
- 容易添加新的查詢意圖
- 支援多語言關鍵字
- 可以為每個意圖添加描述信息

### 4. 測試友好
- 提供完整的測試腳本
- 支援互動式測試
- 錯誤處理完善

## 注意事項

1. **配置檔案路徑**：確保配置檔案路徑正確，預設為 `sales_rag_app/libs/services/sales_assistant/prompts/query_keywords.json`

2. **檔案編碼**：配置檔案使用 UTF-8 編碼，支援中文關鍵字

3. **錯誤處理**：系統會自動處理配置檔案不存在或格式錯誤的情況

4. **大小寫敏感**：關鍵字匹配不區分大小寫，但建議保持一致性

5. **重複關鍵字**：系統會自動避免重複的關鍵字

## 未來改進

1. **權重系統**：為關鍵字添加權重，提高匹配準確性
2. **正則表達式支援**：支援更複雜的關鍵字模式
3. **多語言配置**：支援按語言分離的配置檔案
4. **Web 介面**：提供 Web 介面進行關鍵字管理
5. **自動學習**：根據用戶查詢自動調整關鍵字

## 遷移指南

如果您從舊版本升級：

1. 備份現有的 `service.py` 檔案
2. 更新 `service.py` 檔案
3. 創建 `query_keywords.json` 配置文件
4. 運行測試腳本驗證功能
5. 使用管理腳本調整關鍵字配置

## 支援

如有問題或建議，請檢查：
1. 配置檔案格式是否正確
2. 檔案路徑是否正確
3. 檔案編碼是否為 UTF-8
4. 運行測試腳本檢查錯誤信息 