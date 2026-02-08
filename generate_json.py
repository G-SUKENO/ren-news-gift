import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time
import re

session = requests.Session()
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}

def get_youtube_data():
    print("--- YouTube: 動画解析 ＆ 振り分け中 ---")
    data = {"featured": None, "regulars": [], "shorts": []}
    try:
        channel_id = "UCSxwcQnzA5K6DvofvBn6ATA"
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        res = session.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        entries = soup.find_all('entry')
        
        for i, entry in enumerate(entries):
            video = {
                "id": entry.find('yt:videoId').text,
                "title": entry.find('title').text,
                "thumbnail": entry.find('media:group').find('media:thumbnail')['url']
            }
            
            # 1つ目は「代表動画」へ
            if i == 0:
                data["featured"] = video
                continue
                
            # タイトルに "Shorts" が含まれるかチェック（振り分けロジック）
            if "Shorts" in video["title"] or "ショート" in video["title"] or "#Shorts" in video["title"]:
                data["shorts"].append(video)
            else:
                data["regulars"].append(video)
                
        print(f"  完了: 代表1, 通常{len(data['regulars'])}, ショート{len(data['shorts'])}")
    except:
        print("  YouTube取得失敗")
    return data

def get_og_image(url):
    try:
        time.sleep(0.3)
        res = session.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og: return f"https://wsrv.nl/?url={urllib.parse.quote(og.get('content'))}&w=400&h=400&fit=cover"
    except: pass
    return ""

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
    print("--- 永瀬廉ポータル：ハイブリッド構成 ---")
    yt_data = get_youtube_data()
    news_list = []
    
    # ニュースサイト取得
    configs = [
        ("公式", "https://www.universal-music.co.jp/king-and-prince/news/", ["/news/"]),
        ("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"]),
        ("オリコン", "https://www.oricon.co.jp/prof/637850/article/", ["/news/"]),
        ("Billboard", "https://www.billboard-japan.com/artists/detail/569261", ["/d_news/"])
    ]
    for name, url, keywords in configs:
        news_list += smart_fetch(name, url, keywords)

    final_data = {
        "featured": yt_data["featured"],
        "regulars": yt_data["regulars"],
        "shorts": yt_data["shorts"],
        "news": []
    }
    
    for entry in news_list:
        print(f"画像取得: [{entry['source']}] {entry['title'][:15]}...")
        img = get_og_image(entry['url'])
        final_data["news"].append({
            "title": entry['title'], "source": entry['source'], "url": entry['url'], "img": img
        })

    with open('news
cat << 'EOF' > index.html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>REN NAGASE PORTAL</title>
    <style>
        :root { --bg-color: #000; --card-bg: #111; --accent-color: #d4af37; --text-color: #fff; }
        body { font-family: -apple-system, sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 0; overflow-x: hidden; }
        header { padding: 15px; text-align: center; border-bottom: 1px solid #222; }
        h1 { margin: 0; font-size: 1rem; color: var(--accent-color); letter-spacing: 0.1rem; }
        
        /* SNSハブ */
        .sns-hub { display: flex; justify-content: space-around; padding: 12px 5px; border-bottom: 1px solid #222; }
        .sns-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #fff; width: 18%; }
        .sns-icon { width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--accent-color); display: flex; justify-content: center; align-items: center; font-size: 0.45rem; margin-bottom: 4px; color: var(--accent-color); }
        .sns-label { font-size: 0.5rem; font-weight: bold; }

        .section-label { padding: 15px 15px 5px; font-size: 0.7rem; color: var(--accent-color); font-weight: bold; border-left: 3px solid var(--accent-color); margin-left: 15px; text-transform: uppercase; }

        /* 代表動画 */
        .featured-video { padding: 12px; }
        .v-main { position: relative; padding-bottom: 56.25%; height: 0; border-radius: 12px; overflow: hidden; border: 1px solid #333; }
        .v-main iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }

        /* 通常動画（横長） */
        .video-scroll { display: flex; overflow-x: auto; padding: 10px 15px; gap: 10px; }
        .video-scroll::-webkit-scrollbar { display: none; }
        .v-small { min-width: 14
cat << 'EOF' > generate_json.py
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time
import re

session = requests.Session()
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}

def get_youtube_data():
    print("--- YouTube: 動画解析 ＆ 振り分け中 ---")
    data = {"featured": None, "regulars": [], "shorts": []}
    try:
        channel_id = "UCSxwcQnzA5K6DvofvBn6ATA"
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        res = session.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        entries = soup.find_all('entry')
        
        for i, entry in enumerate(entries):
            video = {
                "id": entry.find('yt:videoId').text,
                "title": entry.find('title').text,
                "thumbnail": entry.find('media:group').find('media:thumbnail')['url']
            }
            
            # 1つ目は「代表動画」へ
            if i == 0:
                data["featured"] = video
                continue
                
            # タイトルに "Shorts" が含まれるかチェック（振り分けロジック）
            if "Shorts" in video["title"] or "ショート" in video["title"] or "#Shorts" in video["title"]:
                data["shorts"].append(video)
            else:
                data["regulars"].append(video)
                
        print(f"  完了: 代表1, 通常{len(data['regulars'])}, ショート{len(data['shorts'])}")
    except:
        print("  YouTube取得失敗")
    return data

def get_og_image(url):
    try:
        time.sleep(0.3)
        res = session.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og: return f"https://wsrv.nl/?url={urllib.parse.quote(og.get('content'))}&w=400&h=400&fit=cover"
    except: pass
    return ""

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
    print("--- 永瀬廉ポータル：ハイブリッド構成 ---")
    yt_data = get_youtube_data()
    news_list = []
    
    # ニュースサイト取得
    configs = [
        ("公式", "https://www.universal-music.co.jp/king-and-prince/news/", ["/news/"]),
        ("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"]),
        ("オリコン", "https://www.oricon.co.jp/prof/637850/article/", ["/news/"]),
        ("Billboard", "https://www.billboard-japan.com/artists/detail/569261", ["/d_news/"])
    ]
    for name, url, keywords in configs:
        news_list += smart_fetch(name, url, keywords)

    final_data = {
        "featured": yt_data["featured"],
        "regulars": yt_data["regulars"],
        "shorts": yt_data["shorts"],
        "news": []
    }
    
    for entry in news_list:
        print(f"画像取得: [{entry['source']}] {entry['title'][:15]}...")
        img = get_og_image(entry['url'])
        final_data["news"].append({
            "title": entry['title'], "source": entry['source'], "url": entry['url'], "img": img
        })

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("\n完了！")

if __name__ == "__main__":
    main()
