import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# PC版の高さを 90vh から 85vh に変更
# (もし以前の 80vh が残っていても置換できるように両方対応)
content = content.replace('height: 90vh;', 'height: 85vh;')
content = content.replace('height: 80vh;', 'height: 85vh;')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ PC版のヒーロー画像を 85vh に調整しました。")
