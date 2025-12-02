import json
import re

def clean_text(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 处理新的 JSON 结构，提取每条帖子的 content
    raw = []
    for post in data:
        text = post.get("content", "").strip()
        if text:
            raw.append(text)

    cleaned = []
    skip_patterns = [
        r"Map link", r"Map Link", r"\[.*?\]", r"More Info",
        r"See also", r"negation numbers", r"resistance numbers",
        r"%", r"\/", r"\d+,\d+", r"Talisman", r"Medallion",
    ]

    for t in raw:
        t = t.strip()
        if not t:
            continue
        if t in cleaned:
            continue
        if any(re.search(p, t, flags=re.IGNORECASE) for p in skip_patterns):
            continue
        if len(t) < 10:
            continue
        cleaned.append(t)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"text": cleaned}, f, ensure_ascii=False, indent=4)

    print("✔ 清洗完成，输出到", output_path)

if __name__ == "__main__":
    input_path = "./data_clean/NGA/nga_posts.json"
    output_path = "./data_clean/NGA/NGA_clean.json"
    clean_text(input_path,output_path)