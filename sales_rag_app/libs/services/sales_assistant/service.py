import json
import pandas as pd
from prettytable import PrettyTable
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
        self.duckdb_query = DuckDBQuery(db_file="sales_rag_app/db/sales_specs.db")
        self.prompt_template = self._load_prompt_template("sales_rag_app/libs/services/sales_assistant/prompts/sales_prompt4.txt")
        
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

    def _create_beautiful_markdown_table(self, comparison_table: list | dict, model_names: list) -> str:
        """
        支援 dict of lists 且自動轉置為「型號為欄，規格為列」的 markdown 表格
        """
        try:
            # 如果是 dict of lists 格式，且有 "Model" 或 "Device Model" 欄位，則自動轉置
            if isinstance(comparison_table, dict):
                # 檢查是否有模型欄位
                model_key = None
                for key in comparison_table.keys():
                    if key.lower() in ["model", "device model", "modelname", "model_type"]:
                        model_key = key
                        break
                
                if model_key:
                    models = comparison_table[model_key]
                    spec_keys = [k for k in comparison_table.keys() if k != model_key]
                    # 產生 list of dicts 格式
                    new_table = []
                    for spec in spec_keys:
                        row = {"feature": spec}
                        for idx, model in enumerate(models):
                            value = comparison_table[spec][idx] if idx < len(comparison_table[spec]) else "N/A"
                            row[model] = value
                        new_table.append(row)
                    comparison_table = new_table
                    model_names = models
                else:
                    # 如果沒有明確的模型欄位，嘗試從其他欄位推斷
                    # 假設第一個欄位是模型名稱
                    first_key = list(comparison_table.keys())[0]
                    if isinstance(comparison_table[first_key], list):
                        models = comparison_table[first_key]
                        spec_keys = [k for k in comparison_table.keys() if k != first_key]
                        new_table = []
                        for spec in spec_keys:
                            row = {"feature": spec}
                            for idx, model in enumerate(models):
                                value = comparison_table[spec][idx] if idx < len(comparison_table[spec]) else "N/A"
                                row[model] = value
                            new_table.append(row)
                        comparison_table = new_table
                        model_names = models
                    else:
                        # 處理簡單的字典格式：{"特征": "对比", "AG958": "v1.0", "APX958": "v2.0"}
                        logging.info("檢測到簡單字典格式，轉換為 list of dicts")
                        keys = list(comparison_table.keys())
                        if len(keys) >= 2:
                            # 第一個鍵通常是特徵名稱，其他鍵是模型名稱
                            feature_key = keys[0]
                            model_keys = keys[1:]
                            
                            # 創建單行表格
                            row = {"feature": comparison_table[feature_key]}
                            for model_key in model_keys:
                                row[model_key] = comparison_table[model_key]
                            
                            comparison_table = [row]
                            model_names = model_keys

            # 確保 comparison_table 是 list of dicts 格式
            if not isinstance(comparison_table, list):
                logging.error(f"comparison_table 格式不正確: {type(comparison_table)}")
                return "表格格式錯誤"

            # 產生 markdown 表格
            header = "| **規格項目** |" + "".join([f" **{name}** |" for name in model_names])
            separator = "| --- |" + " --- |" * len(model_names)
            rows = []
            for row in comparison_table:
                if not isinstance(row, dict):
                    logging.error(f"表格行格式不正確: {type(row)}")
                    continue
                    
                feature = row.get("feature", "N/A")
                row_str = f"| **{feature}** |"
                for model_name in model_names:
                    value = row.get(model_name, "N/A")
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."
                    row_str += f" {value_str} |"
                rows.append(row_str)
            table_lines = [header, separator] + rows
            return "\n".join(table_lines)
        except Exception as e:
            logging.error(f"創建美化表格失敗: {e}", exc_info=True)
            return "表格生成失敗"

    def _create_simple_markdown_table(self, comparison_table: list, model_names: list) -> str:
        """
        創建簡單的 markdown 表格作為備用
        """
        try:
            # 創建標題行
            header = "| **規格項目** |"
            separator = "| --- |"
            
            for name in model_names:
                header += f" **{name}** |"
                separator += " --- |"
            
            # 創建數據行
            rows = []
            for row in comparison_table:
                feature = row.get("feature", "N/A")
                row_str = f"| {feature} |"
                for model_name in model_names:
                    value = row.get(model_name, "N/A")
                    row_str += f" {value} |"
                rows.append(row_str)
            
            # 組合表格
            table_lines = [header, separator] + rows
            return "\n".join(table_lines)
            
        except Exception as e:
            logging.error(f"創建簡單表格也失敗: {e}")
            return "表格生成失敗"

    def _format_response_with_beautiful_table(self, answer_summary: str | dict, comparison_table: list, model_names: list) -> dict:
        """
        格式化回應，包含美化的 markdown 表格
        """
        logging.info(f"_format_response_with_beautiful_table 被調用")
        logging.info(f"answer_summary 類型: {type(answer_summary)}, 值: {answer_summary}")
        logging.info(f"comparison_table 類型: {type(comparison_table)}, 值: {comparison_table}")
        logging.info(f"model_names: {model_names}")
        
        try:
            # 如果 answer_summary 是字典，保持其字典格式
            if isinstance(answer_summary, dict):
                logging.info("answer_summary 是字典格式，保持字典格式")
                # 創建美化的 markdown 表格
                beautiful_table = self._create_beautiful_markdown_table(comparison_table, model_names)
                
                # 檢查表格是否創建成功
                if beautiful_table == "表格格式錯誤" or beautiful_table == "表格生成失敗":
                    # 如果美化表格失敗，嘗試創建簡單表格
                    logging.warning("美化表格創建失敗，嘗試簡單表格")
                    simple_table = self._create_simple_markdown_table(comparison_table, model_names)
                    
                    result = {
                        "answer_summary": answer_summary,  # 保持字典格式
                        "comparison_table": comparison_table,
                        "beautiful_table": simple_table
                    }
                    logging.info(f"美化表格失敗，使用簡單表格，返回結果: {result}")
                    return result
                
                result = {
                    "answer_summary": answer_summary,  # 保持字典格式
                    "comparison_table": comparison_table,
                    "beautiful_table": beautiful_table
                }
                logging.info(f"字典格式處理成功，返回結果: {result}")
                return result
            
            # 如果 comparison_table 是字典格式，先轉換為 list of dicts 格式
            if isinstance(comparison_table, dict):
                logging.info("檢測到字典格式的 comparison_table，正在轉換為 list of dicts 格式")
                converted_table = self._convert_dict_to_list_of_dicts(comparison_table, answer_summary)
                if converted_table:
                    # 創建美化的 markdown 表格
                    beautiful_table = self._create_beautiful_markdown_table(converted_table, model_names)
                    
                    # 組合完整的回應
                    formatted_response = f"{answer_summary}\n\n**詳細規格比較表：**\n\n{beautiful_table}"
                    result = {
                        "answer_summary": formatted_response,
                        "comparison_table": converted_table,  # 返回轉換後的表格
                        "beautiful_table": beautiful_table
                    }
                    logging.info(f"字典格式轉換成功，返回結果: {result}")
                    return result
                else:
                    # 如果轉換失敗，使用改進的字典表格創建方法
                    beautiful_table = self._create_simple_table_from_dict_improved(comparison_table, answer_summary)
                    
                    # 組合完整的回應
                    formatted_response = f"{answer_summary}\n\n**詳細規格比較表：**\n\n{beautiful_table}"
                    result = {
                        "answer_summary": formatted_response,
                        "comparison_table": comparison_table,  # 保持原始格式
                        "beautiful_table": beautiful_table
                    }
                    logging.info(f"字典格式轉換失敗，使用備用方法，返回結果: {result}")
                    return result
            
            # 創建美化的 markdown 表格
            beautiful_table = self._create_beautiful_markdown_table(comparison_table, model_names)
            
            # 檢查表格是否創建成功
            if beautiful_table == "表格格式錯誤" or beautiful_table == "表格生成失敗":
                # 如果美化表格失敗，嘗試創建簡單表格
                logging.warning("美化表格創建失敗，嘗試簡單表格")
                simple_table = self._create_simple_markdown_table(comparison_table, model_names)
                
                # 組合完整的回應
                formatted_response = f"{answer_summary}\n\n**詳細規格比較表：**\n\n{simple_table}"
                
                result = {
                    "answer_summary": formatted_response,
                    "comparison_table": comparison_table,
                    "beautiful_table": simple_table
                }
                logging.info(f"美化表格失敗，使用簡單表格，返回結果: {result}")
                return result
            
            # 組合完整的回應
            formatted_response = f"{answer_summary}\n\n**詳細規格比較表：**\n\n{beautiful_table}"
            
            result = {
                "answer_summary": formatted_response,
                "comparison_table": comparison_table,
                "beautiful_table": beautiful_table
            }
            logging.info(f"標準處理成功，返回結果: {result}")
            return result
            
        except Exception as e:
            logging.error(f"格式化回應失敗: {e}", exc_info=True)
            # 返回基本的錯誤回應
            result = {
                "answer_summary": f"{answer_summary}\n\n表格生成失敗，請稍後再試。",
                "comparison_table": comparison_table,
                "beautiful_table": "表格生成失敗"
            }
            logging.info(f"發生異常，返回錯誤結果: {result}")
            return result

    def _convert_dict_to_list_of_dicts(self, comparison_dict: dict, answer_summary=None) -> list:
        """
        將字典格式的比較表格轉換為 list of dicts 格式
        """
        try:
            if not comparison_dict:
                logging.warning("comparison_dict 為空")
                return []
            
            logging.info(f"開始轉換字典格式，輸入數據: {comparison_dict}")
            
            # 檢查是否包含 main_differences 結構
            if answer_summary and isinstance(answer_summary, dict) and 'main_differences' in answer_summary:
                logging.info("檢測到 main_differences 結構")
                # 使用 main_differences 中的 category 作為 feature names
                main_differences = answer_summary['main_differences']
                converted_table = []
                
                for diff in main_differences:
                    if isinstance(diff, dict):
                        category = diff.get('category', '未知項目')
                        row = {"feature": category}
                        
                        # 從 comparison_dict 中提取對應的值
                        for model_name in comparison_dict.keys():
                            if model_name != "Feature":  # 跳過 Feature 欄位
                                # 找到對應的索引
                                if "Feature" in comparison_dict:
                                    try:
                                        feature_index = comparison_dict["Feature"].index(category)
                                        if model_name in comparison_dict and feature_index < len(comparison_dict[model_name]):
                                            row[model_name] = comparison_dict[model_name][feature_index]
                                        else:
                                            row[model_name] = "N/A"
                                    except ValueError:
                                        row[model_name] = "N/A"
                                else:
                                    row[model_name] = "N/A"
                        
                        converted_table.append(row)
                
                logging.info(f"main_differences 轉換結果: {converted_table}")
                return converted_table
            
            # 處理標準字典格式：第一個鍵包含特徵名稱，其他鍵是模型名稱
            keys = list(comparison_dict.keys())
            logging.info(f"字典鍵: {keys}")
            
            if len(keys) >= 2:
                # 檢查第一個鍵是否包含特徵名稱列表
                first_key = keys[0]
                logging.info(f"第一個鍵: {first_key}, 值類型: {type(comparison_dict[first_key])}")
                
                if isinstance(comparison_dict[first_key], list):
                    features = comparison_dict[first_key]
                    model_names = keys[1:]  # 其他鍵都是模型名稱
                    
                    logging.info(f"特徵列表: {features}")
                    logging.info(f"模型名稱: {model_names}")
                    
                    converted_table = []
                    for i, feature in enumerate(features):
                        row = {"feature": feature}
                        for model_name in model_names:
                            if i < len(comparison_dict[model_name]):
                                row[model_name] = comparison_dict[model_name][i]
                            else:
                                row[model_name] = "N/A"
                        converted_table.append(row)
                    
                    logging.info(f"標準字典格式轉換結果: {converted_table}")
                    return converted_table
            
            # 處理嵌套結構：主要差异 -> [{'型号': 'AG958', '特性': '16.1英寸', ...}, ...]
            for main_key, main_value in comparison_dict.items():
                if isinstance(main_value, list) and len(main_value) > 0:
                    # 檢查是否為模型規格列表
                    if isinstance(main_value[0], dict):
                        logging.info("檢測到嵌套結構")
                        # 提取所有可能的規格項目
                        all_specs = set()
                        for model_spec in main_value:
                            if isinstance(model_spec, dict):
                                all_specs.update(model_spec.keys())
                        
                        # 排除模型名稱相關的欄位
                        model_name_keys = {'型号', 'model', 'modelname', 'device_model'}
                        spec_keys = [key for key in all_specs if key not in model_name_keys]
                        
                        converted_table = []
                        for spec_key in spec_keys:
                            row = {"feature": spec_key}
                            for model_spec in main_value:
                                if isinstance(model_spec, dict):
                                    # 嘗試找到模型名稱
                                    model_name = None
                                    for name_key in model_name_keys:
                                        if name_key in model_spec:
                                            model_name = model_spec[name_key]
                                            break
                                    
                                    if not model_name:
                                        # 如果沒有找到模型名稱，使用索引
                                        model_name = f"Model_{main_value.index(model_spec) + 1}"
                                    
                                    # 獲取規格值
                                    value = model_spec.get(spec_key, "N/A")
                                    row[model_name] = value
                            
                            converted_table.append(row)
                        
                        logging.info(f"嵌套結構轉換結果: {converted_table}")
                        return converted_table
            
            # 標準處理：假設第一個欄位是 Feature，其他欄位是模型名稱
            if "Feature" in comparison_dict:
                logging.info("檢測到 Feature 欄位")
                features = comparison_dict["Feature"]
                model_names = [k for k in comparison_dict.keys() if k != "Feature"]
                
                converted_table = []
                for i, feature in enumerate(features):
                    row = {"feature": feature}
                    for model_name in model_names:
                        if i < len(comparison_dict[model_name]):
                            row[model_name] = comparison_dict[model_name][i]
                        else:
                            row[model_name] = "N/A"
                    converted_table.append(row)
                
                logging.info(f"Feature 欄位轉換結果: {converted_table}")
                return converted_table
            
            logging.warning("無法識別字典格式，返回空列表")
            return []
            
        except Exception as e:
            logging.error(f"轉換字典格式失敗: {e}")
            return []

    def _create_simple_table_from_dict(self, comparison_dict: dict) -> str:
        """
        從字典格式創建簡單的 markdown 表格
        """
        try:
            if not comparison_dict:
                return "無比較數據"
            
            # 找到模型名稱欄位
            model_key = None
            for key in comparison_dict.keys():
                if key.lower() in ["model", "device model", "modelname", "model_type"]:
                    model_key = key
                    break
            
            if not model_key:
                # 如果沒有找到模型欄位，使用第一個欄位
                model_key = list(comparison_dict.keys())[0]
            
            models = comparison_dict[model_key]
            spec_keys = [k for k in comparison_dict.keys() if k != model_key]
            
            if not models or not spec_keys:
                return "數據格式不完整"
            
            # 創建表格 - 使用模型名稱作為列標題
            header = "| **規格項目** |" + "".join([f" **{model}** |" for model in models])
            separator = "| --- |" + " --- |" * len(models)
            
            rows = []
            for spec in spec_keys:
                row_str = f"| **{spec}** |"
                for idx, model in enumerate(models):
                    value = comparison_dict[spec][idx] if idx < len(comparison_dict[spec]) else "N/A"
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."
                    row_str += f" {value_str} |"
                rows.append(row_str)
            
            table_lines = [header, separator] + rows
            return "\n".join(table_lines)
            
        except Exception as e:
            logging.error(f"創建簡單表格失敗: {e}")
            return "表格生成失敗"

    def _create_simple_table_from_dict_improved(self, comparison_dict: dict, answer_summary=None) -> str:
        """
        改進的字典格式表格創建，更好地處理複雜的數據結構，支持 feature name 作為 row header
        """
        try:
            if not comparison_dict:
                return "無比較數據"

            # 檢查是否包含 main_differences 結構
            feature_names = None
            if answer_summary and isinstance(answer_summary, dict) and 'main_differences' in answer_summary:
                feature_names = [d.get('category', f'規格{i+1}') for i, d in enumerate(answer_summary['main_differences'])]

            # 標準處理
            model_names = list(comparison_dict.keys())
            # If feature_names is not found, fallback to generic
            if not feature_names:
                # Use the length of the first value as feature count
                feature_count = len(next(iter(comparison_dict.values())))
                feature_names = [f'規格 {i+1}' for i in range(feature_count)]

            # Create table header
            header = "| **規格項目** |" + "".join([f" **{model}** |" for model in model_names])
            separator = "| --- |" + " --- |" * len(model_names)
            rows = []
            for idx, feature in enumerate(feature_names):
                row_str = f"| **{feature}** |"
                for model in model_names:
                    value = comparison_dict[model][idx] if idx < len(comparison_dict[model]) else "N/A"
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."
                    row_str += f" {value_str} |"
                rows.append(row_str)
            table_lines = [header, separator] + rows
            return "\n".join(table_lines)
        except Exception as e:
            logging.error(f"創建改進表格失敗: {e}")
            return "表格生成失敗"

    def _create_table_from_main_differences(self, comparison_dict: dict) -> str:
        """
        從 main_differences 結構創建表格
        """
        try:
            # 提取 main_differences 數據
            if isinstance(comparison_dict, str):
                # 如果是字符串，嘗試解析
                import ast
                try:
                    comparison_dict = ast.literal_eval(comparison_dict)
                except:
                    return "無法解析數據格式"
            
            main_differences = comparison_dict.get('main_differences', [])
            if not main_differences:
                return "無主要差異數據"
            
            # 創建表格
            header = "| **比較項目** | **AG958** | **APX958** |"
            separator = "| --- | --- | --- |"
            
            rows = []
            for diff in main_differences:
                if isinstance(diff, dict):
                    category = diff.get('category', '未知項目')
                    ag958_value = diff.get('ag958', 'N/A')
                    apx958_value = diff.get('apx958', 'N/A')
                    
                    # 格式化值
                    ag958_str = str(ag958_value)[:50] + "..." if len(str(ag958_value)) > 50 else str(ag958_value)
                    apx958_str = str(apx958_value)[:50] + "..." if len(str(apx958_value)) > 50 else str(apx958_value)
                    
                    row_str = f"| **{category}** | {ag958_str} | {apx958_str} |"
                    rows.append(row_str)
            
            table_lines = [header, separator] + rows
            return "\n".join(table_lines)
            
        except Exception as e:
            logging.error(f"從 main_differences 創建表格失敗: {e}")
            return "表格生成失敗"

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
                        # 提取模型名稱用於美化表格
                        model_names = []
                        for item in context_list_of_dicts:
                            model_name = item.get('modelname', 'Unknown')
                            if model_name not in model_names:
                                model_names.append(model_name)
                        
                        # 使用美化表格格式化回應
                        formatted_response = self._format_response_with_beautiful_table(
                            parsed_json["answer_summary"],
                            parsed_json["comparison_table"],
                            model_names
                        )
                        yield f"data: {json.dumps(formatted_response, ensure_ascii=False)}\n\n"
                    else:
                        # 嘗試將 LLM 的 JSON 轉換為我們需要的格式
                        logging.info("LLM 輸出的 JSON 格式不符合要求，嘗試轉換...")
                        converted_json = self._convert_llm_response_to_required_format(parsed_json, context_list_of_dicts, query)
                        if converted_json:
                            # 提取模型名稱用於美化表格
                            model_names = []
                            for item in context_list_of_dicts:
                                model_name = item.get('modelname', 'Unknown')
                                if model_name not in model_names:
                                    model_names.append(model_name)
                            
                            # 使用美化表格格式化回應
                            formatted_response = self._format_response_with_beautiful_table(
                                converted_json["answer_summary"],
                                converted_json["comparison_table"],
                                model_names
                            )
                            yield f"data: {json.dumps(formatted_response, ensure_ascii=False)}\n\n"
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
                            # 提取模型名稱用於美化表格
                            model_names = []
                            for item in context_list_of_dicts:
                                model_name = item.get('modelname', 'Unknown')
                                if model_name not in model_names:
                                    model_names.append(model_name)
                            
                            # 使用美化表格格式化回應
                            formatted_response = self._format_response_with_beautiful_table(
                                parsed_json["answer_summary"],
                                parsed_json["comparison_table"],
                                model_names
                            )
                            yield f"data: {json.dumps(formatted_response, ensure_ascii=False)}\n\n"
                        else:
                            # 嘗試轉換格式
                            converted_json = self._convert_llm_response_to_required_format(parsed_json, context_list_of_dicts, query)
                            if converted_json:
                                # 提取模型名稱用於美化表格
                                model_names = []
                                for item in context_list_of_dicts:
                                    model_name = item.get('modelname', 'Unknown')
                                    if model_name not in model_names:
                                        model_names.append(model_name)
                                
                                # 使用美化表格格式化回應
                                formatted_response = self._format_response_with_beautiful_table(
                                    converted_json["answer_summary"],
                                    converted_json["comparison_table"],
                                    model_names
                                )
                                yield f"data: {json.dumps(formatted_response, ensure_ascii=False)}\n\n"
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
                    
                    # 使用美化表格格式化回應
                    formatted_response = self._format_response_with_beautiful_table(
                        summary,
                        comparison_table,
                        model_names
                    )
                    
                    logging.info(f"使用備用 JSON: {formatted_response}")
                    yield f"data: {json.dumps(formatted_response, ensure_ascii=False)}\n\n"
                    
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