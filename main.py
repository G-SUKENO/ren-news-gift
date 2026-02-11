import json
import os
import official_collector
import moviewalker_collector
import oricon_collector

def main():
    print("🚀 ニュース抽出を開始します...")
    
    # 各ソースから収集
    official_data = official_collector.collect()
    oricon_data = oricon_collector.collect()
    movie_data = moviewalker_collector.collect()

    # すべてを統合
    all_news = official_data + oricon_data + movie_data
    
    # タイトルの重複排除
    unique_news = []
    seen_titles = set()
    for item in all_news:
        if item['title'] not in seen_titles:
            unique_news.append(item)
            seen_titles.add(item['title'])
    
    # 日付順にソート（新しい順）
    unique_news.sort(key=lambda x: x['date'], reverse=True)
    
    # 最終保存
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=4)
        
    print(f"\n✨ 更新完了！ 合計 {len(unique_news)} 件の記事を統合しました")

if __name__ == "__main__":
    main()
