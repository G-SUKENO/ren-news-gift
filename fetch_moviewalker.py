import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_moviewalker_news():
    # 新ドメイン：永瀬廉パーソンページ
    target_url = "https://press.moviewalker.jp/person/288683/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("MOVIE WALKER PRESS から映画ニュースを抽出中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  [エラー] アクセス拒否 (Status: {r.status_code})")
            return []

        soup = BeautifulSoup(r.content, "html.parser")
        
        # /news/article/ を含むリンクを全取得
        all_links = soup.find_all('a', href=re.compile(r'/news/article/'))
        
        unique_urls = []
        seen = set()
        for a in all_links:
            href = a.get('href', '')
            url = "https://press.moviewalker.jp" + href if href.startswith("/") else href
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)

        news_list = []
        count = 0
        for url in unique_urls[:6]: # 最新6件
            print(f"  詳細解析中: {url.split('/')[-2]}...")
            time.sleep(1.2)
            try:
                rd = requests.get(url, headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                
                # 検閲：一応本文に名前があるかチェック
                if "永瀬廉" not in sd.get_text():
                    continue

                # タイトル：OGPのタイトルが一番綺麗にまとまっていることが多い
                og_title = sd.find("meta", property="og:title")
                title = og_title['content'].split('|')[0].strip() if og_title else "映画ニュース"
                
                # 画像(OGP)：映画のスチール写真
                og_img = sd.find("meta", property="og:image")
                img_url = og_img['content'] if og_img else "images/photo_9.jpg"
                
                # 日付：詳細ページから抽出
                date_node = sd.find("time") or sd.select_one(".p-article-header__date")
                raw_date = date_node.get_text(strip=True) if date_node else ""
                date_match = re.findall(r'\d+', raw_date)
                date_text = f"{date_match[0]}.{date_match[1].zfill(2)}.{date_match[2].zfill(2)}" if len(date_match) >= 3 else raw_date

                news_list.append({
                    "site_name": "MOVIE WALKER",
                    "date": date_text,
                    "title": title,
                    "url": url,
                    "image": img_url
                })
                count += 1
            except:
                continue
                
        return news_list
    except Exception as e:
        print(f"エラー: {e}")
        return []

if __name__ == "__main__":
    new_articles = fetch_moviewalker_news()
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    data["news"] = [n for n in data["news"] if n["site_name"] != "MOVIE WALKER"]
    data["news"].extend(new_articles)
    data["news"].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：MOVIE WALKER PRESS から {len(new_articles)} 件追加しました。")
