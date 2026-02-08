import requests

url = "https://news.google.com/rss/articles/CBMiS0FVX3lxTE9oNjg1T1llbktCaC1fQlJ2VmEzbVE0cnVKTWtaQ0RZWUdsSEM2SkpsSXZpZG1RdXJkTU42TDd2SmxDV0xPQlRnT0JXVQ?oc=5"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

res = requests.get(url, headers=headers, timeout=10)
with open("google_response.html", "w", encoding="utf-8") as f:
    f.write(res.text)

print(f"ステータスコード: {res.status_code}")
print("google_response.html に中身を保存しました。Openコマンドで確認してください。")
