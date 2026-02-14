import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. PWA（アプリ化）設定の削除
# apple-mobile-web-app-capable を no にするか、削除することで通常のブラウザ表示になります
content = re.sub(r'<meta name="apple-mobile-web-app-capable" content="yes">', 
                 '', content)

# 2. メニューの並び順とレイアウトを最新化（START, UNIVERSAL, YouTube, INSTAGRAM, X, TIKTOK）
new_nav = """
<nav class="nav-icons">
    <a href="https://starto.jp/s/p/artist/41" target="_blank" class="nav-item"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/></svg><span>STARTO</span></a>
    <a href="https://www.universal-music.co.jp/king-and-prince/" target="_blank" class="nav-item"><svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg><span>UNIVERSAL</span></a>
    <a href="https://www.youtube.com/@kp_official_523" target="_blank" class="nav-item"><svg viewBox="0 0 24 24"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.42a2.78 2.78 0 0 0-1.94 2C1 8.14 1 12 1 12s0 3.86.46 5.58a2.78 2.78 0 0 0 1.94 2c1.72.42 8.6.42 8.6.42s6.88 0 8.6-.42a2.78 2.78 0 0 0 1.94-2C23 15.86 23 12 23 12s0-3.86-.46-5.58z"/><path d="M9.75 15.02l5.75-3.02-5.75-3.02v6.04z"/></svg><span>YOUTUBE</span></a>
    <a href="https://www.instagram.com/ren.nagase.official/" target="_blank" class="nav-item"><svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37zM17.5 6.5h.01"/></svg><span>INSTAGRAM</span></a>
    <a href="https://x.com/kp_official_523" target="_blank" class="nav-item"><svg viewBox="0 0 24 24"><path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772"/></svg><span>X</span></a>
    <a href="https://www.tiktok.com/@kingandprince_j_universe" target="_blank" class="nav-item"><svg viewBox="0 0 24 24"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/></svg><span>TIKTOK</span></a>
</nav>
"""
content = re.sub(r'<nav class="nav-icons">.*?</nav>', new_nav, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ ローカルテスト用：通常サイト化 ＆ メニュー修正が完了しました。")
