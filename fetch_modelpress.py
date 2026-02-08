import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_modelpress_news():
    # 最強ルート：永瀬廉専用ニュース一覧
    target_url = "https://mdpr.jp/model/detail/2554"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://mdpr.jp/'
    }

    print("モデルプレスの永瀬廉専用ページから抽出中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  [エラー] アクセス拒否 (Status: {r.status_code})")
            return []

        soup = BeautifulSoup(r.content, "html.parser")
        
        # 記事要素の特定（提示されたセレクタ群を使用）
        articles = soup.select(".p-mainPostList__item") or \
                   soup.select("article") or \
                   soup.select(".m-articleList__item")
        
        if not articles:
            articles = [a.parent for a in soup.find_all("a") if "/detail/" in a.get("href", "")]

        news_list = []
        count = 0
        
        for article in articles:
            link = article.find("a") if hasattr(article, 'find') else article
            if not link or not link.get("href"): continue
            
            url = link["href"]
            if "/detail/" not in url: continue
            if not url.startswith("http"): url = "https://mdpr.jp" + url
            
            print(f"  詳細解析中: {url.split('/')[-1]}...")
            time.sleep(1.2)
            try:
                rd = requests.get(url, headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                
                # 【検閲】本文に「永瀬廉」があるかチェック
                article_body = sd.select_one(".p-article__body") or sd.select_one("article")
                if article_body and "永瀬廉" not in article_body.get_text():
                    print("    × 記事本文に名前なし。スキップ。")
                    continue

                # 情報抽出
                title_tag = sd.find("h1") or sd.select_one(".p-article__title")
                title = title_tag.get_text(strip=True) if title_tag else "King & Prince ニュース"
                
                og_img = sd.find("meta", property="og:image")
                img_url = og_img['content'] if og_img else "images/photo_9.jpg"
                
                # 日付：2026.02.09 形式へ
                date_node = sd.find("time") or sd.select_one(".p-article__date")
                raw_date = date_node.get_text(strip=True) if date_node else ""
                date_match = re.findall(r'\d+', raw_date)
                date_text = f"{date_match[0]}.{date_match[1].zfill(2)}.{date_match[2].zfill(2)}" if len(date_match) >= 3 else raw_date

                news_list.append({
                    "site_name": "MODELPRESS",
                    "date": date_text,
                    "title": title,
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
    new_articles = fetch_modelpress_news()
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    # 既存のMODELPRESSをリセットしてゴミ掃除し、追加
    data["news"] = [n for n in data["news"] if n["site_name"] != "MODELPRESS"]
    data["news"].extend(new_articles)
    data["news"].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：モデルプレスから {len(new_articles)} 件の『本物』を追加しました。")
