import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.retriever import Retriever
from llm.ollama_client import OllamaClient
from rag_qa import RAG_QA

if __name__ == "__main__":
    retriever = Retriever(
        model_path="./models/all-MiniLM-L6-v2",
        faiss_path="./data/data_processed/eldenring_index.faiss",
        chunks_path="./data/data_processed/eldenring_chunks.json",
        top_k=3
    )

    llm = OllamaClient(model_name="qwen:4b")

    rag = RAG_QA(retriever,llm)

    q = "如何击败Boss碎星拉塔恩"

    ans = rag.answer(q)

    print("===== 最终答案 =====")
    print(ans)