document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const chatMessages = document.getElementById("chatMessages");
    const chatHistory = document.getElementById("chatHistory");
    const clearHistoryBtn = document.getElementById("clearHistory");

    let messages = [];
    let history = JSON.parse(localStorage.getItem("chatHistory")) || [];

    const loadInitialUI = () => {
        renderHistory();
        // 預設載入歡迎畫面或最新的聊天記錄
        if (history.length > 0) {
            loadChat(history[0].id);
        } else {
            showWelcomeMessage();
        }
    };
    
    // --- Event Listeners ---
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendButton.addEventListener("click", sendMessage);
    clearHistoryBtn.addEventListener("click", clearAllHistory);

    document.querySelector('.preset-buttons').addEventListener('click', (e) => {
        if (e.target.classList.contains('preset-btn')) {
            const question = e.target.dataset.question;
            userInput.value = question;
            sendMessage();
        }
    });

    // --- Core Functions ---
    async function sendMessage() {
        const query = userInput.value.trim();
        if (!query) return;

        // 如果是新對話，則創建歷史記錄
        if (messages.length === 0) {
            startNewChat(query);
        }
        
        appendMessage({ role: "user", content: query });
        userInput.value = "";
        toggleInput(true);

        const thinkingBubble = showThinkingIndicator();

        try {
            const response = await fetch("/api/chat-stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, service_name: "sales_assistant" }),
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            // 處理流式響應
            let isFirstChunk = true;
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonDataString = line.substring(6);
                        if (jsonDataString) {
                            if (isFirstChunk) {
                                thinkingBubble.remove(); // 移除思考中的提示
                                isFirstChunk = false;
                            }
                            try {
                                const jsonData = parseJsonWithErrorHandling(jsonDataString);
                                appendMessage({ role: 'assistant', content: jsonData }, true);
                            } catch (e) {
                                console.error("JSON parsing error:", e, "Data:", jsonDataString);
                                appendMessage({ role: 'assistant', content: { error: `回應格式錯誤：${e.message}` } }, true);
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Fetch error:", error);
            thinkingBubble.remove();
            appendMessage({ role: 'assistant', content: { error: `請求失敗: ${error.message}` } }, true);
        } finally {
            toggleInput(false);
            updateHistory();
        }
    }

    // --- UI & DOM Manipulation ---
    function appendMessage(message, isStreaming = false) {
        const lastMessage = chatMessages.lastElementChild;
        // 如果是串流中的助理訊息且最後一則也是助理訊息，則更新內容
        if (isStreaming && lastMessage && lastMessage.dataset.role === 'assistant') {
            renderMessageContent(lastMessage.querySelector('.message-content'), message.content);
        } else {
            // 否則，創建新的訊息卡片
            const messageContainer = document.createElement('div');
            messageContainer.className = `message-container ${message.role}`;
            messageContainer.dataset.role = message.role;

            const messageCard = document.createElement('div');
            messageCard.className = 'message-card';

            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            renderMessageContent(messageContent, message.content);

            messageCard.appendChild(messageContent);
            
            if (message.role === 'assistant') {
                const copyBtnTemplate = document.getElementById('copy-to-clipboard-template').innerHTML;
                messageCard.insertAdjacentHTML('beforeend', copyBtnTemplate);
                messageCard.querySelector('.copy-btn').addEventListener('click', () => copyToClipboard(message.content));
            }

            messageContainer.appendChild(messageCard);
            chatMessages.appendChild(messageContainer);
        }
        scrollToBottom();
    }

    function renderMessageContent(container, content) {
        if (typeof content === 'string') {
            container.textContent = content;
        } else if (typeof content === 'object' && content !== null) {
            if (content.error) {
                container.innerHTML = `<p style="color: red;"><strong>錯誤：</strong> ${content.error}</p>`;
                return;
            }
            
            let markdownString = "";
            
            // 處理回答摘要或主要內容
            if (content.answer_summary) {
                markdownString += `${content.answer_summary}\n\n`;
            } else if (content.answer) {
                markdownString += `${content.answer}\n\n`;
            } else if (content.response) {
                markdownString += `${content.response}\n\n`;
            }
            
            // 處理不同類型的比較表格
            if (content.comparison_table && content.comparison_table.length > 0) {
                markdownString += renderComparisonTable(content.comparison_table, content.table_type);
            }
            
            // 處理產品清單
            if (content.products && content.products.length > 0) {
                markdownString += renderProductList(content.products);
            }
            
            // 處理規格詳細資訊
            if (content.specifications) {
                markdownString += renderSpecifications(content.specifications);
            }
            
            // 處理推薦內容
            if (content.recommendations && content.recommendations.length > 0) {
                markdownString += renderRecommendations(content.recommendations);
            }
            
            // 處理分析結果
            if (content.analysis) {
                markdownString += `### 分析結果\n${content.analysis}\n\n`;
            }
            
            // 處理結論建議
            if (content.conclusion) {
                markdownString += `### 結論建議\n${content.conclusion}\n\n`;
            } else if (content.summary) {
                markdownString += `### 總結\n${content.summary}\n\n`;
            }
            
            // 處理額外資訊
            if (content.additional_info) {
                markdownString += `### 額外資訊\n${content.additional_info}\n\n`;
            }
            
            // 處理參考資料來源
            if (content.source_references && content.source_references.length > 0) {
                markdownString += `<details><summary>參考資料來源</summary>\n\n`;
                content.source_references.forEach(source => {
                    const cleanedSource = source.replace(/[\r\n]+/g, ' ').trim();
                    if (cleanedSource) markdownString += `> ${cleanedSource}\n\n`;
                });
                markdownString += `</details>`;
            }
            
            container.innerHTML = marked.parse(markdownString);
        }
    }
    
    // 輔助函數：渲染比較表格
    function renderComparisonTable(comparisonData, tableType = 'default') {
        let tableMarkdown = "";
        
        if (comparisonData.length === 0) return tableMarkdown;
        
        // 根據表格類型處理不同格式
        switch (tableType) {
            case 'product_comparison':
                // 通用產品比較格式
                tableMarkdown += `### 產品規格比較\n\n`;
                const headers = Object.keys(comparisonData[0]);
                tableMarkdown += `| ${headers.join(' | ')} |\n`;
                tableMarkdown += `|${headers.map(() => ':---').join('|')}|\n`;
                comparisonData.forEach(row => {
                    const values = headers.map(header => row[header] || 'N/A');
                    tableMarkdown += `| ${values.join(' | ')} |\n`;
                });
                break;
                
            case 'feature_comparison':
                // 功能特性比較格式
                tableMarkdown += `### 功能特性比較\n\n`;
                if (comparisonData[0].feature && comparisonData[0].models) {
                    const modelNames = Object.keys(comparisonData[0].models);
                    tableMarkdown += `| 特性 | ${modelNames.join(' | ')} |\n`;
                    tableMarkdown += `|:---|${modelNames.map(() => ':---').join('|')}|\n`;
                    comparisonData.forEach(row => {
                        const modelValues = modelNames.map(model => row.models[model] || 'N/A');
                        tableMarkdown += `| ${row.feature} | ${modelValues.join(' | ')} |\n`;
                    });
                }
                break;
                
                         default:
                 // 預設格式（向下相容舊格式）
                 tableMarkdown += `### 規格比較\n\n`;
                 if (comparisonData[0].feature) {
                     // 檢測是否為舊的 AG958/AKK839 格式
                     if (comparisonData[0].AG958 !== undefined || comparisonData[0].AKK839 !== undefined) {
                         tableMarkdown += `| 特性 | AG958 | AKK839 |\n`;
                         tableMarkdown += `|:---|:---|:---|\n`;
                         comparisonData.forEach(row => {
                             tableMarkdown += `| ${row.feature || 'N/A'} | ${row.AG958 || 'N/A'} | ${row.AKK839 || 'N/A'} |\n`;
                         });
                     } else {
                         // 動態檢測欄位
                         const allKeys = Object.keys(comparisonData[0]);
                         const featureKey = allKeys.includes('feature') ? 'feature' : allKeys[0];
                         const otherKeys = allKeys.filter(key => key !== featureKey);
                         
                         // 檢測是否為 MODEL_A, MODEL_B 等格式，並轉換為更友好的標題
                         const friendlyHeaders = otherKeys.map(key => {
                             if (key.startsWith('MODEL_')) {
                                 return key.replace('MODEL_', '型號 ');
                             }
                             return key;
                         });
                         
                         tableMarkdown += `| 特性 | ${friendlyHeaders.join(' | ')} |\n`;
                         tableMarkdown += `|:---|${friendlyHeaders.map(() => ':---').join('|')}|\n`;
                         comparisonData.forEach(row => {
                             const values = otherKeys.map(key => {
                                 const value = row[key] || 'N/A';
                                 // 如果值太長，截取部分內容
                                 return value.length > 100 ? value.substring(0, 97) + '...' : value;
                             });
                             tableMarkdown += `| ${row[featureKey] || 'N/A'} | ${values.join(' | ')} |\n`;
                         });
                     }
                 }
        }
        
        return tableMarkdown + `\n`;
    }
    
    // 輔助函數：渲染產品清單
    function renderProductList(products) {
        let listMarkdown = "### 推薦產品\n\n";
        products.forEach((product, index) => {
            listMarkdown += `${index + 1}. **${product.name || product.model}**\n`;
            if (product.price) listMarkdown += `   - 價格：${product.price}\n`;
            if (product.description) listMarkdown += `   - 描述：${product.description}\n`;
            if (product.features && product.features.length > 0) {
                listMarkdown += `   - 主要特色：${product.features.join('、')}\n`;
            }
            listMarkdown += `\n`;
        });
        return listMarkdown;
    }
    
    // 輔助函數：渲染規格詳細資訊
    function renderSpecifications(specifications) {
        let specMarkdown = "### 詳細規格\n\n";
        Object.entries(specifications).forEach(([category, specs]) => {
            specMarkdown += `**${category}**\n`;
            if (typeof specs === 'object') {
                Object.entries(specs).forEach(([key, value]) => {
                    specMarkdown += `- ${key}：${value}\n`;
                });
            } else {
                specMarkdown += `- ${specs}\n`;
            }
            specMarkdown += `\n`;
        });
        return specMarkdown;
    }
    
    // 輔助函數：渲染推薦內容
    function renderRecommendations(recommendations) {
        let recMarkdown = "### 推薦建議\n\n";
        recommendations.forEach((rec, index) => {
            recMarkdown += `${index + 1}. ${rec.title || rec.recommendation}\n`;
            if (rec.reason) recMarkdown += `   - 理由：${rec.reason}\n`;
            if (rec.benefits) recMarkdown += `   - 優勢：${rec.benefits}\n`;
            recMarkdown += `\n`;
        });
        return recMarkdown;
    }
    
    function showWelcomeMessage() {
        chatMessages.innerHTML = ''; // 清空
        const welcome = {
            role: 'assistant',
            content: {
                answer_summary: "您好！我是您的 AI 銷售助理。我可以回答關於多種不同機型的筆記型電腦的問題，並為您進行比較。",
                conclusion: "您可以直接提問，或點擊下方的預設問題按鈕開始。"
            }
        };
        appendMessage(welcome);
    }
    
    function showThinkingIndicator() {
        const container = document.createElement('div');
        container.className = 'message-container assistant';
        container.innerHTML = `
            <div class="message-card">
                <div class="message-content thinking-indicator">
                    <div class="spinner"></div>
                    <span>AI 正在思考中...</span>
                </div>
            </div>
        `;
        chatMessages.appendChild(container);
        scrollToBottom();
        return container;
    }

    function toggleInput(disabled) {
        userInput.disabled = disabled;
        sendButton.disabled = disabled;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- JSON 解析容錯處理 ---
    function parseJsonWithErrorHandling(jsonString) {
        try {
            // 先嘗試直接解析
            return JSON.parse(jsonString);
        } catch (e) {
            console.log("第一次 JSON 解析失敗，嘗試修復...", e.message);
            
            try {
                // 嘗試修復常見的 JSON 格式問題
                let fixedJson = jsonString;
                
                // 1. 修復字符串中的未轉義引號
                fixedJson = fixJsonQuotes(fixedJson);
                
                // 2. 移除多餘的引號
                fixedJson = fixExtraQuotes(fixedJson);
                
                // 3. 修復換行符問題
                fixedJson = fixedJson.replace(/\r?\n/g, '\\n');
                
                // 4. 最後的清理步驟 - 處理剩餘的問題字符
                fixedJson = cleanupJsonString(fixedJson);
                
                // 5. 嘗試解析修復後的 JSON
                const parsed = JSON.parse(fixedJson);
                console.log("JSON 修復成功！");
                return parsed;
                
            } catch (e2) {
                console.log("JSON 修復失敗，使用降級處理", e2.message);
                
                // 降級處理：嘗試提取主要內容
                return fallbackJsonParsing(jsonString);
            }
        }
    }
    
    function fixJsonQuotes(jsonString) {
        // 修復在字符串值中的未轉義引號
        let fixed = jsonString;
        
        // 針對 conclusion 字段的高級引號修復策略
        // 方法1: 處理 。" 模式（句號後引號）
        fixed = fixed.replace(/"conclusion"\s*:\s*"([^"]*?)。"([^"]*?)"([^"]*?)""(?=\s*[,}])/g, (match, p1, p2, p3) => {
            const fixedContent = `${p1}。\\"${p2}\\"${p3}`;
            return `"conclusion": "${fixedContent}"`;
        });
        
        // 方法2: 處理 ：" 模式（中文冒號後引號）
        fixed = fixed.replace(/"conclusion"\s*:\s*"([^"]*?)："([^"]*?)"([^"]*?)""(?=\s*[,}])/g, (match, p1, p2, p3) => {
            const fixedContent = `${p1}：\\"${p2}\\"${p3}`;
            return `"conclusion": "${fixedContent}"`;
        });
        
        // 方法3: 通用的 conclusion 多引號處理
        fixed = fixed.replace(/"conclusion"\s*:\s*"([^"]*)"([^"]*)"([^"]*)""+(?=\s*[,}])/g, (match, p1, p2, p3) => {
            // 智能檢測引號的位置和修復策略
            let fixedContent;
            if (p1.endsWith('。') || p1.endsWith('：') || p1.endsWith('！') || p1.endsWith('？')) {
                // 如果第一部分以標點結尾，很可能是引號該在這裡
                fixedContent = `${p1}\\"${p2}\\"${p3}`;
            } else {
                // 否則嘗試不同的修復方式
                fixedContent = `${p1}\\"${p2}\\"${p3}`;
            }
            return `"conclusion": "${fixedContent}"`;
        });
        
        // 通用字段引號修復
        fixed = fixed.replace(/"(\w+)"\s*:\s*"([^"]*?)([。：！？])"([^"]*?)"([^"]*?)""(?=\s*[,}])/g, (match, field, p1, punctuation, p2, p3) => {
            const fixedContent = `${p1}${punctuation}\\"${p2}\\"${p3}`;
            return `"${field}": "${fixedContent}"`;
        });
        
        // 處理其他欄位中的一般引號問題
        fixed = fixed.replace(/"(\w+)"\s*:\s*"([^"]*)"([^"]*)"([^"]*)"/g, (match, field, p1, p2, p3) => {
            // 如果檢測到中間有未轉義的引號，進行修復
            if (p2.includes(':') || p2.includes('，') || p2.includes('。') || p2.includes('：') || 
                p2.includes('！') || p2.includes('？')) {
                const fixedContent = `${p1}\\"${p2}\\"${p3}`;
                return `"${field}": "${fixedContent}"`;
            }
            return match; // 保持原樣
        });
        
        return fixed;
    }
    
    function fixExtraQuotes(jsonString) {
        // 修復結尾的雙引號問題 (如 ""，應該是 ")
        let fixed = jsonString;
        
        // 修復字段結尾的雙引號問題
        fixed = fixed.replace(/""(\s*[,}])/g, '"$1');
        
        // 處理特殊的三引號或多引號情況
        fixed = fixed.replace(/"""(\s*[,}])/g, '"$1');
        
        // 修復連續引號之間的空格問題
        fixed = fixed.replace(/"\s+""/g, '"');
        
        return fixed;
    }
    
    function cleanupJsonString(jsonString) {
        // 最終的JSON字符串清理函數
        let cleaned = jsonString;
        
        // 1. 處理字段值中嵌入的未轉義引號（更激進的方法）
        cleaned = cleaned.replace(/"(\w+)"\s*:\s*"([^"]*?[。：！？])"([^"]*?)"([^"]*?)""(\s*[,}])/g, (match, field, p1, p2, p3, ending) => {
            const fixedContent = `${p1}\\"${p2}\\"${p3}`;
            return `"${field}": "${fixedContent}"${ending}`;
        });
        
        // 2. 處理任何剩餘的多重引號模式
        cleaned = cleaned.replace(/""""/g, '"');
        cleaned = cleaned.replace(/"""/g, '"');
        
        // 3. 確保字段結尾正確
        cleaned = cleaned.replace(/""(\s*[,}])/g, '"$1');
        
        // 4. 移除可能的控制字符
        cleaned = cleaned.replace(/[\x00-\x1F\x7F]/g, '');
        
        return cleaned;
    }
    
    function fallbackJsonParsing(jsonString) {
        console.log("使用降級解析方式");
        
        try {
            // 嘗試提取主要欄位
            const result = {};
            
            // 提取 answer_summary
            const summaryMatch = jsonString.match(/"answer_summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"/);
            if (summaryMatch) {
                result.answer_summary = summaryMatch[1].replace(/\\"/g, '"');
            }
            
            // 提取 conclusion - 使用多重模式匹配
            let conclusionMatch = jsonString.match(/"conclusion"\s*:\s*"([^"]*(?:\\.[^"]*)*)"/);
            if (!conclusionMatch) {
                // 模式1: 處理 。" 的情況
                conclusionMatch = jsonString.match(/"conclusion"\s*:\s*"([^"]*?)。"([^"]*?)"([^"]*?)"/);
                if (conclusionMatch) {
                    result.conclusion = `${conclusionMatch[1]}。"${conclusionMatch[2]}"${conclusionMatch[3]}`;
                } else {
                    // 模式2: 處理 ：" 的情況
                    conclusionMatch = jsonString.match(/"conclusion"\s*:\s*"([^"]*?)："([^"]*?)"([^"]*?)"/);
                    if (conclusionMatch) {
                        result.conclusion = `${conclusionMatch[1]}："${conclusionMatch[2]}"${conclusionMatch[3]}`;
                    } else {
                        // 模式3: 通用的多引號匹配
                        conclusionMatch = jsonString.match(/"conclusion"\s*:\s*"([^"]*)"([^"]*)"([^"]*)/);
                        if (conclusionMatch) {
                            result.conclusion = `${conclusionMatch[1]}"${conclusionMatch[2]}"${conclusionMatch[3]}`;
                        }
                    }
                }
            } else {
                result.conclusion = conclusionMatch[1].replace(/\\"/g, '"');
            }
            
            // 如果找不到主要內容，則返回錯誤訊息
            if (!result.answer_summary && !result.conclusion) {
                result.error = "無法解析 AI 回應的內容格式";
            }
            
            // 嘗試提取 comparison_table
            const tableMatch = jsonString.match(/"comparison_table"\s*:\s*\[([^\]]*)\]/);
            if (tableMatch) {
                try {
                    result.comparison_table = JSON.parse(`[${tableMatch[1]}]`);
                    result.table_type = 'default'; // 設置預設類型
                } catch (e) {
                    console.log("無法解析 comparison_table，嘗試簡化提取");
                    // 簡化提取：至少嘗試識別有比較數據
                    if (tableMatch[1].includes('MODEL_A') || tableMatch[1].includes('feature')) {
                        result.answer_summary = (result.answer_summary || '') + '\n\n檢測到比較表格數據，但格式解析失敗。';
                    }
                }
            }
            
            // 提取 source_references
            const referencesMatch = jsonString.match(/"source_references"\s*:\s*\[(.*?)\]/);
            if (referencesMatch) {
                try {
                    result.source_references = JSON.parse(`[${referencesMatch[1]}]`);
                } catch (e) {
                    console.log("無法解析 source_references");
                }
            }
            
            return result;
            
        } catch (e) {
            console.error("降級解析也失敗了", e);
            return {
                error: "AI 回應格式無法解析，請重新嘗試",
                raw_response: jsonString.substring(0, 200) + "..." // 顯示部分原始回應
            };
        }
    }

    // --- Chat History Management ---
    function renderHistory() {
        chatHistory.innerHTML = "";
        history.forEach(chat => {
            const historyItem = document.createElement("div");
            historyItem.className = "history-item text-ellipsis";
            historyItem.textContent = chat.title;
            historyItem.dataset.id = chat.id;
            historyItem.addEventListener("click", () => loadChat(chat.id));
            chatHistory.appendChild(historyItem);
        });
    }

    function startNewChat(title) {
        messages = [];
        const newChat = {
            id: Date.now(),
            title: title.substring(0, 25), // 取前25個字元作為標題
            messages: messages
        };
        history.unshift(newChat);
        saveHistory();
        renderHistory();
        setActiveChat(newChat.id);
    }

    function loadChat(id) {
        const chat = history.find(c => c.id === id);
        if (chat) {
            messages = chat.messages;
            chatMessages.innerHTML = "";
            messages.forEach(msg => appendMessage(msg));
            setActiveChat(id);
        }
    }
    
    function updateHistory() {
        // 更新當前對話的訊息
        const currentChatId = document.querySelector('.history-item.active')?.dataset.id;
        if (currentChatId) {
            const chatIndex = history.findIndex(c => c.id == currentChatId);
            if (chatIndex !== -1) {
                // 從 DOM 中收集所有 messages
                const currentMessages = [];
                 chatMessages.querySelectorAll('.message-container').forEach(container => {
                    const role = container.dataset.role;
                    let content;
                    try {
                        // 嘗試解析JSON內容
                        const assistantContent = history[chatIndex].messages.find(m => m.role === 'assistant')?.content;
                         if (role === 'assistant' && typeof assistantContent === 'object') {
                             content = assistantContent;
                         } else {
                            content = container.querySelector('.message-content').textContent.trim();
                         }
                    } catch (e) {
                         content = container.querySelector('.message-content').textContent.trim();
                    }
                    currentMessages.push({ role, content });
                 });
                history[chatIndex].messages = currentMessages;
                saveHistory();
            }
        }
    }

    function saveHistory() {
        localStorage.setItem("chatHistory", JSON.stringify(history));
    }
    
    function clearAllHistory() {
        if (confirm("您確定要清除所有聊天歷史記錄嗎？")) {
            history = [];
            messages = [];
            localStorage.removeItem("chatHistory");
            renderHistory();
            showWelcomeMessage();
        }
    }

    function setActiveChat(id) {
        document.querySelectorAll(".history-item").forEach(item => {
            item.classList.toggle("active", item.dataset.id == id);
        });
    }
    
    function copyToClipboard(content) {
        let textToCopy = '';
        if (typeof content === 'string') {
            textToCopy = content;
        } else if (typeof content === 'object' && content !== null) {
            // 將 JSON 物件轉換為格式化的文字
            if (content.answer_summary) textToCopy += `回答摘要:\n${content.answer_summary}\n\n`;
            if (content.comparison_table && content.comparison_table.length > 0) {
                 textToCopy += `規格比較:\n`;
                 content.comparison_table.forEach(row => {
                     if (row.AG958 !== undefined || row.AKK839 !== undefined) {
                         // 舊格式
                         textToCopy += `- ${row.feature}: AG958(${row.AG958 || 'N/A'}), AKK839(${row.AKK839 || 'N/A'})\n`;
                     } else {
                         // 新格式，動態處理所有欄位
                         const allKeys = Object.keys(row);
                         const featureKey = allKeys.includes('feature') ? 'feature' : allKeys[0];
                         const otherKeys = allKeys.filter(key => key !== featureKey);
                         
                         let comparisonText = `- ${row[featureKey]}:`;
                         otherKeys.forEach(key => {
                             const friendlyKey = key.startsWith('MODEL_') ? key.replace('MODEL_', '型號') : key;
                             const value = row[key] || 'N/A';
                             const shortValue = value.length > 50 ? value.substring(0, 47) + '...' : value;
                             comparisonText += ` ${friendlyKey}(${shortValue})`;
                         });
                         textToCopy += comparisonText + '\n';
                     }
                 });
                 textToCopy += '\n';
            }
            if (content.conclusion) textToCopy += `結論建議:\n${content.conclusion}\n\n`;
        }
        
        navigator.clipboard.writeText(textToCopy.trim()).then(() => {
            alert("已複製到剪貼簿！");
        }).catch(err => {
            console.error('無法複製文字: ', err);
        });
    }

    // --- Initial Load ---
    loadInitialUI();
});