import os
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from utils import get_config, get_pickle
from text_segmentation import TextSegmentation


class KeypoRAGBot:

    def __init__(self, filename):
        os.makedirs("configs", exist_ok=True)
        self.filename = filename
        self.rag_filename = f"configs/{self.filename.split('.')[0]}.pkl"
        self.faiss_path = "configs/keypo_index.faiss"
        self.embeddings = OpenAIEmbeddings(openai_api_key=get_config("configs/llm_config.yml")["OpenAI"]["api_key"])
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        self.prompts = get_config("configs/prompts.yml")
        self.llm_model = get_config("configs/llm_config.yml")["OpenAI"]["model"]
        self.client = OpenAI(api_key=get_config("configs/llm_config.yml")["OpenAI"]["api_key"])

    def make_text_segmentation(self):
        if os.path.exists(self.rag_filename):
            return
        ts = TextSegmentation(filename=self.filename, save_file=True)
        ts.make_segmentation()
        print(f"完成 {self.filename} 文件處理，新增 {self.rag_filename} 作 RAG 使用。")

    def make_vector_embedding(self):
        if os.path.exists(self.faiss_path):
            return
        documents = get_pickle(self.rag_filename)
        docs = [Document(page_content=text) for text in self.text_splitter.split_text("\n".join(documents))]
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(self.faiss_path)
        print(f"完成建立 FAISS 向量資料庫，並新增檔案 {self.faiss_path}。")

    def rag_information(self, query, top_k=3):
        vectorstore = FAISS.load_local(self.faiss_path, self.embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        relevant_docs = retriever.invoke(query)
        return [doc.page_content for doc in relevant_docs]

    def answer(self, query):

        self.make_text_segmentation()
        self.make_vector_embedding()
        
        context = "\n".join(self.rag_information(query))
        fully_prompt = self.prompts["RAG"].replace("QUERY", query).replace("CONTEXT", context)

        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "user", "content": fully_prompt}
            ],
            temperature=0.4,
        )

        text = response.choices[0].message.content

        return {"text": text}