import os
from datetime import datetime

# 配置
MERGED_DIR = "./data/merged_content"  # 存放批次合并文件的文件夹
FINAL_OUTPUT_FILE = "./data/final_data/final_merged_all.txt"  # 最终统一输出文件
EXCLUDE_FILES = ["final_merged_all.txt"]  # 排除最终文件本身，避免重复合并

def merge_to_final_txt():
    # 1. 验证文件夹是否存在
    if not os.path.exists(MERGED_DIR):
        print(f"错误：{MERGED_DIR} 文件夹不存在，请先执行批次合并脚本")
        return
    
    # 2. 读取文件夹下所有txt文件（排除最终文件）
    txt_files = [f for f in os.listdir(MERGED_DIR) 
                if f.endswith(".txt") and f not in EXCLUDE_FILES]
    if not txt_files:
        print(f"错误：{MERGED_DIR} 中没有找到可合并的txt文件（排除了最终文件）")
        return
    
    # 3. 按文件创建时间排序（确保先合并旧批次，后合并新批次，顺序合理）
    txt_files.sort(key=lambda x: os.path.getctime(os.path.join(MERGED_DIR, x)))
    
    # 4. 合并所有文件内容
    final_content = []
    for idx, filename in enumerate(txt_files, 1):
        file_path = os.path.join(MERGED_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                # 添加批次标记（便于后续追溯来源）
                batch_name = filename.replace("merged_content_", "").replace(".txt", "")
                final_content.append(f"===== 批次 {idx}（时间戳：{batch_name}）=====\n{content}\n")
                print(f"已读取：{filename}（字符数：{len(content):,}）")
    
    # 5. 保存最终合并结果
    with open(FINAL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_content).strip())
    
    # 6. 输出统计信息
    total_files = len(txt_files)
    total_chars = len("".join(final_content))
    print(f"\n🎉 最终合并完成！")
    print(f"📊 统计：共合并 {total_files} 个批次文件，合计 {total_chars:,} 个字符")
    print(f"📄 最终文件路径：{FINAL_OUTPUT_FILE}")

if __name__ == "__main__":
    merge_to_final_txt()