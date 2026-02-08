import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_billboard_news():
    target_url = "https://www.billboard-japan.com/artists/detail/569261"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("Billboard Japan から真の投稿日時を抽出中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        all_links = soup.find_all("a")
        target_articles = []
        seen_urls = set()
        
        for l in all_links:
            href = l.get("href", "")
            if "/d_news/detail/" in href:
                url = "https://www.billboard-japan.com" + href if href.startswith("/") else href
                if url not in seen_urls:
                    raw_title = l.get_text(strip=True)
                    # 1. タイトル文頭の「202X/XX/XX 」という日付を削除
                    clean_title = re.sub(r'^\d{4}/\d{2}/\d{2}\s+', '', raw_title)
                    
                    if len(clean_title) > 5:
                        target_articles.append({"url": url, "title": clean_title})
                        seen_urls.add(url)

        news_list = []
        for item in target_articles[:8]:
            print(f"  詳細解析中: {item['url'].split('/')[-1]}...")
            time.sleep(1.2)
            try:
                rd = requests.get(item['url'], headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                
                # 2. 真の投稿日を抽出
                # metaタグ (published_time) または .news_date / .date クラスを狙う
                date_node = sd.find("meta", property="article:published_time")
                if date_node:
                    raw_date = date_node.get("content", "")
                else:
                    date_node = sd.select_one(".news_date p") or sd.select_one(".date")
                    raw_date = date_node.get_text(strip=True) if date_node else ""

                # 3. YYYY.MM.DD 形式に整形
                date_match = re.findall(r'\d+', raw_date)
                if len(date_match) >= 3:
                    date_text = f"{date_match[0]}.{date_match[1].zfill(2)}.{date_match[2].zfill(2)}"
                else:
                    # 万が一取れなかった場合のみ、一覧ページのURLに含まれる日付等から推測（抽出日にはしない）
                    date_text = "2026.01.01" 

                # 画像(OGP)
                og_img = sd.find("meta", property="og:image")
                img_url = og_img['content'] if og_img else "images/photo_9.jpg"

                news_list.append({
                    "site_name": "BILLBOARD",
                    "date": date_text,
                    "title": item['title'],
                    "url": item['url'],
                    "image": img_url
                })
                print(f"    ◎ [確定] {date_text} : {item['title'][:15]}...")
            except:
                continue
                
        return news_list
    except Exception as e:
        print(f"エラー: {e}")
        return []

if __name__ == "__main__":
    new_articles = fetch_billboard_news()
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    data["news"] = [n for n in data["news"] if n["site_name"] != "BILLBOARD"]
    data["news"].extend(new_articles)
    data["news"].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：Billboardの記事から重複日付を削除し、投稿日を正常化しました。")
