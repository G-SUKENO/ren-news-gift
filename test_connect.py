import requests

# ターゲット：Googleニュースの「永瀬廉」RSSフィード（安定性抜群）
url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("接続成功！Googleニュースから情報を取得できました。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
