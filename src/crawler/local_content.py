from bs4 import BeautifulSoup

def extract_content(html):
    soup = BeautifulSoup(html, 'lxml')
    content_div = soup.find('div', class_='Mid2L_con')
    if not content_div:
        return ""
    
    text_tags = content_div.find_all('p')
    content = []
    # 定义需要过滤的关键词（非攻略内容）
    filter_keywords = [
        "领券购买", "招募启事", "交流群", "责任编辑", 
        "本文是否解决了您的问题", "二维码"
    ]
    
    for tag in text_tags:
        # 移除链接标签，保留文本
        for a_tag in tag.find_all('a'):
            a_tag.unwrap()
        text = tag.get_text(strip=True)
        # 过滤短文本和含广告关键词的内容
        if text and len(text) > 1 and not any(kw in text for kw in filter_keywords):
            content.append(text)
    
    return '\n'.join(content)

# 测试
with open('./data/debug_real_pages/page_1.html', 'r', encoding='utf-8') as f:
    html = f.read()
content = extract_content(html)
print(f"提取到的内容长度：{len(content)}字符")
print("提取到的内容：")
print(content)