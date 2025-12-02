from bs4 import BeautifulSoup
import json

def extract_text(html_path:str,output_path:str):
    #html提取
    html_path = html_path
    with open(html_path,"r",encoding="utf-8") as f:
        html = f.read()
    print("HTML content read successfully Length is ",len(html))
    output_path = output_path

    #soup解析
    soup = BeautifulSoup(html,"lxml")
    content_divs = soup.select(".wiki-content, .mw-parser-output, #wiki-content")
    texts = []
    for div in content_divs:
        text = div.get_text("\n", strip=True)
        if len(text) > 50:
            texts.append(text)

    #fallback 抓取所有的<p>
    if not texts:
        ps = soup.find_all("p")
        for p in ps:
            t = p.get_text(strip=True)
            if len(t) > 30:
                texts.append(t)

    data = {"text": texts}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("✔ 提取完成，已保存到", output_path)

if __name__ == "__main__":
    html_path = "./data_raw/margit.html"
    output_path = "./data_clean/margit.json"
    extract_text()
