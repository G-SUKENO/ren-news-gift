import requests
from bs4 import BeautifulSoup
import time

def test_billboard_direct():
    # 検索ページではなく、永瀬廉のアーティスト詳細ページ（ニュース一覧がある場所）を直撃
    target_url = "https://www.billboard-japan.com/artists/detail/569261"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

    print(f"1. Billboard Japan アーティストページを深層解析中...")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # ページ内の「Daily News」セクションから記事リンクを探す
        # Billboardの構成に合わせて、/d_news/detail/ を含むリンクを全抽出
        all_links = soup.find_all("a")
        target_articles = []
        for l in all_links:
            href = l.get("href", "")
            if "/d_news/detail/" in href:
                url = "https://www.billboard-japan.com" + href if href.startswith("/") else href
                if url not in [a['url'] for a in target_articles]:
                    title = l.get_text(strip=True)
                    if len(title) > 10: # 短すぎるタイトル（画像のみ等）を排除
                        target_articles.append({"url": url, "title": title})

        if not target_articles:
            print("   [失敗] ニュースリンクが見つかりません。")
            return

        print(f"   {len(target_articles)}件の記事を特定。画像を確認します。")

        count = 0
        for item in target_articles[:3]:
            print(f"\n--- 記事発見: {item['title'][:25]}... ---")
            try:
                r_det = requests.get(item['url'], headers=headers, timeout=10)
                s_det = BeautifulSoup(r_det.content, "html.parser")
                og_img = s_det.find("meta", property="og:image")
                
                if og_img and og_img.get("content"):
                    print(f"    [成功] 高画質画像URL: {og_img['content'][:60]}...")
                    count += 1
                else:
                    print("    [失敗] 画像が見つかりません。")
            except: pass
            time.sleep(1)

        print(f"\nBillboard Japan 攻略完了（計 {count} 件）")
            
    except Exception as e:
        print(f"   [エラー] {e}")

if __name__ == "__main__":
    test_billboard_direct()
