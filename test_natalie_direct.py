import requests
from bs4 import BeautifulSoup
import time

def test_natalie_direct():
    # 【改良】ナタリーの「ニュース」カテゴリに限定して検索
    search_url = "https://natalie.mu/search/news?query=%E6%B0%B8%E7%80%AC%E5%BB%89"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"1. ナタリーのニュース検索結果に直行中...")
    try:
        r = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # ニュース記事のカードを取得
        articles = soup.select(".NA_card")
        
        if not articles:
            print("   [失敗] ニュース記事が見つかりません。")
            return

        print(f"   {len(articles)}件のニュース記事を発見。上位3件を精査します。")

        count = 0
        for article in articles:
            link_tag = article.select_one(".NA_card_title a") or article.find("a")
            if not link_tag: continue
            
            url = link_tag.get("href", "")
            if "/news/" not in url: continue # 念のためニュース記事か再確認
            
            if url.startswith("/"):
                url = "https://natalie.mu" + url
            
            title = link_tag.get_text(strip=True)
            print(f"\n--- ニュース発見: {title[:25]}... ---")
            print(f"    URL: {url}")
            
            # 記事詳細ページに入って og:image (高画質画像) を取得
            try:
                r_detail = requests.get(url, headers=headers, timeout=10)
                soup_detail = BeautifulSoup(r_detail.content, "html.parser")
                og_img = soup_detail.find("meta", property="og:image")
                
                if og_img and og_img.get("content"):
                    print(f"    [成功] 高画質画像URLを確保！")
                    print(f"    画像: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [失敗] 記事内に画像タグが見つかりませんでした。")
            except:
                print("    [エラー] 記事詳細にアクセスできませんでした。")
            
            time.sleep(1)
            if count >= 3: break # 3件取れたら完了

        print(f"\nナタリー検証終了（計 {count} 件）")
            
    except Exception as e:
        print(f"   [システムエラー] {e}")

if __name__ == "__main__":
    test_natalie_direct()
