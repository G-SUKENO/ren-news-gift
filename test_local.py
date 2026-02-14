import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Xのリンクを正しい公式アカウント (@kp_official_523) に修正
# 既存のXのリンク部分を特定して置換します
content = re.sub(r'href="https://x\.com/[^"]+"(.*?)<span>X</span>', 
                 'href="https://x.com/kp_official_523"\\1<span>X</span>', content)

# 2. デザインの最終確認（念のため再設定）
# 高さ: PC 85vh / SP 70vh
content = re.sub(r'#hero-container \{ position: relative; width: 100%; height: \d+vh;', 
                 '#hero-container { position: relative; width: 100%; height: 85vh;', content)
content = re.sub(r'@media \(max-width: 768px\) \{ #hero-container \{ height: \d+vh; \}', 
                 '@media (max-width: 768px) { #hero-container { height: 70vh; }', content)

# 余白: PC 40px / SP 30px
content = re.sub(r'\.nav-icons \{.*?padding: \d+px 20px 40px;', 
                 '.nav-icons { display: flex; justify-content: center; gap: 30px; padding: 40px 20px 40px;', content, flags=re.DOTALL)
content = re.sub(r'@media \(max-width: 768px\) \{.*?padding: \d+px 10px 30px;', 
                 '@media (max-width: 768px) { .nav-icons { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px 0; padding: 30px 10px 30px;', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ ローカルテスト用：Xリンク修正 ＆ 全デザイン適用が完了しました。")
