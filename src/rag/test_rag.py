import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.retriever import Retriever
from llm.ollama_client import OllamaClient
from rag_qa import RAG_QA

if __name__ == "__main__":
    retriever = Retriever(
        model_path="./models/all-MiniLM-L6-v2",
        faiss_path="./data_clean/margit_index.faiss",
        chunks_path="./data_clean/margit_chunks.json",
        top_k=5
    )

    llm = OllamaClient(model_name="qwen:4b")

    rag = RAG_QA(retriever,llm)

    q = "who is margit"

    ans = rag.answer(q)

    print("===== 最终答案 =====")
    print(ans)