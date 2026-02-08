import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_edgeline_news():
    # エッジライン：永瀬廉 検索結果ページ
    search_url = "https://www.edgeline-tokyo.com/?s=%E6%B0%B8%E7%80%AC%E5%BB%89"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("エッジラインから現場ニュースを抽出中...")
    try:
        r = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # 記事要素（提示されたセレクタをベースに）
        articles = soup.select("article") or soup.select(".post") or soup.select(".entry-card")
        
        news_list = []
        count = 0
        for article in articles:
            link_tag = article.find("a")
            if not link_tag: continue
            
            url = link_tag.get("href", "")
            if not url: continue
            
            # 詳細解析
            print(f"  詳細解析中: {url.split('/')[-2]}...")
            time.sleep(1.2)
            try:
                rd = requests.get(url, headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                
                # 【検閲】本文に「永瀬廉」が含まれているか
                if "永瀬廉" not in sd.get_text():
                    continue

                # タイトル取得
                title_tag = sd.find("h1") or sd.select_one(".entry-title")
                title = title_tag.get_text(strip=True) if title_tag else "永瀬廉 ニュース"
                
                # 画像(OGP)
                og_img = sd.find("meta", property="og:image")
                img_url = og_img['content'] if og_img else "images/photo_9.jpg"
                
                # 日付：詳細ページから抽出（2026.02.09形式へ）
                date_node = sd.find("time") or sd.select_one(".entry-date")
                raw_date = date_node.get_text(strip=True) if date_node else ""
                date_match = re.findall(r'\d+', raw_date)
                date_text = f"{date_match[0]}.{date_match[1].zfill(2)}.{date_match[2].zfill(2)}" if len(date_match) >= 3 else raw_date

                news_list.append({
                    "site_name": "EDGE LINE",
                    "date": date_text,
                    "title": title,
                    "url": url,
                    "image": img_url
                })
                count += 1
                if count >= 6: break # 最新6件まで
            except:
                continue
                
        return news_list
    except Exception as e:
        print(f"エラー: {e}")
        return []

if __name__ == "__main__":
    new_articles = fetch_edgeline_news()
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    # 既存のEDGE LINEを入れ替え
    data["news"] = [n for n in data["news"] if n["site_name"] != "EDGE LINE"]
    data["news"].extend(new_articles)
    data["news"].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：エッジラインから {len(new_articles)} 件の独自ニュースを追加しました。")
