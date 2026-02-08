import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# iPhoneのふりをしてアクセス
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'

def fetch_article_info(rss_url):
    headers = {'User-Agent': UA}
    try:
        res = requests.get(rss_url, timeout=10, headers=headers, allow_redirects=True)
        final_url = res.url
        if "news.google.com" in final_url: return final_url, ""

        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        
        # あらゆる場所から画像を探す（優先順位）
        meta_props = ["og:image", "twitter:image", "og:image:url", "thumbnail"]
        for prop in meta_props:
            tag = soup.find("meta", {"property": prop}) or soup.find("meta", {"name": prop})
            if tag and tag.get("content"):
                img_url = tag["content"]
                if img_url.startswith("http") and "google" not in img_url:
                    break
        
        if img_url:
            print(f"  [Success] 画像を特定しました")
        else:
            print(f"  [Failed] 画像が見つかりません: {final_url[:40]}...")
            
        return final_url, img_url
    except Exception as e:
        print(f"  [Error] {e}")
        return rss_url, ""

def get_news():
    filename = 'news.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: archive = json.load(f)
            except: archive = []
    else: archive = []

    def normalize_title(t):
        return re.sub(r'[^\w]', '', re.sub(r' - .*$', '', t))

    existing_urls = {item['url'] for item in archive}
    existing_titles = {normalize_title(item['title']) for item in archive[:50]}
    
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp", "永瀬廉 site:oricon.co.jp"]
    new_items = []

    print("--- ニュースを取得中 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            res = requests.get(rss_url, timeout=10)
            root = ET.fromstring(res.content)
            
            for item in root.findall('.//item')[:10]:
                raw_title = item.find('title').text
                rss_link = item.find('link').text
                
                # ★ メディア名をGoogleの専用タグから直接取得（これで正確になります）
                source_element = item.find('source')
                source = source_element.text if source_element is not None else "News"
                
                # タイトルからメディア名を消してスッキリさせる
                clean_title = re.sub(f' - {source}$', '', raw_title)

                if (normalize_title(clean_title) not in existing_titles) and (rss_link not in existing_urls):
                    print(f"新着発見: {clean_title[:20]}...")
                    direct_url, img_url = fetch_article_info(rss_link)
                    
                    pub_date = item.find('pubDate').text
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_items.append({
                        "title": clean_title,
                        "source": source,
                        "url": direct_url,
                        "img": img_url,
                        "date": date_obj.strftime('%Y/%m/%d'),
                        "year": date_obj.strftime('%Y'),
                        "timestamp": date_obj.timestamp()
                    })
                    existing_titles.add(normalize_title(clean_title))
                    existing_urls.add(direct_url)
                    time.sleep(1)
        except: continue

    # 画像がない過去記事を5件だけ補完（負荷軽減のため）
    for item in archive[:15]:
        if not item.get('img') or "google" in item.get('img'):
            print(f"画像補完中: {item['title'][:15]}...")
            _, img_url = fetch_article_info(item['url'])
            if img_url: item['img'] = img_url
            time.sleep(1)

    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
EOFcat << 'EOF' > index.html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <link rel="apple-touch-icon" href="icon.png">
    <title>永瀬廉NEWS</title>
    <style>
        :root { --main-bg: #0d0d0d; --card-bg: #1a1a1a; --accent-color: #d4af37; --text-color: #ffffff; --sub-text: #a0a0a0; }
        body { font-family: -apple-system, sans-serif; background: var(--main-bg); color: var(--text-color); margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 500px; }
        h1 { font-size: 18px; text-align: center; color: var(--accent-color); letter-spacing: 4px; margin-bottom: 25px; font-weight: 300; }
        #search-bar { width: 100%; padding: 12px 18px; border-radius: 25px; border: 1px solid #333; background: #222; color: white; margin-bottom: 20px; box-sizing: border-box; outline: none; }
        .news-item { background: var(--card-bg); border-radius: 15px; margin-bottom: 12px; display: flex; height: 90px; border: 1px solid #222; text-decoration: none; color: inherit; overflow: hidden; }
        .news-img { width: 90px; height: 90px; object-fit: cover; background: #222; flex-shrink: 0; }
        .news-content { padding: 10px 12px; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1; min-width: 0; }
        .news-title { font-size: 13px; font-weight: 600; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .meta-row { display: flex; gap: 8px; align-items: center; }
        .source-tag { font-size: 9px; color: var(--accent-color); border: 0.5px solid var(--accent-color); padding: 1px 6px; border-radius: 3px; font-weight: bold; }
        .date { font-size: 10px; color: var(--sub-text); }
        .year-btn { background: #1a1a1a; color: var(--accent-color); border: 1px solid var(--accent-color); padding: 6px 15px; border-radius: 20px; font-size: 11px; margin: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>永瀬廉 NEWS</h1>
        <input type="text" id="search-bar" placeholder="キーワードで検索...">
        <div id="news-list"></div>
        <div id="year-buttons" style="margin-top:30px; border-top:1px solid #222; padding-top:15px;"></div>
    </div>
    <script>
        const placeholder = "https://placehold.jp/24/1a1a1a/d4af37/150x150.png?text=%E2%98%85";
        let allNews = [];
        function renderNews(items) {
            const list = document.getElementById('news-list');
            list.innerHTML = '';
            items.forEach(item => {
                const a = document.createElement('a');
                a.className = 'news-item';
                a.href = item.url;
                a.target = '_blank';
                // 画像URLが有効かチェック
                const imgSrc = (item.img && item.img.startsWith('http')) ? item.img : placeholder;
                a.innerHTML = `
                    <img src="${imgSrc}" onerror="this.src='${placeholder}'" class="news-img">
                    <div class="news-content">
                        <div class="news-title">${item.title}</div>
                        <div class="meta-row">
                            <span class="date">${item.date}</span>
                            <span class="source-tag">${item.source}</span>
                        </div>
                    </div>
                `;
                list.appendChild(a);
            });
        }
        fetch('news.json?t=' + Date.now()).then(res => res.json()).then(data => {
            allNews = data;
            renderNews(allNews.slice(0, 30));
            [...new Set(data.map(n => n.year))].forEach(year => {
                const btn = document.createElement('button');
                btn.className = 'year-btn';
                btn.innerText = year + '年';
                btn.onclick = () => renderNews(allNews.filter(n => n.year === year));
                document.getElementById('year-buttons').appendChild(btn);
            });
        });
        document.getElementById('search-bar').addEventListener('input', (e) => {
            renderNews(allNews.filter(n => n.title.toLowerCase().includes(e.target.value.toLowerCase())));
        });
    </script>
</body>
</html>
