import json
import os

def trim_news():
    file_path = 'news.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'news' in data and len(data['news']) > 50:
                # 最新50件のみを保持（古いものは削除される）
                data['news'] = data['news'][:50]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"整理完了：最新の50件を保持し、古い記事を削除しました。")
            else:
                print("記事数は50件以下です。整理は不要です。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    trim_news()
