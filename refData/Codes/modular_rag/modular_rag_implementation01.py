import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os

# --- 配置 ---
# 設定 Ollama LLM 模型名稱
LLM_MODEL = "deepseek-coder:v2.3-lite"

# 設定嵌入模型
EMBEDDING_MODEL = "deepseek-coder:v2.3-lite" # Ollama 也可以用於嵌入

# --- Streamlit 介面 ---
st.set_page_config(page_title="PDF RAG 聊天機器人", layout="wide")
st.title("📄 PDF RAG 聊天機器人 (Parent-Child Strategy)")
st.markdown("""
    使用 **Modular RAG** 技術和 **Parent-Child** 分塊策略，
    讓你可以上傳 PDF 檔案並使用離線的 `deepseek-coder:v2.3-lite` LLM 進行問答。
""")

# --- 初始化 Session 狀態 ---
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "llm_chain" not in st.session_state:
    st.session_state.llm_chain = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 顯示歷史訊息 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 側邊欄上傳 PDF ---
with st.sidebar:
    st.header("上傳你的 PDF 檔案")
    uploaded_file = st.file_uploader("選擇一個 PDF 檔案", type="pdf")

    if uploaded_file:
        st.success(f"檔案 '{uploaded_file.name}' 已上傳！")
        if st.button("處理 PDF"):
            with st.spinner("正在處理 PDF 檔案並建立知識庫...這可能需要一些時間。"):
                # 1. 載入 PDF
                temp_file_path = f"./temp_{uploaded_file.name}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                loader = PyPDFLoader(temp_file_path)
                docs = loader.load()

                # 2. 定義文本分塊器 (Parent-Child Strategy)
                # 子區塊分塊器 (用於嵌入和檢索)
                child_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=400, # 子區塊大小
                    chunk_overlap=50,
                    length_function=len,
                    is_separator_regex=False,
                )

                # 父區塊分塊器 (用於傳遞給 LLM)
                parent_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=2000, # 父區塊大小
                    chunk_overlap=200,
                    length_function=len,
                    is_separator_regex=False,
                )

                # 3. 初始化嵌入模型
                embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

                # 4. 初始化向量儲存和記憶體儲存
                vectorstore = FAISS.from_documents(docs, embeddings) # 這裡先用所有文件初始化，ParentDocumentRetriever 會處理子區塊
                
                # 記憶體儲存用於儲存父區塊
                store = InMemoryStore()

                # 5. 建立 ParentDocumentRetriever
                # 這個 retriever 會將子區塊儲存在 vectorstore 中，並將父區塊儲存在 store 中
                retriever = ParentDocumentRetriever(
                    vectorstore=vectorstore,
                    docstore=store,
                    child_splitter=child_splitter,
                    parent_splitter=parent_splitter,
                )
                # 將原始文件添加到 retriever 中，這會自動進行父子分塊並儲存
                retriever.add_documents(docs)

                st.session_state.retriever = retriever

                # 6. 初始化 LLM
                llm = Ollama(model=LLM_MODEL)

                # 7. 建立 RAG 鏈
                # 定義用於生成答案的提示模板
                prompt = ChatPromptTemplate.from_template("""
                你是一個有用的 AI 助手。請根據提供的上下文回答問題。
                如果問題無法從提供的上下文資訊中得到答案，請誠實地說你不知道。
                請保持答案簡潔明瞭。

                上下文:
                {context}

                問題: {input}
                """)

                # 建立文件合併鏈，將檢索到的文件組合成 LLM 的輸入
                document_chain = create_stuff_documents_chain(llm, prompt)

                # 建立檢索鏈，它將檢索相關文檔並將其傳遞給 document_chain
                retrieval_chain = create_retrieval_chain(st.session_state.retriever, document_chain)
                
                st.session_state.llm_chain = retrieval_chain

                # 移除臨時文件
                os.remove(temp_file_path)
                
                st.success("PDF 處理完成，您可以開始提問了！")
                st.info("請注意：第一次運行 Ollama 模型可能需要一些時間來載入。")
    else:
        st.session_state.retriever = None
        st.session_state.llm_chain = None
        st.session_state.messages = []
        st.warning("請上傳一個 PDF 檔案來開始。")

# --- 聊天輸入框 ---
if st.session_state.llm_chain:
    if prompt_input := st.chat_input("請輸入你的問題..."):
        st.session_state.messages.append({"role": "user", "content": prompt_input})
        with st.chat_message("user"):
            st.markdown(prompt_input)

        with st.chat_message("assistant"):
            with st.spinner("正在思考中..."):
                response = st.session_state.llm_chain.invoke({"input": prompt_input})
                assistant_response = response["answer"]
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
else:
    st.info("請先在側邊欄上傳並處理你的 PDF 檔案。")