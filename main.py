import json
import os
import official_collector
import moviewalker_collector
import starto_collector
import oricon_collector

def main():
    print("🚀 ニュース抽出を開始します...")
    
    # 1. STARTO (公式)
    starto_data = starto_collector.collect()
    
    # 2. Universal Music (音楽)
    official_data = official_collector.collect()
    
    # 3. MOVIE WALKER (映画)
    movie_data = moviewalker_collector.collect()

    # 4. ORICON (一般ニュース)
    oricon_data = oricon_collector.collect()
    
    # すべてを統合
    all_news = starto_data + official_data + movie_data + oricon_data
    
    # 重複排除（同じタイトルの記事を消す）
    unique_news = []
    seen_titles = set()
    for item in all_news:
        if item['title'] not in seen_titles:
            unique_news.append(item)
            seen_titles.add(item['title'])
    
    # 日付の新しい順に並び替え
    unique_news.sort(key=lambda x: x['date'], reverse=True)
    
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=4)
        
    print(f"\n✨ 更新完了！ 合計 {len(unique_news)} 件のニュースを統合しました")

if __name__ == "__main__":
    main()
