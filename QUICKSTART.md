# SortSnap クイックスタートガイド

## 📦 すぐに始める

### 1. セットアップ（初回のみ）

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 起動

```bash
python main.py
```

## 🚀 基本的な使い方

1. **フォルダを開く**: `Ctrl+O` または メニュー「ファイル」→「フォルダを開く」
2. **画像を並べ替える**: サムネイルをクリック（※ドラッグ&ドロップは未実装）
3. **リネーム設定**: 右パネルで命名規則を選択
4. **保存**: 「💾 保存」ボタンをクリック

## 📋 現在の機能

### ✅ 動作する機能
- フォルダから画像読み込み（.jpg, .jpeg, .png）
- サムネイル表示
- サムネイルサイズ調整（`Ctrl++`, `Ctrl+-`, `Ctrl+0`）
- ソート機能（ファイル名順）
- リネーム（3種類のテンプレート）
- Undo/Redo（`Ctrl+Z`, `Ctrl+Shift+Z`）
- PNG→JPG変換
- 設定の自動保存

### ⚠️ 未実装の機能
- ドラッグ&ドロップによる並べ替え
- 複数選択（Ctrl+クリック、範囲選択）
- 画像拡大表示ダイアログ
- 保存時のプログレスバー
- 新規フォルダ作成モード
- アニメーション表示

## 📂 重要なファイル

| ファイル | 説明 |
|---------|------|
| `README.md` | ユーザーマニュアル（詳細な使い方） |
| `DEVELOPMENT.md` | 開発経過記録（技術的な詳細） |
| `GIT_SETUP.md` | GitHubへのプッシュ手順 |
| `QUICKSTART.md` | 本ファイル（すぐに始めるガイド） |

## 🔧 開発を続ける

### 次に実装すべき機能（優先順位順）

1. **ドラッグ&ドロップ並べ替え** - 最も重要な機能
2. **複数選択機能** - Ctrl+クリック、Shift+クリック
3. **プレビューダイアログ** - 画像拡大表示
4. **プログレスバー** - 保存時の進捗表示

### 開発の流れ

```bash
# 1. 新しいブランチを作成
git checkout -b feature/drag-and-drop

# 2. コードを編集

# 3. テスト
python main.py

# 4. コミット
git add .
git commit -m "feat: ドラッグ&ドロップ機能を実装"

# 5. DEVELOPMENT.mdを更新
# - 実装した機能を記録
# - 既知の問題を更新

# 6. コミット＆プッシュ
git add DEVELOPMENT.md
git commit -m "docs: DEVELOPMENT.mdを更新"
git push -u origin feature/drag-and-drop
```

## 🐛 トラブルシューティング

### アプリが起動しない
```bash
# Python バージョン確認（3.10以降が必要）
python --version

# 依存関係を再インストール
pip install --upgrade -r requirements.txt
```

### 画像が読み込めない
- 対応形式: .jpg, .jpeg, .png のみ
- フォルダのアクセス権限を確認

### ログを確認
```
logs/sortsnap_log_*.txt
```

## 📞 引き継ぎ・質問

### 引き継ぎを受ける場合
1. このファイル（QUICKSTART.md）を読む
2. `DEVELOPMENT.md`で現状を把握
3. `README.md`で機能を確認
4. `python main.py`で動作確認

### コードの場所
- **画像操作**: `src/controllers/image_controller.py`
- **UI**: `src/views/main_window.py`
- **設定**: `src/models/config_model.py`

---

**最終更新**: 2025-10-06
**ステータス**: Phase 1完了、基本機能動作OK
