# SalesRAG 快速啟動指南

## 🚀 一鍵啟動

```bash
# 進入專案目錄
cd /home/mapleleaf/LCJRepos/projects/SalesRAG

# 方法 1: 使用快速啟動腳本 (推薦)
python quick_start.py

# 方法 2: 直接啟動服務
python sales_rag_app/main.py
```

## 📱 瀏覽器測試

### 1. 開啟測試介面
```
http://localhost:8000/test
```

### 2. 快速測試案例

#### 基本查詢測試
- **CPU 性能比較**: `比較 958 和 819 系列的 CPU 性能`
- **遊戲筆電查詢**: `最新的遊戲筆電有哪些？`
- **商務筆電查詢**: `適合商務使用的輕薄筆電`

#### 澄清對話測試 (會觸發智能澄清)
- **基本需求**: `我想要一台筆電`
- **一般推薦**: `有什麼推薦的嗎？`
- **規格查詢**: `筆電規格`

## 🎯 測試步驟

### 方法 1: 使用網頁測試介面

1. **啟動系統**
   ```bash
   python quick_start.py
   ```
   
2. **瀏覽器會自動開啟測試頁面**
   - 如果沒有自動開啟，手動訪問 `http://localhost:8000/test`

3. **測試基本查詢**
   - 在"基本查詢測試"區域輸入查詢
   - 點擊快速測試按鈕試用預設查詢

4. **測試澄清對話**
   - 在"澄清對話測試"區域輸入模糊查詢
   - 系統會自動顯示澄清問題和選項
   - 點擊選項進行互動

### 方法 2: 使用瀏覽器開發者工具

1. **開啟開發者工具** (`F12`)

2. **切換到 Console 標籤**

3. **執行測試代碼**:

```javascript
// 測試基本查詢
async function testQuery() {
    const response = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: "比較 958 和 819 系列的 CPU 性能",
            service_name: "sales_assistant"
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        console.log('收到:', chunk);
    }
}

testQuery();
```

```javascript
// 測試澄清對話
async function testClarification() {
    const response = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: "我想要一台筆電",
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
                console.log('澄清數據:', data);
                
                if (data.message_type === 'clarification_request') {
                    console.log('問題:', data.question);
                    console.log('選項:', data.options);
                    // 保存對話 ID 用於後續回應
                    window.conversationId = data.conversation_id;
                }
            }
        }
    }
}

testClarification();
```

```javascript
// 回應澄清問題 (在執行上述代碼後)
async function respondClarification(choice) {
    const response = await fetch('/api/clarification-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            conversation_id: window.conversationId,
            user_choice: choice,
            service_name: "sales_assistant"
        })
    });
    
    const result = await response.json();
    console.log('回應結果:', result);
}

// 選擇遊戲娛樂
respondClarification('gaming');
```

## 📊 功能特色

### 1. 階層式意圖檢測
- **13 種基礎意圖**: display, cpu, gpu, memory, storage, battery, portability, connectivity, comparison, specifications, latest, usage_scenario, budget
- **35+ 種細分意圖**: 每個基礎意圖包含 2-3 個細分意圖
- **智能權重計算**: 細分意圖權重更高，提供更精確的分析

### 2. 智能澄清對話
- **自動觸發**: 當信心度 < 0.6 時自動觸發
- **多種觸發條件**: 
  - 低信心度查詢
  - 一般意圖檢測
  - 無實體識別
  - 意圖衝突
- **6 種澄清類型**: 使用場景、預算範圍、性能優先、特殊需求、比較重點、型號偏好

### 3. 個性化推薦
- **使用場景映射**: 
  - 遊戲娛樂 → 958 系列
  - 商務辦公 → 819 系列
  - 設計創作 → 958 系列
  - 學習研究 → 839 系列
- **優先規格識別**: 根據澄清結果確定關鍵規格
- **增強意圖生成**: 信心度提升至 0.9

## 🔧 故障排除

### 問題 1: 端口被占用
```bash
# 檢查端口占用
lsof -i :8000

# 使用其他端口
python quick_start.py  # 然後選擇不同端口
```

### 問題 2: 澄清對話未觸發
- 確保使用模糊查詢，如 "我想要一台筆電"
- 避免使用明確的型號或規格詞彙

### 問題 3: 依賴項目缺失
```bash
# 安裝依賴
pip install -r requirements.txt

# 或個別安裝
pip install fastapi uvicorn jinja2 python-multipart
```

## 📈 測試結果示例

### 成功的澄清對話流程:
1. **用戶查詢**: "我想要一台筆電"
2. **系統檢測**: 信心度 0.0，觸發澄清
3. **澄清問題**: "請問您的主要使用場景是什麼？"
4. **用戶選擇**: "遊戲娛樂"
5. **系統回應**: 推薦 958 系列，重點比較 GPU、CPU、記憶體

### 成功的直接查詢:
1. **用戶查詢**: "比較 958 和 819 系列的 CPU 性能"
2. **系統檢測**: 信心度 0.8，直接處理
3. **系統回應**: 提供詳細的 CPU 性能比較表格

## 🌟 進階功能

- **實時統計**: 查詢次數、澄清觸發率、平均回應時間
- **錯誤處理**: 完整的錯誤恢復機制
- **多語言支持**: 繁體中文、簡體中文、英文
- **流式回應**: Server-Sent Events 提供即時體驗

---

🎉 **準備就緒！開始探索 SalesRAG 的智能推薦功能吧！**