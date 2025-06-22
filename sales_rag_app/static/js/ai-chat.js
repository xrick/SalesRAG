document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const chatMessages = document.getElementById("chatMessages");
    const chatHistory = document.getElementById("chatHistory");
    const clearHistoryBtn = document.getElementById("clearHistory");

    let messages = [];
    let history = JSON.parse(localStorage.getItem("chatHistory")) || [];

    // Enhanced markdown configuration
    marked.setOptions({
        breaks: true,
        gfm: true,
        tables: true,
        sanitize: false,
        smartLists: true,
        smartypants: true
    });

    // Custom renderer for better table handling
    const renderer = new marked.Renderer();
    
    // Enhanced table rendering with fallback
    renderer.table = function(header, body) {
        try {
            // Try to render the table normally
            const tableHtml = `
                <div class="table-container">
                    <table class="enhanced-table">
                        <thead>${header}</thead>
                        <tbody>${body}</tbody>
                    </table>
                </div>
            `;
            return tableHtml;
        } catch (error) {
            console.warn("Table rendering failed, using fallback:", error);
            return createTableFallback(header, body);
        }
    };

    // Enhanced code block rendering
    renderer.code = function(code, language) {
        const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
        const highlighted = hljs.highlight(code, { language: validLanguage }).value;
        return `<pre><code class="hljs ${validLanguage}">${highlighted}</code></pre>`;
    };

    marked.use({ renderer });

    // Table fallback function
    function createTableFallback(header, body) {
        try {
            // Parse the table structure
            const headerMatch = header.match(/<tr>(.*?)<\/tr>/);
            const bodyMatches = body.match(/<tr>(.*?)<\/tr>/g);
            
            if (!headerMatch) {
                return `<div class="message-warning">⚠️ 表格格式無法解析，顯示原始內容</div>`;
            }

            const headerCells = headerMatch[1].match(/<th>(.*?)<\/th>/g) || [];
            const headers = headerCells.map(cell => cell.replace(/<\/?th>/g, '').trim());
            
            const rows = [];
            if (bodyMatches) {
                bodyMatches.forEach(rowMatch => {
                    const cellMatches = rowMatch.match(/<td>(.*?)<\/td>/g) || [];
                    const cells = cellMatches.map(cell => cell.replace(/<\/?td>/g, '').trim());
                    if (cells.length > 0) {
                        rows.push(cells);
                    }
                });
            }

            // Create a simple table structure
            let tableHtml = '<div class="table-fallback">';
            tableHtml += '<div class="table-fallback-header">';
            tableHtml += '<span class="table-fallback-title">📊 規格比較表</span>';
            tableHtml += '<button class="table-fallback-toggle" onclick="toggleTableFallback(this)">顯示原始數據</button>';
            tableHtml += '</div>';
            
            if (headers.length > 0 && rows.length > 0) {
                tableHtml += '<table class="enhanced-table">';
                tableHtml += '<thead><tr>';
                headers.forEach(header => {
                    tableHtml += `<th>${header}</th>`;
                });
                tableHtml += '</tr></thead>';
                tableHtml += '<tbody>';
                rows.forEach(row => {
                    tableHtml += '<tr>';
                    row.forEach(cell => {
                        tableHtml += `<td>${cell}</td>`;
                    });
                    tableHtml += '</tr>';
                });
                tableHtml += '</tbody></table>';
            }
            
            // Add raw data as fallback
            const rawData = `Headers: ${headers.join(' | ')}\n${rows.map(row => row.join(' | ')).join('\n')}`;
            tableHtml += `<div class="table-fallback-content">${rawData}</div>`;
            tableHtml += '</div>';
            
            return tableHtml;
        } catch (error) {
            console.error("Table fallback creation failed:", error);
            return `<div class="message-error">❌ 表格渲染失敗: ${error.message}</div>`;
        }
    }

    // Global function for table fallback toggle
    window.toggleTableFallback = function(button) {
        const container = button.closest('.table-fallback');
        const content = container.querySelector('.table-fallback-content');
        const isVisible = content.classList.contains('show');
        
        if (isVisible) {
            content.classList.remove('show');
            button.textContent = '顯示原始數據';
        } else {
            content.classList.add('show');
            button.textContent = '隱藏原始數據';
        }
    };

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
            let accumulatedContent = "";
            
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
                                const messageData = JSON.parse(jsonDataString);
                                
                                // Handle backend response format
                                let content = "";
                                if (messageData.answer_summary) {
                                    content = messageData.answer_summary;
                                } else if (messageData.content) {
                                    content = messageData.content;
                                } else if (typeof messageData === 'string') {
                                    content = messageData;
                                }
                                
                                accumulatedContent += content;
                                
                                // Create proper message object for frontend
                                const frontendMessage = {
                                    role: 'assistant',
                                    content: content,
                                    content_type: 'markdown'
                                };
                                
                                appendMessage(frontendMessage, true);
                            } catch (e) {
                                console.error("JSON parsing error:", e, "Data:", jsonDataString);
                                appendMessage({ 
                                    role: 'assistant', 
                                    content: `JSON解析錯誤：${e.message}`,
                                    content_type: "text"
                                }, true);
                            }
                        }
                    }
                }
            }
            
            // Post-process the accumulated content for better table handling
            if (accumulatedContent) {
                postProcessContent(accumulatedContent);
            }
            
        } catch (error) {
            console.error("Fetch error:", error);
            thinkingBubble.remove();
            appendMessage({ 
                role: 'assistant', 
                content: `請求失敗: ${error.message}`,
                content_type: "text"
            }, true);
        } finally {
            toggleInput(false);
            updateHistory();
        }
    }

    // Post-process content for better table handling
    function postProcessContent(content) {
        const lastMessage = chatMessages.lastElementChild;
        if (!lastMessage || lastMessage.dataset.role !== 'assistant') return;
        
        const messageContent = lastMessage.querySelector('.message-content');
        if (!messageContent) return;
        
        // Check for malformed tables and fix them
        const tableRegex = /\|.*\|/g;
        const tables = content.match(tableRegex);
        
        if (tables && tables.length > 0) {
            // Try to fix common table issues
            let fixedContent = content;
            
            // Fix tables without proper headers
            fixedContent = fixedContent.replace(/\|([^|]+)\|([^|]+)\|/g, (match, col1, col2) => {
                if (!match.includes('---')) {
                    return `| ${col1.trim()} | ${col2.trim()} |\n| --- | --- |\n${match}`;
                }
                return match;
            });
            
            // Update the content if it was fixed
            if (fixedContent !== content) {
                try {
                    messageContent.innerHTML = marked.parse(fixedContent);
                } catch (error) {
                    console.warn("Failed to re-render fixed content:", error);
                }
            }
        }
    }

    // --- UI & DOM Manipulation ---
    function appendMessage(message, isStreaming = false) {
        const lastMessage = chatMessages.lastElementChild;
        // 如果是串流中的助理訊息且最後一則也是助理訊息，則更新內容
        if (isStreaming && lastMessage && lastMessage.dataset.role === 'assistant') {
            renderMessageContent(lastMessage.querySelector('.message-content'), message);
        } else {
            // 否則，創建新的訊息卡片
            const messageContainer = document.createElement('div');
            messageContainer.className = `message-container ${message.role}`;
            messageContainer.dataset.role = message.role;

            const messageCard = document.createElement('div');
            messageCard.className = 'message-card';

            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            renderMessageContent(messageContent, message);

            messageCard.appendChild(messageContent);
            
            if (message.role === 'assistant') {
                const copyBtnTemplate = document.getElementById('copy-to-clipboard-template').innerHTML;
                messageCard.insertAdjacentHTML('beforeend', copyBtnTemplate);
                messageCard.querySelector('.copy-btn').addEventListener('click', () => copyToClipboard(message));
            }

            messageContainer.appendChild(messageCard);
            chatMessages.appendChild(messageContainer);
        }
        scrollToBottom();
    }

    function renderMessageContent(container, message) {
        // 簡化的內容渲染邏輯 - 主要處理後端已格式化的內容
        if (typeof message === 'string') {
            // 向下相容：處理純字符串內容
            try {
                container.innerHTML = marked.parse(message);
            } catch (error) {
                console.warn("Markdown parsing failed, using plain text:", error);
                container.textContent = message;
            }
            return;
        }
        
        if (typeof message !== 'object' || !message) {
            container.textContent = String(message || '');
            return;
        }

        // 處理新的響應格式
        if (message.content_type === 'markdown' || message.role === 'assistant') {
            const content = message.content || message;
            
            if (typeof content === 'string') {
                try {
                    // 使用增強的 markdown 渲染
                    container.innerHTML = marked.parse(content);
                    
                    // 檢查是否有表格渲染問題
                    const tables = container.querySelectorAll('table');
                    tables.forEach(table => {
                        if (!table.querySelector('thead') || !table.querySelector('tbody')) {
                            // 表格結構不完整，嘗試修復
                            fixTableStructure(table);
                        }
                    });
                    
                } catch (error) {
                    console.warn("Enhanced markdown parsing failed:", error);
                    // 嘗試使用簡單的 markdown 解析
                    try {
                        container.innerHTML = marked.parse(content, { renderer: new marked.Renderer() });
                    } catch (fallbackError) {
                        console.error("All markdown parsing failed:", fallbackError);
                        container.innerHTML = `<div class="message-warning">⚠️ 內容格式解析失敗，顯示原始文本</div><pre>${content}</pre>`;
                    }
                }
            } else if (typeof content === 'object') {
                // 向下相容：處理舊的JSON格式
                renderLegacyJsonContent(container, content);
            } else {
                container.textContent = String(content);
            }
        } else {
            // 用戶訊息或其他類型
            const content = message.content || message;
            if (typeof content === 'string') {
                container.textContent = content;
            } else {
                container.textContent = JSON.stringify(content, null, 2);
            }
        }
        
        // 顯示元數據（如果有）
        if (message.metadata && Object.keys(message.metadata).length > 0) {
            const metadataElement = document.createElement('div');
            metadataElement.className = 'message-metadata';
            metadataElement.style.cssText = 'font-size: 0.8em; color: #666; margin-top: 8px; font-style: italic;';
            
            const metaInfo = [];
            if (message.metadata.has_table) metaInfo.push('📊 包含比較表格');
            if (message.metadata.has_recommendations) metaInfo.push('💡 包含建議');
            if (message.metadata.source_count) metaInfo.push(`📚 ${message.metadata.source_count}個資料來源`);
            if (message.metadata.parse_error) metaInfo.push('⚠️ 格式解析問題');
            
            if (metaInfo.length > 0) {
                metadataElement.textContent = metaInfo.join(' • ');
                container.appendChild(metadataElement);
            }
        }
    }

    // Fix table structure
    function fixTableStructure(table) {
        try {
            const rows = table.querySelectorAll('tr');
            if (rows.length === 0) return;
            
            // Check if table has proper structure
            const hasThead = table.querySelector('thead');
            const hasTbody = table.querySelector('tbody');
            
            if (!hasThead || !hasTbody) {
                // Reconstruct table structure
                const newTable = document.createElement('table');
                newTable.className = 'enhanced-table';
                
                const thead = document.createElement('thead');
                const tbody = document.createElement('tbody');
                
                rows.forEach((row, index) => {
                    if (index === 0) {
                        // First row becomes header
                        thead.appendChild(row.cloneNode(true));
                    } else {
                        // Other rows go to body
                        tbody.appendChild(row.cloneNode(true));
                    }
                });
                
                newTable.appendChild(thead);
                newTable.appendChild(tbody);
                
                // Replace the old table
                table.parentNode.replaceChild(newTable, table);
            }
        } catch (error) {
            console.warn("Failed to fix table structure:", error);
        }
    }

    // 向下相容函數：處理舊的JSON格式
    function renderLegacyJsonContent(container, content) {
        if (content.error) {
            container.innerHTML = `<div class="message-error">❌ 錯誤：${content.error}</div>`;
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
        
        // 處理比較表格（簡化版 - 因為複雜邏輯已移到後端）
        if (content.comparison_table && content.comparison_table.length > 0) {
            markdownString += renderSimpleComparisonTable(content.comparison_table);
        }
        
        // 處理結論建議
        if (content.conclusion) {
            markdownString += `### 結論建議\n${content.conclusion}\n\n`;
        } else if (content.summary) {
            markdownString += `### 總結\n${content.summary}\n\n`;
        }
        
        // 處理參考資料來源
        if (content.source_references && content.source_references.length > 0) {
            markdownString += `<details><summary>📚 參考資料來源</summary>\n\n`;
            content.source_references.forEach(source => {
                const cleanedSource = source.replace(/[\r\n]+/g, ' ').trim();
                if (cleanedSource) markdownString += `> ${cleanedSource}\n\n`;
            });
            markdownString += `</details>`;
        }
        
        try {
            container.innerHTML = marked.parse(markdownString);
        } catch (error) {
            console.warn("Legacy content parsing failed:", error);
            container.innerHTML = `<div class="message-warning">⚠️ 內容格式解析失敗</div><pre>${JSON.stringify(content, null, 2)}</pre>`;
        }
    }
    
    // 簡化的比較表格渲染（向下相容）
    function renderSimpleComparisonTable(comparisonData) {
        let tableMarkdown = "### 📊 規格比較\n\n";
        
        if (comparisonData.length === 0) return tableMarkdown;
        
        const headers = Object.keys(comparisonData[0]);
        tableMarkdown += `| ${headers.join(' | ')} |\n`;
        tableMarkdown += `|${headers.map(() => ':---').join('|')}|\n`;
        
        comparisonData.forEach(row => {
            const values = headers.map(header => {
                const value = row[header] || 'N/A';
                return typeof value === 'string' && value.length > 50 ? 
                    value.substring(0, 47) + '...' : value;
            });
            tableMarkdown += `| ${values.join(' | ')} |\n`;
        });
        
        return tableMarkdown + `\n`;
    }
    
    function showWelcomeMessage() {
        chatMessages.innerHTML = ''; // 清空
        const welcome = {
            role: 'assistant',
            content: `# 👋 歡迎使用筆記型電腦銷售助手！

我是您的 AI 銷售助理，專門協助您比較和分析不同機型的筆記型電腦。

## 🚀 我可以幫您：

- **📊 規格比較** - 詳細比較不同機型的硬體規格
- **💡 購買建議** - 根據您的需求提供專業建議
- **🔍 詳細分析** - 深入分析各機型的優缺點
- **📈 性價比評估** - 幫助您做出最佳選擇

## 💡 使用方式：

您可以直接提問，或點擊下方的**預設問題**按鈕開始。例如：
- "比較 AG958 和 APX958 的主要差異"
- "哪款筆記型電腦更適合遊戲？"
- "不同機型的散熱設計有什麼不同？"

開始您的查詢吧！`,
            content_type: "markdown"
        };
        appendMessage(welcome);
    }
    
    function showThinkingIndicator() {
        const container = document.createElement('div');
        container.className = 'message-container assistant';
        container.innerHTML = `
            <div class="message-card">
                <div class="message-content">
                    <div class="processing-indicator">
                        <div class="processing-spinner"></div>
                        <span>🤔 AI 正在分析您的問題...</span>
                    </div>
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
        if (disabled) {
            sendButton.innerHTML = '<span>處理中...</span>';
        } else {
            sendButton.innerHTML = '<span>發送</span>';
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
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
                        // 簡化內容提取邏輯
                        const messageContent = container.querySelector('.message-content');
                        if (role === 'user') {
                            content = messageContent.textContent.trim();
                        } else {
                            // 助理訊息保存為markdown格式
                            content = {
                                content: messageContent.innerHTML,
                                content_type: "markdown",
                                role: "assistant"
                            };
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
    
    function copyToClipboard(message) {
        let textToCopy = '';
        
        if (typeof message === 'string') {
            textToCopy = message;
        } else if (message.content_type === 'markdown') {
            // 對於markdown內容，提取純文本
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = marked.parse(message.content);
            textToCopy = tempDiv.textContent || tempDiv.innerText || message.content;
        } else if (typeof message.content === 'string') {
            textToCopy = message.content;
        } else {
            // 向下相容：處理舊格式
            textToCopy = JSON.stringify(message, null, 2);
        }
        
        navigator.clipboard.writeText(textToCopy.trim()).then(() => {
            // 視覺反饋
            const copyBtn = event.target;
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '已複製！';
            copyBtn.style.color = '#4CAF50';
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.color = '';
            }, 2000);
        }).catch(err => {
            console.error('無法複製文字: ', err);
            alert('複製失敗，請手動選擇文字複製');
        });
    }

    // --- Initial Load ---
    loadInitialUI();
});