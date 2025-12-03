import os

# 配置
INPUT_DIR = "./data/extracted_text"  # 存放提取的正文文件夹
OUTPUT_FILE = "./data/merged_content.txt"  # 合并后的文件

def merge_texts():
    # 读取所有txt文件，按页码排序（确保顺序正确）
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.startswith("content_") and f.endswith(".txt")]
    # 按页码排序（如content_1.txt < content_2.txt）
    txt_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    
    # 合并内容
    merged_content = []
    for idx, filename in enumerate(txt_files, 1):
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                # 可选：添加分页标记，便于后续追溯来源
                merged_content.append(f"=== 第{idx}页内容 ===\n{content}\n")
    
    # 保存合并结果
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(merged_content))
    
    print(f"合并完成，共{len(txt_files)}个文件，保存至：{OUTPUT_FILE}")

if __name__ == "__main__":
    merge_texts()