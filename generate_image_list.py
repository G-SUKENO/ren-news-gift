import os
import json

def generate():
    img_dir = 'images'
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG')
    
    if not os.path.exists(img_dir):
        print(f"Error: {img_dir} directory not found.")
        return

    images = [f'images/{f}' for f in os.listdir(img_dir) if f.endswith(valid_extensions)]
    images.sort()
    
    with open('image_list.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(images)}枚の画像を登録しました。")

if __name__ == "__main__":
    generate()
