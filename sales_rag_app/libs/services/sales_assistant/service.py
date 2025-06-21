import json
import pandas as pd
from ..base_service import BaseService
from ...RAG.DB.MilvusQuery import MilvusQuery
from ...RAG.DB.DuckDBQuery import DuckDBQuery
from ...RAG.LLM.LLMInitializer import LLMInitializer
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 全域變數：存儲所有可用的modelname
AVAILABLE_MODELNAMES = [
    'AB819-S: FP6',
    'AG958',
    'AG958P',
    'AG958V',
    'AHP819: FP7R2',
    'AHP839',
    'AHP958',
    'AKK839',
    'AMD819-S: FT6',
    'AMD819: FT6',
    'APX819: FP7R2',
    'APX839',
    'APX958',
    'ARB819-S: FP7R2',
    'ARB839'
]

# 全域變數：存儲所有可用的modeltype
AVAILABLE_MODELTYPES = [
    '819',
    '839',
    '958'
]

'''
[
    'modeltype', 'version', 'modelname', 'mainboard', 'devtime',
    'pm', 'structconfig', 'lcd', 'touchpanel', 'iointerface', 
    'ledind', 'powerbutton', 'keyboard', 'webcamera', 'touchpad', 
    'fingerprint', 'audio', 'battery', 'cpu', 'gpu', 'memory', 
    'lcdconnector', 'storage', 'wifislot', 'thermal', 'tpm', 'rtc', 
    'wireless', 'lan', 'bluetooth', 'softwareconfig', 'ai', 'accessory', 
    'certfications', 'otherfeatures'
]
'''
class SalesAssistantService(BaseService):
    def __init__(self):
        self.llm = LLMInitializer().get_llm()
        self.milvus_query = MilvusQuery(collection_name="sales_notebook_specs")
        self.duckdb_query = DuckDBQuery(db_file="db/sales_specs.db")
        self.prompt_template = self._load_prompt_template("libs/services/sales_assistant/prompts/sales_prompt4.txt")
        
        # ★ 修正點 1：修正 spec_fields 列表，使其與 .xlsx 檔案的標題列完全一致
        self.spec_fields = [
            'modeltype', 'version', 'modelname', 'mainboard', 'devtime',
            'pm', 'structconfig', 'lcd', 'touchpanel', 'iointerface', 
            'ledind', 'powerbutton', 'keyboard', 'webcamera', 'touchpad', 
            'fingerprint', 'audio', 'battery', 'cpu', 'gpu', 'memory', 
            'lcdconnector', 'storage', 'wifislot', 'thermal', 'tpm', 'rtc', 
            'wireless', 'lan', 'bluetooth', 'softwareconfig', 'ai', 'accessory', 
            'certfications', 'otherfeatures'
        ]

    def _load_prompt_template(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _check_query_contains_modelname(self, query: str) -> tuple[bool, list]:
        """
        檢查查詢中是否包含有效的modelname
        返回: (是否包含modelname, 找到的modelname列表)
        """
        found_modelnames = []
        query_lower = query.lower()
        
        for modelname in AVAILABLE_MODELNAMES:
            if modelname.lower() in query_lower:
                found_modelnames.append(modelname)
        
        return len(found_modelnames) > 0, found_modelnames

    def _check_query_contains_modeltype(self, query: str) -> tuple[bool, list]:
        """
        檢查查詢中是否包含有效的modeltype
        返回: (是否包含modeltype, 找到的modeltype列表)
        """
        found_modeltypes = []
        query_lower = query.lower()
        
        for modeltype in AVAILABLE_MODELTYPES:
            if modeltype.lower() in query_lower:
                found_modeltypes.append(modeltype)
        
        return len(found_modeltypes) > 0, found_modeltypes

    def _get_models_by_type(self, modeltype: str) -> list:
        """
        根據modeltype獲取所有相關的modelname
        """
        try:
            sql_query = "SELECT DISTINCT modelname FROM specs WHERE modeltype = ? AND modelname IS NOT NULL AND modelname != '' AND modelname != 'nan' ORDER BY modelname"
            result = self.duckdb_query.query_with_params(sql_query, [modeltype])
            
            if result:
                modelnames = [row[0] for row in result if row[0] and str(row[0]).lower() != 'nan']
                logging.info(f"根據modeltype '{modeltype}' 找到的modelname: {modelnames}")
                return modelnames
            else:
                logging.warning(f"未找到modeltype為 '{modeltype}' 的modelname")
                return []
                
        except Exception as e:
            logging.error(f"查詢modeltype '{modeltype}' 相關modelname時發生錯誤: {e}")
            return []

    async def chat_stream(self, query: str, **kwargs):
        """
        執行 RAG 流程，使用修正後的欄位名稱。
        """
        try:
            # 首先檢查查詢中是否包含有效的modeltype
            contains_modeltype, found_modeltypes = self._check_query_contains_modeltype(query)
            
            # 檢查查詢中是否包含有效的modelname
            contains_modelname, found_modelnames = self._check_query_contains_modelname(query)
            
            # 如果同時包含modeltype和modelname，以modeltype為主
            if contains_modeltype and contains_modelname:
                logging.info(f"查詢同時包含modeltype和modelname，以modeltype為主")
                logging.info(f"找到的modeltype: {found_modeltypes}")
                logging.info(f"找到的modelname: {found_modelnames}")
                
                # 只取第一個modeltype
                target_modeltype = found_modeltypes[0]
                logging.info(f"使用第一個modeltype: {target_modeltype}")
                
                # 根據modeltype獲取所有相關的modelname
                target_modelnames = self._get_models_by_type(target_modeltype)
                
                if not target_modelnames:
                    error_message = f"未找到modeltype為 '{target_modeltype}' 的筆電型號。"
                    error_obj = {
                        "answer_summary": error_message,
                        "comparison_table": []
                    }
                    yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"
                    return
                
                # 直接使用DuckDB查詢這些modelname的資料
                logging.info(f"根據modeltype '{target_modeltype}' 查詢相關modelname: {target_modelnames}")
                
            elif contains_modeltype:
                # 只有modeltype，沒有modelname
                logging.info(f"查詢只包含modeltype: {found_modeltypes}")
                
                # 只取第一個modeltype
                target_modeltype = found_modeltypes[0]
                logging.info(f"使用第一個modeltype: {target_modeltype}")
                
                # 根據modeltype獲取所有相關的modelname
                target_modelnames = self._get_models_by_type(target_modeltype)
                
                if not target_modelnames:
                    error_message = f"未找到modeltype為 '{target_modeltype}' 的筆電型號。"
                    error_obj = {
                        "answer_summary": error_message,
                        "comparison_table": []
                    }
                    yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"
                    return
                
                # 直接使用DuckDB查詢這些modelname的資料
                logging.info(f"根據modeltype '{target_modeltype}' 查詢相關modelname: {target_modelnames}")
                
            elif contains_modelname:
                # 只有modelname，沒有modeltype
                logging.info(f"查詢只包含modelname: {found_modelnames}")
                target_modelnames = found_modelnames
                
            else:
                # 既沒有modeltype也沒有modelname
                available_types_str = "\n".join([f"- {modeltype}" for modeltype in AVAILABLE_MODELTYPES])
                available_models_str = "\n".join([f"- {model}" for model in AVAILABLE_MODELNAMES])
                error_message = f"您的查詢中沒有包含任何有效的筆電型號或系列。請明確指定要比較的型號名稱或系列。\n\n可用的系列包括：\n{available_types_str}\n\n可用的型號包括：\n{available_models_str}\n\n請重新提問，例如：'比較 958 系列的 CPU 性能' 或 '比較 AB819-S: FP6 和 AG958 的 CPU 性能'"
                
                error_obj = {
                    "answer_summary": error_message,
                    "comparison_table": []
                }
                yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"
                return

            # 使用DuckDB直接查詢指定的modelname
            logging.info(f"步驟 2: DuckDB 精確查詢 - 型號: {target_modelnames}")
            
            placeholders = ', '.join(['?'] * len(target_modelnames))
            sql_query = f"SELECT * FROM specs WHERE modelname IN ({placeholders})"
            
            full_specs_records = self.duckdb_query.query_with_params(sql_query, target_modelnames)

            if not full_specs_records:
                logging.error(f"DuckDB 查詢失敗或未找到型號為 {target_modelnames} 的資料。")
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
                
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_content = cleaned_response_str[json_start:json_end+1]
                    logging.info(f"提取的 JSON 內容: {json_content}")
                    
                    # 嘗試解析 JSON
                    parsed_json = json.loads(json_content)
                    
                    # 檢查是否已經是正確的格式
                    if "answer_summary" in parsed_json and "comparison_table" in parsed_json:
                        yield f"data: {json.dumps(parsed_json, ensure_ascii=False)}\n\n"
                    else:
                        # 嘗試將 LLM 的 JSON 轉換為我們需要的格式
                        logging.info("LLM 輸出的 JSON 格式不符合要求，嘗試轉換...")
                        converted_json = self._convert_llm_response_to_required_format(parsed_json, context_list_of_dicts, query)
                        if converted_json:
                            yield f"data: {json.dumps(converted_json, ensure_ascii=False)}\n\n"
                        else:
                            raise ValueError("無法轉換 LLM 回應為所需格式")
                else:
                    # 如果找不到 JSON，嘗試清理回應並重新尋找
                    logging.warning("在回應中找不到有效的 JSON 物件，嘗試清理回應...")
                    
                    # 移除可能的 markdown 格式
                    cleaned_response_str = cleaned_response_str.replace("```json", "").replace("```", "")
                    cleaned_response_str = cleaned_response_str.strip()
                    
                    # 再次尋找 JSON
                    json_start = cleaned_response_str.find("{")
                    json_end = cleaned_response_str.rfind("}")
                    
                    if json_start != -1 and json_end != -1 and json_end > json_start:
                        json_content = cleaned_response_str[json_start:json_end+1]
                        logging.info(f"清理後提取的 JSON 內容: {json_content}")
                        parsed_json = json.loads(json_content)
                        
                        if "answer_summary" in parsed_json and "comparison_table" in parsed_json:
                            yield f"data: {json.dumps(parsed_json, ensure_ascii=False)}\n\n"
                        else:
                            # 嘗試轉換格式
                            converted_json = self._convert_llm_response_to_required_format(parsed_json, context_list_of_dicts, query)
                            if converted_json:
                                yield f"data: {json.dumps(converted_json, ensure_ascii=False)}\n\n"
                            else:
                                raise ValueError("清理後的 JSON 結構仍不正確且無法轉換")
                    else:
                        raise ValueError("在 LLM 回應中找不到有效的 JSON 物件")
                        
            except (json.JSONDecodeError, ValueError) as json_err:
                logging.error(f"JSON 解析失敗: {json_err}")
                logging.error(f"原始回應: {response_str}")
                
                # 嘗試從回應中提取有用的資訊並手動構建 JSON
                try:
                    # 提取模型名稱
                    model_names = []
                    for item in context_list_of_dicts:
                        model_name = item.get('modelname', 'Unknown')
                        if model_name not in model_names:
                            model_names.append(model_name)
                    
                    # 構建基本的比較表格
                    comparison_table = []
                    if len(model_names) >= 2:
                        # 添加一些基本特徵的比較
                        features_to_compare = ['cpu', 'memory', 'storage', 'battery']
                        for feature in features_to_compare:
                            row = {"feature": feature}
                            for model_name in model_names:
                                # 找到對應模型的資料
                                for item in context_list_of_dicts:
                                    if item.get('modelname') == model_name:
                                        row[model_name] = item.get(feature, 'N/A')
                                        break
                            comparison_table.append(row)
                    
                    # 構建摘要
                    summary = f"根據提供的資料，比較了 {len(model_names)} 個筆電型號的規格。"
                    
                    fallback_json = {
                        "answer_summary": summary,
                        "comparison_table": comparison_table
                    }
                    
                    logging.info(f"使用備用 JSON: {fallback_json}")
                    yield f"data: {json.dumps(fallback_json, ensure_ascii=False)}\n\n"
                    
                except Exception as fallback_err:
                    logging.error(f"備用 JSON 構建也失敗: {fallback_err}")
                    error_obj = {
                        "answer_summary": "抱歉，AI 回應的格式不正確，無法解析。",
                        "comparison_table": []
                    }
                    yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"

        except Exception as e:
            logging.error(f"在 chat_stream 中發生未預期的錯誤: {e}", exc_info=True)
            error_obj = {"error": f"服務內部發生錯誤: {e}"}
            yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"

    def _convert_llm_response_to_required_format(self, parsed_json, context_list_of_dicts, query):
        """
        將 LLM 的不同 JSON 格式轉換為我們需要的標準格式
        """
        try:
            # 提取模型名稱
            model_names = []
            for item in context_list_of_dicts:
                model_name = item.get('modelname', 'Unknown')
                if model_name not in model_names:
                    model_names.append(model_name)
            
            # 嘗試從 LLM 回應中提取摘要
            answer_summary = ""
            comparison_table = []
            
            # 檢查是否有常見的 LLM 回應格式
            if "more_suitable_for_gaming" in parsed_json:
                # 處理遊戲性能比較格式
                gaming_data = parsed_json["more_suitable_for_gaming"]
                if "model" in gaming_data and "reasons" in gaming_data:
                    model = gaming_data["model"]
                    reasons = gaming_data["reasons"]
                    answer_summary = f"根據分析，{model} 型號更適合遊戲需求。"
                    
                    # 構建比較表格
                    for reason in reasons:
                        if "CPU" in reason:
                            comparison_table.append({
                                "feature": "CPU 性能",
                                **{name: self._extract_cpu_info(name, context_list_of_dicts) for name in model_names}
                            })
                        elif "GPU" in reason:
                            comparison_table.append({
                                "feature": "GPU 性能", 
                                **{name: self._extract_gpu_info(name, context_list_of_dicts) for name in model_names}
                            })
                        elif "TDP" in reason or "Thermal" in reason:
                            comparison_table.append({
                                "feature": "散熱設計",
                                **{name: self._extract_thermal_info(name, context_list_of_dicts) for name in model_names}
                            })
            
            elif "summary" in parsed_json:
                # 處理有摘要的格式
                answer_summary = parsed_json["summary"]
                if "comparison" in parsed_json:
                    comparison_table = parsed_json["comparison"]
            
            elif "analysis" in parsed_json:
                # 處理分析格式
                answer_summary = parsed_json["analysis"]
                if "features" in parsed_json:
                    comparison_table = parsed_json["features"]
            
            else:
                # 如果無法識別格式，使用預設處理
                answer_summary = f"根據提供的資料，比較了 {len(model_names)} 個筆電型號的規格。"
                
                # 構建基本的比較表格
                features_to_compare = ['cpu', 'memory', 'storage', 'battery']
                for feature in features_to_compare:
                    row = {"feature": feature}
                    for model_name in model_names:
                        for item in context_list_of_dicts:
                            if item.get('modelname') == model_name:
                                row[model_name] = item.get(feature, 'N/A')
                                break
                    comparison_table.append(row)
            
            # 如果沒有摘要，生成一個
            if not answer_summary:
                answer_summary = f"根據查詢 '{query}'，比較了 {len(model_names)} 個筆電型號的相關規格。"
            
            return {
                "answer_summary": answer_summary,
                "comparison_table": comparison_table
            }
            
        except Exception as e:
            logging.error(f"轉換 LLM 回應格式失敗: {e}")
            return None
    
    def _extract_cpu_info(self, model_name, context_list_of_dicts):
        """提取 CPU 資訊"""
        for item in context_list_of_dicts:
            if item.get('modelname') == model_name:
                return item.get('cpu', 'N/A')
        return 'N/A'
    
    def _extract_gpu_info(self, model_name, context_list_of_dicts):
        """提取 GPU 資訊"""
        for item in context_list_of_dicts:
            if item.get('modelname') == model_name:
                return item.get('gpu', 'N/A')
        return 'N/A'
    
    def _extract_thermal_info(self, model_name, context_list_of_dicts):
        """提取散熱資訊"""
        for item in context_list_of_dicts:
            if item.get('modelname') == model_name:
                return item.get('thermal', 'N/A')
        return 'N/A'