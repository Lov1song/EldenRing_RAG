import faiss
import numpy as np
from embedding_text import encode
import json

def build_faiss(emb_path:str,out_path:str):
    embeddings = np.load(emb_path)
    print(embeddings.shape)

    # 创建 FAISS 索引
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print(f"✔ 已创建 FAISS 索引，包含 {index.ntotal} 条向量")
    faiss.write_index(index, out_path)
    print("✔ FAISS 索引已保存")

if __name__ == "__main__":
    emb_path = "./embeddings/margit_embeddings.npy"
    out_path = "./data_clean/margit_index.faiss"
    build_faiss(emb_path,out_path)