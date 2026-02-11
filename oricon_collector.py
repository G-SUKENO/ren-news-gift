import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def collect():
    print("📡 ORICON NEWS：最終攻略（文字コード補正版）...")
    
    # 検索結果URL
    url = "https://www.oricon.co.jp/search/result.php?types=article&search_string=%89i%90%A3%97%F5"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        # オリコン特有の文字コード(Shift-JIS)を強制適用
        res.encoding = 'shift_jis' 
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 記事へのリンク（/news/数字/full/ または /news/数字/）をすべて探す
        all_links = soup.find_all('a', href=re.compile(r'/news/\d+'))
        
        items = []
        seen_urls = set()

        print(f"🔎 ページ内のリンクから精査中...")

        for a in all_links:
            if len(items) >= 5: break
            
            href = a['href']
            full_url = "https://www.oricon.co.jp" + href if href.startswith('/') else href
            
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                
                # タイトルを取得（aタグの中身、またはimgのaltから）
                title = a.get_text(strip=True)
                if not title and a.find('img'):
                    title = a.find('img').get('alt', '')
                
                # 「永瀬廉」が含まれる記事だけを厳選
                if "永瀬廉" in title or "King" in title:
                    # 画像を探す（同じaタグ内、または周辺）
                    img_tag = a.find('img')
                    thumbnail = img_tag['src'] if img_tag else ""
                    
                    items.append({
                        "site_name": "ORICON NEWS",
                        "title": title,
                        "link": full_url,
                        "date": datetime.now().strftime("%Y.%m.%d"),
                        "thumbnail": thumbnail
                    })
                    print(f"✅ 奪取成功: {title[:15]}...")

        return items
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        return []

if __name__ == "__main__":
    result = collect()
    print(f"\n最終結果: {len(result)} 件取得")
