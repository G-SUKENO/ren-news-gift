import requests
from bs4 import BeautifulSoup

url = "https://www.oricon.co.jp/search/result.php?types=news&word=%E6%B0%B8%E7%80%AC%E5%BB%89"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. そもそもリンク（aタグ）がいくつあるか？
    links = soup.find_all('a')
    print(f"発見されたaタグの総数: {len(links)}")
    
    # 2. 検索結果っぽい部分（メインコンテンツ）のHTMLを一部表示
    main = soup.find('main') or soup.find('div', id='main')
    if main:
        print("\n--- メインコンテンツの冒頭500文字 ---")
        print(main.get_text()[:500])
    else:
        print("\nMainタグが見つかりません。")

except Exception as e:
    print(f"Error: {e}")
