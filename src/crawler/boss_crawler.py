import requests
import os

url = "https://eldenring.wiki.fextralife.com/Margit,+the+Fell+Omen"
response = requests.get(url)
html = response.text
save_path = "./data_raw/margit.html"
os.makedirs("./data_raw",exist_ok=True)

with open(save_path,"w",encoding="utf-8") as f:
    f.write(html)

print("HTML content get successfully and save to",save_path)