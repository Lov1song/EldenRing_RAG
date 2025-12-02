# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from readability import Document
import json
import time
import os

# ========================
# 配置
# ========================
BASE_URL = "https://ngabbs.com/thread.php?key=艾尔登法环&content=4"  # 替换你的 NGA 关键字和板块参数
HEADERS = {
    "User-Agent": "Mozilla/5.0 ...",
    "Cookie": "guestJs=1764662156_1xl2u3r; Hm_lvt_6933ef97905336bef84f9609785bcc3d=1764662163; HMACCOUNT=4871269F8CFF23EE; HM_tbj=jmkl29%7C1bs.u0; ngacn0comUserInfo=Ay10421%09Ay10421%0939%0939%09%0910%090%094%090%090%09; ngacn0comUserInfoCheck=b22fa32377d33ae39265cbd34a23033e; ngacn0comInfoCheckTime=1764662248; ngaPassportUid=67015871; ngaPassportUrlencodedUname=Ay10421; ngaPassportCid=X9v45qkpt1vv9g9nioo9b7t4p300pn6lis8qeklt; lastpath=/read.php?tid=44721614; lastvisit=1764663830; bbsmisccookies=%7B%22pv_count_for_insad%22%3A%7B0%3A-42%2C1%3A1764694860%7D%2C%22insad_views%22%3A%7B0%3A1%2C1%3A1764694860%7D%2C%22uisetting%22%3A%7B0%3A%22b%22%2C1%3A1764664130%7D%7D; Hm_lpvt_6933ef97905336bef84f9609785bcc3d=1764663830"
}
SAVE_DIR = "./data_clean/NGA"
MAX_PAGE = 10
DELAY = 1.0  # 每页抓取间隔

# ----------------------------
# 爬取函数
# ----------------------------
def fetch_page(url):
    """抓取网页内容"""
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "gbk"  # NGA 常用编码
    return resp.text

def extract_posts(html):
    """自动提取帖子正文"""
    soup = BeautifulSoup(html, "html.parser")
    posts = []

    # NGA 帖子列表每个帖子的链接
    for a in soup.select("a[href*='tid=']"):
        post_url = "https://ngabbs.com/" + a['href']
        # 去重
        if post_url in [p['url'] for p in posts]:
            continue
        posts.append({"url": post_url})
    return posts

def fetch_post_content(post_url):
    """抓取单个帖子正文"""
    html = fetch_page(post_url)
    doc = Document(html)
    title = doc.title()
    content_html = doc.summary()
    soup = BeautifulSoup(content_html, "html.parser")
    text = soup.get_text("\n").strip()
    return {"title": title, "content": text, "url": post_url}

# ========================
# 主流程
# ========================
all_posts = []

for page in range(1, MAX_PAGE + 1):
    print(f"[INFO] 抓取第 {page} 页...")
    url = BASE_URL.format(page)
    html = fetch_page(url)
    posts = extract_posts(html)

    print(f"[INFO] 第 {page} 页抓取 {len(posts)} 条帖子")
    for post in posts:
        try:
            data = fetch_post_content(post['url'])
            all_posts.append(data)
            time.sleep(1)  # 避免访问过快
        except Exception as e:
            print(f"[ERROR] 抓取 {post['url']} 失败: {e}")

# 保存结果
save_path = os.path.join(SAVE_DIR, "nga_posts.json")
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)

print(f"[INFO] 总共抓取 {len(all_posts)} 条帖子，已保存到 {save_path}")