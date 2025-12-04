import os
from datetime import datetime  # 用于生成/处理时间戳

# 配置（核心修改：输出目录改为 merged_content 文件夹）
EXTRACTED_ROOT_DIR = "./data/extracted_text"  # 提取文本的根目录（包含所有时间戳子文件夹）
OUTPUT_ROOT_DIR = "./data/merged_content"  # 新建的合并文件存放文件夹
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"  # 时间戳格式（和之前脚本一致）

def merge_texts(target_timestamp=None, custom_output_name=None):
    """
    合并指定时间戳文件夹下的文本，或合并最新批次的文本
    :param target_timestamp: 可选，指定要合并的时间戳（如 "20251203_153020"）
    :param custom_output_name: 可选，自定义输出文件名（不包含后缀）
    """
    # 新增：确保 merged_content 文件夹存在（不存在则自动创建）
    if not os.path.exists(OUTPUT_ROOT_DIR):
        os.makedirs(OUTPUT_ROOT_DIR)
        print(f"✅ 已创建合并文件存放文件夹：{OUTPUT_ROOT_DIR}")
    
    # 1. 确定要合并的目标文件夹
    if target_timestamp:
        # 方式1：指定时间戳文件夹（如 ./data/extracted_text/20251203_153020）
        target_dir = os.path.join(EXTRACTED_ROOT_DIR, target_timestamp)
        if not os.path.exists(target_dir):
            print(f"错误：指定的时间戳文件夹不存在 → {target_dir}")
            return
    else:
        # 方式2：默认合并最新的批次（按文件夹创建时间排序）
        all_timestamp_dirs = [d for d in os.listdir(EXTRACTED_ROOT_DIR) 
                            if os.path.isdir(os.path.join(EXTRACTED_ROOT_DIR, d)) 
                            and len(d) == 14  # 匹配时间戳格式（14位：20251203_153020）
                            and "_" in d]
        if not all_timestamp_dirs:
            print(f"错误：{EXTRACTED_ROOT_DIR} 中没有找到时间戳文件夹")
            return
        # 按文件夹创建时间倒序排序，取最新的一个
        all_timestamp_dirs.sort(key=lambda x: os.path.getctime(os.path.join(EXTRACTED_ROOT_DIR, x)), reverse=True)
        target_timestamp = all_timestamp_dirs[0]
        target_dir = os.path.join(EXTRACTED_ROOT_DIR, target_timestamp)
        print(f"未指定时间戳，自动合并最新批次 → {target_timestamp}")
    
    # 2. 读取目标文件夹下的所有content_*.txt文件，按页码排序
    txt_files = [f for f in os.listdir(target_dir) if f.startswith("content_") and f.endswith(".txt")]
    if not txt_files:
        print(f"错误：{target_dir} 中没有找到content_*.txt文件")
        return
    # 按页码排序（确保和原攻略顺序一致）
    txt_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    
    # 3. 合并内容（保留分页标记，便于追溯）
    merged_content = []
    for idx, filename in enumerate(txt_files, 1):
        file_path = os.path.join(target_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                merged_content.append(f"=== 第{idx}页内容 ===\n{content}\n")
    
    # 4. 确定输出文件名和路径（核心：输出到 merged_content 文件夹）
    if custom_output_name:
        output_filename = f"{custom_output_name}.txt"
    else:
        # 输出文件名带时间戳（如 merged_content_20251203_153020.txt）
        output_filename = f"merged_content_{target_timestamp}.txt"
    output_path = os.path.join(OUTPUT_ROOT_DIR, output_filename)  # 输出路径指向新文件夹
    
    # 5. 保存合并结果
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(merged_content))
    
    print(f"\n✅ 合并完成！")
    print(f"📁 合并来源：{target_dir}")
    print(f"📄 合并文件：{output_path}")
    print(f"📊 合并统计：共{len(txt_files)}个文件，合计{len(''.join(merged_content)):,}个字符")

if __name__ == "__main__":
    # 三种使用方式，按需选择（注释掉不需要的）
    
    # 方式1：指定时间戳合并（推荐，精准关联批次）
    merge_texts(target_timestamp="20251203_102211")
    
    # 方式2：默认合并最新批次（快速使用）
    # merge_texts()
