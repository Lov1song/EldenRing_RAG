import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin
from datetime import datetime  # 新增：用于生成时间戳

# 基础配置
BASE_URL = "https://www.gamersky.com/handbook/202203/1463764.shtml"
SAVE_DIR = "./data/html_pages"  # 主目录
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
RETRY_TIMES = 5  # 增加重试次数
VISITED_URLS = set()

def get_next_page_url(current_url):
    """通过URL规律生成下一页链接（核心修正）"""
    # 第一页URL：https://www.gamersky.com/handbook/202202/1461277.shtml
    # 第二页规律：https://www.gamersky.com/handbook/202202/1461277_2.shtml
    if "_" in current_url:
        # 从"1461277_2.shtml"中提取数字2并+1
        prefix, page_part = current_url.split("_")
        current_num = int(page_part.split(".shtml")[0])
        next_num = current_num + 1
        return f"{prefix}_{next_num}.shtml"
    else:
        # 第一页转第二页
        return current_url.replace(".shtml", "_2.shtml")

def is_valid_page(url):
    """验证生成的下一页URL是否有效（状态码200）"""
    try:
        response = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def crawl_page(url):
    if url in VISITED_URLS:
        return None
    for _ in range(RETRY_TIMES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.encoding = "utf-8"
            if response.status_code == 200:
                VISITED_URLS.add(url)
                return response.text
            else:
                print(f"页面{url}无效，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"页面{url}爬取失败（重试中）：{str(e)}")
            time.sleep(1)
    print(f"页面{url}超过最大重试次数，放弃")
    return None

def main():
    # 1. 生成时间戳（格式：年月日_时分秒，例如 20251203_153020）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 2. 创建带时间戳的文件夹（主目录/SAVE_DIR + 时间戳子目录）
    timestamp_dir = os.path.join(SAVE_DIR, timestamp)  # 完整路径：./data/html_pages/20251203_153020
    if not os.path.exists(timestamp_dir):
        os.makedirs(timestamp_dir)  # 递归创建主目录和子目录（如果主目录不存在也会自动创建）
    
    current_url = BASE_URL
    page_num = 1
    
    while current_url:
        print(f"爬取第{page_num}页：{current_url}")
        html = crawl_page(current_url)
        if not html:
            print(f"第{page_num}页无效，终止流程")
            break
        
        # 3. 保存路径修改为：带时间戳的文件夹/page_xxx.html
        save_path = os.path.join(timestamp_dir, f"page_{page_num}.html")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"已保存第{page_num}页到：{save_path}")
        
        # 生成下一页URL并验证
        next_url = get_next_page_url(current_url)
        # 验证下一页是否有效（防止越界）
        if next_url and is_valid_page(next_url) and next_url not in VISITED_URLS:
            current_url = next_url
        else:
            current_url = None  # 无有效下一页
        
        page_num += 1
        time.sleep(2)  # 延长间隔，避免反爬
    
    print(f"爬取结束，共获取{page_num - 1}页内容，保存路径：{timestamp_dir}")

if __name__ == "__main__":
    main()