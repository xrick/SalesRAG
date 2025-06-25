import json
import pandas as pd
from prettytable import PrettyTable
from ..base_service import BaseService
from ...RAG.DB.MilvusQuery import MilvusQuery
from ...RAG.DB.DuckDBQuery import DuckDBQuery
from ...RAG.LLM.LLMInitializer import LLMInitializer
import logging
import re

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
                    
                    # 不將表格添加到 answer_summary 中，讓前端處理
                    result = {
                        "answer_summary": answer_summary,  # 保持原始格式
                        "comparison_table": converted_table,  # 返回轉換後的表格
                        "beautiful_table": beautiful_table
                    }
                    logging.info(f"字典格式轉換成功，返回結果: {result}")
                    return result
                else:
                    # 如果轉換失敗，使用改進的字典表格創建方法
                    beautiful_table = self._create_simple_table_from_dict_improved(comparison_table, answer_summary)
                    
                    # 不將表格添加到 answer_summary 中，讓前端處理
                    result = {
                        "answer_summary": answer_summary,  # 保持原始格式
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
                
                # 不將表格添加到 answer_summary 中，讓前端處理
                result = {
                    "answer_summary": answer_summary,  # 保持原始格式
                    "comparison_table": comparison_table,
                    "beautiful_table": simple_table
                }
                logging.info(f"美化表格失敗，使用簡單表格，返回結果: {result}")
                return result
            
            # 不將表格添加到 answer_summary 中，讓前端處理
            result = {
                "answer_summary": answer_summary,  # 保持原始格式
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
                        
                        # 特殊處理：如果第一個字典包含 "Model" 和 "Specification" 鍵
                        if "Model" in main_value[0] and "Specification" in main_value[0]:
                            logging.info("檢測到 Model/Specification 格式")
                            converted_table = []
                            for item in main_value:
                                if isinstance(item, dict) and "Model" in item and "Specification" in item:
                                    # 創建一行顯示規格
                                    spec_row = {"feature": "Memory Specification", item["Model"]: item["Specification"]}
                                    converted_table.append(spec_row)
                            logging.info(f"Model/Specification 格式轉換結果: {converted_table}")
                            return converted_table
                        
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
        
        # 改进：使用更严格的匹配逻辑
        for modelname in AVAILABLE_MODELNAMES:
            modelname_lower = modelname.lower()
            # 使用单词边界匹配，避免部分匹配
            if re.search(r'\b' + re.escape(modelname_lower) + r'\b', query_lower):
                found_modelnames.append(modelname)
        
        # 如果没有找到完全匹配，检查是否有相似的模型名称
        if not found_modelnames:
            # 提取查询中可能的模型名称模式
            potential_models = re.findall(r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?::\s*[A-Z]+\d+)?', query)
            logging.info(f"查询中发现的潜在模型名称: {potential_models}")
            
            # 检查这些潜在模型是否在可用列表中
            for potential_model in potential_models:
                if potential_model in AVAILABLE_MODELNAMES:
                    found_modelnames.append(potential_model)
        
        logging.info(f"查询验证结果 - 查询: '{query}', 找到的模型名称: {found_modelnames}")
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
            
            # 如果同時包含modeltype和modelname，優先使用modelname
            if contains_modeltype and contains_modelname:
                logging.info(f"查詢同時包含modeltype和modelname，優先使用modelname")
                logging.info(f"找到的modeltype: {found_modeltypes}")
                logging.info(f"找到的modelname: {found_modelnames}")
                
                # 優先使用明確指定的modelname
                target_modelnames = found_modelnames
                logging.info(f"使用明確指定的modelname: {target_modelnames}")
                
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
                # 如果既没有modeltype也没有modelname
                available_types_str = "\n".join([f"- {modeltype}" for modeltype in AVAILABLE_MODELTYPES])
                available_models_str = "\n".join([f"- {model}" for model in AVAILABLE_MODELNAMES])
                
                # 检查查询中是否包含可能的错误模型名称
                potential_models = re.findall(r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?::\s*[A-Z]+\d+)?', query)
                error_message = f"您的查询中提到的模型名称不在我们的数据库中。"
                
                if potential_models:
                    error_message += f"\n\n您提到的模型名称: {', '.join(potential_models)}"
                    error_message += f"\n\n可能的正确模型名称:"
                    # 为每个可能的错误模型提供建议
                    for potential_model in potential_models:
                        suggestions = []
                        for available_model in AVAILABLE_MODELNAMES:
                            # 简单的相似度检查
                            if potential_model[:3] in available_model or potential_model[-3:] in available_model:
                                suggestions.append(available_model)
                        if suggestions:
                            error_message += f"\n- '{potential_model}' 可能是: {', '.join(suggestions[:3])}"
                
                error_message += f"\n\n可用的系列包括：\n{available_types_str}"
                error_message += f"\n\n可用的型號包括：\n{available_models_str}"
                error_message += f"\n\n請重新提問，例如：'比較 958 系列的 CPU 性能' 或 '比較 AB819-S: FP6 和 AG958 的 CPU 性能'"
                
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
                # 提供更详细的错误信息
                error_message = f"抱歉，在我们的数据库中未找到以下型号的资料：{', '.join(target_modelnames)}"
                error_message += f"\n\n请检查型号名称是否正确，或查看可用的型号列表。"
                yield f"data: {json.dumps({'answer_summary': error_message, 'comparison_table': []}, ensure_ascii=False)}\n\n"
                return

            logging.info(f"成功查询到 {len(full_specs_records)} 条记录")
            # 记录查询到的实际模型名称
            found_modelnames = [record[self.spec_fields.index('modelname')] for record in full_specs_records]
            logging.info(f"查询到的实际模型名称: {found_modelnames}")

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
                        # 提取模型名稱用於美化表格和 post-process
                        model_names = []
                        for item in context_list_of_dicts:
                            model_name = item.get('modelname', 'Unknown')
                            if model_name not in model_names:
                                model_names.append(model_name)
                        
                        # ★ 使用兩步驟策略：分離驗證answer_summary和comparison_table
                        logging.info("開始使用兩步驟策略處理LLM回應")
                        processed_response = self._process_llm_response_robust(parsed_json, context_list_of_dicts, target_modelnames, query)
                        
                        logging.info(f"兩步驟策略處理完成 - answer_summary: {processed_response.get('answer_summary', '')}")
                        logging.info(f"兩步驟策略處理完成 - comparison_table: {processed_response.get('comparison_table', '')}")
                        yield f"data: {json.dumps(processed_response, ensure_ascii=False)}\n\n"
                        return
                    else:
                        logging.error("LLM回應格式不正確，缺少必要欄位")
                        fallback_response = self._generate_fallback_response(query, context_list_of_dicts, target_modelnames)
                        yield f"data: {json.dumps(fallback_response, ensure_ascii=False)}\n\n"
                        return
                else:
                    logging.error("無法從LLM回應中提取JSON")
                    fallback_response = self._generate_fallback_response(query, context_list_of_dicts, target_modelnames)
                    yield f"data: {json.dumps(fallback_response, ensure_ascii=False)}\n\n"
                    return
                    
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析失敗: {e}")
                fallback_response = self._generate_fallback_response(query, context_list_of_dicts, target_modelnames)
                yield f"data: {json.dumps(fallback_response, ensure_ascii=False)}\n\n"
                return
            except Exception as e:
                logging.error(f"處理LLM回應時發生錯誤: {e}")
                fallback_response = self._generate_fallback_response(query, context_list_of_dicts, target_modelnames)
                yield f"data: {json.dumps(fallback_response, ensure_ascii=False)}\n\n"
                return
                
        except Exception as e:
            logging.error(f"chat_stream 發生錯誤: {e}", exc_info=True)
            error_obj = {
                "answer_summary": f"處理您的查詢時發生錯誤: {str(e)}",
                "comparison_table": []
            }
            yield f"data: {json.dumps(error_obj, ensure_ascii=False)}\n\n"

    def _validate_llm_response(self, parsed_json, target_modelnames):
        """
        驗證LLM回答是否包含正確的模型名稱
        """
        try:
            logging.info(f"開始驗證LLM回答，目標模型名稱: {target_modelnames}")
            
            # 定義無效的品牌和GPU型號列表
            invalid_brands = ["Acer", "ASUS", "Lenovo", "Dell", "MSI", "Razer", "NVIDIA", "Nvidia"]
            invalid_gpu_models = ["RTX", "GTX", "RTX 3060", "RTX 3070", "RTX 3080", "RTX 3090", "RTX 4060", "RTX 4070", "RTX 4080", "RTX 4090", "GTX 1650", "GTX 1660"]
            
            # 創建模型名稱的變體列表（處理冒號等格式差異）
            def get_model_variants(model_name):
                variants = [model_name]
                # 添加沒有冒號的版本
                if ":" in model_name:
                    variants.append(model_name.replace(":", ""))
                # 添加有冒號的版本
                else:
                    # 嘗試添加冒號
                    parts = model_name.split()
                    if len(parts) >= 2:
                        variants.append(f"{parts[0]}: {' '.join(parts[1:])}")
                return variants
            
            target_model_variants = []
            for model_name in target_modelnames:
                target_model_variants.extend(get_model_variants(model_name))
            
            logging.info(f"目標模型名稱變體: {target_model_variants}")
            
            # 檢查answer_summary中是否包含正確的模型名稱
            answer_summary = parsed_json.get("answer_summary", "")
            logging.info(f"檢查answer_summary: {answer_summary}")
            
            if answer_summary:
                # 首先檢查是否包含任何目標模型名稱或其變體
                has_valid_model = False
                for model_variant in target_model_variants:
                    if model_variant in answer_summary:
                        has_valid_model = True
                        logging.info(f"找到有效模型名稱變體: {model_variant}")
                        break
                
                # 如果没有找到有效模型名称，检查是否有其他可能的模型名称
                if not has_valid_model:
                    # 根据目标模型名称是否包含特殊符号来选择正则表达式
                    potential_models = []
                    
                    for target_model in target_modelnames:
                        if ":" in target_model:
                            # 如果目标模型包含冒号，使用匹配冒号格式的正则表达式
                            pattern = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s*:\s*[A-Z]+\d+[A-Z]*)'
                            matches = re.findall(pattern, answer_summary)
                            potential_models.extend(matches)
                            
                            # 也匹配没有冒号的版本 - 修复正则表达式以匹配完整的模型名称
                            pattern_no_colon = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s+[A-Z]+\d+[A-Z]*\d*)'
                            matches_no_colon = re.findall(pattern_no_colon, answer_summary)
                            potential_models.extend(matches_no_colon)
                        else:
                            # 如果目标模型不包含冒号，使用简单格式的正则表达式
                            pattern = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?'
                            matches = re.findall(pattern, answer_summary)
                            potential_models.extend(matches)
                    
                    # 去重
                    potential_models = list(set(potential_models))
                    logging.info(f"在answer_summary中找到的潜在模型名称: {potential_models}")
                    
                    for potential_model in potential_models:
                        # 检查是否是目标模型的变体
                        is_valid_variant = False
                        for model_variant in target_model_variants:
                            if potential_model == model_variant:
                                is_valid_variant = True
                                logging.info(f"找到有效模型名称变体: {potential_model} -> {model_variant}")
                                break
                        
                        if not is_valid_variant and potential_model not in AVAILABLE_MODELNAMES:
                            # 检查是否是已知的无效模型名称
                            known_invalid_models = ["M20W", "A520", "R7 5900HS", "Ryzen 7 958", "Ryzen 9 7640H"]
                            if potential_model not in known_invalid_models:
                                logging.warning(f"LLM回答包含不存在的模型名称: {potential_model}")
                                return False
                
                # 检查无效品牌 - 改进：避免将模型名称中的字母组合误认为品牌
                for brand in invalid_brands:
                    # 使用单词边界匹配，避免将模型名称中的字母组合误认为品牌
                    if re.search(r'\b' + re.escape(brand) + r'\b', answer_summary):
                        logging.warning(f"LLM回答包含无效品牌: {brand}")
                        return False
                
                # 检查无效GPU型号
                for gpu_model in invalid_gpu_models:
                    if gpu_model in answer_summary:
                        logging.warning(f"LLM回答包含无效GPU型号: {gpu_model}")
                        return False
                
                # 如果包含正确的模型名称，即使有其他内容也认为有效
                if has_valid_model:
                    logging.info("LLM回答包含正确的模型名称，验证通过")
                    return True
                else:
                    logging.warning("LLM回答中未找到任何目标模型名称")
                    return False
            
            # 检查comparison_table中的模型名称
            comparison_table = parsed_json.get("comparison_table", [])
            logging.info(f"检查comparison_table: {comparison_table}")
            
            if isinstance(comparison_table, list) and comparison_table:
                # 检查表格中的模型名称
                for row in comparison_table:
                    if isinstance(row, dict):
                        # 检查是否包含正确的模型名称作为键
                        for model_variant in target_model_variants:
                            if model_variant in row:
                                logging.info(f"在comparison_table中找到有效模型名称变体: {model_variant}")
                                return True
                        
                        # 检查是否包含错误的模型名称
                        for key in row.keys():
                            if key != "feature" and key not in target_model_variants:
                                # 检查是否包含常见错误模型名称
                                invalid_models = ["A520", "M20W", "R7 5900HS", "Ryzen 7 958", "Ryzen 9 7640H"]
                                for invalid_model in invalid_models:
                                    if invalid_model in key:
                                        logging.warning(f"LLM回答包含无效模型名称: {invalid_model}")
                                        return False
                        
                        # 检查值中是否包含无效GPU型号
                        for value in row.values():
                            if isinstance(value, str):
                                for gpu_model in invalid_gpu_models:
                                    if gpu_model in value:
                                        logging.warning(f"LLM回答包含无效GPU型号: {gpu_model}")
                                        return False
            
            # 如果comparison_table是字典格式
            elif isinstance(comparison_table, dict):
                # 检查字典中的模型名称
                for key in comparison_table.keys():
                    if key != "modelname" and key not in target_model_variants:
                        # 检查是否是模式匹配的无效模型名称
                        if re.match(r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s*:\s*[A-Z]+\d+)?', key):
                            if key not in AVAILABLE_MODELNAMES:
                                logging.warning(f"LLM回答包含不存在的模型名称: {key}")
                                return False
                
                # 检查是否包含正确的模型名称
                for model_variant in target_model_variants:
                    if model_variant in comparison_table:
                        logging.info(f"在comparison_table字典中找到有效模型名称变体: {model_variant}")
                        return True
            
            # 如果没有找到任何目标模型名称，认为无效
            logging.warning("LLM回答中未找到任何目标模型名称")
            return False
            
        except Exception as e:
            logging.error(f"驗證LLM回應時發生錯誤: {e}")
            return False

    def _validate_llm_response_separated(self, parsed_json, target_modelnames):
        """
        分离验证：answer_summary和comparison_table独立验证
        返回验证结果字典，包含每个部分的验证状态
        """
        try:
            logging.info(f"開始分離驗證LLM回答，目標模型名稱: {target_modelnames}")
            
            # 定义无效的品牌和GPU型号列表
            invalid_brands = ["Acer", "ASUS", "Lenovo", "Dell", "MSI", "Razer", "NVIDIA", "Nvidia"]
            invalid_gpu_models = ["RTX", "GTX", "RTX 3060", "RTX 3070", "RTX 3080", "RTX 3090", "RTX 4060", "RTX 4070", "RTX 4080", "RTX 4090", "GTX 1650", "GTX 1660"]
            
            # 创建模型名称的变体列表
            def get_model_variants(model_name):
                variants = [model_name]
                if ":" in model_name:
                    variants.append(model_name.replace(":", ""))
                else:
                    parts = model_name.split()
                    if len(parts) >= 2:
                        variants.append(f"{parts[0]}: {' '.join(parts[1:])}")
                return variants
            
            target_model_variants = []
            for model_name in target_modelnames:
                target_model_variants.extend(get_model_variants(model_name))
            
            logging.info(f"目標模型名稱變體: {target_model_variants}")
            
            # 步骤1：验证answer_summary
            summary_valid = False
            answer_summary = parsed_json.get("answer_summary", "")
            
            if answer_summary:
                logging.info(f"驗證answer_summary: {answer_summary}")
                
                # 检查是否包含正确的模型名称
                has_valid_model = False
                for model_variant in target_model_variants:
                    if model_variant in answer_summary:
                        has_valid_model = True
                        logging.info(f"在answer_summary中找到有效模型名稱變體: {model_variant}")
                        break
                
                # 如果没有找到直接匹配，使用正则表达式查找
                if not has_valid_model:
                    potential_models = []
                    for target_model in target_modelnames:
                        if ":" in target_model:
                            pattern = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s*:\s*[A-Z]+\d+[A-Z]*)'
                            matches = re.findall(pattern, answer_summary)
                            potential_models.extend(matches)
                            
                            pattern_no_colon = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s+[A-Z]+\d+[A-Z]*\d*)'
                            matches_no_colon = re.findall(pattern_no_colon, answer_summary)
                            potential_models.extend(matches_no_colon)
                        else:
                            pattern = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?'
                            matches = re.findall(pattern, answer_summary)
                            potential_models.extend(matches)
                    
                    potential_models = list(set(potential_models))
                    logging.info(f"在answer_summary中找到的潜在模型名称: {potential_models}")
                    
                    for potential_model in potential_models:
                        for model_variant in target_model_variants:
                            if potential_model == model_variant:
                                has_valid_model = True
                                logging.info(f"通過正則表達式找到有效模型名称变体: {potential_model}")
                                break
                        if has_valid_model:
                            break
                
                # 检查无效品牌（使用单词边界）
                has_invalid_brand = False
                for brand in invalid_brands:
                    if re.search(r'\b' + re.escape(brand) + r'\b', answer_summary):
                        logging.warning(f"answer_summary包含无效品牌: {brand}")
                        has_invalid_brand = True
                        break
                
                # 检查无效GPU型号
                has_invalid_gpu = False
                for gpu_model in invalid_gpu_models:
                    if gpu_model in answer_summary:
                        logging.warning(f"answer_summary包含无效GPU型号: {gpu_model}")
                        has_invalid_gpu = True
                        break
                
                # 如果包含正确的模型名称且没有无效内容，认为summary有效
                if has_valid_model and not has_invalid_brand and not has_invalid_gpu:
                    summary_valid = True
                    logging.info("answer_summary驗證通過")
                else:
                    logging.warning("answer_summary驗證失敗")
            
            # 步骤2：验证comparison_table
            table_valid = False
            comparison_table = parsed_json.get("comparison_table", [])
            
            if comparison_table:
                logging.info(f"驗證comparison_table: {comparison_table}")
                
                # 检查表格格式和内容
                if isinstance(comparison_table, list) and comparison_table:
                    # 检查是否包含正确的模型名称作为键
                    has_valid_model_in_table = False
                    has_invalid_content = False
                    
                    for row in comparison_table:
                        if isinstance(row, dict):
                            # 检查是否包含正确的模型名称
                            for model_variant in target_model_variants:
                                if model_variant in row:
                                    has_valid_model_in_table = True
                                    logging.info(f"在comparison_table中找到有效模型名称变体: {model_variant}")
                                    break
                            
                            # 检查是否包含错误的模型名称
                            for key in row.keys():
                                if key != "feature" and key not in target_model_variants:
                                    invalid_models = ["A520", "M20W", "R7 5900HS", "Ryzen 7 958", "Ryzen 9 7640H"]
                                    for invalid_model in invalid_models:
                                        if invalid_model in key:
                                            logging.warning(f"comparison_table包含无效模型名称: {invalid_model}")
                                            has_invalid_content = True
                                            break
                            
                            # 检查值中是否包含无效GPU型号
                            for value in row.values():
                                if isinstance(value, str):
                                    for gpu_model in invalid_gpu_models:
                                        if gpu_model in value:
                                            logging.warning(f"comparison_table包含无效GPU型号: {gpu_model}")
                                            has_invalid_content = True
                                            break
                    
                    if has_valid_model_in_table and not has_invalid_content:
                        table_valid = True
                        logging.info("comparison_table驗證通過")
                    else:
                        logging.warning("comparison_table驗證失敗")
                
                elif isinstance(comparison_table, dict):
                    # 字典格式的验证
                    has_valid_model_in_table = False
                    has_invalid_content = False
                    
                    for key in comparison_table.keys():
                        if key != "modelname" and key not in target_model_variants:
                            if re.match(r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s*:\s*[A-Z]+\d+)?', key):
                                if key not in AVAILABLE_MODELNAMES:
                                    logging.warning(f"comparison_table包含不存在的模型名称: {key}")
                                    has_invalid_content = True
                    
                    for model_variant in target_model_variants:
                        if model_variant in comparison_table:
                            has_valid_model_in_table = True
                            logging.info(f"在comparison_table字典中找到有效模型名称变体: {model_variant}")
                            break
                    
                    if has_valid_model_in_table and not has_invalid_content:
                        table_valid = True
                        logging.info("comparison_table字典格式驗證通過")
                    else:
                        logging.warning("comparison_table字典格式驗證失敗")
            
            # 返回分离验证结果
            validation_result = {
                "summary_valid": summary_valid,
                "table_valid": table_valid,
                "answer_summary": answer_summary if summary_valid else None,
                "comparison_table": comparison_table if table_valid else None
            }
            
            logging.info(f"分離驗證結果: summary_valid={summary_valid}, table_valid={table_valid}")
            return validation_result
            
        except Exception as e:
            logging.error(f"分離驗證LLM回應時發生錯誤: {e}")
            return {
                "summary_valid": False,
                "table_valid": False,
                "answer_summary": None,
                "comparison_table": None
            }

    def _generate_fallback_response(self, query, context_list_of_dicts, target_modelnames):
        """
        生成備用回應，基於實際數據創建比較表格
        """
        try:
            # 檢查是否有實際數據
            if not context_list_of_dicts:
                # 如果沒有數據，說明查詢的模型不存在
                potential_models = re.findall(r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?::\s*[A-Z]+\d+)?', query)
                if potential_models:
                    error_message = f"抱歉，您查詢的模型 '{', '.join(potential_models)}' 在我们的數據庫中不存在。"
                    error_message += f"\n\n可用的模型包括：\n"
                    for model in AVAILABLE_MODELNAMES:
                        error_message += f"- {model}\n"
                    error_message += f"\n請使用正確的模型名稱重新查詢。"
                    
                    return {
                        "answer_summary": error_message,
                        "comparison_table": []
                    }
                else:
                    return {
                        "answer_summary": "抱歉，無法找到相關的產品數據。請檢查您的查詢。",
                        "comparison_table": []
                    }
            
            # 根據查詢類型決定要比較的特徵
            if "遊戲" in query or "gaming" in query.lower():
                features = [
                    ("CPU Model", "cpu"),
                    ("GPU Model", "gpu"), 
                    ("Thermal Design", "thermal"),
                    ("Memory Type", "memory"),
                    ("Storage Type", "storage")
                ]
            elif "電池" in query or "續航" in query or "battery" in query.lower():
                features = [
                    ("Battery Capacity", "battery"),
                    ("Battery Life", "battery"),
                    ("Charging Speed", "battery")
                ]
            elif "輕便" in query or "重量" in query or "weight" in query.lower() or "portable" in query.lower():
                features = [
                    ("Weight", "structconfig"),
                    ("Dimensions", "structconfig"),
                    ("Form Factor", "structconfig"),
                    ("Material", "structconfig")
                ]
            elif "cpu" in query.lower() or "處理器" in query:
                features = [
                    ("CPU Model", "cpu"),
                    ("CPU Architecture", "cpu"),
                    ("CPU TDP", "cpu")
                ]
            elif "gpu" in query.lower() or "顯卡" in query:
                features = [
                    ("GPU Model", "gpu"),
                    ("GPU Memory", "gpu"),
                    ("GPU Power", "gpu")
                ]
            else:
                # 通用比較
                features = [
                    ("CPU Model", "cpu"),
                    ("GPU Model", "gpu"),
                    ("Memory Type", "memory"),
                    ("Storage Type", "storage"),
                    ("Battery Capacity", "battery")
                ]
            
            # 構建比較表格
            comparison_table = []
            for feature_name, data_field in features:
                row = {"feature": feature_name}
                for model_name in target_modelnames:
                    # 找到對應模型的數據
                    model_data = next((item for item in context_list_of_dicts if item.get("modelname") == model_name), None)
                    if model_data:
                        field_data = model_data.get(data_field, "")
                        # 提取關鍵信息
                        if data_field == "cpu":
                            # 提取CPU型號
                            cpu_match = re.search(r"Ryzen™\s+\d+\s+\d+[A-Z]*[HS]*", field_data)
                            row[model_name] = cpu_match.group(0) if cpu_match else "N/A"
                        elif data_field == "gpu":
                            # 提取GPU型號
                            gpu_match = re.search(r"AMD Radeon™\s+[A-Z0-9]+[A-Z]*", field_data)
                            row[model_name] = gpu_match.group(0) if gpu_match else "N/A"
                        elif data_field == "memory":
                            # 提取記憶體類型
                            memory_match = re.search(r"DDR\d+", field_data)
                            row[model_name] = memory_match.group(0) if memory_match else "N/A"
                        elif data_field == "storage":
                            # 提取儲存類型
                            storage_match = re.search(r"M\.2.*?PCIe.*?NVMe", field_data)
                            row[model_name] = storage_match.group(0) if storage_match else "N/A"
                        elif data_field == "battery":
                            # 提取電池容量
                            battery_match = re.search(r"(\d+\.?\d*)\s*Wh", field_data)
                            row[model_name] = f"{battery_match.group(1)}Wh" if battery_match else "N/A"
                        elif data_field == "thermal":
                            # 提取散熱設計
                            thermal_match = re.search(r"(\d+)W", field_data)
                            row[model_name] = f"{thermal_match.group(1)}W" if thermal_match else "N/A"
                        elif data_field == "structconfig":
                            # 提取結構配置信息
                            if feature_name == "Weight":
                                weight_match = re.search(r"Weight:\s*(\d+)\s*g", field_data)
                                if weight_match:
                                    weight_g = int(weight_match.group(1))
                                    weight_kg = weight_g / 1000
                                    row[model_name] = f"{weight_g}g ({weight_kg:.1f}kg)"
                                else:
                                    row[model_name] = "N/A"
                            elif feature_name == "Dimensions":
                                dim_match = re.search(r"Dimension:\s*([\d\.]+\s*×\s*[\d\.]+\s*×\s*[\d\.]+\s*mm)", field_data)
                                row[model_name] = dim_match.group(1) if dim_match else "N/A"
                            elif feature_name == "Form Factor":
                                form_match = re.search(r"Form:\s*([^\n]+)", field_data)
                                row[model_name] = form_match.group(1) if form_match else "N/A"
                            elif feature_name == "Material":
                                material_match = re.search(r"Material[^:]*:\s*([^\n]+)", field_data)
                                row[model_name] = material_match.group(1) if material_match else "N/A"
                            else:
                                row[model_name] = "N/A"
                        else:
                            row[model_name] = "N/A"
                    else:
                        row[model_name] = "N/A"
                comparison_table.append(row)
            
            # 生成摘要
            if "輕便" in query or "重量" in query or "weight" in query.lower() or "portable" in query.lower():
                # 提取重量信息進行比較
                weights = {}
                for model_name in target_modelnames:
                    model_data = next((item for item in context_list_of_dicts if item.get("modelname") == model_name), None)
                    if model_data:
                        structconfig = model_data.get("structconfig", "")
                        weight_match = re.search(r"Weight:\s*(\d+)\s*g", structconfig)
                        if weight_match:
                            weights[model_name] = int(weight_match.group(1))
                
                if len(weights) >= 2:
                    # 找到最輕的型號
                    lightest_model = min(weights.keys(), key=lambda x: weights[x])
                    lightest_weight = weights[lightest_model]
                    heaviest_model = max(weights.keys(), key=lambda x: weights[x])
                    heaviest_weight = weights[heaviest_model]
                    
                    if lightest_weight < heaviest_weight:
                        weight_diff = heaviest_weight - lightest_weight
                        summary = f"根據重量比較，{lightest_model} 最輕便，重量為 {lightest_weight}g ({lightest_weight/1000:.1f}kg)，比 {heaviest_model} 輕 {weight_diff}g。"
                    else:
                        summary = f"根據提供的数据，{len(target_modelnames)} 个型号的重量相同或相近。"
                else:
                    summary = f"根据提供的数据，比较了 {len(target_modelnames)} 个笔电型号的重量规格。"
            elif "遊戲" in query or "gaming" in query.lower():
                summary = f"根据实际数据，{target_modelnames[0]} 系列包含 {len(target_modelnames)} 个游戏笔记型电脑型号，各有不同的性能配置。"
            else:
                summary = f"根据提供的数据，比较了 {len(target_modelnames)} 个笔电型号的规格。"
            
            # 使用美化表格格式化回應
            formatted_response = self._format_response_with_beautiful_table(
                summary,
                comparison_table,
                target_modelnames
            )
            
            return formatted_response
            
        except Exception as e:
            logging.error(f"生成備用回應時發生錯誤: {e}")
            return {
                "answer_summary": "抱歉，處理數據時發生錯誤。",
                "comparison_table": []
            }

    def _process_llm_response(self, parsed_json, context_list_of_dicts, target_modelnames):
        """
        處理LLM回應並生成最終結果
        """
        try:
            # 提取模型名稱
            model_names = []
            for item in context_list_of_dicts:
                model_name = item.get('modelname', 'Unknown')
                if model_name not in model_names:
                    model_names.append(model_name)
            
            # 檢查comparison_table格式並修正
            comparison_table = parsed_json.get("comparison_table", [])
            if isinstance(comparison_table, dict):
                # 轉換字典格式為列表格式
                comparison_table = self._convert_dict_to_list_of_dicts(comparison_table)
            
            # 使用美化表格格式化回應
            formatted_response = self._format_response_with_beautiful_table(
                parsed_json.get("answer_summary", ""),
                comparison_table,
                model_names
            )
            
            logging.info(f"LLM回答处理成功，answer_summary: {parsed_json.get('answer_summary', '')}")
            return formatted_response
            
        except Exception as e:
            logging.error(f"處理LLM回應時發生錯誤: {e}")
            return {
                "answer_summary": "抱歉，AI 回應的格式不正確，無法解析。",
                "comparison_table": []
            }

    def _process_llm_response_robust(self, parsed_json, context_list_of_dicts, target_modelnames, query):
        """
        更稳健的响应处理：使用两步骤策略
        优先使用LLM的answer_summary，即使comparison_table有问题
        """
        try:
            logging.info("開始使用兩步驟策略處理LLM回應")
            
            # 步骤1：分离验证
            validation_result = self._validate_llm_response_separated(parsed_json, target_modelnames)
            
            # 步骤2：优先使用LLM的answer_summary
            if validation_result["summary_valid"]:
                answer_summary = validation_result["answer_summary"]
                logging.info(f"使用LLM的answer_summary: {answer_summary}")
            else:
                # 生成备用summary
                answer_summary = self._generate_fallback_summary(query, context_list_of_dicts, target_modelnames)
                logging.info(f"使用備用answer_summary: {answer_summary}")
            
            # 步骤3：处理comparison_table
            if validation_result["table_valid"]:
                comparison_table = validation_result["comparison_table"]
                logging.info(f"使用LLM的comparison_table: {comparison_table}")
            else:
                # 生成备用table
                comparison_table = self._generate_fallback_table(context_list_of_dicts, target_modelnames, query)
                logging.info(f"使用備用comparison_table: {comparison_table}")
            
            # 步骤4：格式化最终响应
            formatted_response = self._format_response_with_beautiful_table(
                answer_summary,
                comparison_table,
                target_modelnames
            )
            
            logging.info(f"兩步驟策略處理完成 - answer_summary: {formatted_response.get('answer_summary', '')}")
            return formatted_response
            
        except Exception as e:
            logging.error(f"兩步驟策略處理失敗: {e}")
            # 如果两步骤策略失败，回退到原来的方法
            return self._process_llm_response(parsed_json, context_list_of_dicts, target_modelnames)

    def _generate_fallback_summary(self, query, context_list_of_dicts, target_modelnames):
        """
        生成备用的answer_summary
        """
        try:
            # 根据查询类型生成不同的摘要
            if "螢幕" in query or "顯示" in query or "screen" in query.lower():
                if len(target_modelnames) > 1:
                    return f"根據提供的数据，{len(target_modelnames)}个型号的螢幕規格比較如下。"
                else:
                    return f"根據提供的数据，{target_modelnames[0]}的螢幕規格如下。"
            elif "電池" in query or "續航" in query or "battery" in query.lower():
                if len(target_modelnames) > 1:
                    return f"根據提供的数据，{len(target_modelnames)}个型号的電池規格比較如下。"
                else:
                    return f"根據提供的数据，{target_modelnames[0]}的電池規格如下。"
            elif "cpu" in query.lower() or "處理器" in query:
                if len(target_modelnames) > 1:
                    return f"根據提供的数据，{len(target_modelnames)}个型号的CPU規格比較如下。"
                else:
                    return f"根據提供的数据，{target_modelnames[0]}的CPU規格如下。"
            elif "gpu" in query.lower() or "顯卡" in query:
                if len(target_modelnames) > 1:
                    return f"根據提供的数据，{len(target_modelnames)}个型号的GPU規格比較如下。"
                else:
                    return f"根據提供的数据，{target_modelnames[0]}的GPU規格如下。"
            elif "輕便" in query or "重量" in query or "weight" in query.lower():
                if len(target_modelnames) > 1:
                    return f"根據提供的数据，{len(target_modelnames)}个型号的重量和便攜性比較如下。"
                else:
                    return f"根據提供的数据，{target_modelnames[0]}的重量和便攜性規格如下。"
            else:
                # 通用摘要
                if len(target_modelnames) > 1:
                    return f"根據提供的数据，{len(target_modelnames)}个型号的規格比較如下。"
                else:
                    return f"根據提供的数据，{target_modelnames[0]}的規格如下。"
                    
        except Exception as e:
            logging.error(f"生成備用summary失敗: {e}")
            return f"根據提供的数据，比較了 {len(target_modelnames)} 个笔电型号的规格。"

    def _generate_fallback_table(self, context_list_of_dicts, target_modelnames, query):
        """
        生成备用的comparison_table
        """
        try:
            # 根据查询类型决定要比较的特征
            if "螢幕" in query or "顯示" in query or "screen" in query.lower():
                features = [
                    ("Display Size", "lcd"),
                    ("Resolution", "lcd"),
                    ("Refresh Rate", "lcd"),
                    ("Panel Type", "lcd")
                ]
            elif "電池" in query or "續航" in query or "battery" in query.lower():
                features = [
                    ("Battery Capacity", "battery"),
                    ("Battery Life", "battery"),
                    ("Charging Speed", "battery")
                ]
            elif "cpu" in query.lower() or "處理器" in query:
                features = [
                    ("CPU Model", "cpu"),
                    ("CPU Architecture", "cpu"),
                    ("CPU TDP", "cpu")
                ]
            elif "gpu" in query.lower() or "顯卡" in query:
                features = [
                    ("GPU Model", "gpu"),
                    ("GPU Memory", "gpu"),
                    ("GPU Power", "gpu")
                ]
            elif "輕便" in query or "重量" in query or "weight" in query.lower():
                features = [
                    ("Weight", "structconfig"),
                    ("Dimensions", "structconfig"),
                    ("Form Factor", "structconfig")
                ]
            else:
                # 通用比较
                features = [
                    ("CPU Model", "cpu"),
                    ("GPU Model", "gpu"),
                    ("Memory Type", "memory"),
                    ("Storage Type", "storage"),
                    ("Battery Capacity", "battery")
                ]
            
            # 构建比较表格
            comparison_table = []
            for feature_name, data_field in features:
                row = {"feature": feature_name}
                for model_name in target_modelnames:
                    # 找到对应模型的数据
                    model_data = next((item for item in context_list_of_dicts if item.get("modelname") == model_name), None)
                    if model_data:
                        field_data = model_data.get(data_field, "")
                        # 提取关键信息
                        if data_field == "cpu":
                            # 提取CPU型号
                            cpu_match = re.search(r"Ryzen™\s+\d+\s+\d+[A-Z]*[HS]*", field_data)
                            row[model_name] = cpu_match.group(0) if cpu_match else "N/A"
                        elif data_field == "gpu":
                            # 提取GPU型号
                            gpu_match = re.search(r"AMD Radeon™\s+[A-Z0-9]+[A-Z]*", field_data)
                            row[model_name] = gpu_match.group(0) if gpu_match else "N/A"
                        elif data_field == "memory":
                            # 提取内存类型
                            memory_match = re.search(r"DDR\d+", field_data)
                            row[model_name] = memory_match.group(0) if memory_match else "N/A"
                        elif data_field == "storage":
                            # 提取存储类型
                            storage_match = re.search(r"M\.2.*?PCIe.*?NVMe", field_data)
                            row[model_name] = storage_match.group(0) if storage_match else "N/A"
                        elif data_field == "battery":
                            # 提取电池容量
                            battery_match = re.search(r"(\d+\.?\d*)\s*Wh", field_data)
                            row[model_name] = f"{battery_match.group(1)}Wh" if battery_match else "N/A"
                        elif data_field == "lcd":
                            # 提取屏幕信息
                            if "FHD" in field_data:
                                row[model_name] = "FHD 1920×1080"
                            elif "QHD" in field_data:
                                row[model_name] = "QHD 2560×1440"
                            else:
                                row[model_name] = "N/A"
                        elif data_field == "structconfig":
                            # 提取重量信息
                            weight_match = re.search(r"Weight:\s*(\d+)\s*g", field_data)
                            if weight_match:
                                weight_g = int(weight_match.group(1))
                                row[model_name] = f"{weight_g}g ({weight_g/1000:.1f}kg)"
                            else:
                                row[model_name] = "N/A"
                        else:
                            row[model_name] = "N/A"
                    else:
                        row[model_name] = "N/A"
                
                comparison_table.append(row)
            
            return comparison_table
            
        except Exception as e:
            logging.error(f"生成備用table失敗: {e}")
            return []