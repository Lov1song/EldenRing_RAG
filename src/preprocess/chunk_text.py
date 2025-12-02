import json
import re

def chunk_text(input_path:str,output_path:str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = data["text"]
    chunk_size = 300  # 每个 chunk 最大字符数
    overlap = 50      # 重叠字符数
    chunks = []
    for t in texts:
        # 按句子切分，保留标点
        sentences = re.split(r'(?<=[.!?])\s+', t.strip())
        buffer = ""
        for sent in sentences:
            if len(buffer) + len(sent) <= chunk_size:
                buffer += " " + sent if buffer else sent
            else:
                # 保存当前 chunk
                chunks.append(buffer)
                # 保留重叠部分
                buffer = buffer[-overlap:] + sent if overlap > 0 else sent
        if buffer:
            chunks.append(buffer)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"text": chunks}, f, ensure_ascii=False, indent=4)

    print(f"✔ 分段完成，共 {len(chunks)} 个 chunk，已保存到 {output_path}")

if __name__ == "__main__":
    input_path = "./data_clean/NGA/NGA_cleaned.json"
    output_path = "./data_clean/NGA/NGA_chunks.json"




