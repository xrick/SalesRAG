# SalesRAG

SalesRAG 是一個基於 RAG (Retrieval-Augmented Generation) 的銷售助手系統，專門用於筆電產品規格查詢和比較。

## 專案結構

```
SalesRAG/
├── sales_rag_app/                    # 主要應用程式
│   ├── libs/                        # 核心庫
│   │   ├── services/                # 服務層
│   │   │   └── sales_assistant/     # 銷售助手服務
│   │   │       ├── prompts/         # 提示模板和配置
│   │   │       │   ├── sales_prompt4.txt
│   │   │       │   ├── query_keywords.json
│   │   │       │   └── entity_patterns.json
│   │   │       ├── service.py       # 主要服務類別
│   │   │       └── entity_recognition.py  # 實體識別模組
│   │   └── RAG/                     # RAG 相關模組
│   ├── static/                      # 靜態文件
│   ├── templates/                   # HTML 模板
│   └── main.py                      # 應用程式入口
├── tests/                           # 測試文件
│   ├── README.md                    # 測試說明
│   ├── test_entity_recognition.py   # 實體識別測試
│   ├── test_keyword_management.py   # 關鍵字管理測試
│   └── ...                          # 其他測試文件
├── run_tests.py                     # 測試運行腳本
├── manage_keywords.py               # 關鍵字管理腳本
├── KEYWORD_MANAGEMENT_README.md     # 關鍵字管理說明
└── README.md                        # 本文件
```

## 核心功能

### 1. 實體識別與意圖檢測
- **實體識別**：識別筆電型號、規格類型、比較詞彙等
- **意圖檢測**：檢測用戶查詢意圖（CPU、GPU、記憶體、電池等）
- **關係建模**：建立實體與意圖之間的語義關聯

### 2. 關鍵字管理系統
- **配置驅動**：使用 JSON 配置文件管理關鍵字
- **多語言支援**：支援繁體中文、簡體中文和英文
- **動態管理**：支援添加、移除、保存關鍵字

### 3. RAG 查詢系統
- **精確數據檢索**：根據查詢意圖獲取相關數據
- **智能回應生成**：基於檢索結果生成結構化回應
- **表格生成**：自動生成比較表格

## 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 運行應用程式
```bash
python sales_rag_app/main.py
```

### 運行測試
```bash
# 使用測試運行腳本
python run_tests.py

# 或直接運行特定測試
python tests/test_entity_recognition.py
python tests/test_keyword_management.py
```

### 管理關鍵字
```bash
python manage_keywords.py
```

## 測試

專案包含完整的測試套件，位於 `tests/` 資料夾中：

### 測試分類
- **核心功能測試**：實體識別、關鍵字管理
- **服務功能測試**：完整流程、數據檢查
- **表格生成測試**：各種表格格式處理
- **LLM 回應測試**：回應處理和驗證

### 運行測試
```bash
# 運行所有測試
python run_tests.py

# 運行核心功能測試
python tests/test_entity_recognition.py
python tests/test_keyword_management.py
```

## 配置

### 關鍵字配置
編輯 `sales_rag_app/libs/services/sales_assistant/prompts/query_keywords.json` 來管理查詢意圖關鍵字。

### 實體識別配置
編輯 `sales_rag_app/libs/services/sales_assistant/prompts/entity_patterns.json` 來管理實體識別模式。

## 技術架構

- **後端框架**：FastAPI
- **自然語言處理**：基於規則的實體識別和意圖檢測
- **向量數據庫**：Milvus
- **關係數據庫**：DuckDB
- **LLM 整合**：Ollama
- **前端**：HTML + JavaScript

## 貢獻

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 運行測試確保通過
5. 發起 Pull Request

## 授權

本專案採用 MIT 授權條款。