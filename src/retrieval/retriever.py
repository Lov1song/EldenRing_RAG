import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import faiss
import json
import torch
from embedding.local_embedding import LocalEmbedding



class Retriever:
    def __init__(self,model_path:str="",faiss_path:str="",chunks_path:str="",top_k:int=5):
        self.topk = top_k
        self.encoder = LocalEmbedding(model_path)
        self.index = faiss.read_index(faiss_path)
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)['text']

    def search(self,query):
        query_emb = self.encoder.encode([query]).numpy()
        D, I = self.index.search(query_emb, self.topk)
        results = []
        for dist,idx in zip(D[0],I[0]):
            idx = int(idx)
            text = self.chunks[idx]
            results.append((idx,text,float(dist)))

        return results
    
    

