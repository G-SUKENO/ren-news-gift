import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def collect():
    print("📡 ORICON NEWS：高精度・文字化け対策版で攻略...")
    url = "https://www.oricon.co.jp/search/result.php?types=article&search_string=%89i%90%A3%97%F5"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

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
            if full_url in seen_urls: continue
            seen_urls.add(full_url)
                
            try:
                res_d = requests.get(full_url, headers=headers, timeout=5)
                # 文字コードを自動判別（文字化け対策）
                res_d.encoding = res_d.apparent_encoding
                soup_d = BeautifulSoup(res_d.text, 'html.parser')
                
                # 日付：複数のパターンに対応
                time_tag = soup_d.find('time') or soup_d.find('p', class_='time')
                date_str = datetime.now().strftime("%Y.%m.%d")
                if time_tag:
                    raw_date = time_tag.get_text(strip=True)
                    match = re.search(r'(\d{4})[./-](\d{2})[./-](\d{2})', raw_date)
                    if match:
                        date_str = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"

                # タイトルと画像
                og_title = soup_d.find('meta', property='og:title')
                title = og_title['content'].split(' | ')[0] if og_title else ""
                og_img = soup_d.find('meta', property='og:image')
                thumbnail = og_img['content'] if og_img else ""

                if "永瀬廉" in title or "King" in title:
                    items.append({
                        "site_name": "ORICON NEWS",
                        "title": title.strip(),
                        "link": full_url,
                        "date": date_str,
                        "thumbnail": thumbnail
                    })
                    print(f"✅ 成功: {title[:10]}... ({date_str})")
            except:
                continue
        return items
    except Exception as e:
        print(f"❌ エラー: {e}"); return []

if __name__ == "__main__":
    collect()
