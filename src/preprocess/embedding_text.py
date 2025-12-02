import torch
from transformers import AutoTokenizer, AutoModel
import json
import numpy as np
def encode(model,tokenizer,texts, batch_size=32):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        encoded_input = tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model(**encoded_input)
        # mean pooling
        embeddings = model_output.last_hidden_state.mean(dim=1)
        # L2 normalize
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        all_embeddings.append(embeddings)
    return torch.cat(all_embeddings)

def build_embeddings(model,tokenizer,chunk_path:str,output_path:str):
    with open(chunk_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = data["text"]  
    embeddings = encode(model,tokenizer,texts,batch_size=32)
    np.save(output_path, embeddings.cpu().numpy())
    print(f"✔ 已生成 {len(texts)} 条 embeddings，保存到",output_path)

if __name__ == "__main__":
    model_path = "./models/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)
    chunk_path = "./data_clean/NGA/NGA_chunks.json"
    output_path = "./data_clean/NGA/NGA_embeddings.npy"
    build_embeddings(model,tokenizer,chunk_path,output_path)



