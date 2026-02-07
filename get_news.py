import requests
import xml.etree.ElementTree as ET

url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
root = ET.fromstring(response.content)

print("--- 永瀬廉 最新ニュース（リンク付き） ---")
for item in root.findall(".//item")[:5]:
    title = item.find("title").text
    link = item.find("link").text
    print(f"【表題】: {title}")
    print(f"【URL】: {link}\n")
