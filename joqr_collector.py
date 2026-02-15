import requests
from bs4 import BeautifulSoup

def collect():
    # 庭ラジ（永瀬廉）に関連する記事が集まるURL
    url = "https://www.joqr.co.jp/tag/%E6%B0%B8%E7%80%AC%E5%BB%89/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = []

        # 記事のリンクが含まれる「article」タグを直接狙い撃ち
        items = soup.find_all('article')
        
        for item in items:
            a_tag = item.find('a', href=True)
            if not a_tag or '/articles/' not in a_tag['href']:
                continue
                
            # タイトル（h2やh3、またはクラス名にtitleを含むもの）
            title_tag = item.find(['h2', 'h3']) or item.find(class_=lambda x: x and 'title' in x)
            if not title_tag: continue
            title = title_tag.get_text(strip=True)

            # 重複除外
            if any(a['title'] == title for a in articles): continue

            # 日付
            date_tag = item.find(class_=lambda x: x and 'date' in x) or item.find('time')
            date_str = date_tag.get_text(strip=True).replace('.', '-') if date_tag else "2026-02-15"
            
            # 画像URLの抽出
            img_tag = item.find('img')
            thumbnail = ""
            if img_tag:
                thumbnail = img_tag.get('src') or img_tag.get('data-src') or ""

            articles.append({
                'site_name': '文化放送 (庭ラジ)',
                'title': title,
                'link': a_tag['href'],
                'date': date_str,
                'thumbnail': thumbnail
            })
        
        return articles
    except Exception as e:
        print(f"❌ 文化放送エラー: {e}")
        return []
