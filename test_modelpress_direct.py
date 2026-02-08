import requests
from bs4 import BeautifulSoup
import time

def test_modelpress_direct():
    # 【最新ルート】モデルプレスの「永瀬廉」専用ニュース一覧
    target_url = "https://mdpr.jp/model/detail/2554"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://mdpr.jp/'
    }

    print(f"1. モデルプレスの永瀬廉ニュース一覧（専用ページ）に直行中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"   [エラー] アクセス拒否されました (Status: {r.status_code})")
            return

        soup = BeautifulSoup(r.content, "html.parser")
        
        # モデルプレスの専用ページでは、記事が特定のリスト内に並んでいます
        # セレクタを広めに設定して確実に捕まえます
        articles = soup.select(".p-mainPostList__item") or \
                   soup.select("article") or \
                   soup.select(".m-articleList__item")
        
        if not articles:
            # 最終手段：リンクに /detail/ が含まれるものを全抽出
            articles = [a.parent for a in soup.find_all("a") if "/detail/" in a.get("href", "")]

        print(f"   ページ解析完了。{len(articles)}件の候補を精査します。")

        count = 0
        for article in articles:
            link = article.find("a") if hasattr(article, 'find') else article
            if not link or not link.get("href"): continue
            
            url = link["href"]
            if "/detail/" not in url: continue
            if not url.startswith("http"): url = "https://mdpr.jp" + url
            
            # タイトル取得
            title_tag = article.select_one(".p-mainPostList__title") or \
                        article.select_one(".m-articleList__title") or \
                        article.find(["h2", "h3"]) or link
            title_text = title_tag.get_text(strip=True)
            
            if not title_text: continue

            print(f"\n--- ニュース発見: {title_text[:25]}... ---")
            print(f"    URL: {url}")
            
            # 詳細ページに入って、モデルプレス自慢の高画質画像を確保
            try:
                rd = requests.get(url, headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                og_img = sd.find("meta", property="og:image")
                
                if og_img and og_img.get("content"):
                    print(f"    [成功] 高画質画像URLを確保！")
                    print(f"    画像: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [失敗] 画像タグが見つかりませんでした。")
            except:
                print("    [エラー] 詳細ページにアクセスできませんでした。")
            
            time.sleep(1)
            if count >= 3: break

        print(f"\nモデルプレス検証終了（計 {count} 件）")
            
    except Exception as e:
        print(f"   [システムエラー] {e}")

if __name__ == "__main__":
    test_modelpress_direct()
