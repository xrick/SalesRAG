[MODE: EXECUTE]

遵照您的指示，我將開始執行已批准的計畫。

**IMPLEMENTATION CHECKLIST:**

1.  `[✓]` 創建一個新文件 `parent_child_chunking_demo.py`。
2.  `[✓]` 在文件中定義 `ParentDocument` 資料類別。
3.  `[✓]` 定義 `ChildChunk` 資料類別。
4.  `[✓]` 實現 `TopicBasedChunker` 類別。
5.  `[✓]` 在 `TopicBasedChunker` 中定義議題關鍵字字典。
6.  `[✓]` 在 `TopicBasedChunker` 中實現 `chunk_document` 方法。
7.  `[✓]` 實現 `SimpleVectorStore` 類別。
8.  `[✓]` 在 `SimpleVectorStore` 中定義數據存儲結構。
9.  `[✓]` 在 `SimpleVectorStore` 中實現 `add_documents` 方法。
10. `[✓]` 在 `SimpleVectorStore` 中實現 `retrieve` 方法。
11. `[✓]` 創建模擬的筆記型電腦產品描述資料。
12. `[✓]` 實例化 `TopicBasedChunker` 和 `SimpleVectorStore`。
13. `[✓]` 將模擬資料轉換成 `ParentDocument` 物件。
14. `[✓]` 遍歷、處理並存儲文件與區塊。
15. `[✓]` 定義範例使用者查詢。
16. `[✓]` 執行查詢。
17. `[✓]` 打印檢索結果。
18. `[✓]` 為程式碼添加註解。

以下是 `parent_child_chunking_demo.py` 的完整實作程式碼：

```python:parent_child_chunking_demo.py
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set

# 2. & 3. Define the data structures for parent and child documents.
# We use dataclasses for a clear and concise representation.
@dataclass
class ParentDocument:
    """
    Represents a full, original document. This is the "parent" in our model.
    The content of this document will be returned to the user for full context.
    """
    doc_id: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class ChildChunk:
    """
    Represents a small, specific chunk of text derived from a ParentDocument.
    This is the "child" that will be used for retrieval.
    """
    chunk_id: str
    parent_doc_id: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)

# 4. Implement the TopicBasedChunker class.
class TopicBasedChunker:
    """
    A chunker that splits a ParentDocument into topic-specific ChildChunks.
    This chunker uses a keyword-based approach to identify the topic of each sentence.
    """

    def __init__(self):
        """
        5. Initialize the chunker with a dictionary of topic keywords.
        Each key is a topic, and the value is a list of keywords associated with it.
        """
        self.topic_keywords: Dict[str, List[str]] = {
            "price": ["sale", "deal", "offer", "discount", "price", "$", "nt$"],
            "performance": ["cpu", "processor", "ram", "memory", "gpu", "graphics", "storage", "ssd"],
            "display": ["screen", "display", "oled", "4k", "resolution", "nits", "infinityedge"],
            "battery": ["battery", "hours", "mah", "power"]
        }
        self._chunk_counter = 0

    def chunk_document(self, doc: ParentDocument) -> List[ChildChunk]:
        """
        6. Implements the logic to chunk a parent document.
        It splits the document by sentences and assigns a topic to each sentence
        if it contains relevant keywords.
        """
        chunks: List[ChildChunk] = []
        # Split content into sentences. A more robust solution would use NLTK or spaCy,
        # but regex is sufficient for this demonstration.
        sentences = re.split(r'(?<=[.!?])\s+', doc.content)

        for sentence in sentences:
            if not sentence:
                continue
            
            # Convert sentence to lowercase for case-insensitive matching.
            lower_sentence = sentence.lower()

            for topic, keywords in self.topic_keywords.items():
                if any(keyword in lower_sentence for keyword in keywords):
                    # If a keyword matches, create a ChildChunk for this topic.
                    chunk = ChildChunk(
                        chunk_id=f"{doc.doc_id}-chunk-{self._chunk_counter}",
                        parent_doc_id=doc.doc_id,
                        content=sentence.strip(),
                        metadata={"topic": topic}
                    )
                    chunks.append(chunk)
                    self._chunk_counter += 1
                    # A sentence can belong to multiple topics, but for simplicity,
                    # we stop after the first match. You could modify this to create
                    # multiple chunks for the same sentence if it covers multiple topics.
                    break 
        return chunks

# 7. Implement the SimpleVectorStore class.
class SimpleVectorStore:
    """
    A simplified simulation of a vector store for demonstration purposes.
    Instead of using vector embeddings, it performs a simple text search on child chunks.
    """

    def __init__(self):
        """
        8. Initialize storage for parent documents and child chunks.
        """
        self.parent_documents: Dict[str, ParentDocument] = {}
        self.child_chunks: List[ChildChunk] = []

    def add_documents(self, docs: List[ParentDocument], chunks: List[ChildChunk]):
        """
        9. Add parent documents and their corresponding child chunks to the store.
        """
        for doc in docs:
            self.parent_documents[doc.doc_id] = doc
        self.child_chunks.extend(chunks)

    def retrieve(self, query: str) -> List[ParentDocument]:
        """
        10. Implements the core retrieval logic.
        It finds relevant child chunks based on the query and returns their parent documents.
        """
        lower_query = query.lower()
        
        # Find relevant child chunks by simple keyword matching.
        # In a real system, this would involve embedding the query and doing a similarity search.
        relevant_parent_ids: Set[str] = set()
        for chunk in self.child_chunks:
            if any(term in chunk.content.lower() for term in lower_query.split()):
                relevant_parent_ids.add(chunk.parent_doc_id)
        
        # Retrieve the full parent documents for the relevant chunks.
        retrieved_docs = [self.parent_documents[doc_id] for doc_id in relevant_parent_ids]
        return retrieved_docs

# This is the main execution block that runs the demonstration.
if __name__ == "__main__":
    # 11. Create mock data for laptop product descriptions.
    dell_xps_text = (
        "Introducing the new Dell XPS 15. It features a stunning 4K OLED display that brings your content to life. "
        "Under the hood, it's powered by the latest 13th Gen Intel Core i9 processor and 32GB of RAM. "
        "For storage, you get a super-fast 1TB NVMe SSD. The battery life is exceptional, lasting up to 10 hours on a single charge. "
        "Special holiday offer: save $300 on your purchase! The final price is only $2199."
    )

    macbook_pro_text = (
        "The MacBook Pro 16-inch is a creative powerhouse. Its Liquid Retina XDR display is the best ever in a notebook. "
        "It comes with the powerful M3 Pro chip, a 12-core CPU that handles demanding tasks with ease. "
        "With 36GB of unified memory, multitasking is seamless. This model has no current sale. "
        "The exceptional power efficiency delivers up to 22 hours of battery life. Starting price is NT$79,900."
    )
    
    # 12. Instantiate the chunker and the vector store.
    chunker = TopicBasedChunker()
    vector_store = SimpleVectorStore()

    # 13. Create ParentDocument objects.
    parent_docs = [
        ParentDocument(doc_id="dell-xps-15", content=dell_xps_text, metadata={"product_name": "Dell XPS 15"}),
        ParentDocument(doc_id="macbook-pro-16", content=macbook_pro_text, metadata={"product_name": "MacBook Pro 16-inch"})
    ]

    # 14. Process each document: chunk it and add both parent and children to the store.
    print("--- Indexing Documents ---")
    all_child_chunks = []
    for doc in parent_docs:
        chunks = chunker.chunk_document(doc)
        all_child_chunks.extend(chunks)
        print(f"Created {len(chunks)} child chunks for document: {doc.doc_id}")
        for chunk in chunks:
            print(f"  - Chunk {chunk.chunk_id} (Topic: {chunk.metadata['topic']}): '{chunk.content}'")

    vector_store.add_documents(parent_docs, all_child_chunks)
    print("\n--- Indexing Complete ---\n")

    # 15. Define a user query.
    # This query asks about "deals", which should match price-related child chunks.
    user_query = "are there any deals on high performance laptops?"
    
    # 16. Execute the retrieval process.
    print(f"--- Performing retrieval for query: '{user_query}' ---")
    retrieved_documents = vector_store.retrieve(user_query)
    
    # 17. Display the results.
    # The output should be the full parent document(s) that contained the relevant child chunk.
    print(f"\n--- Retrieval Results ---")
    if retrieved_documents:
        for doc in retrieved_documents:
            print(f"Found relevant document: {doc.metadata['product_name']} ({doc.doc_id})")
            print("Full Content:")
            print(f"'{doc.content}'")
    else:
        print("No relevant documents found.")

```

**Status: SUCCESSFUL**

所有計畫中的步驟都已完成，並且程式碼已成功實作。我現在可以進入 **REVIEW** 模式來驗證實作，或者如果您還有其他任務，我可以繼續執行。

請指示下一步操作。