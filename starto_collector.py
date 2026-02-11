import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

def collect():
    print("📡 STARTO ENTERTAINMENT 裏口（ID直接推測）攻略開始...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    
    # 最近のニュースIDは 1000〜2000 あたりに集中していることが多いです
    # まずは最新のIDを特定するために一覧ページからヒントを探すのは諦め、
    # 最近の「Universal Music」などの日付に近いIDを推測するか、
    # 以前成功していた「1b3400c」以前のログからIDの傾向を読み取ります。
    
    # 今回は「直近の大きな数字」から逆順に20個ほど生存確認をします
    # ※数字はサイトの最新状況に合わせて調整が必要ですが、直近のIDを決め打ちします
    start_id = 1500 # この数字は変動します。404が出なくなるまで調整
    items = []
    
    print(f"🔎 最新記事を探索中 (ID: {start_id} から逆走)...")

    # 1500から1400まで、記事が存在するか直接確認しに行く
    check_count = 0
    for i in range(start_id, start_id - 100, -1):
        if len(items) >= 5: break # 5件取れたら終了
        
        detail_url = f"https://starto.jp/s/p/news/detail/{i}?artist=41"
        try:
            res = requests.get(detail_url, headers=headers, timeout=3)
            if res.status_code == 200 and "King & Prince" in res.text:
                soup = BeautifulSoup(res.text, 'html.parser')
                og_title = soup.find('meta', property='og:title')
                title = re.sub(r'：STARTO.*$', '', og_title['content']).strip() if og_title else "STARTO News"
                
                # 重複やログイン画面を排除
                if "ログイン" in title or "最新情報" in title: continue
                
                og_img = soup.find('meta', property='og:image')
                thumbnail = og_img['content'] if og_img else ""
                
                items.append({
                    "site_name": "STARTO ENTERTAINMENT",
                    "title": title,
                    "link": detail_url,
                    "date": datetime.now().strftime("%Y.%m.%d"),
                    "thumbnail": thumbnail
                })
                print(f"✅ 奪取成功! [ID:{i}]: {title[:15]}...")
            
            check_count += 1
            if check_count % 10 == 0: print(f"...{check_count}件チェック済み")
        except:
            continue
            
    return items

if __name__ == "__main__":
    result = collect()
    print(f"\n最終結果: {len(result)} 件")
