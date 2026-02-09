import json
import os
import official_collector
import moviewalker_collector

def main():
    print("🚀 ニュース抽出を開始します...")
    
    # 公式データ
    official_data = official_collector.collect()
    
    # MOVIE WALKER (映画特化メディア)
    movie_data = moviewalker_collector.collect()
    
    # 統合
    all_news = official_data + movie_data
    
    # 重複排除
    unique_news = []
    seen_titles = set()
    for item in all_news:
        if item['title'] not in seen_titles:
            unique_news.append(item)
            seen_titles.add(item['title'])
    
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=4)
        
    print(f"\n✨ 更新完了！ 合計 {len(unique_news)} 件")

if __name__ == "__main__":
    main()
