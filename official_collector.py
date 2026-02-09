import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def collect():
    print("📡 Universal Musicを攻略中...")
    items = []
    seen_titles = set()
    base_url = "https://www.universal-music.co.jp/king-and-prince/news/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    today = datetime.now()

    # 過去60日分スキャンして、新しい順に12件拾う
    for i in range(60):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"{base_url}{date_str}/"
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                title_tag = soup.find('meta', property='og:title')
                title = title_tag['content'].split('|')[0].strip() if title_tag else "News"
                
                # 重複チェック
                if title not in seen_titles:
                    img_tag = soup.find('meta', property='og:image')
                    items.append({
                        "site_name": "Universal Music",
                        "title": title,
                        "link": url,
                        "date": date_str.replace('-', '.'),
                        "thumbnail": img_tag['content'] if img_tag else ""
                    })
                    seen_titles.add(title)
                    print(f"✅ 発見: {date_str} - {title[:15]}...")
        except: continue
        if len(items) >= 12: break
    return items
