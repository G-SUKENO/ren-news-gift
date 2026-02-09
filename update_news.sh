#!/bin/bash

echo "🚀 ニュース更新プロセスを開始します..."

# 1. 各サイトのスクリプトを順番に実行
# ※各スクリプトが「既存のnews.jsonに追記して50件維持する」ロジックになっていることが前提です
python3 fetch_official.py
python3 fetch_natalie.py
python3 fetch_oricon.py
python3 fetch_billboard.py
python3 fetch_modelpress.py
python3 fetch_edgeline.py
python3 fetch_moviewalker.py

echo "✅ 全サイトの巡回が完了しました。"
