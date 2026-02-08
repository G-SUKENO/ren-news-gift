import requests
from bs4 import BeautifulSoup
import time

def test_edgeline_direct():
    # エッジラインの「永瀬廉」検索結果に直接アクセス
    search_url = "https://www.edgeline-tokyo.com/?s=%E6%B0%B8%E7%80%AC%E5%BB%89"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"1. エッジラインの検索ページに直行中...")
    try:
        r = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # エッジラインの記事は <article> タグにまとまっています
        articles = soup.select("article")
        
        if not articles:
            # 念のための予備セレクタ
            articles = soup.select(".post") or soup.select(".entry-card")

        if not articles:
            print("   [失敗] 記事が見つかりませんでした。")
            return

        print(f"   {len(articles)}件の記事を発見。上位3件を精査します。")

        count = 0
        for article in articles:
            link_tag = article.find("a")
            if not link_tag: continue
            
            url = link_tag.get("href", "")
            # タイトルは h2 や .entry-title などから取得
            title_tag = article.select_one("h2") or article.select_one(".entry-title") or link_tag
            title_text = title_tag.get_text(strip=True)
            
            # あまりに関係ない記事（もしあれば）は除外
            if not title_text: continue

            print(f"\n--- 記事発見: {title_text[:25]}... ---")
            print(f"    URL: {url}")
            
            # 詳細ページに入って、独自アングルの og:image を確保
            try:
                r_detail = requests.get(url, headers=headers, timeout=10)
                soup_detail = BeautifulSoup(r_detail.content, "html.parser")
                og_img = soup_detail.find("meta", property="og:image")
                
                if og_img and og_img.get("content"):
                    print(f"    [成功] 高画質画像URLを確保！")
                    print(f"    画像: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [失敗] 画像が見つかりませんでした。")
            except:
                print("    [エラー] 記事詳細にアクセスできませんでした。")
            
            time.sleep(1) # 1秒待機
            if count >= 3: break

        print(f"\nエッジライン検証終了（計 {count} 件）")
            
    except Exception as e:
        print(f"   [システムエラー] {e}")

if __name__ == "__main__":
    test_edgeline_direct()
