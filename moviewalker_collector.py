import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def collect():
    print("📡 MOVIE WALKER：画像タグから全情報をブっこ抜き中...")
    url = "https://press.moviewalker.jp/search/free_search.cgi?keyword=%E6%B0%B8%E7%80%AC%E5%BB%89&comkind=news"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        items = []
        # 全ての画像タグをスキャン
        images = soup.find_all('img')
        
        for img in images:
            if len(items) >= 10: break
            
            alt = img.get('alt', '')
            # altに「永瀬廉」が含まれている画像だけをターゲットにする
            if "永瀬廉" not in alt: continue
            
            # 1. タイトル (alt属性から取得)
            title = alt.strip()
            
            # 2. サムネイル (data-src, srcの順)
            thumbnail = img.get('data-src') or img.get('src') or ""
            if thumbnail.startswith('//'): thumbnail = "https:" + thumbnail
            elif thumbnail.startswith('/') and not thumbnail.startswith('//'): thumbnail = "https://press.moviewalker.jp" + thumbnail
            
            # 3. リンク (親要素のaタグを探す)
            parent_a = img.find_parent('a')
            if not parent_a: continue
            link = parent_a.get('href', '')
            if not link.startswith('http'): link = "https://press.moviewalker.jp" + link
            
            # 4. 日付 (周辺テキストから正規表現で抜く)
            date_str = datetime.now().strftime("%Y.%m.%d")
            container = img.find_parent('li') or img.find_parent('div')
            if container:
                date_match = re.search(r'(\d{4})[./](\d{2})[./](\d{2})', container.get_text())
                if date_match:
                    date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"

            items.append({
                "site_name": "MOVIE WALKER",
                "title": title,
                "link": link,
                "date": date_str,
                "thumbnail": thumbnail
            })
            print(f"📸 成功: {title[:15]}... [画像あり]")
                
        return items
    except Exception as e:
        print(f"❌ 解析失敗: {e}"); return []

if __name__ == '__main__':
    res = collect()
    print(f"\n📊 最終結果: {len(res)} 件")
