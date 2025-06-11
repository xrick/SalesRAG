document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const chatBox = document.getElementById("chat-box");

    // 自動調整輸入框高度
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = `${userInput.scrollHeight}px`;
    });

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        // 清空輸入框並重設高度
        userInput.value = "";
        userInput.style.height = "auto";

        // 顯示使用者訊息
        appendMessage(query, "user");

        // 禁用傳送按鈕
        sendButton.disabled = true;

        // 顯示"思考中"訊息
        const thinkingBubble = appendMessage("AI 正在思考中", "assistant thinking");

        try {
            const response = await fetch("/api/chat-stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, service_name: "sales_assistant" })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "請求失敗");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;

            // 清空"思考中"的內容，準備接收串流
            thinkingBubble.classList.remove("thinking");
            const responseContent = thinkingBubble.querySelector('.message-content');
            responseContent.innerHTML = "";

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                const chunk = decoder.decode(value, { stream: true });
                
                // 處理 SSE 數據
                const lines = chunk.split('\n\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonDataString = line.substring(6);
                        if (jsonDataString) {
                            try {
                                const jsonData = JSON.parse(jsonDataString);
                                renderResponse(responseContent, jsonData);
                            } catch (e) {
                                console.error("解析 JSON 失敗:", e, "Data:", jsonDataString);
                                responseContent.innerHTML += "<p style='color:red;'>回應格式錯誤。</p>";
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error("聊天請求錯誤:", error);
            const errorContent = thinkingBubble.querySelector('.message-content');
            errorContent.innerHTML = `<p style='color:red;'>抱歉，發生錯誤：${error.message}</p>`;
        } finally {
            sendButton.disabled = false;
            userInput.focus();
        }
    });

    function appendMessage(text, type) {
        const messageBubble = document.createElement("div");
        messageBubble.className = `message-bubble ${type}`;
        
        const messageContent = document.createElement("div");
        messageContent.className = "message-content";
        messageContent.innerText = text;

        messageBubble.appendChild(messageContent);
        chatBox.appendChild(messageBubble);
        chatBox.scrollTop = chatBox.scrollHeight;
        return messageBubble;
    }

    function renderResponse(container, data) {
        if (data.error) {
            container.innerHTML = `<p class='error'>助理發生錯誤: ${data.error}</p>`;
            return;
        }

        let markdownString = "";

        if (data.answer_summary) {
            markdownString += `### 回答摘要\n${data.answer_summary}\n\n`;
        }

        if (data.comparison_table && data.comparison_table.length > 0) {
            markdownString += `### 規格比較\n\n`;
            markdownString += `| 特性 | AG958 | AKK839 |\n`;
            markdownString += `|:---|:---|:---|\n`;
            data.comparison_table.forEach(row => {
                markdownString += `| ${row.feature || 'N/A'} | ${row.AG958 || 'N/A'} | ${row.AKK839 || 'N/A'} |\n`;
            });
            markdownString += `\n`;
        }

        if (data.conclusion) {
            markdownString += `### 結論建議\n${data.conclusion}\n\n`;
        }
        
        if (data.source_references && data.source_references.length > 0) {
            markdownString += `<details><summary>參考資料來源</summary>\n\n`;
            data.source_references.forEach(source => {
                const cleanedSource = source.replace(/[\r\n]+/g, ' ').trim();
                if(cleanedSource) {
                    markdownString += `> ${cleanedSource}\n\n`;
                }
            });
            markdownString += `</details>`;
        }
        
        // 使用 marked.js 將 Markdown 渲染為 HTML
        container.innerHTML = marked.parse(markdownString);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
