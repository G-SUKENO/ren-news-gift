import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_natalie_news():
    # 永瀬廉（King & Prince）のニュースアーカイブ
    target_url = "https://natalie.mu/music/artist/103289/news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("音楽ナタリー：『永瀬廉』タイトル強制フィルタで厳選中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # ニュースリンクを抽出
        links = soup.find_all('a', href=re.compile(r'/music/news/\d+'))
        unique_urls = []
        for l in links:
            href = l.get('href', '')
            url = "https://natalie.mu" + href if href.startswith("/") else href
            if url not in unique_urls:
                unique_urls.append(url)

        news_list = []
        for url in unique_urls[:15]:
            time.sleep(1.0)
            try:
                rd = requests.get(url, headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                
                # 【鉄の掟】タイトルを抽出
                title_node = sd.find("h1") or sd.select_one(".NA_article_title")
                title = title_node.get_text(strip=True) if title_node else ""
                
                # --- ここが修正の核心 ---
                # タイトルに「永瀬廉」という文字列が入っていない記事は、問答無用で破棄
                if "永瀬廉" not in title:
                    print(f"  × スキップ（名前なし）: {title[:20]}...")
                    continue

                # 画像(OGP)
                og_img = sd.find("meta", property="og:image")
                img_url = og_img['content'] if og_img else "images/photo_9.jpg"
                
                # 日付：2026.02.09 形式
                date_node = sd.find("time") or sd.select_one(".NA_article_date")
                raw_date = date_node.get_text(strip=True) if date_node else ""
                dm = re.findall(r'\d+', raw_date)
                date_text = f"{dm[0]}.{dm[1].zfill(2)}.{dm[2].zfill(2)}" if len(dm) >= 3 else raw_date

                news_list.append({
                    "site_name": "NATALIE",
                    "date": date_text,
                    "title": title,
                    "url": url,
                    "image": img_url
                })
                print(f"  ◎ [採用] {title[:20]}...")
            except:
                continue
                
        return news_list
    except Exception as e:
        print(f"エラー: {e}")
        return []

if __name__ == "__main__":
    new_articles = fetch_natalie_news()
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    # 既存のNATALIEデータを消して、今回の厳選分だけを入れる
    data["news"] = [n for n in data["news"] if n["site_name"] != "NATALIE"]
    data["news"].extend(new_articles)
    data["news"].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：タイトルに『永瀬廉』を含む記事を {len(new_articles)} 件だけ残しました。")
