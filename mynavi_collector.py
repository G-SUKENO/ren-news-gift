import requests
from bs4 import BeautifulSoup
import re

def get_ogp_image(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        og_img = soup.find("meta", property="og:image")
        if og_img:
            return og_img["content"]
    except:
        pass
    return ""

def collect():
    print("📅 投稿日時を精密に解析して抽出中...")
    url = "https://news.mynavi.jp/freeword?utf8=%E2%9C%93&q=%E6%B0%B8%E7%80%AC%E5%BB%89&commit=%E6%A4%9C%E7%B4%A2"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = []
        
        links = soup.find_all('a', href=True)
        
        for a in links:
            href = a['href']
            if '/article/' in href:
                raw_text = a.get_text(strip=True)
                
                # タイトルに永瀬廉が含まれているか（ノイズ除去）
                if "永瀬廉" not in raw_text:
                    continue
                
                # --- 日付の分離ロジック ---
                # テキスト内の「202X/XX/XX」というパターンを探す
                date_match = re.search(r'\d{4}/\d{2}/\d{2}', raw_text)
                if date_match:
                    found_date = date_match.group(0).replace('/', '-') # 2026-01-24 形式へ
                    # タイトルから日付以降の部分を削り取る
                    title = raw_text.split(date_match.group(0))[0].strip()
                else:
                    found_date = "2026-02-15" # 万が一のバックアップ
                    title = raw_text

                link = "https://news.mynavi.jp" + href if href.startswith('/') else href
                if any(art['link'] == link for art in articles):
                    continue
                
                print(f"✅ 日付確定 [{found_date}]: {title[:15]}...")
                thumbnail = get_ogp_image(link)
                
                articles.append({
                    'site_name': 'マイナビニュース',
                    'title': title,
                    'link': link,
                    'date': found_date,
                    'thumbnail': thumbnail
                })
                
                if len(articles) >= 5: break
        
        return articles
    except:
        return []
