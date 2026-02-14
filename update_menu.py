import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSSの更新：PCでは横1列、スマホでは3列2段のグリッド配置
new_css = """
        .nav-icons { display: flex; justify-content: center; gap: 30px; padding: 85px 20px 40px; position: relative; z-index: 3; flex-wrap: wrap; background: var(--black); }
        @media (max-width: 768px) {
            .nav-icons { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px 0; padding: 60px 10px 30px; }
            .nav-item { grid-column: span 1; }
        }
        .nav-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: var(--gold); transition: 0.4s; }
        .nav-item svg { width: 28px; height: 28px; fill: none; stroke: var(--gold); stroke-width: 1.2; margin-bottom: 10px; }
        .nav-item span { font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 300; }
"""

# 既存の .nav-icons 関連のCSSを新しいものに差し替え
content = re.sub(r'\.nav-icons \{.*?\}\s+@media \(max-width: 768px\) \{.*?\.nav-item:nth-child\(5\) \{ grid-column: 5 / span 2; \}\s+\}', new_css, content, flags=re.DOTALL)

# 2. HTMLの書き換え：指示された並び順とXの追加
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

# 既存のnav要素を置換
content = re.sub(r'<nav class="nav-icons">.*?</nav>', new_nav, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ ローカルテスト用：並び順・デザイン維持版を適用しました。")
