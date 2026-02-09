import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

def get_ogp_info(url, site_name):
    """個別記事から情報を抜き取る万能プラグイン"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200: return None
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # タイトル取得
        og_title = soup.find('meta', property='og:title')
        title = og_title['content'].strip() if og_title else "News Update"
        # 不要な末尾のサイト名をカットしてスッキリさせる
        title = re.sub(r' \| .*$| - .*$|：STARTO.*$', '', title).strip()
        
        # 画像取得
        og_img = soup.find('meta', property='og:image')
        thumbnail = og_img['content'] if og_img else ""
        
        return {
            "site_name": site_name,
            "title": title,
            "link": url,
            "date": datetime.now().strftime("%Y.%m.%d"),
            "thumbnail": thumbnail
        }
    except:
        return None

def collect_all():
    news_items = []
    seen_titles = set()
    
    # --- 1. STARTO ENTERTAINMENT 攻略 ---
    print("📡 STARTO ENTERTAINMENTを深層解析中...")
    try:
        # K&Pニュース一覧ページ
        starto_list_url = "https://starto.jp/s/p/artist/41/news"
        res = requests.get(starto_list_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ページ内のリンクから詳細記事(/news/detail/...)を根こそぎ抽出
        links = soup.find_all('a', href=re.compile(r'/news/detail/'))
        found_urls = []
        for a in links:
            href = a['href']
            full_url = href if href.startswith('http') else "https://starto.jp" + href
            if full_url not in found_urls:
                found_urls.append(full_url)

        for url in found_urls[:5]:
            info = get_ogp_info(url, "STARTO ENTERTAINMENT")
            if info and info['title'] not in seen_titles:
                news_items.append(info)
                seen_titles.add(info['title'])
                print(f"✅ STARTO記事発見: {info['title'][:20]}...")
    except Exception as e:
        print(f"❌ STARTO解析失敗: {e}")

    # --- 2. Universal Music 攻略 ---
    print("📡 Universal Musicを広域解析中...")
    base_url = "https://www.universal-music.co.jp/king-and-prince/news/"
    today = datetime.now()
    for i in range(30): # 直近30日分
        target_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"{base_url}{target_date}/"
        try:
            res = requests.head(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
            if res.status_code == 200:
                info = get_ogp_info(url, "Universal Music")
                if info and info['title'] not in seen_titles:
                    info['date'] = target_date.replace('-', '.')
                    news_items.append(info)
                    seen_titles.add(info['title'])
                    print(f"✅ Universal記事発見: {target_date}")
        except:
            continue
        if len(news_items) >= 15: break

    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(news_items, f, ensure_ascii=False, indent=4)
    print(f"✨ 合計 {len(news_items)} 件の記事を保存しました。")

if __name__ == "__main__":
    collect_all()
