import torch
import json
import numpy as np
import os  # 新增：用于路径检查
from transformers import AutoTokenizer, AutoModel
from base_processor import BaseProcessor

def encode(model, tokenizer, texts, batch_size=32):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        encoded_input = tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model(** encoded_input)
        embeddings = model_output.last_hidden_state.mean(dim=1)
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        all_embeddings.append(embeddings)
    return torch.cat(all_embeddings)

class EmbeddingProcessor(BaseProcessor):
    def __init__(self):
        self.tokenizer = None
        self.model = None
    
    def _load_model(self, model_path: str):
        """延迟加载模型，添加路径校验"""
        if not os.path.exists(model_path):  # 新增：路径检查
            raise FileNotFoundError(f"模型路径不存在：{model_path}，请检查配置")
        if not self.tokenizer or not self.model:
            try:  # 新增：捕获加载异常
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModel.from_pretrained(model_path)
                print(f"✅ 加载本地模型成功：{model_path}")
            except Exception as e:
                raise RuntimeError(f"模型加载失败：{str(e)}")
    
    def process(self, input_path: str, output_path: str, config: dict = None):
        default_config = {
            "model_path": "./models/all-MiniLM-L6-v2",
            "batch_size": 32
        }
        config = {** default_config, **(config or {})}
        
        self._load_model(config["model_path"])
        
        # 新增：检查输入文件存在性
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在：{input_path}")
        
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        texts = data["text"]
        if not texts:
            print("⚠ 未读取到有效文本，跳过embedding生成")
            return
        print(f"📄 读取到 {len(texts)} 条分块文本")
        
        embeddings = encode(self.model, self.tokenizer, texts, batch_size=config["batch_size"])
        
        # 新增：确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        np.save(output_path, embeddings.cpu().numpy())
        print(f"✔ Embedding生成完成！共 {len(texts)} 条向量，保存到：{output_path}")