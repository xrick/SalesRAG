import os
import re
import duckdb
import pandas as pd
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

# --- 設定 ---
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
DUCKDB_FILE = "sales_rag_app/db/sales_specs.db"
COLLECTION_NAME = "sales_notebook_specs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DATA_DIR = "data"

# --- 文本解析函數 ---
def parse_spec_file(file_path):
    """解析 .txt 規格檔案，提取鍵值對"""
    specs = {}
    current_section = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            section_match = re.match(r'^\[(.*)\]$', line)
            if section_match:
                current_section = section_match.group(1)
                specs[current_section] = {}
            elif ':' in line and current_section:
                key, value = map(str.strip, line.split(':', 1))
                if key in specs[current_section]:
                    # 處理重複的鍵，例如 Options
                    if isinstance(specs[current_section][key], list):
                        specs[current_section][key].append(value)
                    else:
                        specs[current_section][key] = [specs[current_section][key], value]
                else:
                    specs[current_section][key] = value
    return specs

def specs_to_dataframe(specs, model_name):
    """將解析後的規格轉換為 DataFrame"""
    records = []
    for section, details in specs.items():
        if isinstance(details, dict):
            for feature, value in details.items():
                # 將列表值轉換為字串
                value_str = ", ".join(value) if isinstance(value, list) else value
                records.append([model_name, section, feature, value_str])
    return pd.DataFrame(records, columns=['model_name', 'section', 'feature', 'value'])

# --- 主執行流程 ---
def main():
    # --- 1. 處理結構化資料 (DuckDB) ---
    print("--- 正在處理結構化規格資料並存入 DuckDB ---")
    if os.path.exists(DUCKDB_FILE):
        os.remove(DUCKDB_FILE)

    con = duckdb.connect(database=DUCKDB_FILE, read_only=False)

    ag958_specs = parse_spec_file(os.path.join(DATA_DIR, "AG958.txt"))
    akk839_specs = parse_spec_file(os.path.join(DATA_DIR, "AKK839.txt"))

    df_ag958 = specs_to_dataframe(ag958_specs, "AG958")
    df_akk839 = specs_to_dataframe(akk839_specs, "AKK839")

    df_total = pd.concat([df_ag958, df_akk839], ignore_index=True)

    con.execute("CREATE TABLE specs AS SELECT * FROM df_total")
    print(f"成功將 {len(df_total)} 筆規格資料存入 DuckDB。")
    con.close()

    # --- 2. 處理非結構化資料 (Milvus) ---
    print("\n--- 正在處理文本資料並存入 Milvus ---")
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

    if utility.has_collection(COLLECTION_NAME):
        print(f"找到舊的 Collection '{COLLECTION_NAME}'，正在刪除...")
        utility.drop_collection(COLLECTION_NAME)

    # 定義 Collection Schema
    fields = [
        FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
    ]
    schema = CollectionSchema(fields, "銷售筆電規格知識庫")
    collection = Collection(COLLECTION_NAME, schema)

    # 讀取所有文件
    all_docs = []
    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 使用 LangChain 的 TextSplitter
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = text_splitter.split_text(content)
            for i, chunk in enumerate(chunks):
                all_docs.append({
                    "pk": f"{filename}_{i}",
                    "text": chunk,
                    "source": filename
                })

    print(f"共讀取並分割成 {len(all_docs)} 個文本區塊。")

    # 產生嵌入向量
    print("正在產生嵌入向量...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    texts_to_embed = [doc['text'] for doc in all_docs]
    vectors = embeddings.embed_documents(texts_to_embed)

    # 準備插入 Milvus 的資料
    entities = [
        [doc['pk'] for doc in all_docs],
        [doc['text'] for doc in all_docs],
        [doc['source'] for doc in all_docs],
        vectors
    ]

    # 插入資料
    print("正在將資料插入 Milvus...")
    collection.insert(entities)
    collection.flush()

    # 創建索引
    print("正在為向量創建索引 (IVF_FLAT)...")
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index("embedding", index_params)
    collection.load()

    print(f"成功將 {len(all_docs)} 筆資料導入 Milvus Collection '{COLLECTION_NAME}'。")
    print("\n資料導入完成！")

if __name__ == "__main__":
    main()