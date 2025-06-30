<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Python實體識別與意圖檢測系統實現

基於自然語言處理技術，本文實現了一個完整的Python程式，能夠對用戶輸入文本進行**實體識別**（Named Entity Recognition, NER）和**意圖檢測**（Intent Detection），並將結果以JSON格式存儲，同時記錄實體與意圖之間的關係[^1][^2]。

## 系統架構與設計

本系統採用模組化設計，主要包含三個核心組件：實體識別模組、意圖檢測模組和關係識別模組[^3][^4]。系統基於spaCy自然語言處理庫進行實體識別，使用規則匹配和關鍵詞分析進行意圖檢測[^1][^5]。

### 技術棧選擇

系統使用以下主要技術和庫[^1][^3][^4]：

- **spaCy**: 提供強大的NER功能和中文語言模型支持
- **scikit-learn**: 用於機器學習分類器實現
- **transformers**: 支持BERT等先進模型的集成
- **JSON**: 標準化數據存儲格式


## 核心組件實現

### 實體識別模組

實體識別模組基於spaCy的pre-trained模型，能夠識別多種實體類型[^1][^2]：

```python
def recognize_entities(self, text: str) -> List[Entity]:
    """實體識別"""
    doc = self.nlp(text)
    entities = []
    
    for ent in doc.ents:
        entity = Entity(
            text=ent.text,
            label=ent.label_,
            start=ent.start_char,
            end=ent.end_char
        )
        entities.append(entity)
        
    return entities
```

系統能識別的實體類型包括[^5][^2]：

- **PERSON**: 人名
- **ORG**: 組織機構
- **GPE**: 地理政治實體
- **DATE**: 日期時間
- **CARDINAL**: 數字
- **MONEY**: 金錢數額


### 意圖檢測模組

意圖檢測採用混合方法，結合關鍵詞匹配和正則表達式模式識別[^6][^7]：

```python
def detect_intent(self, text: str) -> Intent:
    """改進的意圖檢測"""
    best_intent = '其他'
    best_confidence = 0.0
    matched_keywords = []
    
    # 對每個意圖進行匹配
    for intent_name, patterns in self.intent_patterns.items():
        score = 0.0
        temp_keywords = []
        
        # 關鍵詞匹配
        for keyword in patterns['keywords']:
            if keyword in text:
                score += 1.0
                temp_keywords.append(keyword)
        
        # 模式匹配
        for pattern in patterns['patterns']:
            if re.search(pattern, text):
                score += 2.0  # 模式匹配權重更高
```

系統預定義的意圖類別包括[^6][^7]：

- **預約**: 安排會面、訂購服務
- **查詢**: 搜尋信息、狀態查詢
- **投訴**: 表達不滿、問題反饋
- **購買**: 商品採購、價格詢問
- **取消**: 撤銷預約、退訂服務
- **幫助**: 尋求協助、問題解決
- **問候**: 日常問候、寒暄


### 關係識別模組

關係識別模組建立實體與意圖之間的語義連接，分析其在文本中的相互作用[^8][^9]：

```python
def identify_relations(self, text: str, entities: List[Entity], intent: Intent) -> List[EntityIntentRelation]:
    """識別實體與意圖之間的關係"""
    relations = []
    
    for entity in entities:
        # 判斷關係類型
        relation_type = self._determine_relation_type(entity, intent, text)
        
        # 計算關係信心度
        confidence = self._calculate_relation_confidence(entity, intent, text)
        
        relation = EntityIntentRelation(
            entity_text=entity.text,
            entity_label=entity.label,
            intent_name=intent.name,
            relation_type=relation_type,
            confidence=confidence
        )
        relations.append(relation)
```

關係類型定義包括[^8][^10]：

- **appointment_date**: 預約日期
- **appointment_time**: 預約時間
- **target_person**: 目標人物
- **location_query**: 地點查詢
- **purchase_item**: 購買物品
- **related_to**: 一般關聯


## 數據結構設計

系統採用物件導向設計，定義了清晰的數據結構[^11][^12]：

```python
@dataclass
class Entity:
    """實體類別"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0

@dataclass
class Intent:
    """意圖類別"""
    name: str
    confidence: float
    keywords: List[str]

@dataclass
class EntityIntentRelation:
    """實體與意圖關係"""
    entity_text: str
    entity_label: str
    intent_name: str
    relation_type: str
    confidence: float
```


## JSON存儲格式

系統將處理結果以結構化的JSON格式存儲，包含元數據和詳細的分析結果[^13][^12]：

JSON文件結構包含以下主要部分[^13][^11]：

### 元數據（Metadata）

- **created_at**: 創建時間戳
- **total_entries**: 處理條目總數
- **version**: 系統版本號


### 處理結果（Results）

每條處理結果包含[^13][^12]：

- **original_text**: 原始輸入文本
- **timestamp**: 處理時間戳
- **entities**: 識別出的實體列表
- **intent**: 檢測到的意圖信息
- **relations**: 實體與意圖的關係記錄


## 使用示例

以下展示系統的實際使用方法[^1][^4]：

```python
# 創建系統實例
nlp_system = ImprovedEntityRecognitionIntentDetection()

# 處理文本
text = "我想預約明天下午2點與王醫生見面"
result = nlp_system.process_text(text)

# 保存結果到JSON
nlp_system.save_to_json([result], 'output.json')
```


## 結果分析

系統在測試數據上展現了良好的性能表現[^9][^14]：

### 實體識別精度

- 日期時間識別準確率較高，能正確識別"明天"、"下午2點"等時間表達
- 地理位置識別有效，如"台北"等地名能被正確標記為GPE類型[^5][^2]


### 意圖檢測效能

- 改進的關鍵詞匹配算法提升了意圖識別準確度
- 多層次匹配策略（關鍵詞+模式匹配）增強了系統魯棒性[^6][^7]


### 關係識別質量

- 系統能有效建立實體與意圖間的語義關聯
- 關係信心度計算考慮了實體位置和上下文信息[^8][^10]


## 系統優勢與特點

本實現具有以下顯著優勢[^1][^6]：

1. **模組化設計**: 各組件獨立可測試，便於維護和擴展
2. **多語言支持**: 基於spaCy框架，支持中文和英文處理
3. **關係建模**: 不僅識別實體和意圖，還分析其相互關係
4. **標準化輸出**: JSON格式便於後續處理和系統集成
5. **擴展性強**: 可輕鬆添加新的意圖類別和實體類型

## 結語

本Python程式成功實現了用戶需求，提供了完整的實體識別與意圖檢測解決方案[^1][^7]。系統不僅能準確分析文本中的實體和意圖，還能建立它們之間的關聯關係，並以結構化的JSON格式保存所有分析結果[^13][^11]。這為後續的自然語言理解應用和智能對話系統提供了堅實的技術基礎[^15][^6]。

<div style="text-align: center">⁂</div>

[^1]: https://www.linkedin.com/pulse/quick-start-entity-recognition-spacy-travis-myers-p6tne

[^2]: https://spacy.io/api/entityrecognizer

[^3]: https://www.kdnuggets.com/implement-named-entity-recognition-with-hugging-face-transformers

[^4]: https://www.linkedin.com/pulse/day-20-named-entity-recognition-ner-notebook-vinod-kumar-g-r-0v7gc

[^5]: https://vocus.cc/article/64ad4ab6fd89780001f182eb

[^6]: https://quidget.ai/blog/ai-automation/intent-classification-for-chatbots-guide/

[^7]: https://spotintelligence.com/2023/11/03/intent-classification-nlp/

[^8]: https://forum.rasa.com/t/custom-entity-and-relation-extraction/601

[^9]: https://arxiv.org/pdf/2109.03221.pdf

[^10]: https://nlpcraft.apache.org/intent-matching.html

[^11]: https://docs.pydantic.dev/latest/concepts/json_schema/

[^12]: https://json-schema.org/learn/getting-started-step-by-step

[^13]: https://cookbook.chat-data.com/docs/train-chatbots-with-json

[^14]: https://aclanthology.org/2024.cl4health-1.33.pdf

[^15]: https://microsoft.github.io/kernel-memory/how-to/intent-detection

[^16]: https://github.com/MLArtist/intent-detection-using-XLM-Roberta

[^17]: https://stackoverflow.com/questions/44213549/python-nlp-intent-identification

[^18]: https://docs.chatbotbuilder.ai/support/solutions/articles/150000184166-get-data-from-json

[^19]: https://github.com/staudenmeir/eloquent-json-relations

[^20]: https://stackoverflow.com/questions/77777440/json-serialization-issue-with-bidirectional-onetoone-relationship/77779320

[^21]: https://www.youtube.com/watch?v=QNSJbKQLElM

[^22]: https://stackoverflow.com/questions/25014650/json-schema-example-for-oneof-objects

[^23]: https://hannibunny.github.io/mlbook/transformer/intent_classification_with_bert.html

[^24]: https://www.diva-portal.org/smash/get/diva2:1763051/FULLTEXT01.pdf

[^25]: https://machinelearningmastery.com/how-to-do-named-entity-recognition-ner-with-a-bert-model/

[^26]: https://spacy.io/universe/project/video-spacys-ner-model-alt

[^27]: https://github.com/bioNLU-coling2024/biomed-NER-intent_detection

[^28]: https://stackoverflow.com/questions/57236318/how-to-post-manytoone-entity-using-json-format

[^29]: https://stackoverflow.com/questions/65955232/how-can-i-find-relationship-between-two-entities-or-words-using-nlp

[^30]: https://realpython.com/natural-language-processing-spacy-python/

[^31]: https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/cae26b4864a13635f423e5096e2c5a42/4f654368-00aa-49d2-b243-621d472f24b2/06b13a0a.json

