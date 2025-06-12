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
                                const jsonData = JSON.parse(jsonDataString);
                                appendMessage({ role: 'assistant', content: jsonData }, true);
                            } catch (e) {
                                console.error("JSON parsing error:", e, "Data:", jsonDataString);
                                appendMessage({ role: 'assistant', content: { error: "回應格式錯誤" } }, true);
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
            if (content.answer_summary) markdownString += `${content.answer_summary}\n\n`;
            
            if (content.comparison_table && content.comparison_table.length > 0) {
                markdownString += `### 規格比較\n\n`;
                markdownString += `| 特性 | AG958 | AKK839 |\n`;
                markdownString += `|:---|:---|:---|\n`;
                content.comparison_table.forEach(row => {
                    markdownString += `| ${row.feature || 'N/A'} | ${row.AG958 || 'N/A'} | ${row.AKK839 || 'N/A'} |\n`;
                });
                markdownString += `\n`;
            }

            if (content.conclusion) markdownString += `### 結論建議\n${content.conclusion}\n\n`;
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
    
    function showWelcomeMessage() {
        chatMessages.innerHTML = ''; // 清空
        const welcome = {
            role: 'assistant',
            content: {
                answer_summary: "您好！我是您的 AI 銷售助理。我可以回答關於 **AG958** 和 **AKK839** 筆記型電腦的問題，並為您進行比較。",
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
                     textToCopy += `- ${row.feature}: AG958(${row.AG958 || 'N/A'}), AKK839(${row.AKK839 || 'N/A'})\n`;
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