import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retriever import Retriever
if __name__ == "__main__":
    retriever = Retriever(
        model_path="./models/all-MiniLM-L6-v2",
        faiss_path="./data_clean/margit_index.faiss",
        chunks_path="./data_clean/margit_chunks.json",
        top_k=5
    )
    print("==== Elden Ring RAG 检索 ====")
    # while True:
    q = input("\n输入问题： ")
    if q.strip() == "":
        exit()
    results = retriever.search(q)
    print("\n===== 检索结果 =====")
    for i, (idx, text, dist) in enumerate(results):
        print(f"{i+1}. [chunk {idx}]  score={dist:.4f}")
        print(text)
        print()
