import json
import oricon_collector
import modelpress_collector
import official_collector  # これがUNIVERSALの正体

def main():
    all_news = []
    
    # 1. UNIVERSAL (official_collector) から取得
    print("📡 UNIVERSAL MUSIC：取得開始...")
    try:
        all_news.extend(official_collector.collect())
    except Exception as e:
        print(f"❌ UNIVERSAL取得エラー: {e}")
    
    # 2. ORICON NEWS から取得
    print("📡 ORICON NEWS：取得開始...")
    try:
        all_news.extend(oricon_collector.collect())
    except Exception as e:
        print(f"❌ ORICON取得エラー: {e}")
    
    # 3. MODELPRESS から取得
    print("📡 MODELPRESS：取得開始...")
    try:
        all_news.extend(modelpress_collector.collect())
    except Exception as e:
        print(f"❌ MODELPRESS取得エラー: {e}")
    
    # 日付順に並び替え（新しい順）
    all_news.sort(key=lambda x: x.get('date', '0000.00.00'), reverse=True)
    
    # 重複削除
    unique_news = []
    seen_titles = set()
    for news in all_news:
        if news['title'] not in seen_titles:
            unique_news.append(news)
            seen_titles.add(news['title'])
    
    # 保存
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news[:20], f, ensure_ascii=False, indent=4)
    
    print(f"✨ 完了：合計 {len(unique_news[:20])} 件のニュースを保存しました！")

if __name__ == '__main__':
    main()
