import requests
import base64
import re
from bs4 import BeautifulSoup

# テスト用のGoogleニュースURL（先ほどあなたが取得したものの一つ）
test_url = "https://news.google.com/rss/articles/CBMiS0FVX3lxTE9oNjg1T1llbktCaC1fQlJ2VmEzbVE0cnVKTWtaQ0RZWUdsSEM2SkpsSXZpZG1RdXJkTU42TDd2SmxDV0xPQlRnT0JXVQ?oc=5"

def debug_check(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    
    print(f"1. 元のURL: {url[:50]}...")
    
    # 手順A: リンクのデコードを試みる
    try:
        code = url.split("articles/")[1].split("?")[0]
        decoded = base64.urlsafe_b64decode(code + '==').decode('latin-1')
        real_url = re.search(r'https?://[^\s<>"\x00-\x1f]+', decoded).group(0)
        print(f"2. デコード結果 (成功): {real_url}")
    except Exception as e:
        print(f"2. デコード結果 (失敗): {e}")
        real_url = url

    # 手順B: 実際にそのURLにアクセスして、リダイレクト先を確認
    try:
        res = requests.get(real_url, headers=headers, timeout=10, allow_redirects=True)
        print(f"3. 最終的な到達先URL: {res.url}")
        
        # 手順C: 画像タグ（og:image）の捜索
        soup = BeautifulSoup(res.text, 'html.parser')
        og_img = soup.find("meta", property="og:image")
        if og_img:
            print(f"4. 画像タグ発見: {og_img.get('content')[:50]}...")
        else:
            print("4. 画像タグが見つかりません。")
            
    except Exception as e:
        print(f"3-4. アクセスエラー: {e}")

if __name__ == "__main__":
    debug_check(test_url)
