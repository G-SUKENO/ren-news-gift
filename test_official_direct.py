import requests
from bs4 import BeautifulSoup
import time

def test_official_direct():
    url = "https://www.universal-music.co.jp/king-and-prince/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"1. ユニバーサル公式の最新ニュースを深層スキャン中...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # 広い範囲でニュース記事のリンクを探す
        # リンクの中に /king-and-prince/news/〇〇 という文字列があるものを全抽出
        news_links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "/king-and-prince/news/20" in href: # 202x年などの記事URLを狙う
                if href not in [l['url'] for l in news_links]:
                    title = a.get_text(strip=True)
                    if len(title) > 5:
                        news_links.append({"url": href, "title": title})

        if not news_links:
            print("   [注意] 記事リンクが見つかりません。タグ一覧をチェックします。")
            # 念のため、主要なクラス名の要素をリストアップ
            containers = soup.find_all(["article", "li", "div"], class_=True)
            for c in containers[:10]:
                print(f"     発見したクラス: {c['class']}")
            return

        print(f"   {len(news_links)}件の公式ニュースを確認。上位3件を解析します。")

        count = 0
        for item in news_links[:3]:
            article_url = item['url']
            if article_url.startswith("/"):
                article_url = "https://www.universal-music.co.jp" + article_url
            
            print(f"\n--- 公式発見: {item['title'][:25]}... ---")
            print(f"    URL: {article_url}")
            
            # 記事詳細から og:image を確保
            try:
                rd = requests.get(article_url, headers=headers, timeout=10)
                sd = BeautifulSoup(rd.content, "html.parser")
                og_img = sd.find("meta", property="og:image")
                
                if og_img:
                    print(f"    [成功] 公式画像URLを発見！")
                    print(f"    画像: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [情報] 個別画像はありません。")
            except:
                print("    [エラー] 詳細ページにアクセスできません。")
            
            time.sleep(1)

        print(f"\n公式サイト検証終了（計 {count} 件）")
            
    except Exception as e:
        print(f"   [システムエラー] {e}")

if __name__ == "__main__":
    test_official_direct()
