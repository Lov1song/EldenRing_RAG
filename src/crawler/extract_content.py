import os
from bs4 import BeautifulSoup
import re
from datetime import datetime  # 新增：用于生成时间戳

# 配置
HTML_DIR = "./data/html_pages"  # 存放爬取的HTML文件夹（可改为具体时间戳文件夹路径，如 ./data/html_pages/20251203_153020）
OUTPUT_ROOT_DIR = "./data/extracted_text"  # 提取文本的根目录
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"  # 时间戳格式（和爬虫脚本一致）

def clean_text(text):
    """清洗文本：去除多余空白、特殊字符"""
    # 去除连续空白（换行、空格等）
    text = re.sub(r'\s+', ' ', text).strip()
    # 去除特殊符号（保留中文、英文、数字和基本标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9,.!?;:\'\"()（）《》<>]', ' ', text)
    return text

def extract_main_content(html_path):
    """从单页HTML中提取正文"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    # 定位正文容器（核心标签：class="Mid2L_con"）
    content_container = soup.find("div", class_="Mid2L_con")
    if not content_container:
        return ""
    
    # 移除无关元素（分页控件、广告、脚本等）
    for tag in content_container.find_all([
        "div", "script", "style", "iframe",  # 可能包含广告/控件的标签
        "a"  # 超链接（非正文内容）
    ]):
        # 保留<p>标签内的文本，但移除<a>链接本身
        if tag.name == "a":
            tag.extract()
        # 移除分页控件（<div class="post_ding_top">）
        elif tag.get("class") and "post_ding_top" in tag.get("class"):
            tag.extract()
        # 移除广告相关div（如包含"advert"等关键词）
        elif "advert" in tag.get("class", []) or "ad" in tag.get("id", ""):
            tag.extract()
    
    # 提取所有文本并清洗
    raw_text = content_container.get_text()
    cleaned_text = clean_text(raw_text)
    return cleaned_text

def batch_extract(target_html_dir=None, custom_timestamp=None):
    """
    批量处理所有HTML文件
    :param target_html_dir: 可选，指定要处理的HTML文件夹（如 ./data/html_pages/20251203_153020）
    :param custom_timestamp: 可选，自定义时间戳（用于关联爬取批次）
    """
    # 1. 确定要处理的HTML文件夹（默认用配置中的HTML_DIR）
    current_html_dir = target_html_dir or HTML_DIR
    if not os.path.exists(current_html_dir):
        print(f"错误：HTML文件夹不存在 → {current_html_dir}")
        return
    
    # 2. 生成时间戳（默认用当前时间，支持自定义关联爬取批次）
    timestamp = custom_timestamp or datetime.now().strftime(TIMESTAMP_FORMAT)
    
    # 3. 创建带时间戳的输出文件夹（根目录+时间戳子目录）
    output_timestamp_dir = os.path.join(OUTPUT_ROOT_DIR, timestamp)
    if not os.path.exists(output_timestamp_dir):
        os.makedirs(output_timestamp_dir)
    
    # 4. 遍历所有HTML文件
    html_files = [f for f in os.listdir(current_html_dir) if f.endswith(".html")]
    if not html_files:
        print(f"警告：{current_html_dir} 中没有找到HTML文件")
        return
    
    for filename in html_files:
        html_path = os.path.join(current_html_dir, filename)
        page_num = filename.split("_")[-1].split(".")[0]  # 从page_1.html提取页码
        
        # 提取正文
        content = extract_main_content(html_path)
        if not content:
            print(f"警告：{filename} 未提取到正文")
            continue
        
        # 5. 保存到带时间戳的文件夹中
        output_path = os.path.join(output_timestamp_dir, f"content_{page_num}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"已提取 → 第{page_num}页 → {output_path}")
    
    # 6. 额外：生成合并后的总文本文件（方便后续RAG流水线直接使用）
    merged_content = ""
    for filename in sorted(html_files, key=lambda x: int(x.split("_")[-1].split(".")[0])):
        html_path = os.path.join(current_html_dir, filename)
        content = extract_main_content(html_path)
        if content:
            merged_content += content + "\n\n"  # 每页文本用两个换行分隔
    
    merged_output_path = os.path.join(output_timestamp_dir, "merged_all.txt")
    with open(merged_output_path, "w", encoding="utf-8") as f:
        f.write(merged_content.strip())
    print(f"\n✅ 所有页面提取完成！合并文件保存到 → {merged_output_path}")
    print(f"📁 提取的文本总目录 → {output_timestamp_dir}")

if __name__ == "__main__":
    # 例如：处理20251203_153020批次的爬取结果，提取后的文本也用同一个时间戳
    target_html_dir = "./data/html_pages/20251203_155633"  # 替换为你的爬取批次文件夹路径
    custom_timestamp = "20251203_155633"  # 和爬取批次的时间戳一致
    batch_extract(target_html_dir=target_html_dir, custom_timestamp=custom_timestamp)