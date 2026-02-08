import json, os
from datetime import datetime

DATA_FILE = 'news.json'
IMAGE_DIR = 'images' # あなたがGitHubにアップしたフォルダ名

def get_your_uploaded_images():
    print(f"--- [{IMAGE_DIR}] フォルダ内の画像をスキャン中 ---")
    images = []
    if os.path.exists(IMAGE_DIR):
        # 画像ファイル（jpg, png, webpなど）をアルファベット順に取得
        files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        for f in files:
            # HTML(index.html)から見た正しい相対パスを作成
            # ここが重要です：ニュースの画像は一切混ぜません
            images.append(f"./{IMAGE_DIR}/{f}")
            print(f"  確認済み: {f}")
    return images

def main():
    # 1. あなたが用意した画像だけを取得
    your_images = get_your_uploaded_images()
    
    # 2. 現在の news.json を読み込む（他のデータを壊さないため）
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # 3. 画像データだけを「あなたの画像」で上書き
    data["images"] = your_images
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. 保存
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n完了: {len(your_images)}枚の画像（あなたのアップロード分）をスライダー用に固定しました。")

if __name__ == "__main__":
    main()
