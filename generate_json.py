import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time
import re

session = requests.Session()
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}

def get_youtube_videos():
    print("--- YouTube: チャンネルフィードを解析中 ---")
    videos = []
    try:
        channel_id = "UCSxwcQnzA5K6DvofvBn6ATA"
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        res = session.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        entries = soup.find_all('entry')
        
        for entry in entries:
            videos.append({
                "id": entry.find('yt:videoId').text,
                "title": entry.find('title').text,
                "thumbnail": entry.find('media:group').find('media:thumbnail')['url']
            })
        print(f"  成功: {len(videos)} 件の動画を取得")
    except:
        print("  YouTube取得失敗")
    return videos

def get_og_image(url):
    try:
        time.sleep(0.3)
        res = session.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og: return f"https://wsrv.nl/?url={urllib.parse.quote(og.get('content'))}&w=400&h=400&fit=cover"
    except: pass
    return ""

def scrape_modelpress():
    print("--- モデルプレス 攻略中 ---")
    items = []
    try:
        res = session.get("https://mdpr.jp/model/detail/2554", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if re.search(r'/\d+$', a['href']):
                title = a.get_text(strip=True)
                if len(title) > 10 and any(k in title for k in ["永瀬廉", "キンプリ", "King"]):
                    items.append({"title": title, "url": urllib.parse.urljoin("https://mdpr.jp", a['href']), "source": "モデルプレス"})
            if len(items) >= 5: break
    except: pass
    return items

def smart_fetch(name, url, keywords):
    print(f"--- {name} 攻略中 ---")
    items = []
    try:
        res = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if any(k in a['href'] for k in keywords):
                title = a.get_text(strip=True)
                if len(title) > 10 and any(k in title for k in ["永瀬廉", "キンプリ", "King"]):
                    items.append({"title": title, "url": urllib.parse.urljoin(url, a['href']), "source": name})
            if len(items) >= 5: break
    except: pass
    return items

def main():
    print("--- 永瀬廉ポータル：YouTubeホーム再現ミッション ---")
    video_list = get_youtube_videos()
    news_list = []
    news_list += smart_fetch("公式", "https://www.universal-music.co.jp/king-and-prince/news/", ["/news/"])
    news_list += scrape_modelpress()
    configs = [
        ("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"]),
        ("オリコン", "https://www.oricon.co.jp/prof/637850/article/", ["/news/"]),
        ("Billboard", "https://www.billboard-japan.com/artists/detail/569261", ["/d_news/"]),
        ("RealSound", "https://realsound.jp/?s=永瀬廉", ["/2026/", "/2025/"])
    ]
    for name, url, keywords in configs:
        news_list += smart_fetch(name, url, keywords)

    unique_news = {n['url']: n for n in news_list}.values()
    final_data = {"videos": video_list, "news": []}
    
    for entry in list(unique_news):
        print(f"画像取得: [{entry['source']}] {entry['title'][:15]}...")
        img = get_og_image(entry['url'])
        final_data["news"].append({
            "title": entry['title'], "source": entry['source'], "url": entry['url'], "img": img,
            "date": datetime.now().strftime('%Y/%m/%d')
        })

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：全情報を保存しました。")

if __name__ == "__main__":
    main()
