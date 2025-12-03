import json
import re
import os  # 新增
from base_processor import BaseProcessor

class ChunkProcessor(BaseProcessor):
    def process(self, input_path: str, output_path: str, config = None) -> None:
        default_config = {
            "chunk_size": 300,
            "overlap": 50,
            "split_pattern": r'(?<=[.!?])\s+'
        }
        config = {** default_config, **(config or {})}
        
        # 新增：检查输入文件
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在：{input_path}")
        
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        texts = data.get("text", [])
        if not texts:
            print("⚠ 未读取到有效文本，跳过分块")
            return
        
        chunks = []
        for text in texts:
            sentences = re.split(config["split_pattern"], text.strip())
            buffer = ""
            for sent in sentences:
                # 新增：处理单句超长
                if len(sent) > config["chunk_size"]:
                    # 按chunk_size拆分超长句
                    for i in range(0, len(sent), config["chunk_size"]):
                        sub_sent = sent[i:i+config["chunk_size"]]
                        chunks.append(sub_sent)
                    continue  # 跳过后续buffer逻辑
                
                if len(buffer) + len(sent) <= config["chunk_size"]:
                    buffer += " " + sent if buffer else sent
                else:
                    chunks.append(buffer)
                    buffer = buffer[-config["overlap"]:] + sent if config["overlap"] > 0 else sent
            if buffer:
                chunks.append(buffer)
        
        # 新增：去重（避免重复chunk）
        chunks = list(dict.fromkeys(chunks))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # 确保目录存在
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"text": chunks}, f, ensure_ascii=False, indent=4)
        
        print(f"✔ 分块完成，保存到 {output_path}（{len(chunks)}个chunk）")