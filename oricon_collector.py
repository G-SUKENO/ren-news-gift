import requests
from bs4 import BeautifulSoup
import re
import time

def collect():
    print("📡 ORICON NEWS：永瀬廉専用アーカイブを直接攻略中...")
    items = []
    # 永瀬廉のニュース一覧ページ（ここには過去数ヶ月分の「廉さん記事」しか載っていません）
    url = "https://www.oricon.co.jp/prof/717830/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # このページにある「全ての記事リンク」を一旦全部拾う
        # オリコンの個別ニュースは必ず /news/数字/full/ という形式
        all_links = soup.find_all('a', href=re.compile(r'/news/\d+/full/'))
        
        target_urls = []
        for a in all_links:
            href = a['href']
            full_url = "https://www.oricon.co.jp" + href if href.startswith('/') else href
            if full_url not in target_urls:
                target_urls.append(full_url)

        print(f"🔎 アーカイブ内に {len(target_urls)} 件の対象URLを発見。精密解析を開始...")

        for detail_url in target_urls[:8]: # 最新8件を深掘り
            try:
                time.sleep(0.5)
                res_d = requests.get(detail_url, headers=headers, timeout=5)
                res_d.encoding = res_d.apparent_encoding
                soup_d = BeautifulSoup(res_d.text, 'html.parser')
                
                # OGP情報（SNS共有用データ）を最優先で取得
                og_title = soup_d.find('meta', property='og:title')
                title = og_title['content'].split(' | ')[0] if og_title else ""
                
                og_img = soup_d.find('meta', property='og:image')
                thumbnail = og_img['content'] if og_img else ""
                
                # 日付
                time_tag = soup_d.find('time')
                date = time_tag.get_text(strip=True) if time_tag else ""

                if title and "oricon.co.jp" in thumbnail: # ちゃんと画像があるものだけ
                    items.append({
                        "site_name": "ORICON NEWS",
                        "title": title.strip(),
                        "link": detail_url,
                        "date": date,
                        "thumbnail": thumbnail
                    })
                    print(f"✅ 奪取成功: {title[:15]}...")
            except:
                continue

    except Exception as e:
        print(f"❌ 解析失敗: {e}")
        
    return items
