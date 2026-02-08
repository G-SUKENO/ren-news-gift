import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_oricon_news():
    # 永瀬廉の公式プロフィール内記事一覧（ここが一番確実に記事が並んでいる）
    target_url = "https://www.oricon.co.jp/prof/637850/article/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("オリコンの永瀬廉専用ページから抽出中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # 記事要素の特定
        articles = soup.select("article") or soup.select(".block-news-list li")
        if not articles:
            articles = soup.find_all("div", class_="media-body") or soup.find_all("li")

        news_list = []
        count = 0
        
        for article in articles:
            link_tag = article.find("a")
            if not link_tag: continue
            
            url = link_tag.get("href", "")
            if "/news/" not in url: continue
            if url.startswith("/"):
                url = "https://www.oricon.co.jp" + url
            
            # タイトル取得
            title_tag = article.find(["h2", "p", "h3"]) or link_tag
            title_text = title_tag.get_text(strip=True)
            if not title_text: continue

            # 記事詳細へ入って画像と日付を抜く
            print(f"  詳細解析中: {title_text[:20]}...")
            time.sleep(1.2) # 負荷軽減
            try:
                r_detail = requests.get(url, headers=headers, timeout=10)
                soup_detail = BeautifulSoup(r_detail.content, "html.parser")
                
                # 画像(OGP)
                og_img = soup_detail.find("meta", property="og:image")
                img_url = og_img['content'] if og_img else "images/photo_9.jpg"
                
                # 日付
                date_node = soup_detail.find("time") or soup_detail.select_one(".time")
                date_text = date_node.get_text(strip=True) if date_node else ""

                news_list.append({
                    "site_name": "ORICON",
                    "date": date_text,
                    "title": title_text,
                    "url": url,
                    "image": img_url
                })
                count += 1
                if count >= 8: break # 最新8件まで
            except:
                continue
                
        return news_list
    except Exception as e:
        print(f"エラー発生: {e}")
        return []

if __name__ == "__main__":
    new_articles = fetch_oricon_news()
    
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    existing_urls = {item['url'] for item in data.get("news", [])}
    added_count = 0
    for art in new_articles:
        if art['url'] not in existing_urls:
            data["news"].append(art)
            added_count += 1
    
    # 日付順に並び替え
    data["news"].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\n完了：オリコンから {added_count} 件の『本物』を追記しました。")
