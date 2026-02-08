import json, requests, time
from datetime import datetime

# あなたのGitHubのユーザー名とリポジトリ名
GITHUB_USER = "G-SUKENO"
REPO_NAME = "ren-news-gift"
DATA_FILE = "news.json"

def main():
    print(f"--- GitHub上の画像をスキャン中: {GITHUB_USER}/{REPO_NAME} ---")
    
    # GitHub APIを使って、imagesフォルダ内のファイル一覧を直接取得する
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/images"
    
    images = []
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            files = response.json()
            for file in files:
                # 画像ファイルだけを抽出
                if file["name"].lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    # GitHub Pagesで表示するための公開URLを生成
                    # https://g-sukeno.github.io/ren-news-gift/images/xxx.jpg
                    image_url = f"https://{GITHUB_USER.lower()}.github.io/{REPO_NAME}/images/{file['name']}"
                    images.append(image_url)
                    print(f"  発見: {file['name']}")
        else:
            print(f"  APIエラー: {response.status_code}")
    except Exception as e:
        print(f"  エラー: {e}")

    # 既存のデータを壊さず、imagesだけをGitHubのURLで更新
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: pass

    data["images"] = images
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n完了: GitHub上の画像 {len(images)} 枚を登録しました。")

if __name__ == "__main__":
    import os
    main()
