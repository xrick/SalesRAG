import json
from langchain_core.prompts import PromptTemplate
from ..base_service import BaseService
from ...RAG.DB.MilvusQuery import MilvusQuery
from ...RAG.DB.DuckDBQuery import DuckDBQuery
from ...RAG.LLM.LLMInitializer import LLMInitializer

import logging

###setup debug
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class SalesAssistantService(BaseService):
    def __init__(self):
        # 初始化 LLM
        self.llm = LLMInitializer().get_llm()

        # 初始化資料庫查詢器
        self.milvus_query = MilvusQuery(collection_name="sales_notebook_specs")
        self.duckdb_query = DuckDBQuery(db_file="db/sales_specs.db")

        # 載入提示模板
        self.prompt_template = self._load_prompt_template("libs/services/sales_assistant/prompts/sales_prompt2.txt")

    def _load_prompt_template(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

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
            final_prompt = self.prompt_template.replace("{context}", final_context).replace("{query}", query)

            print("\n=== FINAL PROMPT ===")
            print(final_prompt)
            print("===================\n")

            # 4. LLM 互動與串流
            response_str = self.llm.invoke(final_prompt)
            
            # Log the raw response for debugging
            print("\n=== RAW LLM RESPONSE ===")
            print(response_str)
            print("=======================\n")

            # 嘗試解析 LLM 回傳的字串為 JSON
            try:
                # 提取 JSON 部分
                json_start = response_str.find("```json")
                if json_start == -1:
                    json_start = response_str.find("```")
                if json_start != -1:
                    json_start = response_str.find("{", json_start)
                    json_end = response_str.rfind("}")
                    if json_start != -1 and json_end != -1:
                        cleaned_response_str = response_str[json_start:json_end+1]
                    else:
                        raise ValueError("無法找到有效的 JSON 內容")
                else:
                    raise ValueError("無法找到 JSON 代碼塊")

                print("\n=== EXTRACTED JSON ===")
                print(cleaned_response_str)
                print("=====================\n")
                
                # 嘗試修復常見的 JSON 格式問題
                cleaned_response_str = cleaned_response_str.replace("'", '"')  # 替換單引號為雙引號
                cleaned_response_str = cleaned_response_str.replace("\n", " ")  # 移除換行符
                cleaned_response_str = cleaned_response_str.replace("  ", " ")  # 移除多餘空格
                
                print("\n=== FINAL JSON STRING ===")
                print(cleaned_response_str)
                print("=======================\n")
                
                parsed_json = json.loads(cleaned_response_str)
                # 使用 Server-Sent Events (SSE) 格式回傳完整的 JSON 物件
                yield f"data: {json.dumps(parsed_json, ensure_ascii=False)}\n\n"
            except (json.JSONDecodeError, ValueError) as json_err:
                print(f"\n=== JSON DECODE ERROR ===")
                print(f"Error message: {json_err}")
                if isinstance(json_err, json.JSONDecodeError):
                    print(f"Error position: {json_err.pos}")
                    print(f"Error line: {json_err.lineno}")
                    print(f"Error column: {json_err.colno}")
                print(f"Failed to parse response: {cleaned_response_str}")
                print("========================\n")
                
                # 如果 LLM 沒有回傳標準 JSON，則將其包裝在一個錯誤物件中回傳
                error_obj = {
                    "answer_summary": "抱歉，AI 回應的格式不正確，無法解析。",
                    "comparison_table": [],
                    "conclusion": "請稍後再試或調整您的問題。",
                    "source_references": [f"Raw response from AI: {response_str}"]
                }
                yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"\n=== UNEXPECTED ERROR ===")
            print(f"Error in SalesAssistantService.chat_stream: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            print("=======================\n")
            error_obj = {"error": "An unexpected error occurred in the service."}
            yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"
