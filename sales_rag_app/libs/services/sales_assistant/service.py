import json
from langchain_core.prompts import PromptTemplate
from ..base_service import BaseService
from ...RAG.DB.MilvusQuery import MilvusQuery
from ...RAG.DB.DuckDBQuery import DuckDBQuery
from ...RAG.LLM.LLMInitializer import LLMInitializer

class SalesAssistantService(BaseService):
    def __init__(self):
        # 初始化 LLM
        self.llm = LLMInitializer().get_llm()

        # 初始化資料庫查詢器
        self.milvus_query = MilvusQuery(collection_name="sales_notebook_specs")
        self.duckdb_query = DuckDBQuery(db_file="sales_rag_app/db/sales_specs.db")

        # 載入提示模板
        self.prompt_template = self._load_prompt_template("sales_rag_app/libs/services/sales_assistant/prompts/sales_prompt.txt")

    def _load_prompt_template(self, path: str) -> PromptTemplate:
        with open(path, 'r', encoding='utf-8') as f:
            template_str = f.read()
        return PromptTemplate.from_template(template_str)

    def _get_structured_specs(self, keywords: list) -> dict:
        """從 DuckDB 查詢結構化資料"""
        specs = {}
        for keyword in keywords:
            query_sql = f"SELECT model_name, feature, value FROM specs WHERE feature ILIKE '%{keyword}%' OR value ILIKE '%{keyword}%'"
            results = self.duckdb_query.query(query_sql)
            if results:
                for row in results:
                    feature_key = f"{row[1]} ({row[0]})" # e.g. "TDP (AG958)"
                    specs[feature_key] = row[2]
        return specs

    async def chat_stream(self, query: str, **kwargs):
        """執行完整的 RAG 流程"""
        try:
            # 1. 知識檢索
            # 從 Milvus 進行語意搜尋
            retrieved_docs = self.milvus_query.search(query, top_k=5)
            semantic_context = "\n---\n".join([f"Source: {doc['source']}\nContent: {doc['text']}" for doc in retrieved_docs])

            # 從 DuckDB 進行關鍵字查詢
            # (簡易的關鍵字提取，實際應用可更複雜)
            keywords_to_check = ["TDP", "CPU", "RAM", "Weight", "Dimensions", "Battery", "Wi-Fi"]
            found_keywords = [kw for kw in keywords_to_check if kw.lower() in query.lower()]
            structured_context_dict = self._get_structured_specs(found_keywords)
            structured_context = "\n".join([f"- {k}: {v}" for k, v in structured_context_dict.items()])

            # 2. 上下文組合
            final_context = f"### 相關文件片段 (語意搜尋結果):\n{semantic_context}\n\n"
            if structured_context:
                final_context += f"### 精確規格資料 (關鍵字查詢結果):\n{structured_context}"

            # 3. 建構提示
            final_prompt = self.prompt_template.format(context=final_context, query=query)

            print("--- FINAL PROMPT ---")
            print(final_prompt)
            print("--------------------")

            # 4. LLM 互動與串流
            response_str = self.llm.invoke(final_prompt)

            # 嘗試解析 LLM 回傳的字串為 JSON
            try:
                # LLM 可能回傳被 Markdown 包裹的 JSON，需要清理
                cleaned_response_str = response_str.strip().removeprefix("```json").removesuffix("```").strip()
                parsed_json = json.loads(cleaned_response_str)
                # 使用 Server-Sent Events (SSE) 格式回傳完整的 JSON 物件
                yield f"data: {json.dumps(parsed_json, ensure_ascii=False)}\n\n"
            except json.JSONDecodeError:
                # 如果 LLM 沒有回傳標準 JSON，則將其包裝在一個錯誤物件中回傳
                error_obj = {
                    "answer_summary": "抱歉，AI 回應的格式不正確，無法解析。",
                    "comparison_table": [],
                    "conclusion": "請稍後再試或調整您的問題。",
                    "source_references": [f"Raw response from AI: {response_str}"]
                }
                yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"Error in SalesAssistantService.chat_stream: {e}")
            error_obj = {"error": "An unexpected error occurred in the service."}
            yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"
````

#### **`sales_rag_app/libs/services/sales_assistant/prompts/sales_prompt.txt`**

````text
### SYSTEM PROMPT ###
你是一位頂級的筆記型電腦技術銷售專家。你的任務是根據提供的「上下文資料」，精確、客觀地回答使用者關於 AG958 和 AKK839 這兩款筆記型電腦的問題。

### 指令 ###
1.  **角色扮演**：始終以專業、自信的銷售專家口吻回答。
2.  **資料來源**：你的所有回答都「必須」嚴格基於提供的「上下文資料」。上下文中可能包含「規格文件」和「分析文件」。嚴禁回答任何在上下文中找不到的資訊。如果資料不足，請直接回答「根據我目前的資料，無法回答這個問題。」
3.  **比較問題**：如果使用者提出比較性的問題 (例如「哪台比較好」、「有什麼不同」)，你必須同時列出兩台機型的相關規格，並根據數據進行客觀比較。
4.  **單一模型問題**：如果使用者只問單一機型，請專注回答該機型的資訊，但如果上下文中包含與另一機型的對比，可以適度提及以突顯其特點。
5.  **輸出格式**：你的回答「必須」是一個完整的、格式正確的 JSON 物件，不得包含任何 JSON 格式以外的文字 (例如 "Here is the JSON:" 或 Markdown 的 ```json 標籤)。JSON 結構如下：

{
  "answer_summary": "對使用者問題的總結性回答，以自然語言呈現，應簡潔明瞭。",
  "comparison_table": [
    {
      "feature": "比較的特性 (例如 '散熱設計')",
      "AG958": "AG958 在此特性上的規格或描述",
      "AKK839": "AKK839 在此特性上的規格或描述"
    },
    {
      "feature": "CPU 型號",
      "AG958": "AMD Ryzen 9 6900HX",
      "AKK839": "AMD Ryzen 9 8945HS"
    }
  ],
  "conclusion": "基於比較後的專家結論或建議。例如：'如果您追求極致的遊戲性能，AG958 更適合；若您需要兼顧效能與便攜性，AKK839 是不錯的選擇。'",
  "source_references": [
    "來源文件的片段一...",
    "來源文件的片段二..."
  ]
}

### 上下文資料 ###
---
{context}
---

### 使用者問題 ###
{query}

### 你的 JSON 回答 ###
````

#### **`sales_rag_app/libs/RAG/DB/DatabaseQuery.py`**

```python
from abc import ABC, abstractmethod

class DatabaseQuery(ABC):
    @abstractmethod
    def connect(self):
        raise NotImplementedError

    @abstractmethod
    def query(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError