import json
import os
import re
from datetime import datetime

COLLECTOR_MAP = {
    'official_collector': 'UNIVERSAL MUSIC',
    'oricon_collector': 'ORICON NEWS',
    'modelpress_collector': 'モデルプレス',
    'moviewalker_collector': 'MOVIE WALKER',
    'starto_collector': 'STARTO ENTERTAINMENT',
    'mynavi_collector': 'マイナビニュース',
    'natalie_collector': '映画ナタリー'
}

def normalize_date(date_str):
    """バラバラな日付形式を 'YYYY-MM-DD' に統一する"""
    if not date_str:
        return "2000-01-01"
    # 数字だけを抽出 (2026, 02, 03 など)
    parts = re.findall(r'\d+', date_str)
    if len(parts) >= 3:
        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    return "2000-01-01"

def clean_title(title):
    title = re.sub(r'^(エンタメ|レポート|ニュース|画像|写真|映画)[:\s]*', '', title)
    return title.strip()

def main():
    print("🗂️ 全記事を統合し、時系列で並び替え中...")
    
    all_news = []
    for mod_name, label in COLLECTOR_MAP.items():
        try:
            mod = __import__(mod_name)
            res = mod.collect()
            if res:
                for item in res:
                    # 日付を統一
                    item['date'] = normalize_date(item['date'])
                    item['title'] = clean_title(item['title'])
                    all_news.append(item)
                print(f"✅ {label}: {len(res)} 件取得")
        except Exception as e:
            print(f"⚠️ {label} の取得に失敗: {e}")

    # 1. 重複を削除 (リンクURLで判定)
    unique_news = []
    seen_links = set()
    for item in all_news:
        if item['link'] not in seen_links:
            unique_news.append(item)
            seen_links.add(item['link'])

    # 2. 【最重要】日付順にソート (新しい順)
    # 文字列として '2026-02-15' > '2026-02-03' なので正確に並びます
    unique_news.sort(key=lambda x: x['date'], reverse=True)
    
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ 統合完了！ 合計 {len(unique_news)} 件の記事を時系列に並べました。")
    print("ブラウザを更新して、最新順に並んでいるか確認してください！")

if __name__ == '__main__':
    main()
