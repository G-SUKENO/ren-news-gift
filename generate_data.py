import os
import json

def generate_image_list():
    img_dir = 'images'
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    
    # imagesフォルダ内の画像を探す（深いフォルダは無視して直下のみ）
    images = [f"{img_dir}/{f}" for f in os.listdir(img_dir) 
              if f.lower().endswith(valid_extensions)]
    
    # リストを保存
    with open('image_list.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=4)
    print(f"📸 画像リスト完了: {len(images)}枚を登録しました")

if __name__ == "__main__":
    generate_image_list()
