import os
import json

def generate():
    image_dir = 'images'
    if not os.path.exists(image_dir):
        print("❌ imagesフォルダが見つかりません。")
        return
    # 対応する拡張子を網羅
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.JPG', '.JPEG', '.PNG')
    images = [f for f in os.listdir(image_dir) if f.lower().endswith(valid_extensions)]
    images.sort()
    
    # 手元のMacで中身を確認するために表示
    print(f"✅ {len(images)}枚の画像をリスト化しました。")
    
    with open('image_list.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate()
