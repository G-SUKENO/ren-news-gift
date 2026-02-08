import requests
from bs4 import BeautifulSoup
import time

def test_moviewalker_direct():
    # 【最新】press.moviewalker.jp へのドメイン変更と新ID（288683）に対応
    target_url = "https://press.moviewalker.jp/person/288683/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"1. 新ドメイン（press.moviewalker.jp）を深層スキャン中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"   [エラー] アクセス拒否されました (Status: {r.status_code})")
            return

        soup = BeautifulSoup(r.content, "html.parser")
        
        # 新サイトの構造に合わせて、ニュース記事のリンク（/news/article/）を抽出
        news_links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            # ニュース記事へのリンクを特定
            if "/news/article/" in href:
                url = "https://press.moviewalker.jp" + href if href.startswith("/") else href
                if url not in [l['url'] for l in news_links]:
                    title = a.get_text(strip=True)
                    # タイトルが空の場合は、近くのタイトルクラスから取得を試みる
                    if not title:
                        parent = a.find_parent(["div", "li"])
                        title_tag = parent.select_one(".p-news-card__title") if parent else None
                        title = title_tag.get_text(strip=True) if title_tag else "映画ニュース"
                    
                    if len(title) > 5:
                        news_links.append({"url": url, "title": title})

        if not news_links:
            print("   [失敗] ニュースリンクが見つかりません。")
            return

        print(f"   {len(news_links)}件の映画ニュースを確認。上位3件を解析します。")

        count = 0
        for item in news_links[:3]:
            print(f"\n--- 映画ニュース発見: {item['title'][:25]}... ---")
            print(f"    URL: {item['url']}")
            
            # 記事詳細から og:image (映画スチール) を確保
            try:
                rd = requests.get(item['url'], headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                og_img = sd.find("meta", property="og:image")
                
                if og_img:
                    print(f"    [成功] 映画スチール画像URLを発見！")
                    print(f"    画像: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [失敗] 画像が見つかりませんでした。")
            except:
                print("    [エラー] 詳細ページにアクセスできません。")
            
            time.sleep(1)

        print(f"\nMOVIE WALKER PRESS 検証終了（計 {count} 件）")
            
    except Exception as e:
        print(f"   [システムエラー] {e}")

if __name__ == "__main__":
    test_moviewalker_direct()
