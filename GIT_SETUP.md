# Git セットアップ手順

## ローカルリポジトリ作成完了

✅ Gitリポジトリの初期化完了
✅ 全ファイルのコミット完了
✅ DEVELOPMENT.mdに開発経過を記録完了

## GitHub（またはGitLab）へのプッシュ手順

### 1. GitHubでリポジトリを作成

1. https://github.com にアクセス
2. 「New repository」をクリック
3. リポジトリ名: `SortSnap`
4. Description: `画像ファイル並べ替え・リネームツール`
5. Public または Private を選択
6. **"Initialize this repository with a README" はチェックしない**
7. 「Create repository」をクリック

### 2. リモートリポジトリを追加してプッシュ

GitHubでリポジトリ作成後、以下のコマンドを実行:

```bash
# リモートリポジトリを追加（URLはGitHubで表示されたものを使用）
git remote add origin https://github.com/YOUR_USERNAME/SortSnap.git

# ブランチ名をmainに変更（オプション）
git branch -M main

# プッシュ
git push -u origin main
```

### 3. SSH認証を使う場合

```bash
# リモートリポジトリを追加（SSH URL）
git remote add origin git@github.com:YOUR_USERNAME/SortSnap.git

# プッシュ
git push -u origin main
```

## 現在のコミット状況

```
コミットハッシュ: 0a0bf0c
コミットメッセージ: feat: SortSnap初期実装完了（Phase 1）
ファイル数: 26個
追加行数: 4,842行
```

## 含まれるファイル

### ドキュメント
- README.md - ユーザーマニュアル
- DEVELOPMENT.md - 開発経過記録
- GIT_SETUP.md - Git セットアップ手順（本ファイル）
- SortSnap_要件定義書_v2.0.md
- SortSnap_技術要件定義書_v1.0.md

### ソースコード
- main.py - メインエントリーポイント
- requirements.txt - 依存関係
- .gitignore - Git除外設定

### src/ ディレクトリ
- models/ - データモデル（ImageModel, ConfigModel, HistoryModel）
- controllers/ - ビジネスロジック（ImageController, RenameController, FileController）
- views/ - UI（MainWindow, SettingsPanel, PreviewArea）
- utils/ - ユーティリティ（Logger, Validator, AnimationPlayer, Constants）

### その他
- animations/animations.csv - アニメーション定義

## 次回以降の作業フロー

### 変更をコミット

```bash
# 変更をステージング
git add .

# コミット
git commit -m "feat: 新機能の説明"

# プッシュ
git push
```

### ブランチを使った開発

```bash
# 新しいブランチを作成
git checkout -b feature/drag-and-drop

# 作業...

# コミット
git add .
git commit -m "feat: ドラッグ&ドロップ機能を実装"

# プッシュ
git push -u origin feature/drag-and-drop

# GitHubでプルリクエストを作成してマージ
```

## リポジトリのクローン（別の環境で作業する場合）

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/SortSnap.git

# ディレクトリに移動
cd SortSnap

# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート（Windows）
venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
python main.py
```

## トラブルシューティング

### プッシュ時に認証エラーが出る場合

1. **Personal Access Token（PAT）を使用**
   - GitHub Settings → Developer settings → Personal access tokens
   - "Generate new token (classic)" を選択
   - `repo` スコープにチェック
   - トークンをコピー
   - プッシュ時にパスワードの代わりにトークンを使用

2. **SSH鍵を設定**
   ```bash
   # SSH鍵を生成
   ssh-keygen -t ed25519 -C "your_email@example.com"

   # 公開鍵をコピー
   cat ~/.ssh/id_ed25519.pub

   # GitHubのSettings → SSH and GPG keys → New SSH keyに貼り付け
   ```

### リモートURLの確認・変更

```bash
# 現在のリモートURLを確認
git remote -v

# リモートURLを変更
git remote set-url origin NEW_URL
```

## 開発経過の記録方法

新しい機能を追加したら、`DEVELOPMENT.md`を更新してコミット:

```bash
# DEVELOPMENT.mdを編集
# - 開発履歴セクションに日付と実装内容を追記
# - 実装済み機能リストを更新
# - 既知の問題を更新

# コミット
git add DEVELOPMENT.md
git commit -m "docs: DEVELOPMENT.mdを更新"
git push
```

## 引き継ぎ時の手順

1. **リポジトリをクローン**
2. **DEVELOPMENT.mdを確認** - 開発経過と現状を把握
3. **README.mdを確認** - 使い方を理解
4. **要件定義書を確認** - 実装すべき機能を把握
5. **次の開発ステップを確認** - 優先順位を確認

---

**作成日**: 2025-10-06
**リポジトリ**: https://github.com/hiiitaaa/SortSnap
**ステータス**: ✅ プッシュ済み
