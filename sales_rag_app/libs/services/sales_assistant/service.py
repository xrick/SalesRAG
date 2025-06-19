import json
import pandas as pd
from ..base_service import BaseService
from ...RAG.DB.MilvusQuery import MilvusQuery
from ...RAG.DB.DuckDBQuery import DuckDBQuery
from ...RAG.LLM.LLMInitializer import LLMInitializer
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


'''
['modeltype', 'version', 'modelname', 'mainboard', 
'devtime', 'pm', 'structconfig', 'lcd', 'touchpanel', 
'iointerface', 'ledind', 'powerbutton', 'keyboard', 
'webcamera', 'touchpad', 'fingerprint', 'audio', 
'battery', 'cpu', 'gpu', 'memory', 'lcdconnector', 
'storage', 'wifi', 'thermal', 'tpm', 'rtc', 'wireless', 
'softwareconfig', 'ai', 'accessory', 'otherfeatures', 
'cetfication', 'Unnamed: 33', 'Unnamed: 34']
'''
class SalesAssistantService(BaseService):
    def __init__(self):
        self.llm = LLMInitializer().get_llm()
        self.milvus_query = MilvusQuery(collection_name="sales_notebook_specs_csv")
        self.duckdb_query = DuckDBQuery(db_file="db/sales_specs.db")
        self.prompt_template = self._load_prompt_template("libs/services/sales_assistant/prompts/sales_prompt4.txt")
        
        # ★ 修正點 1：修正 spec_fields 列表，使其與 .csv 檔案的標題列完全一致
        self.spec_fields = [
            'modeltype', 
            'version', 
            'modelname', 
            'mainboard', 
            'devtime', 'pm', 
            'structconfig', 'lcd', 
            'touchpanel', 
            'iointerface', 'ledind', 
            'powerbutton', 'keyboard', 
            'webcamera', 'touchpad', 
            'fingerprint', 'audio', 
            'battery', 'cpu', 'gpu', 
            'memory', 'lcdconnector', 
            'storage', 'wifi', 'thermal', 
            'tpm', 'rtc', 'wireless', 
            'softwareconfig', 'ai', 
            'accessory', 'otherfeatures', 
            'cetfication'
        ]

    def _load_prompt_template(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    async def chat_stream(self, query: str, **kwargs):
        """
        執行 RAG 流程，使用修正後的欄位名稱。
        """
        try:
            # 1. 使用 Milvus 找出相關的筆電型號
            logging.info(f"步驟 1: Milvus 語意搜尋 - '{query}'")
            retrieved_milvus = self.milvus_query.search(query, top_k=5)
            
            # 新增詳細日誌來檢查 Milvus 回傳的資料
            logging.info(f"Milvus 原始搜尋結果數量: {len(retrieved_milvus)}")
            for i, doc in enumerate(retrieved_milvus):
                logging.info(f"結果 {i+1}: {doc}")
            
            # ★ 修正點 2：過濾掉 'nan' 值，只保留有效的型號
            relevant_models = []
            for doc in retrieved_milvus:
                modelname = doc.get('modelname')
                logging.info(f"檢查 modelname: '{modelname}' (類型: {type(modelname)})")
                if modelname and modelname != 'nan' and str(modelname).lower() != 'nan':
                    relevant_models.append(modelname)
                    logging.info(f"添加有效型號: {modelname}")
                else:
                    logging.info(f"跳過無效型號: {modelname}")
            
            # 去重
            relevant_models = list(set(relevant_models))
            
            if not relevant_models:
                logging.warning("Milvus 未找到任何有效的筆電型號。")
                yield f"data: {json.dumps({'answer_summary': '抱歉，我們的資料庫中找不到與您問題相關的筆電型號。', 'comparison_table': []}, ensure_ascii=False)}\n\n"
                return

            logging.info(f"Milvus 找到相關型號: {relevant_models}")

            # 2. 使用 DuckDB 根據型號取得完整、乾淨的規格資料
            logging.info(f"步驟 2: DuckDB 精確查詢 - 型號: {relevant_models}")
            
            placeholders = ', '.join(['?'] * len(relevant_models))
            # ★ 修正點 3：在 SQL 查詢中使用 'modelname' 欄位
            sql_query = f"SELECT * FROM specs WHERE modelname IN ({placeholders})"
            
            full_specs_records = self.duckdb_query.query_with_params(sql_query, relevant_models)

            if not full_specs_records:
                logging.error(f"DuckDB 查詢失敗或未找到型號為 {relevant_models} 的資料。")
                yield f"data: {json.dumps({'answer_summary': '發生了點問題，無法從資料庫中取得產品詳細規格。', 'comparison_table': []}, ensure_ascii=False)}\n\n"
                return

            # 3. 將查詢結果格式化為 LLM 需要的上下文
            context_list_of_dicts = [dict(zip(self.spec_fields, record)) for record in full_specs_records]
            # ★ 修正點 4：在傳遞給 LLM 的 JSON 中，使用 'modelname' 作為統一的鍵，方便 prompt 處理
            for item in context_list_of_dicts:
                item['modelname'] = item.get('modelname', 'Unknown Model')

            context_str = json.dumps(context_list_of_dicts, indent=2, ensure_ascii=False)
            logging.info("成功將 DuckDB 資料轉換為 JSON 上下文。")

            # 4. 建構提示並請求 LLM
            final_prompt = self.prompt_template.replace("{context}", context_str).replace("{query}", query)
            logging.info("\n=== 最終傳送給 LLM 的提示 (Final Prompt) ===\n" + final_prompt + "\n========================================")

            response_str = self.llm.invoke(final_prompt)
            logging.info(f"\n=== 從 LLM 收到的原始回應 ===\n{response_str}\n=============================")

            # 5. 解析並回傳 JSON
            try:
                # 首先檢查是否有 <think> 標籤，如果有則提取 </think> 之後的內容
                think_end = response_str.find("</think>")
                if think_end != -1:
                    # 提取 </think> 之後的內容
                    cleaned_response_str = response_str[think_end + 8:].strip()
                    logging.info(f"提取 </think> 之後的內容: {cleaned_response_str}")
                else:
                    # 如果沒有 <think> 標籤，使用原始回應
                    cleaned_response_str = response_str
                
                # 在清理後的內容中尋找 JSON
                json_start = cleaned_response_str.find("{")
                json_end = cleaned_response_str.rfind("}")
                if json_start != -1 and json_end != -1:
                    json_content = cleaned_response_str[json_start:json_end+1]
                    parsed_json = json.loads(json_content)
                    yield f"data: {json.dumps(parsed_json, ensure_ascii=False)}\n\n"
                else:
                    raise ValueError("在 LLM 回應中找不到有效的 JSON 物件。")
            except (json.JSONDecodeError, ValueError) as json_err:
                logging.error(f"JSON 解析失敗: {json_err}\n原始回應: {response_str}")
                error_obj = {
                    "answer_summary": "抱歉，AI 回應的格式不正確，無法解析。",
                    "comparison_table": []
                }
                yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"

        except Exception as e:
            logging.error(f"在 chat_stream 中發生未預期的錯誤: {e}", exc_info=True)
            error_obj = {"error": f"服務內部發生錯誤: {e}"}
            yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"