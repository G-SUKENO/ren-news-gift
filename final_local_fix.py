import re

# 1. index.html の余白 (padding-top) を修正
file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# PC版の余白を 40px に（85px から変更）
content = content.replace('padding: 85px 20px 40px;', 'padding: 40px 20px 40px;')
# スマホ版の余白を 30px に（60px から変更）
content = content.replace('padding: 60px 10px 30px;', 'padding: 30px 10px 30px;')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. oricon_collector.py を「日付・文字化け完全対策版」に更新
oricon_code = """
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def collect():
    print("📡 ORICON NEWS：最終デバッグ（日付・文字化け対策）...")
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
                res_d.encoding = res_d.apparent_encoding # 文字化け対策
                soup_d = BeautifulSoup(res_d.text, 'html.parser')
                
                # 正確な日付を取得
                time_tag = soup_d.find('time') or soup_d.find('p', class_='time')
                date_str = datetime.now().strftime("%Y.%m.%d")
                if time_tag:
                    raw_text = time_tag.get_text(strip=True)
                    match = re.search(r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})', raw_text)
                    if match:
                        date_str = f"{match.group(1)}.{match.group(2).zfill(2)}.{match.group(3).zfill(2)}"

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
                    print(f"✅ 取得: {date_str} | {title[:15]}...")
            except: continue
        return items
    except Exception as e:
        print(f"❌ エラー: {e}"); return []

if __name__ == '__main__': collect()
"""
with open('oricon_collector.py', 'w', encoding='utf-8') as f:
    f.write(oricon_code.strip())

print("✨ 余白修正(PC:40px/SP:30px) と ニュース取得プログラムの更新が完了しました！")
