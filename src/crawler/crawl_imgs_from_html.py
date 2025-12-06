# src/crawl/crawl_imgs_from_html.py
import os
import re
import requests
import json
from bs4 import BeautifulSoup
from PIL import Image
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

# ===================== 核心配置（修复有效图片误判）=====================
HTML_ROOT_DIR = getattr(config, "HTML_ROOT_DIR", "./data/html_pages")
IMG_SAVE_ROOT = getattr(config, "IMG_ROOT_DIR", "./data/game_images")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.gamersky.com/"  # 关键：模拟游民星空referer，避免403
}
RETRY_TIMES = 3
# 仅过滤真正的广告域名（排除img1.gamersky.com）
INVALID_IMG_DOMAINS = ["ad.gamersky.com", "banner.gamersky.com", "logo.gamersky.com"]
# 广告关键词（其他游戏/无关内容）
AD_KEYWORDS = ["SILKSONG", "原神", "王者荣耀", "和平精英", "手游", "端游", "新游"]
# 艾尔登法环专属关键词（文字+URL路径特征）
ELDENRING_KEYWORDS = [
    # 文字特征
    "eldenring", "艾尔登法环", "艾尔登", "Elden Ring", "交界地", "黄金树", "梅琳娜",
    # URL路径特征（从你的有效URL提取，关键修复）
    "image2022/02", "20220224_ax_156_1", "ax_156_1"
]
VALID_IMG_EXT = ["jpg", "jpeg", "png", "gif"]
MIN_IMG_SIZE = 1024  # 1KB（过滤极小广告图）
MIN_IMG_DIMENSION = 300  # 宽/高≥300px（过滤小广告）

# ===================== 工具函数 =====================
def complete_url(relative_url, base_url="https://www.gamersky.com"):
    """补全URL，适配img1.gamersky.com的路径"""
    if not relative_url:
        return ""
    if relative_url.startswith("http"):
        return relative_url
    elif relative_url.startswith("//"):
        return "https:" + relative_url
    elif relative_url.startswith("/"):
        return base_url + relative_url
    else:
        return base_url + "/" + relative_url

def is_valid_img(img_url):
    """修复误判：检查广告+艾尔登特征（文字/路径）"""
    if not img_url:
        return False
    # 1. 过滤广告域名
    if any(domain in img_url for domain in INVALID_IMG_DOMAINS):
        return False
    # 2. 过滤其他游戏广告
    if any(kw in img_url for kw in AD_KEYWORDS):
        return False
    # 3. 匹配艾尔登法环的文字或URL路径特征
    for kw in ELDENRING_KEYWORDS:
        if kw in img_url:
            return True
    return False

def is_valid_img_dimension(img_path):
    """过滤小尺寸广告图"""
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            return width >= MIN_IMG_DIMENSION or height >= MIN_IMG_DIMENSION
    except Exception as e:
        print(f"⚠️ 检查尺寸失败（{img_path}）：{e}")
        return False

# ===================== 单张HTML图片提取 =====================
def crawl_imgs_from_single_html(html_path, img_save_dir, page_num):
    # 读取HTML
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 读取HTML失败：{e}")
        return []

    # 解析img标签（优先data-src，适配懒加载）
    soup = BeautifulSoup(html_content, "html.parser")
    img_tags = soup.find_all("img")
    print(f"🔍 提取到{len(img_tags)}个img标签")

    img_urls = []
    for idx, img_tag in enumerate(img_tags):
        # 优先取懒加载属性，再取src
        img_url = img_tag.get("data-src") or img_tag.get("src") or img_tag.get("data-original")
        if img_url:
            full_url = complete_url(img_url)
            if is_valid_img(full_url):
                img_urls.append(full_url)
                print(f"   ✅ 有效URL {idx+1}：{full_url}（含艾尔登特征）")
            else:
                print(f"   ❌ 过滤URL {idx+1}：{full_url}（无艾尔登特征/广告）")
        else:
            print(f"   ❌ 无效标签 {idx+1}：无src/data-src属性")

    if not img_urls:
        print(f"⚠️ 无有效艾尔登法环图片")
        return []

    # 下载图片（带重试+尺寸过滤）
    downloaded_imgs = []
    for img_idx, img_url in enumerate(img_urls, 1):
        # 生成文件名（page_页码_序号.后缀）
        img_ext = img_url.split(".")[-1].lower() if "." in img_url else "jpg"
        if img_ext not in VALID_IMG_EXT:
            img_ext = "jpg"
        img_filename = f"page_{page_num}_{img_idx}.{img_ext}"
        img_save_path = os.path.join(img_save_dir, img_filename)

        # 避免重复下载
        if os.path.exists(img_save_path):
            if is_valid_img_dimension(img_save_path):
                print(f"ℹ️ 已存在有效图片，跳过：{img_filename}")
                downloaded_imgs.append({"filename": img_filename, "path": img_save_path})
            else:
                print(f"ℹ️ 已存在但尺寸过小，删除：{img_filename}")
                os.remove(img_save_path)
            continue

        # 下载重试逻辑
        success = False
        for retry in range(RETRY_TIMES):
            try:
                response = requests.get(img_url, headers=HEADERS, timeout=15, stream=True)
                if response.status_code == 200:
                    img_size = len(response.content)
                    # 过滤极小文件
                    if img_size < MIN_IMG_SIZE:
                        print(f"⚠️ 文件过小（{img_size}B），跳过：{img_url}")
                        break
                    # 保存图片
                    with open(img_save_path, "wb") as f:
                        f.write(response.content)
                    # 二次过滤尺寸
                    if is_valid_img_dimension(img_save_path):
                        print(f"✅ 下载成功：{img_filename}（{img_size/1024:.2f}KB，尺寸合规）")
                        downloaded_imgs.append({"filename": img_filename, "path": img_save_path})
                    else:
                        print(f"⚠️ 尺寸过小（<{MIN_IMG_DIMENSION}px），删除：{img_filename}")
                        os.remove(img_save_path)
                    success = True
                    break
                else:
                    print(f"⚠️ 状态码{response.status_code}，重试{retry+1}/{RETRY_TIMES}")
            except Exception as e:
                print(f"⚠️ 下载异常（{e}），重试{retry+1}/{RETRY_TIMES}")

        if not success:
            print(f"❌ 下载失败（超过重试次数）：{img_url}")

    return downloaded_imgs

# ===================== 批量处理 =====================
def batch_crawl_imgs_by_timestamp(target_timestamp=None):
    # 确认HTML目录
    if not os.path.exists(HTML_ROOT_DIR):
        print(f"❌ HTML根目录不存在：{HTML_ROOT_DIR}")
        return

    # 选择目标批次（指定/最新）
    all_timestamps = [d for d in os.listdir(HTML_ROOT_DIR) if os.path.isdir(os.path.join(HTML_ROOT_DIR, d))]
    if not all_timestamps:
        print(f"❌ 无时间戳批次目录")
        return

    if target_timestamp and target_timestamp in all_timestamps:
        html_batch_dir = os.path.join(HTML_ROOT_DIR, target_timestamp)
    else:
        all_timestamps.sort(reverse=True)
        target_timestamp = all_timestamps[0]
        html_batch_dir = os.path.join(HTML_ROOT_DIR, target_timestamp)
    print(f"📌 开始处理批次：{target_timestamp}")
    print(f"🔍 HTML目录：{html_batch_dir}")

    # 创建图片保存目录
    img_batch_dir = os.path.join(IMG_SAVE_ROOT, target_timestamp)
    os.makedirs(img_batch_dir, exist_ok=True)
    print(f"📁 图片保存目录：{img_batch_dir}")

    # 遍历HTML文件（按页码排序）
    html_files = [f for f in os.listdir(html_batch_dir) if f.startswith("page_") and f.endswith(".html")]
    if not html_files:
        print(f"❌ 无page_*.html文件")
        return
    html_files.sort(key=lambda x: int(re.findall(r"page_(\d+)\.html", x)[0]))

    # 测试模式：先处理前3个HTML（快速验证）
    test_html_files = html_files
    print(f"\n⚠️ 测试模式：处理前{len(test_html_files)}个HTML（验证有效图片）")

    total_downloaded = 0
    for html_file in test_html_files:
        page_num = re.findall(r"page_(\d+)\.html", html_file)[0]
        html_path = os.path.join(html_batch_dir, html_file)
        print(f"\n===== 处理第{page_num}页：{html_file} =====")
        
        # 提取并下载图片
        page_imgs = crawl_imgs_from_single_html(html_path, img_batch_dir, page_num)
        total_downloaded += len(page_imgs)

    # 最终统计
    print(f"\n🎉 批次处理完成！")
    print(f"📊 统计：处理{len(test_html_files)}个HTML，下载{total_downloaded}张有效游戏图")
    print(f"🗂️  图片目录：{img_batch_dir}")
    print(f"\n💡 提示：若需处理全部HTML，删除'test_html_files = html_files[:3]'即可")

if __name__ == "__main__":
    # 替换为你的实际批次时间戳（如"20251203_151414"）
    batch_crawl_imgs_by_timestamp(target_timestamp="20251203_155633")