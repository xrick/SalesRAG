import json
import re
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

# 嘗試導入 pytablewriter，如果不存在則使用內建實現
try:
    import pytablewriter
    HAS_PYTABLEWRITER = True
except ImportError:
    HAS_PYTABLEWRITER = False
    logging.warning("pytablewriter not found, using built-in table generation")

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

    def _robust_json_parse(self, response_str: str) -> dict:
        """強健的JSON解析，支持多種修復策略"""
        # 首先嘗試提取JSON部分
        json_content = self._extract_json_content(response_str)
        
        # 嘗試直接解析
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            logging.info(f"第一次JSON解析失敗: {e}, 嘗試修復...")
            
        # 嘗試修復後解析
        try:
            fixed_json = self._fix_json_quotes(json_content)
            return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            logging.info(f"修復後JSON解析仍失敗: {e}, 使用降級解析...")
            
        # 降級解析 - 提取關鍵字段
        return self._fallback_parse(response_str)
    
    def _extract_json_content(self, response_str: str) -> str:
        """提取JSON內容"""
        # 尋找JSON代碼塊
        json_start = response_str.find("```json")
        if json_start == -1:
            json_start = response_str.find("```")
        
        if json_start != -1:
            json_start = response_str.find("{", json_start)
            json_end = response_str.rfind("}")
            if json_start != -1 and json_end != -1:
                return response_str[json_start:json_end+1]
        
        # 如果找不到代碼塊，嘗試找整個JSON
        json_start = response_str.find("{")
        json_end = response_str.rfind("}")
        if json_start != -1 and json_end != -1:
            return response_str[json_start:json_end+1]
            
        raise ValueError("無法找到有效的JSON內容")
    
    def _fix_json_quotes(self, json_str: str) -> str:
        """修復JSON中的引號問題"""
        fixed = json_str
        
        # 基本清理
        fixed = fixed.replace("'", '"')  # 單引號改雙引號
        fixed = re.sub(r'\n+', ' ', fixed)  # 換行符替換為空格
        fixed = re.sub(r'\s+', ' ', fixed)  # 多重空格合併
        
        # 修復conclusion字段的複雜引號問題
        patterns = [
            # 處理 例如："...內容..." 的模式
            (r'"conclusion"\s*:\s*"([^"]*?)(例如|比如|如下|建議|結論|總結|具體)："([^"]*?)"([^"]*?)""', 
             r'"conclusion": "\1\2：\\"\3\\"\4"'),
            # 處理 。"...內容..." 的模式
            (r'"conclusion"\s*:\s*"([^"]*?)。"([^"]*?)"([^"]*?)""', 
             r'"conclusion": "\1。\\"\2\\"\3"'),
            # 處理 ："...內容..." 的模式
            (r'"conclusion"\s*:\s*"([^"]*?)："([^"]*?)"([^"]*?)""', 
             r'"conclusion": "\1：\\"\2\\"\3"'),
            # 通用多引號處理
            (r'"conclusion"\s*:\s*"([^"]*)"([^"]*)"([^"]*)""+', 
             r'"conclusion": "\1\\"\2\\"\3"'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, fixed):
                fixed = re.sub(pattern, replacement, fixed)
                break
        
        # 處理其他字段的引號問題
        fixed = re.sub(r'""(\s*[,}])', r'"\1', fixed)  # 去除雙引號結尾
        
        return fixed
    
    def _fallback_parse(self, response_str: str) -> dict:
        """降級解析 - 提取關鍵信息"""
        result = {}
        
        # 提取 answer_summary
        summary_match = re.search(r'"answer_summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response_str)
        if summary_match:
            result["answer_summary"] = summary_match.group(1).replace('\\"', '"')
        
        # 提取 conclusion
        conclusion_patterns = [
            r'"conclusion"\s*:\s*"([^"]*?)(例如|比如|如下|建議|結論|總結|具體)："([^"]*?)"([^"]*?)"',
            r'"conclusion"\s*:\s*"([^"]*?)。"([^"]*?)"([^"]*?)"',
            r'"conclusion"\s*:\s*"([^"]*?)："([^"]*?)"([^"]*?)"',
            r'"conclusion"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
        ]
        
        for pattern in conclusion_patterns:
            match = re.search(pattern, response_str)
            if match:
                if len(match.groups()) == 4:  # 複雜模式
                    result["conclusion"] = f"{match.group(1)}{match.group(2)}：\"{match.group(3)}\"{match.group(4)}"
                elif len(match.groups()) == 3:  # 三組模式
                    result["conclusion"] = f"{match.group(1)}\"{match.group(2)}\"{match.group(3)}"
                else:  # 簡單模式
                    result["conclusion"] = match.group(1).replace('\\"', '"')
                break
        
        # 嘗試提取 comparison_table（簡化版）
        try:
            table_match = re.search(r'"comparison_table"\s*:\s*(\[.*?\])', response_str, re.DOTALL)
            if table_match:
                result["comparison_table"] = json.loads(table_match.group(1))
        except:
            result["comparison_table"] = []
        
        # 提取 source_references
        try:
            ref_match = re.search(r'"source_references"\s*:\s*(\[.*?\])', response_str)
            if ref_match:
                result["source_references"] = json.loads(ref_match.group(1))
        except:
            result["source_references"] = []
        
        if not result.get("answer_summary") and not result.get("conclusion"):
            result["error"] = "無法解析AI回應內容"
            
        return result
    
    def _generate_markdown_table(self, comparison_data: list, table_type: str = "default") -> str:
        """在後端生成markdown表格"""
        if not comparison_data:
            return ""
        
        # 使用pytablewriter（如果可用）或內建實現
        if HAS_PYTABLEWRITER:
            return self._generate_table_with_pytablewriter(comparison_data, table_type)
        else:
            return self._generate_table_builtin(comparison_data, table_type)
    
    def _generate_table_with_pytablewriter(self, data: list, table_type: str) -> str:
        """使用pytablewriter生成表格"""
        try:
            if not data:
                return ""
                
            # 分析數據結構
            first_row = data[0]
            headers = list(first_row.keys())
            
            # 美化表頭
            beautified_headers = [self._beautify_header(h) for h in headers]
            
            # 準備數據
            table_data = []
            for row in data:
                formatted_row = []
                for key in headers:
                    value = row.get(key, 'N/A')
                    formatted_value = self._format_cell_value(value)
                    formatted_row.append(formatted_value)
                table_data.append(formatted_row)
            
            # 生成表格
            writer = pytablewriter.MarkdownTableWriter(
                headers=beautified_headers,
                value_matrix=table_data,
                margin=1
            )
            
            table_content = writer.dumps()
            
            # 添加標題
            title = self._generate_table_title(data, table_type)
            return f"### {title}\n\n{table_content}\n"
            
        except Exception as e:
            logging.error(f"pytablewriter生成表格失敗: {e}")
            return self._generate_table_builtin(data, table_type)
    
    def _generate_table_builtin(self, data: list, table_type: str) -> str:
        """內建的表格生成實現"""
        if not data:
            return ""
            
        first_row = data[0]
        headers = list(first_row.keys())
        
        # 美化表頭
        beautified_headers = [self._beautify_header(h) for h in headers]
        
        # 生成標題
        title = self._generate_table_title(data, table_type)
        markdown = f"### {title}\n\n"
        
        # 生成表頭
        markdown += f"| {' | '.join(beautified_headers)} |\n"
        markdown += f"|{' | '.join([':---' for _ in headers])}|\n"
        
        # 生成數據行
        for row in data:
            formatted_row = []
            for key in headers:
                value = row.get(key, 'N/A')
                formatted_value = self._format_cell_value(value)
                formatted_row.append(formatted_value)
            markdown += f"| {' | '.join(formatted_row)} |\n"
        
        return markdown + "\n"
    
    def _beautify_header(self, header: str) -> str:
        """美化表頭"""
        conversions = {
            'MODEL_A': '🔸 型號 A',
            'MODEL_B': '🔹 型號 B',
            'MODEL_C': '🔸 型號 C',
            'MODEL_D': '🔹 型號 D',
            'feature': '📝 特性',
            'price': '💰 價格',
            'performance': '⚡ 效能',
            'design': '🎨 設計',
            'battery': '🔋 電池',
            'display': '🖥️ 顯示器',
            'storage': '💾 儲存',
            'memory': '🧠 記憶體',
            'processor': '🔧 處理器',
            'graphics': '🎮 顯卡'
        }
        
        if header in conversions:
            return conversions[header]
        
        if header.startswith('MODEL_'):
            model_id = header.replace('MODEL_', '')
            return f"🔸 型號 {model_id}"
        
        # 一般化處理
        return header.replace('_', ' ').replace('-', ' ').title()
    
    def _format_cell_value(self, value) -> str:
        """格式化單元格值"""
        if value is None or value == "":
            return "`N/A`"
        
        if isinstance(value, (int, float)):
            if value > 1000:
                return f"**{value:,}**"
            return str(value)
        
        value_str = str(value)
        
        # 處理長文本
        if len(value_str) > 60:
            truncated = value_str[:57] + "..."
            return f"<details><summary>{truncated}</summary>{value_str}</details>"
        
        # 轉義markdown特殊字符
        value_str = value_str.replace('|', '\\|').replace('\n', '<br/>')
        
        # 重要信息加粗
        if 10 < len(value_str) < 50 and not ':' in value_str:
            return f"**{value_str}**"
        
        return value_str
    
    def _generate_table_title(self, data: list, table_type: str) -> str:
        """生成表格標題"""
        if table_type == "product_comparison":
            return f"📊 {len(data)}項產品規格比較"
        elif table_type == "feature_comparison":
            return "🔍 功能特性比較"
        else:
            model_count = sum(1 for key in data[0].keys() if 'MODEL_' in key.upper())
            if model_count >= 2:
                return f"📊 {model_count}款產品規格比較"
            return "📋 詳細規格比較"
    
    def _create_formatted_response(self, parsed_data: dict) -> str:
        """創建格式化的回應內容"""
        content_parts = []
        
        # 答案摘要
        if parsed_data.get("answer_summary"):
            content_parts.append(parsed_data["answer_summary"])
        
        # 比較表格
        if parsed_data.get("comparison_table"):
            table_type = parsed_data.get("table_type", "default")
            table_markdown = self._generate_markdown_table(
                parsed_data["comparison_table"], 
                table_type
            )
            if table_markdown:
                content_parts.append(table_markdown)
        
        # 產品清單
        if parsed_data.get("products"):
            products_markdown = self._generate_product_list(parsed_data["products"])
            content_parts.append(products_markdown)
        
        # 規格詳細資訊
        if parsed_data.get("specifications"):
            specs_markdown = self._generate_specifications(parsed_data["specifications"])
            content_parts.append(specs_markdown)
        
        # 推薦建議
        if parsed_data.get("recommendations"):
            rec_markdown = self._generate_recommendations(parsed_data["recommendations"])
            content_parts.append(rec_markdown)
        
        # 分析結果
        if parsed_data.get("analysis"):
            content_parts.append(f"### 分析結果\n{parsed_data['analysis']}")
        
        # 結論建議
        if parsed_data.get("conclusion"):
            content_parts.append(f"### 結論建議\n{parsed_data['conclusion']}")
        elif parsed_data.get("summary"):
            content_parts.append(f"### 總結\n{parsed_data['summary']}")
        
        # 額外資訊
        if parsed_data.get("additional_info"):
            content_parts.append(f"### 額外資訊\n{parsed_data['additional_info']}")
        
        # 參考資料來源
        if parsed_data.get("source_references"):
            refs = parsed_data["source_references"]
            if refs:
                content_parts.append(f"<details><summary>參考資料來源</summary>\n\n")
                for ref in refs:
                    clean_ref = re.sub(r'[\r\n]+', ' ', str(ref)).strip()
                    if clean_ref:
                        content_parts.append(f"> {clean_ref}")
                content_parts.append("</details>")
        
        return "\n\n".join(content_parts)
    
    def _generate_product_list(self, products: list) -> str:
        """生成產品清單"""
        markdown = "### 推薦產品\n\n"
        for i, product in enumerate(products, 1):
            markdown += f"{i}. **{product.get('name', product.get('model', 'Unknown'))}**\n"
            if product.get('price'):
                markdown += f"   - 價格：{product['price']}\n"
            if product.get('description'):
                markdown += f"   - 描述：{product['description']}\n"
            if product.get('features'):
                features = product['features']
                if isinstance(features, list):
                    markdown += f"   - 主要特色：{', '.join(features)}\n"
            markdown += "\n"
        return markdown
    
    def _generate_specifications(self, specifications: dict) -> str:
        """生成規格詳細資訊"""
        markdown = "### 詳細規格\n\n"
        for category, specs in specifications.items():
            markdown += f"**{category}**\n"
            if isinstance(specs, dict):
                for key, value in specs.items():
                    markdown += f"- {key}：{value}\n"
            else:
                markdown += f"- {specs}\n"
            markdown += "\n"
        return markdown
    
    def _generate_recommendations(self, recommendations: list) -> str:
        """生成推薦內容"""
        markdown = "### 推薦建議\n\n"
        for i, rec in enumerate(recommendations, 1):
            title = rec.get('title', rec.get('recommendation', f'建議 {i}'))
            markdown += f"{i}. {title}\n"
            if rec.get('reason'):
                markdown += f"   - 理由：{rec['reason']}\n"
            if rec.get('benefits'):
                markdown += f"   - 優勢：{rec['benefits']}\n"
            markdown += "\n"
        return markdown

    async def chat_stream(self, query: str, **kwargs):
        """執行完整的 RAG 流程，在後端處理所有格式化"""
        try:
            # 1. 知識檢索
            retrieved_docs = self.milvus_query.search(query, top_k=5)
            semantic_context = "\n---\n".join([f"Source: {doc['source']}\nContent: {doc['text']}" for doc in retrieved_docs])

            # 從 DuckDB 進行關鍵字查詢
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

            # 4. LLM 互動
            response_str = self.llm.invoke(final_prompt)
            
            print("\n=== RAW LLM RESPONSE ===")
            print(response_str)
            print("=======================\n")

            # 5. 強健的JSON解析
            try:
                parsed_data = self._robust_json_parse(response_str)
                print("\n=== PARSED DATA ===")
                print(json.dumps(parsed_data, ensure_ascii=False, indent=2))
                print("===================\n")
                
                # 6. 在後端生成完整的markdown內容
                formatted_content = self._create_formatted_response(parsed_data)
                
                print("\n=== FORMATTED CONTENT ===")
                print(formatted_content)
                print("========================\n")
                
                # 7. 返回簡化的響應結構
                final_response = {
                    "role": "assistant",
                    "content": formatted_content,
                    "content_type": "markdown",
                    "metadata": {
                        "has_table": bool(parsed_data.get("comparison_table")),
                        "has_recommendations": bool(parsed_data.get("recommendations")),
                        "source_count": len(parsed_data.get("source_references", []))
                    }
                }
                
                yield f"data: {json.dumps(final_response, ensure_ascii=False)}\n\n"
                
            except Exception as parse_error:
                logging.error(f"JSON解析失敗: {parse_error}")
                
                # 完全降級：返回原始回應
                fallback_response = {
                    "role": "assistant", 
                    "content": f"## AI 回應\n\n{response_str}\n\n> **注意**: 回應格式解析失敗，顯示原始內容",
                    "content_type": "markdown",
                    "metadata": {"parse_error": True}
                }
                
                yield f"data: {json.dumps(fallback_response, ensure_ascii=False)}\n\n"

        except Exception as e:
            logging.error(f"Service錯誤: {str(e)}")
            error_response = {
                "role": "assistant",
                "content": "抱歉，處理您的請求時發生錯誤，請稍後再試。",
                "content_type": "markdown",
                "metadata": {"error": True}
            }
            yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"
