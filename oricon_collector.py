import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def collect():
    print("📡 ORICON NEWS：高画質・正確な日付で再攻略...")
    url = "https://www.oricon.co.jp/search/result.php?types=article&search_string=%89i%90%A3%97%F5"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'shift_jis' 
        soup = BeautifulSoup(res.text, 'html.parser')
        
        all_links = soup.find_all('a', href=re.compile(r'/news/\d+'))
        items = []
        seen_urls = set()

        for a in all_links:
            if len(items) >= 5: break
            href = a['href']
            full_url = "https://www.oricon.co.jp" + href if href.startswith('/') else href
            
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                
                # 詳細ページに潜入して「日付」と「高画質画像」を奪取
                try:
                    res_d = requests.get(full_url, headers=headers, timeout=5)
                    res_d.encoding = 'utf-8'
                    soup_d = BeautifulSoup(res_d.text, 'html.parser')
                    
                    # 1. 正確な日付を取得
                    time_tag = soup_d.find('time')
                    date_val = time_tag.get_text(strip=True) if time_tag else datetime.now().strftime("%Y.%m.%d")
                    # 「2024-01-01 12:00」形式を「2024.01.01」に整形
                    clean_date = re.search(r'\d{4}-\d{2}-\d{2}', date_val)
                    date_str = clean_date.group().replace('-', '.') if clean_date else date_val

                    # 2. 高画質画像を取得 (OGPの画像は比較的デカい)
                    og_img = soup_d.find('meta', property='og:image')
                    thumbnail = og_img['content'] if og_img else ""
                    
                    # 3. タイトル
                    og_title = soup_d.find('meta', property='og:title')
                    title = og_title['content'].split(' | ')[0] if og_title else ""

                    if "永瀬廉" in title or "King" in title:
                        items.append({
                            "site_name": "ORICON NEWS",
                            "title": title,
                            "link": full_url,
                            "date": date_str,
                            "thumbnail": thumbnail
                        })
                        print(f"✅ 奪取完了: {title[:15]}... ({date_str})")
                except:
                    continue

        return items
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []

if __name__ == "__main__":
    collect()
