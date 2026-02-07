import requests
import xml.etree.ElementTree as ET
import json

url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
root = ET.fromstring(response.content)

news_list = []
for item in root.findall(".//item")[:10]: # 少し増やして10件にします
    news_list.append({
        "title": item.find("title").text,
        "url": item.find("link").text
    })

# news.json という名前で保存
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(news_list, f, ensure_ascii=False, indent=4)

print("news.json を作成しました！")
