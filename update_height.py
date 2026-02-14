import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. PC版の高さ変更 (80vh -> 90vh)
content = content.replace('height: 80vh;', 'height: 90vh;')

# 2. スマホ版の高さ変更 (65vh -> 70vh)
# 既存のメディアクエリ内の高さを置換します
content = re.sub(r'@media \(max-width: 768px\) \{ #hero-container \{ height: 65vh; \}', 
                 '@media (max-width: 768px) { #hero-container { height: 70vh; }', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ ヒーロー画像の高さを PC:90vh / スマホ:70vh に更新しました。")
