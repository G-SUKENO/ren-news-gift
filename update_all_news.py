import subprocess
import json
import os

# 実行するスクリプトのリスト
scripts = [
    "fetch_official.py",
    "fetch_natalie.py",
    "fetch_oricon.py",
    "fetch_billboard.py",
    "fetch_modelpress.py",
    "fetch_edgeline.py",
    "fetch_moviewalker.py"
]

def run_updates():
    print("🚀 全サイトのニュース更新を開始します...")
    
    for script in scripts:
        if os.path.exists(script):
            print(f"📡 {script} を実行中...")
            try:
                # 各スクリプトを実行（各スクリプトが news.json を更新する前提）
                subprocess.run(["python3", script], check=True)
            except Exception as e:
                print(f"⚠️ {script} でエラーが発生しました: {e}")
        else:
            print(f"❓ {script} が見つかりません。スキップします。")

    print("✅ すべての更新プロセスが完了しました。")

if __name__ == "__main__":
    run_updates()
