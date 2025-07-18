# SalesRAG 系統啟動與測試指南

## 系統概述

SalesRAG 是一個基於 RAG（Retrieval-Augmented Generation）的智能筆電銷售助理系統，具備以下核心功能：

- **階層式意圖檢測**：支援 13 種基礎意圖和 35+ 種細分意圖
- **智能澄清對話**：當用戶意圖不明確時，系統會主動詢問澄清問題
- **精準產品推薦**：基於澄清結果提供個性化的筆電推薦
- **實時流式回應**：支援 Server-Sent Events (SSE) 的即時回應

## 系統架構

```
SalesRAG/
├── sales_rag_app/
│   ├── main.py                 # FastAPI 主應用
│   ├── libs/
│   │   ├── services/
│   │   │   └── sales_assistant/
│   │   │       ├── service.py              # 主服務邏輯
│   │   │       ├── entity_recognition.py   # 實體識別系統
│   │   │       ├── clarification_manager.py # 澄清對話管理器
│   │   │       └── prompts/
│   │   │           ├── query_keywords.json        # 階層式意圖配置
│   │   │           └── clarification_templates.json # 澄清問題模板
│   │   └── RAG/
│   │       ├── llm_initializer.py  # LLM 初始化
│   │       ├── milvus_query.py     # 向量搜索
│   │       └── duckdb_query.py     # 結構化查詢
│   ├── static/          # 靜態資源
│   ├── templates/       # HTML 模板
│   └── db/             # 數據庫檔案
└── test_hierarchical_intent.py  # 功能測試腳本
```

## 環境要求

- **Python**: 3.8+
- **依賴套件**: 詳見 `requirements.txt`
- **數據庫**: DuckDB (本地檔案)
- **向量搜索**: Milvus (需要額外設置)

## 快速啟動

### 1. 環境準備

```bash
# 進入專案目錄
cd /home/mapleleaf/LCJRepos/projects/SalesRAG

# 安裝依賴
pip install -r requirements.txt

# 設置環境變數（如果需要）
cp .env.example .env  # 如果存在的話
```

### 2. 啟動系統

```bash
# 方法 1: 直接運行主應用
python sales_rag_app/main.py

# 方法 2: 使用 uvicorn
uvicorn sales_rag_app.main:app --host 0.0.0.0 --port 8000

# 方法 3: 開發模式（自動重載）
uvicorn sales_rag_app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 驗證啟動

訪問 `http://localhost:8000`，您應該看到系統的主頁面。

## 瀏覽器測試指南

### 1. 基本功能測試

#### 1.1 開啟開發者工具
1. 打開瀏覽器（推薦 Chrome/Firefox）
2. 訪問 `http://localhost:8000`
3. 按 `F12` 開啟開發者工具
4. 切換到 **Console** 標籤

#### 1.2 測試基本查詢
在 Console 中執行以下 JavaScript 代碼：

```javascript
// 測試基本查詢
async function testBasicQuery() {
    const response = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: "比較 958 系列和 819 系列的 CPU 性能",
            service_name: "sales_assistant"
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        console.log('收到數據:', chunk);
    }
}

// 執行測試
testBasicQuery();
```

### 2. 澄清對話測試

#### 2.1 觸發澄清對話
測試會觸發澄清對話的低信心度查詢：

```javascript
// 測試澄清對話觸發
async function testClarificationTrigger() {
    const response = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: "我想要一台筆電",  // 這會觸發澄清對話
            service_name: "sales_assistant"
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.substring(6));
                console.log('澄清回應:', data);
                
                // 如果收到澄清請求，保存對話 ID
                if (data.message_type === 'clarification_request') {
                    window.currentConversationId = data.conversation_id;
                    console.log('澄清問題:', data.question);
                    console.log('選項:', data.options);
                }
            }
        }
    }
}

// 執行測試
testClarificationTrigger();
```

#### 2.2 回應澄清問題
當收到澄清請求後，回應澄清問題：

```javascript
// 回應澄清問題
async function respondToClarification(choice) {
    if (!window.currentConversationId) {
        console.log('沒有活躍的澄清對話');
        return;
    }
    
    const response = await fetch('/api/clarification-response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conversation_id: window.currentConversationId,
            user_choice: choice,
            user_input: "",
            service_name: "sales_assistant"
        })
    });
    
    const result = await response.json();
    console.log('澄清回應結果:', result);
    
    // 如果需要繼續澄清
    if (result.message_type === 'clarification_request') {
        console.log('繼續澄清 - 問題:', result.question);
        console.log('選項:', result.options);
    }
    
    // 如果澄清完成
    if (result.message_type === 'final_response') {
        console.log('澄清完成!');
        console.log('最終回應:', result.answer_summary);
        console.log('澄清總結:', result.clarification_summary);
    }
}

// 範例：選擇 "gaming"（遊戲娛樂）
respondToClarification('gaming');
```

### 3. 完整的澄清對話測試流程

```javascript
// 完整的澄清對話測試
async function fullClarificationTest() {
    console.log('=== 開始完整澄清對話測試 ===');
    
    // 步驟 1: 發送模糊查詢
    console.log('步驟 1: 發送模糊查詢');
    const response1 = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: "推薦一台筆電",
            service_name: "sales_assistant"
        })
    });
    
    const reader1 = response1.body.getReader();
    const decoder1 = new TextDecoder();
    
    let conversationId = null;
    
    while (true) {
        const { value, done } = await reader1.read();
        if (done) break;
        
        const chunk = decoder1.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.substring(6));
                if (data.message_type === 'clarification_request') {
                    conversationId = data.conversation_id;
                    console.log('收到澄清請求:', data.question);
                    console.log('選項:', data.options.map(opt => `${opt.id}: ${opt.label}`));
                }
            }
        }
    }
    
    if (!conversationId) {
        console.log('未觸發澄清對話');
        return;
    }
    
    // 步驟 2: 回應第一個澄清問題
    console.log('步驟 2: 回應澄清問題 - 選擇 gaming');
    const response2 = await fetch('/api/clarification-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            conversation_id: conversationId,
            user_choice: 'gaming',
            service_name: "sales_assistant"
        })
    });
    
    const result = await response2.json();
    console.log('澄清回應結果:', result);
    
    if (result.message_type === 'final_response') {
        console.log('=== 澄清完成 ===');
        console.log('最終推薦:', result.answer_summary);
        console.log('澄清總結:', result.clarification_summary);
    }
}

// 執行完整測試
fullClarificationTest();
```

## 測試案例

### 1. 階層式意圖檢測測試

```javascript
// 測試不同類型的查詢
const testQueries = [
    "我想要一台適合玩遊戲的筆電",     // 應檢測到 gaming sub-intent
    "有沒有適合商務使用的輕薄筆電？",   // 應檢測到 business + ultralight
    "比較 958 和 819 系列的 CPU 性能", // 應檢測到 comparison + cpu
    "最新的高階筆電有哪些？",          // 應檢測到 latest + premium
    "我需要一台筆電"                   // 應觸發澄清對話
];

// 批量測試
async function batchTest() {
    for (const query of testQueries) {
        console.log(`\n測試查詢: ${query}`);
        console.log('='.repeat(50));
        
        const response = await fetch('/api/chat-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, service_name: "sales_assistant" })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            if (chunk.includes('data: ')) {
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.substring(6));
                        console.log('回應類型:', data.message_type || 'standard');
                        
                        if (data.message_type === 'clarification_request') {
                            console.log('觸發澄清對話');
                            console.log('問題:', data.question);
                        } else if (data.answer_summary) {
                            console.log('回應摘要:', data.answer_summary.substring(0, 100) + '...');
                        }
                    }
                }
            }
        }
        
        // 等待 1 秒後測試下一個
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// 執行批量測試
batchTest();
```

### 2. 澄清對話選項測試

```javascript
// 測試所有澄清選項
async function testAllClarificationOptions() {
    const options = ['gaming', 'business', 'creation', 'study'];
    
    for (const option of options) {
        console.log(`\n測試選項: ${option}`);
        console.log('='.repeat(30));
        
        // 觸發澄清
        const response1 = await fetch('/api/chat-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: "我想要一台筆電",
                service_name: "sales_assistant"
            })
        });
        
        const reader1 = response1.body.getReader();
        const decoder1 = new TextDecoder();
        let conversationId = null;
        
        while (true) {
            const { value, done } = await reader1.read();
            if (done) break;
            
            const chunk = decoder1.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.substring(6));
                    if (data.message_type === 'clarification_request') {
                        conversationId = data.conversation_id;
                        break;
                    }
                }
            }
        }
        
        if (conversationId) {
            // 回應澄清
            const response2 = await fetch('/api/clarification-response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    user_choice: option,
                    service_name: "sales_assistant"
                })
            });
            
            const result = await response2.json();
            console.log(`選項 ${option} 的結果:`, result.clarification_summary);
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// 執行測試
testAllClarificationOptions();
```

## 常見問題排除

### 1. 系統無法啟動

**檢查項目：**
- 確認 Python 版本是 3.8+
- 檢查所有依賴是否正確安裝
- 確認端口 8000 沒有被占用

```bash
# 檢查端口占用
lsof -i :8000

# 強制結束占用進程
kill -9 <PID>
```

### 2. 澄清對話未觸發

**可能原因：**
- 查詢信心度過高（超過 0.6）
- 系統檢測到明確的意圖

**測試方法：**
```javascript
// 使用確保會觸發澄清的查詢
const lowConfidenceQueries = [
    "我想要一台筆電",
    "有什麼推薦的嗎？",
    "筆電規格"
];
```

### 3. API 回應錯誤

**檢查方法：**
```javascript
// 檢查 API 狀態
fetch('/api/get-services')
    .then(response => response.json())
    .then(data => console.log('服務狀態:', data));
```

### 4. 數據庫連接問題

**檢查項目：**
- 確認 `sales_rag_app/db/sales_specs.db` 檔案存在
- 檢查 DuckDB 相關錯誤訊息

## 進階測試

### 1. 性能測試

```javascript
// 並發測試
async function performanceTest() {
    const promises = [];
    const startTime = Date.now();
    
    for (let i = 0; i < 10; i++) {
        promises.push(
            fetch('/api/chat-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: `測試查詢 ${i}`,
                    service_name: "sales_assistant"
                })
            })
        );
    }
    
    const results = await Promise.all(promises);
    const endTime = Date.now();
    
    console.log(`並發測試完成: ${results.length} 個請求`);
    console.log(`耗時: ${endTime - startTime}ms`);
}

performanceTest();
```

### 2. 錯誤處理測試

```javascript
// 測試錯誤處理
async function errorHandlingTest() {
    const errorCases = [
        { query: "", expected: "Query cannot be empty" },
        { query: "test", service_name: "non_existent", expected: "Service not found" }
    ];
    
    for (const testCase of errorCases) {
        const response = await fetch('/api/chat-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testCase)
        });
        
        console.log(`測試案例: ${JSON.stringify(testCase)}`);
        console.log(`狀態碼: ${response.status}`);
        
        if (!response.ok) {
            const error = await response.json();
            console.log(`錯誤訊息: ${error.error}`);
        }
    }
}

errorHandlingTest();
```

## 結論

本系統提供了完整的智能筆電推薦功能，包括：

1. **智能意圖檢測** - 理解用戶真實需求
2. **澄清對話機制** - 在不確定時主動詢問
3. **個性化推薦** - 基於澄清結果提供精準建議
4. **實時回應** - 流式回應提供良好用戶體驗

透過以上測試方法，您可以全面驗證系統的各項功能，確保系統運作正常。

---

**技術支援：** 如遇問題，請檢查系統日誌或聯繫開發團隊。