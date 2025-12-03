import os
from bs4 import BeautifulSoup
import re

# 配置
HTML_DIR = "./data/html_pages"  # 存放爬取的HTML文件夹
OUTPUT_DIR = "./data/extracted_text"  # 提取的正文存放文件夹

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

def batch_extract():
    """批量处理所有HTML文件"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 遍历所有HTML文件
    for filename in os.listdir(HTML_DIR):
        if filename.endswith(".html"):
            html_path = os.path.join(HTML_DIR, filename)
            page_num = filename.split("_")[-1].split(".")[0]  # 从page_1.html提取页码
            
            # 提取正文
            content = extract_main_content(html_path)
            if not content:
                print(f"警告：{filename}未提取到正文")
                continue
            
            # 保存结果
            output_path = os.path.join(OUTPUT_DIR, f"content_{page_num}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"已提取第{page_num}页正文到：{output_path}")

if __name__ == "__main__":
    batch_extract()