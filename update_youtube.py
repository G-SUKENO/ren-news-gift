import json
import urllib.request
import re
import time

def get_video_title(video_id):
    try:
        # oEmbedというYouTube公式のタイトル取得機能を使います
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data.get('title', "King & Prince Short")
    except:
        return "King & Prince Short"

def fix_titles():
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data.get('shorts', [])
        if not items:
            items = data.get('news', [])
            
        print(f"{len(items)}件の動画タイトルをYouTubeから直接取得して修正します。少々お待ちください...")
        
        for item in items:
            vid_id = item.get('id')
            if vid_id:
                new_title = get_video_title(vid_id)
                print(f"取得成功: {new_title}")
                item['title'] = new_title
                time.sleep(0.5) # YouTube側に優しく、少し間隔を空けます

        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print("\n完了！news.json のタイトルをすべて最新化しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_titles()
