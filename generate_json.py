import json, os
from datetime import datetime

DATA_FILE = 'news.json'
IMAGE_DIR = 'images'

def main():
    print(f"--- [{IMAGE_DIR}] 内の画像のみで固定を開始します ---")
    
    # 1. あなたが用意した images フォルダ内のファイル名だけを取得
    your_images = []
    if os.path.exists(IMAGE_DIR):
        files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        for f in files:
            # HTML側から見たパスを生成
            your_images.append(f"./{IMAGE_DIR}/{f}")
            print(f"  採用: {f}")

    # 2. 既存のデータを読み込むが、imagesリストは完全に「空」にしてから上書き
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # 3. ニュース由来の画像を一切含まず、あなたの画像だけで固定
    data["images"] = your_images
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n完了: {len(your_images)}枚の自作画像だけで固定しました。外部画像は排除されました。")

if __name__ == "__main__":
    main()
