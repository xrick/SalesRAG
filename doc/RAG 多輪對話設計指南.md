<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# RAG 多輪對話設計指南

在 Retrieval-Augmented Generation（RAG）應用中加入**多輪澄清機制**，可有效避免一次性詢問帶來的資訊落差，並逐步引導使用者說出真正需求。以下從架構、對話策略、技術要點到 UX 實務給出完整設計藍圖。

多輪 RAG 對話流程總覽

![多輪 RAG 對話設計流程示意圖](https://user-gen-media-assets.s3.amazonaws.com/gpt4o_images/a60a6bf4-4e8f-46d0-9620-f6a1058ec875.png)

多輪 RAG 對話設計流程示意圖

## 1. 架構總覽

### 1.1 角色分層

1. Front-end Chat Interface
    - 即時呈現候選澄清選項、答案與來源
2. Dialogue Manager
    - 控制 turn-taking、意圖偵測、回合計數
3. History-Aware Retriever
    - 利用最新提問＋歷史對話生成「獨立檢索查詢」
4. Vector Store / Index
    - 向量檢索 + Metadata filter
5. LLM Answer Generator
    - 將檢索片段（context）與使用者問題合併生成回覆
6. Feedback \& Logging
    - 儲存澄清問答供 RLHF 或 RLAIF 強化

### 1.2 關鍵模組

| 模組 | 功能 | 核心技術 | 注意事項 |
| :-- | :-- | :-- | :-- |
| Question Re-phraser | 將含代詞/省略的追問重寫成獨立問題 | history-aware prompt | 避免過長上下文造成 token 爆 |
| Ambiguity Detector | 判定是否需要澄清 | 信心閾值、歧義類型分類 | 引入二階標註「未來回合績效」可提升判定準確[^1] |
| Clarification Generator | 產生針對性澄清問句 | AT-CoT / ReAct | 問句須可由使用者單句回答 |
| Disambiguation UX | 提供多選或自由輸入 | button list、quick reply | 視通路（App/Web/LINE）調整 |

## 2. 多輪對話策略

### 2.1 澄清時機

1. **Retriever 回傳不足**：top-k 得分低於閾值
2. **多意圖競合**：>1 個意圖分數相近（如 0.55 vs 0.53）
3. **問題含空格槽（slot）**：日期、人名、產品型號缺失

### 2.2 澄清類型

| 類型 | 範例 | 設計提要 |
| :-- | :-- | :-- |
| 缺值填充 | 「請問想查哪一天的報價？」 | slot-filling；限制回答格式 |
| 多意圖選擇 | 「您要退貨還是查詢退貨進度？」 | 提供 2-3 選項；加入「其他」 |
| 範圍限定 | 「是指公司整體營收，還是特定事業部？」 | 引導到最小可回答單元 |
| 資料時效 | 「需要今年最新財報，還是歷史平均？」 | 決定檢索時間窗口 |

### 2.3 對話結束判定

1. 使用者明確肯定（“沒問題了”）
2. 連續兩次回答「不需要更多資訊」
3. 回合數達上限（如 8 turns）自動收斂總結

## 3. 技術實踐細節

### 3.1 History-Aware Retriever

```python
contextualize_prompt = """
Given chat history and latest user question,
produce a standalone search query without answering.
"""
retriever_chain = create_history_aware_retriever(
    llm, vector_retriever, contextualize_prompt
)
```

- 減少多餘歷史訊息干擾
- 支援 streaming API，保持低延遲


### 3.2 Clarification Question Selection

1. 產生 N=3 候選問句
2. 估算每句「信息增益」≈ 檢索置信度提升
3. 選擇最高者發出；其餘存入記憶庫供日後微調

### 3.3 Query Decomposition

對複合問題先分解子詢問，再逐一檢索並合併推理，可提升多 hop 指標 36%[^2]。

### 3.4 RLHF / Double-Turn Preference

將「澄清後回答正確」視為 reward，優於單回合標註[^1]。

## 4. UX 設計原則

### 4.1 一致、自然的語氣

- 系統提示（system prompt）確保語調前後一致
- 回覆過長時提供 TL;DR + 「想看詳細？」連結


### 4.2 明確顯示可選動作

![Example of a multi-turn WhatsApp chatbot conversation guiding a user through a product return process with options and follow-up questions.](https://pplx-res.cloudinary.com/image/upload/v1750003587/pplx_project_search_images/8800191b22990f0bb9e30b58fb079488cc30b8fa.jpg)

Example of a multi-turn WhatsApp chatbot conversation guiding a user through a product return process with options and follow-up questions.

### 4.3 當前上下文提示條

- 在輸入框上方簡短顯示目前查詢主題
- 提供「修改」按鈕快速回溯


### 4.4 檔案多源支援

- 後台允許一次上傳 PDF/Excel/Word，建立向量索引
- 以 Metadata 標示版本、語言、保密等級

![Chatbot platform interface showing multi-source file uploads to support instant answers in multi-turn conversations.](https://pplx-res.cloudinary.com/image/upload/v1752633778/pplx_project_search_images/5041188531ba496d37a984bec49d027fbae24696.jpg)

Chatbot platform interface showing multi-source file uploads to support instant answers in multi-turn conversations.

## 5. 性能與評估

| 指標 | 目標值 | 量測方式 |
| :-- | :-- | :-- |
| Clarification Trigger Precision | ≥ 0.85 | 人工標註隨機樣本 |
| Turn-per-Query 平均 | ≤ 3 | 日誌統計 |
| Top-1 Answer F1 | +10% vs 無澄清 | HotpotQA / 自訂測試集 |
| UX CSAT | > 4.3/5 | 事後問卷 |

## 6. 迭代與最佳化

1. 追蹤每回合澄清問句 → 回答正確率，調整 prompt
2. 對高頻「無答案」案例進行資料補充或內部工具 hook
3. 週期性重新向量化最新文件，避免時效落差

## 結語

透過**歧義檢測 → 精準澄清 → 動態檢索 → 答覆生成**的閉環設計，RAG 應用能在保持高準確度的同時，讓使用者以最少步驟獲得真正想問的答案，並持續透過回饋強化整體體驗。

<div style="text-align: center">⁂</div>

[^1]: https://arxiv.org/html/2410.13788v1

[^2]: https://arxiv.org/abs/2507.00355

[^3]: https://vocus.cc/article/67210b48fd89780001df592f

[^4]: https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview

[^5]: https://www.retellai.com/glossary/multi-turn-conversation

[^6]: https://www.linkedin.com/posts/andriyburkov_did-you-notice-that-chat-llms-dont-ask-clarifying-activity-7208241144814563328-vFlp

[^7]: https://python.langchain.com/docs/versions/migrating_chains/conversation_retrieval_chain/

[^8]: https://idataagent.com/2024/05/12/the-ultimate-introduction-to-rag-technology-detailed-explanation-of-infrastructure-and-working-principles/

[^9]: https://en.wikipedia.org/wiki/Retrieval-augmented_generation

[^10]: https://www.lyzr.ai/glossaries/multi-turn-conversational-agents/

[^11]: https://openreview.net/forum?id=cwuSAR7EKd

[^12]: https://python.langchain.com/api_reference/langchain/chains/langchain.chains.conversational_retrieval.base.ConversationalRetrievalChain.html

[^13]: https://www.purestorage.com/tw/knowledge/what-is-retrieval-augmented-generation.html

[^14]: https://www.k2view.com/what-is-retrieval-augmented-generation

[^15]: https://aclanthology.org/2024.scichat-1.8/

[^16]: https://arxiv.org/abs/2410.13788

[^17]: https://api.python.langchain.com/en/latest/chains/langchain.chains.conversational_retrieval.base.ConversationalRetrievalChain.html

[^18]: https://ithelp.ithome.com.tw/articles/10348870

[^19]: https://aws.amazon.com/what-is/retrieval-augmented-generation/

[^20]: https://poly.ai/blog/multi-turn-conversations-what-are-they-and-why-do-they-matter-for-your-customers/

[^21]: https://www.reddit.com/r/LangChain/comments/1i53cz4/how_do_i_get_an_llm_to_ask_clarifying_questions/

[^22]: https://python.langchain.com.cn/docs/modules/chains/popular/chat_vector_db

[^23]: https://www.indexme.co.uk/clarification-prompting-guide/

[^24]: https://www.informalwriting.cc/p/ai-interaction-beyond-search

[^25]: https://dev.to/guilhermecxe/how-a-history-aware-retriever-works-5e07

[^26]: https://blog.kore.ai/cobus-greyling/craft-successful-conversational-user-interfaces-align-user-intent-with-developed-intent

[^27]: https://www.reddit.com/r/PromptEngineering/comments/1e4xwbp/how_to_train_llms_to_ask_follow_up_questions/

[^28]: https://www.indeed.com/career-advice/career-development/clarifying-questions

[^29]: https://blog.csdn.net/fenglingguitar/article/details/142455201

[^30]: https://api.python.langchain.com/en/latest/chains/langchain.chains.history_aware_retriever.create_history_aware_retriever.html

[^31]: https://arxiv.org/pdf/2009.01509.pdf

[^32]: https://zilliz.com/ai-faq/how-can-an-llm-be-guided-to-ask-a-followup-question-when-the-retrieved-information-is-insufficient-think-in-terms-of-conversational-rag-or-an-agent-that-can-perform-multiple-retrievethenread-cycles

[^33]: https://learningimpactmodel.com/blog-detail.php?blog=Asking+Clarifying+Questions-90

[^34]: https://www.aidoczh.com/langchain/v0.2/docs/tutorials/qa_chat_history/

[^35]: https://github.com/langchain-ai/langchain/discussions/24653

[^36]: https://arxiv.org/abs/2308.08496

[^37]: https://arxiv.org/pdf/2407.12017.pdf

[^38]: https://www.reddit.com/r/ChatGPTCoding/comments/13x2be7/no_one_told_me_how_important_ask_clarifying/

[^39]: https://www.aidoczh.com/langchain/v0.2/docs/how_to/qa_chat_history_how_to/

[^40]: https://www.reddit.com/r/LangChain/comments/1h68m63/history_aware_retriever/

[^41]: https://aws.amazon.com/blogs/machine-learning/part-3-how-to-approach-conversation-design-with-amazon-lex-building-and-testing/

[^42]: https://milvus.io/ai-quick-reference/how-can-an-llm-be-guided-to-ask-a-followup-question-when-the-retrieved-information-is-insufficient-think-in-terms-of-conversational-rag-or-an-agent-that-can-perform-multiple-retrievethenread-cycles

[^43]: https://jenz.ai/term/react-prompting/

[^44]: https://blog.lancedb.com/better-rag-with-active-retrieval-augmented-generation-flare-3b66646e2a9f/

[^45]: https://www.reddit.com/r/LangChain/comments/1708wxo/followup_questions_to_previous_conversations/

[^46]: https://www.zendesk.com/blog/conversational-ux/

[^47]: https://www.themoonlight.io/en/review/question-decomposition-for-retrieval-augmented-generation

[^48]: https://arize.com/docs/phoenix/cookbook/prompt-engineering/react-prompting

[^49]: https://openreview.net/forum?id=awtd0XhzKQ

[^50]: https://github.com/langchain-ai/langchain/discussions/17803

[^51]: https://www.albannaclinic.com/ai-news/conversational-ux-ui-explained-a-beginner-s-guide/

[^52]: https://www.themoonlight.io/de/review/question-decomposition-for-retrieval-augmented-generation

[^53]: https://www.mercity.ai/blog-post/react-prompting-and-react-based-agentic-systems

[^54]: https://flareapp.io/terms-of-use

[^55]: https://stephaniewalter.design/blog/a-cheatsheet-for-user-interview-and-follow-ups-questions/

[^56]: https://www.promptingguide.ai/techniques/react

[^57]: https://support.flarehr.com/hc/en-us/articles/900003179763-How-to-send-an-Information-Request

[^58]: https://www.youtube.com/watch?v=X5DmBQSkzHA

[^59]: https://www.reforge.com/guides/design-a-conversational-ux-experience

[^60]: https://haystack.deepset.ai/blog/query-decomposition

[^61]: https://uxmag.com/articles/7-principles-of-conversational-design-banner

[^62]: https://aclanthology.org/D19-1172/

[^63]: https://www.stan.vision/journal/conversational-ux-design-how-to-enhance-user-engagement

[^64]: https://aclanthology.org/2020.acl-main.651/

[^65]: https://blog.epsilla.com/advanced-rag-optimization-boosting-answer-quality-on-complex-questions-through-query-decomposition-e9d836eaf0d5

[^66]: https://exotel.com/blog/conversational-ux/

[^67]: https://aws.amazon.com/blogs/machine-learning/introducing-multi-turn-conversation-with-an-agent-node-for-amazon-bedrock-flows-preview/

[^68]: https://github.com/aliannejadi/ClariQ

[^69]: https://api.js.langchain.com/functions/langchain.chains_history_aware_retriever.createHistoryAwareRetriever.html

[^70]: https://haystack.deepset.ai/cookbook/query_decomposition

[^71]: https://aclanthology.org/2020.emnlp-main.150/

[^72]: https://github.com/vaibhav4595/ClarQ

[^73]: https://dev.to/jamesli/in-depth-understanding-of-rag-query-transformation-optimization-multi-query-problem-decomposition-and-step-back-27jg

[^74]: https://developers.liveperson.com/conversation-builder-dialogs-disambiguation-dialogs.html

[^75]: https://zilliz.com/ai-faq/how-can-amazon-bedrock-support-multiturn-conversational-applications-like-chatbots-that-maintain-context-over-several-interactions

[^76]: https://www.dfki.de/fileadmin/user_upload/import/14889_To_Clarify_or_not_to_Clarify__A_Comparative_Analysis_of_Clarification_Classification_with_Fine_Tuning__Prompt_Tuning__and_Prompt_Engineering-final.pdf

[^77]: https://cloud.ibm.com/docs/watson-assistant?topic=watson-assistant-dialog-runtime

[^78]: https://community.openai.com/t/how-to-use-chroma-db-as-retriever/768358

[^79]: https://www.linkedin.com/pulse/why-dont-llms-ask-clarifying-questions-kalle-kulonen-se8kf

[^80]: https://aclanthology.org/2023.emnlp-main.41.pdf

[^81]: https://all.docs.genesys.com/GDE/Current/User/Intent_Disambiguation

[^82]: https://github.com/awslabs/agent-squad

[^83]: https://stackoverflow.com/questions/78826732/how-do-create-history-aware-retriever-and-runnablewithmessagehistory-interact-wh

[^84]: https://arxiv.org/html/2405.15784v1

[^85]: https://arxiv.org/html/2504.12113v1

[^86]: https://www.humanfirst.ai/blog/intent-disambiguation

[^87]: https://aws.amazon.com/about-aws/whats-new/2025/01/amazon-bedrock-flows-multi-turn-conversation-support/

[^88]: https://github.com/langchain-ai/langchain/discussions/16002

