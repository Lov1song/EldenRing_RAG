import faiss
import numpy as np
import os  # 新增
from base_processor import BaseProcessor

class FaissProcessor(BaseProcessor):
    def process(self, input_path: str, output_path: str, config=None) -> None:
        # 新增：检查输入文件
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"嵌入文件不存在：{input_path}")
        
        embeddings = np.load(input_path)
        if embeddings.size == 0:  # 新增：检查空嵌入
            raise ValueError("嵌入向量为空，无法构建索引")
        print(f"加载嵌入：{embeddings.shape}")
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        if index.ntotal == 0:  # 新增：检查索引是否为空
            raise RuntimeError("索引构建失败，未添加任何向量")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # 确保目录存在
        faiss.write_index(index, output_path)
        print(f"✔ FAISS索引构建完成，保存到 {output_path}（{index.ntotal}条向量）")