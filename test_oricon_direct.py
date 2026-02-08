import requests
from bs4 import BeautifulSoup
import time

def test_oricon_direct():
    # 【最強ルート】オリコンの「永瀬廉 ニュース一覧」ページ
    target_url = "https://www.oricon.co.jp/prof/637850/article/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"1. オリコンの永瀬廉専用ニュースページに直行中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # オリコンのプロフページにある記事リストを取得
        # 通常、articleタグや .block-news-list 内の li に並んでいます
        articles = soup.select("article") or soup.select(".block-news-list li")
        
        if not articles:
            # 万が一のための予備セレクタ
            articles = soup.find_all("div", class_="media-body") or soup.find_all("li")

        print(f"   ページ解析完了。{len(articles)}件の要素をチェックします。")

        count = 0
        for article in articles:
            link_tag = article.find("a")
            if not link_tag: continue
            
            url = link_tag.get("href", "")
            if "/news/" not in url: continue
            
            if url.startswith("/"):
                url = "https://www.oricon.co.jp" + url
            
            # タイトル取得（h2やpタグの中身を探す）
            title_tag = article.find(["h2", "p", "h3"]) or link_tag
            title_text = title_tag.get_text(strip=True)
            
            if not title_text or "永瀬廉" not in title_text and count > 5:
                continue # あまりに関係ない記事（広告など）は飛ばす

            print(f"\n--- 記事発見: {title_text[:25]}... ---")
            print(f"    URL: {url}")
            
            # 画像の確保
            try:
                r_detail = requests.get(url, headers=headers, timeout=10)
                soup_detail = BeautifulSoup(r_detail.content, "html.parser")
                og_img = soup_detail.find("meta", property="og:image")
                
                if og_img:
                    print(f"    [成功] 高画質画像URLを確保！")
                    print(f"    画像: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [失敗] 画像タグがありません。")
            except:
                print("    [エラー] 記事の中まで入れませんでした。")
            
            time.sleep(1)
            if count >= 3: break

        if count == 0:
            print("   [注意] 記事が見つかりましたが、画像が取得できませんでした。")
            
    except Exception as e:
        print(f"   [システムエラー] {e}")

if __name__ == "__main__":
    test_oricon_direct()
