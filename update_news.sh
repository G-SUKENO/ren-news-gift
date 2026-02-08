#!/bin/bash
echo "🌟 永瀬廉 ニュースポータル一括更新開始 🌟"

# 各サイトからの抽出
python3 fetch_official.py
python3 fetch_oricon.py
python3 fetch_natalie.py
python3 fetch_modelpress.py
python3 fetch_moviewalker.py
python3 fetch_edgeline.py
python3 fetch_billboard.py

# 最後に50件に切り詰める
python3 trim_news.py

echo "✅ すべての更新と整理が完了しました。"
