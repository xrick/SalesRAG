我来分析这个SalesRAG项目中prompt的核心机制。让我先查看相关的prompt文件来了解完整的机制。

Read file: sales_rag_app/libs/services/sales_assistant/prompts/sales_prompt4.txt
现在让我查看一下LLM初始化器来了解模型配置：

Read file: sales_rag_app/libs/RAG/LLM/LLMInitializer.py
现在让我查看一下主要的聊天流程：

Read file: sales_rag_app/main.py
基于对代码的分析，我来详细解释SalesRAG项目中prompt的核心机制：

## SalesRAG项目Prompt核心机制分析

### 1. **整体架构设计**

这个项目采用了**RAG (Retrieval-Augmented Generation)** 架构，prompt机制是整个系统的核心组件：

```
用户查询 → 数据检索 → Prompt构建 → LLM生成 → 响应格式化
```

### 2. **Prompt模板系统**

#### 2.1 模板加载机制

```python
# 在SalesAssistantService中
self.prompt_template = self._load_prompt_template("sales_rag_app/libs/services/sales_assistant/prompts/sales_prompt4.txt")
```

#### 2.2 动态变量替换

```python
final_prompt = self.prompt_template.replace("{context}", context_str).replace("{query}", query)
```

### 3. **Prompt的核心结构**

#### 3.1 系统角色定义

```
[SYSTEM]
You are a notebook technical sales expert. Your mission is to analyze the provided structured data about notebook models and provide a precise, objective comparison based ONLY on the data provided.
```

#### 3.2 严格的输出格式约束

```json
{
  "answer_summary": "Your summary answer here",
  "comparison_table": [
    {
      "feature": "Feature name",
      "MODEL_NAME_1": "Specification for model 1",
      "MODEL_NAME_2": "Specification for model 2"
    }
  ]
}
```

### 4. **数据安全机制**

#### 4.1 绝对数据限制

- **禁止虚构模型名称**：不允许生成不在数据中的模型名
- **禁止外部知识**：不能引用外部品牌知识
- **GPU限制**：只允许AMD Radeon GPU，禁止NVIDIA GPU
- **数据真实性**：必须基于提供的数据，不能假设

#### 4.2 验证机制

```python
def _validate_llm_response(self, parsed_json, target_modelnames):
    # 验证LLM回答是否包含正确的模型名称
    # 检查无效品牌和GPU型号
```

### 5. **查询理解与路由**

#### 5.1 模型名称检测

```python
def _check_query_contains_modelname(self, query: str) -> tuple[bool, list]:
    # 检查查询中是否包含有效的modelname
  
def _check_query_contains_modeltype(self, query: str) -> tuple[bool, list]:
    # 检查查询中是否包含有效的modeltype
```

#### 5.2 智能路由逻辑

- **优先级处理**：modelname > modeltype
- **系列扩展**：根据modeltype自动获取相关modelname
- **数据验证**：确保查询的模型在数据库中存在

### 6. **上下文构建机制**

#### 6.1 数据检索

```python
# 使用DuckDB直接查询指定的modelname
placeholders = ', '.join(['?'] * len(target_modelnames))
sql_query = f"SELECT * FROM specs WHERE modelname IN ({placeholders})"
full_specs_records = self.duckdb_query.query_with_params(sql_query, target_modelnames)
```

#### 6.2 上下文格式化

```python
# 将查询结果格式化为LLM需要的上下文
context_list_of_dicts = [dict(zip(self.spec_fields, record)) for record in full_specs_records]
context_str = json.dumps(context_list_of_dicts, indent=2, ensure_ascii=False)
```

### 7. **响应处理与格式化**

#### 7.1 多格式表格支持

```python
def _create_beautiful_markdown_table(self, comparison_table: list | dict, model_names: list) -> str:
    # 支持dict of lists格式且自动转置为「型号为栏，规格为列」的markdown表格
```

#### 7.2 备用响应机制

```python
def _generate_fallback_response(self, query, context_list_of_dicts, target_modelnames):
    # 当LLM响应无效时，基于实际数据创建比较表格
```

### 8. **LLM配置**

#### 8.1 模型选择

```python
# 使用Ollama本地模型
model_name: str = "deepseek-r1:7b"
temperature: float = 0.1  # 低温度确保输出一致性
```

#### 8.2 错误处理

- **JSON解析失败**：自动回退到备用响应
- **模型连接失败**：提供明确的错误信息
- **数据缺失**：使用"N/A"标记并说明限制

### 9. **Prompt工程的核心特点**

#### 9.1 结构化约束

- **固定表格格式**：确保输出的一致性
- **字段映射**：将用户查询映射到具体的数据字段
- **验证规则**：多层验证确保数据准确性

#### 9.2 语义理解

- **查询类型识别**：电池、CPU、GPU、重量等
- **特征映射**：根据查询类型选择相关特征
- **数据可用性检查**：确保请求的数据确实存在

### 10. **安全性与可靠性**

#### 10.1 数据隔离

- 严格限制LLM只能使用提供的数据
- 禁止外部知识引用
- 防止数据泄露和虚构

#### 10.2 错误恢复

- 多层备用机制
- 详细的错误日志
- 用户友好的错误信息

这个prompt机制的核心优势在于：

1. **数据安全性**：严格限制LLM只能使用提供的数据
2. **输出一致性**：通过结构化约束确保格式统一
3. **智能路由**：根据查询类型自动选择相关数据
4. **错误恢复**：多层备用机制确保系统稳定性
5. **用户体验**：提供美观的表格展示和清晰的比较结果
