import os
import json

def generate():
    image_dir = 'images'
    if not os.path.exists(image_dir):
        print("❌ imagesフォルダが見つかりません。")
        return
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    images = [f for f in os.listdir(image_dir) if f.lower().endswith(valid_extensions)]
    # 名前順にソートしてリスト化
    images.sort()
    with open('image_list.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=4)
    print(f"✅ {len(images)}枚の画像を名簿(image_list.json)に登録しました。")

if __name__ == "__main__":
    generate()
