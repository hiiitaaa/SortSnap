"""CSVファイルをUTF-8 BOM付きで保存するスクリプト

Excelで開く際の文字化けを防ぐため、BOM付きで保存します。
"""

import codecs

# CSVファイルを読み込み
with open('animations/animations.csv', 'r', encoding='utf-8') as f:
    content = f.read()

# UTF-8 BOM付きで保存
with codecs.open('animations/animations.csv', 'w', encoding='utf-8-sig') as f:
    f.write(content)

print("OK: animations/animations.csv をUTF-8 BOM付きで保存しました")
print("Excelで開いても文字化けしません")
