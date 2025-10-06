SortSnap_技術要件定義書_v1.0.md
markdown# SortSnap 技術要件定義書

**バージョン**: 1.0  
**作成日**: 2025年10月6日  
**最終更新**: 2025年10月6日

---

## 目次

1. [技術スタック](#1-技術スタック)
2. [アーキテクチャ設計](#2-アーキテクチャ設計)
3. [モジュール構成](#3-モジュール構成)
4. [データ構造](#4-データ構造)
5. [主要クラス設計](#5-主要クラス設計)
6. [UI実装詳細](#6-ui実装詳細)
7. [パフォーマンス最適化](#7-パフォーマンス最適化)
8. [ビルド・パッケージング](#8-ビルドパッケージング)
9. [開発環境](#9-開発環境)
10. [テスト戦略](#10-テスト戦略)
11. [セキュリティ考慮事項](#11-セキュリティ考慮事項)
12. [デプロイメント](#12-デプロイメント)

---

## 1. 技術スタック

### 1.1 コア技術

| 技術 | バージョン | 用途 |
|---|---|---|
| **Python** | 3.10+ | メイン開発言語 |
| **PyQt6** | 6.6+ | GUIフレームワーク |
| **Pillow** | 10.0+ | 画像処理 |
| **PyInstaller** | 6.0+ | 実行ファイル化 |

**選定理由**:
- **Python**: クロスプラットフォーム、豊富なライブラリ
- **PyQt6**: 成熟したGUIフレームワーク、高いパフォーマンス
- **Pillow**: 軽量で高速な画像処理
- **PyInstaller**: 単一実行ファイル生成が容易

### 1.2 標準ライブラリ
```python
import json          # 設定ファイル管理
import os            # ファイルシステム操作
import sys           # システム情報
import logging       # ログ管理
import datetime      # 日付処理
import pathlib       # パス操作
import glob          # ファイル検索
import shutil        # ファイル操作
import csv           # アニメーション定義読み込み
1.3 除外するライブラリ
以下のライブラリは使用しない（ファイルサイズ削減、起動高速化）:

numpy
pandas
matplotlib
opencv-cv2（Pillowで十分）
requests（オフライン動作）


2. アーキテクチャ設計
2.1 設計パターン
MVC（Model-View-Controller）パターンを採用
┌─────────────────────────────────────┐
│         View（PyQt6 GUI）           │
│  - MainWindow                       │
│  - SettingsPanel                    │
│  - ImagePreviewArea                 │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│      Controller（ビジネスロジック） │
│  - ImageController                  │
│  - RenameController                 │
│  - FileController                   │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│         Model（データ層）           │
│  - ImageModel                       │
│  - ConfigModel                      │
│  - HistoryModel                     │
└─────────────────────────────────────┘
2.2 ディレクトリ構造
SortSnap/
├── main.py                      # エントリーポイント
├── config.json                  # 設定ファイル（実行時生成）
├── requirements.txt             # 依存関係
├── README.md                    # ユーザーマニュアル
│
├── src/
│   ├── __init__.py
│   │
│   ├── models/                  # データモデル
│   │   ├── __init__.py
│   │   ├── image_model.py       # 画像データ管理
│   │   ├── config_model.py      # 設定データ管理
│   │   └── history_model.py     # Undo/Redo履歴管理
│   │
│   ├── controllers/             # コントローラー
│   │   ├── __init__.py
│   │   ├── image_controller.py  # 画像操作ロジック
│   │   ├── rename_controller.py # リネームロジック
│   │   └── file_controller.py   # ファイル操作ロジック
│   │
│   ├── views/                   # UI
│   │   ├── __init__.py
│   │   ├── main_window.py       # メインウィンドウ
│   │   ├── settings_panel.py    # 設定パネル
│   │   ├── preview_area.py      # 画像プレビューエリア
│   │   ├── preview_dialog.py    # 拡大表示ダイアログ
│   │   ├── progress_dialog.py   # プログレスバー
│   │   └── splash_screen.py     # スプラッシュスクリーン
│   │
│   ├── utils/                   # ユーティリティ
│   │   ├── __init__.py
│   │   ├── logger.py            # ログ管理
│   │   ├── validator.py         # ファイル名検証
│   │   ├── animation.py         # アニメーション再生
│   │   └── constants.py         # 定数定義
│   │
│   └── resources/               # リソース
│       ├── icons/               # アイコン画像
│       └── styles/              # スタイルシート
│
├── animations/                  # アニメーション
│   ├── animations.csv
│   └── frames/
│       ├── splash_001.png ~ splash_030.png
│       └── idle_001.png ~ idle_060.png
│
├── logs/                        # ログフォルダ（実行時生成）
│   └── sortsnap_log_*.txt
│
└── build/                       # ビルド出力（.gitignore）
    ├── SortSnap.exe             # Windows版
    └── SortSnap.app             # macOS版

3. モジュール構成
3.1 モデル層
3.1.1 ImageModel
責務: 画像データの管理
pythonclass ImageModel:
    """画像データを管理するモデル"""
    
    def __init__(self, file_path: str):
        self.file_path: str           # 元ファイルパス
        self.filename: str            # ファイル名
        self.extension: str           # 拡張子
        self.size: tuple              # (幅, 高さ)
        self.file_size: int           # ファイルサイズ（bytes）
        self.thumbnail: QPixmap       # サムネイル画像
        self.index: int               # 現在の並び順
        self.selected: bool = False   # 選択状態
    
    def load_thumbnail(self, size: int = 200):
        """サムネイルを生成"""
        pass
    
    def get_new_filename(self, template: str, number: int, digits: int) -> str:
        """リネーム後のファイル名を生成"""
        pass
3.1.2 ConfigModel
責務: 設定データの永続化
pythonclass ConfigModel:
    """設定データを管理するモデル"""
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "mode": "folder",
        "last_input_folder": "",
        "last_output_folder": "",
        "rename_template": "sequential",
        "rename_prefix": "",
        "rename_start_number": 1,
        "rename_digits": 3,
        "jpg_convert": False,
        "jpg_quality": 95,
        "show_save_confirmation": True,
        "thumbnail_size": 200,
        "window_size": [1920, 1080],
        "window_position": None,
        "enable_animations": True
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load()
    
    def load(self) -> dict:
        """設定ファイルを読み込み"""
        pass
    
    def save(self):
        """設定ファイルを保存"""
        pass
    
    def get(self, key: str, default=None):
        """設定値を取得"""
        pass
    
    def set(self, key: str, value):
        """設定値を更新して即座に保存"""
        pass
3.1.3 HistoryModel
責務: Undo/Redo履歴の管理
pythonclass HistoryModel:
    """Undo/Redo履歴を管理するモデル"""
    
    MAX_HISTORY = 50  # 最大履歴数
    
    def __init__(self):
        self.undo_stack: list = []  # Undoスタック
        self.redo_stack: list = []  # Redoスタック
    
    def push(self, action: dict):
        """アクションを履歴に追加"""
        pass
    
    def undo(self) -> dict:
        """Undoを実行して前の状態を返す"""
        pass
    
    def redo(self) -> dict:
        """Redoを実行"""
        pass
    
    def can_undo(self) -> bool:
        """Undo可能か"""
        pass
    
    def can_redo(self) -> bool:
        """Redo可能か"""
        pass
    
    def clear(self):
        """履歴をクリア"""
        pass
アクションデータ構造:
python{
    "type": "delete",  # delete, reorder, sort
    "timestamp": "2025-10-06 14:30:15",
    "data": {
        # typeに応じたデータ
    }
}

3.2 コントローラー層
3.2.1 ImageController
責務: 画像の読み込み、並べ替え、削除などの操作
pythonclass ImageController:
    """画像操作を管理するコントローラー"""
    
    def __init__(self):
        self.images: list[ImageModel] = []
        self.history: HistoryModel = HistoryModel()
    
    def load_from_folder(self, folder_path: str) -> list[ImageModel]:
        """フォルダから画像を読み込み"""
        pass
    
    def load_from_files(self, file_paths: list[str]) -> list[ImageModel]:
        """ファイルリストから画像を読み込み"""
        pass
    
    def reorder(self, from_index: int, to_index: int):
        """画像の順序を変更（履歴に記録）"""
        pass
    
    def delete_images(self, indices: list[int]):
        """画像を削除（履歴に記録）"""
        pass
    
    def sort_by_name(self, ascending: bool = True):
        """ファイル名順にソート（履歴に記録）"""
        pass
    
    def undo(self):
        """Undoを実行"""
        pass
    
    def redo(self):
        """Redoを実行"""
        pass
3.2.2 RenameController
責務: リネームロジック
pythonclass RenameController:
    """リネーム処理を管理するコントローラー"""
    
    TEMPLATES = {
        "sequential": "{number}.{ext}",
        "text_number": "{prefix}_{number}.{ext}",
        "date_number": "{date}_{number}.{ext}"
    }
    
    def generate_filename(
        self,
        template: str,
        prefix: str = "",
        number: int = 1,
        digits: int = 3,
        extension: str = "jpg"
    ) -> str:
        """ファイル名を生成"""
        pass
    
    def validate_filename(self, filename: str) -> tuple[bool, list[str]]:
        """ファイル名を検証（有効性、エラーリスト）"""
        pass
    
    def sanitize_filename(self, filename: str) -> str:
        """ファイル名を安全な形式に変換"""
        pass
    
    def generate_sample_names(
        self,
        template: str,
        prefix: str,
        start: int,
        digits: int,
        count: int = 3
    ) -> list[str]:
        """サンプルファイル名を生成"""
        pass
3.2.3 FileController
責務: ファイル保存、フォルダ作成
pythonclass FileController:
    """ファイル操作を管理するコントローラー"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def save_images(
        self,
        images: list[ImageModel],
        output_path: str,
        rename_settings: dict,
        jpg_convert: bool = False,
        jpg_quality: int = 95,
        progress_callback=None,
        cancel_flag=None
    ) -> tuple[int, int, list[dict]]:
        """
        画像を保存
        
        Returns:
            (成功数, 失敗数, エラーリスト)
        """
        pass
    
    def create_folder(self, parent_path: str, folder_name: str) -> str:
        """新規フォルダを作成"""
        pass
    
    def convert_png_to_jpg(
        self,
        image_path: str,
        output_path: str,
        quality: int = 95
    ) -> bool:
        """PNG→JPG変換"""
        pass

3.3 ビュー層
3.3.1 MainWindow
責務: メインウィンドウの管理
pythonclass MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigModel()
        self.image_controller = ImageController()
        self.rename_controller = RenameController()
        self.file_controller = FileController()
        
        self.init_ui()
        self.setup_menu_bar()
        self.setup_shortcuts()
        self.restore_state()
    
    def init_ui(self):
        """UIを初期化"""
        # 左右分割レイアウト
        # - 左: PreviewArea (4/5)
        # - 右: SettingsPanel (1/5)
        pass
    
    def setup_menu_bar(self):
        """メニューバーを構築"""
        pass
    
    def setup_shortcuts(self):
        """キーボードショートカットを設定"""
        pass
    
    def open_folder(self):
        """フォルダを開く"""
        pass
    
    def save_images(self):
        """保存実行"""
        pass
3.3.2 PreviewArea
責務: 画像プレビューエリア
pythonclass PreviewArea(QWidget):
    """画像プレビューエリア"""
    
    # シグナル
    selection_changed = pyqtSignal(list)  # 選択変更
    order_changed = pyqtSignal()          # 順序変更
    
    def __init__(self):
        super().__init__()
        self.images: list[ImageModel] = []
        self.selected_indices: list[int] = []
        self.thumbnail_size: int = 200
        
        self.init_ui()
        self.setup_drag_drop()
    
    def init_ui(self):
        """UIを初期化（グリッドレイアウト）"""
        pass
    
    def load_images(self, images: list[ImageModel]):
        """画像を読み込んで表示"""
        pass
    
    def update_thumbnail_size(self, size: int):
        """サムネイルサイズを変更"""
        pass
    
    def handle_drag(self, event):
        """ドラッグ処理"""
        pass
    
    def handle_drop(self, event):
        """ドロップ処理"""
        pass
    
    def show_idle_animation(self):
        """idleアニメーションを表示"""
        pass
3.3.3 SettingsPanel
責務: 設定パネル
pythonclass SettingsPanel(QWidget):
    """設定パネル"""
    
    # シグナル
    mode_changed = pyqtSignal(str)          # モード変更
    settings_changed = pyqtSignal(dict)     # 設定変更
    save_requested = pyqtSignal()           # 保存リクエスト
    
    def __init__(self, config: ConfigModel):
        super().__init__()
        self.config = config
        self.init_ui()
        self.restore_settings()
    
    def init_ui(self):
        """UIを初期化"""
        # セクション1: モード選択
        # セクション2: リネーム設定
        # セクション3: JPG変換設定
        # セクション4: 出力先設定
        # セクション5: 保存ボタン
        pass
    
    def get_rename_settings(self) -> dict:
        """リネーム設定を取得"""
        pass
    
    def update_sample_names(self):
        """サンプル名をリアルタイム更新"""
        pass
    
    def validate_inputs(self) -> tuple[bool, str]:
        """入力値を検証"""
        pass
3.3.4 PreviewDialog
責務: 拡大表示ダイアログ
pythonclass PreviewDialog(QDialog):
    """画像拡大表示ダイアログ"""
    
    # シグナル
    image_deleted = pyqtSignal(int)  # 画像削除
    
    def __init__(self, images: list[ImageModel], current_index: int):
        super().__init__()
        self.images = images
        self.current_index = current_index
        self.zoom_level = 1.0
        
        self.init_ui()
        self.load_image(current_index)
    
    def init_ui(self):
        """UIを初期化（オーバーレイスタイル）"""
        pass
    
    def load_image(self, index: int):
        """画像を読み込んで表示"""
        pass
    
    def next_image(self):
        """次の画像へ"""
        pass
    
    def previous_image(self):
        """前の画像へ"""
        pass
    
    def zoom_in(self):
        """ズームイン"""
        pass
    
    def zoom_out(self):
        """ズームアウト"""
        pass
    
    def delete_current_image(self):
        """現在の画像を削除"""
        pass
3.3.5 ProgressDialog
責務: プログレスバーダイアログ
pythonclass ProgressDialog(QDialog):
    """保存処理プログレスバー"""
    
    # シグナル
    cancel_requested = pyqtSignal()
    
    def __init__(self, total: int):
        super().__init__()
        self.total = total
        self.current = 0
        self.start_time = time.time()
        
        self.init_ui()
    
    def init_ui(self):
        """UIを初期化"""
        pass
    
    def update_progress(self, current: int, filename: str):
        """進捗を更新（100msごとに呼ばれる）"""
        pass
    
    def calculate_remaining_time(self) -> str:
        """残り時間を計算"""
        pass
    
    def cancel(self):
        """キャンセル確認"""
        pass
3.3.6 SplashScreen
責務: スプラッシュスクリーン
pythonclass SplashScreen(QSplashScreen):
    """起動時のスプラッシュスクリーン"""
    
    def __init__(self):
        super().__init__()
        self.animation_player = AnimationPlayer("splash")
        self.init_ui()
    
    def init_ui(self):
        """UIを初期化"""
        pass
    
    def show_message(self, message: str, progress: int):
        """メッセージと進捗を表示"""
        pass

3.4 ユーティリティ
3.4.1 Logger
責務: ログ管理
pythonclass Logger:
    """ログ管理クラス"""
    
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.setup_logger()
        self.rotate_logs()
    
    def setup_logger(self):
        """ロガーをセットアップ"""
        pass
    
    def rotate_logs(self, max_logs: int = 30):
        """ログローテーション（30件まで保持）"""
        pass
    
    def info(self, message: str):
        """INFOログ"""
        pass
    
    def warning(self, message: str):
        """WARNINGログ"""
        pass
    
    def error(self, message: str, exc_info: bool = True):
        """ERRORログ（スタックトレース含む）"""
        pass
3.4.2 Validator
責務: ファイル名検証
pythonclass Validator:
    """ファイル名検証ユーティリティ"""
    
    INVALID_CHARS = r'<>:"/\|?*'
    RESERVED_NAMES = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 260
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, list[str]]:
        """ファイル名を検証"""
        errors = []
        
        # 不正文字チェック
        # 予約語チェック
        # 長さチェック
        # 先頭・末尾チェック
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """ファイル名を安全に変換"""
        # 不正文字を _ に置換
        # 末尾のスペース・ピリオドを削除
        pass
3.4.3 AnimationPlayer
責務: アニメーション再生
pythonclass AnimationPlayer(QWidget):
    """アニメーション再生クラス"""
    
    def __init__(self, animation_id: str):
        super().__init__()
        self.animation_id = animation_id
        self.animation_data = self.load_animation_csv(animation_id)
        self.frames = self.load_frames()
        self.current_frame = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
    
    def load_animation_csv(self, animation_id: str) -> dict:
        """animations.csvから定義を読み込み"""
        pass
    
    def load_frames(self) -> list[QPixmap]:
        """全フレームをプリロード"""
        pass
    
    def play(self):
        """再生開始"""
        frame_duration = 1000 / self.animation_data['fps']
        self.timer.start(frame_duration)
    
    def stop(self):
        """再生停止"""
        self.timer.stop()
    
    def update_frame(self):
        """フレームを更新"""
        self.update()
        self.current_frame += 1
        
        if self.current_frame >= len(self.frames):
            if self.animation_data['loop']:
                self.current_frame = 0
            else:
                self.stop()
3.4.4 Constants
責務: 定数定義
python# constants.py

APP_NAME = "SortSnap"
APP_VERSION = "1.0.0"
BUILD_DATE = "2025-10-15"

# ファイル形式
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png"]

# デフォルト値
DEFAULT_THUMBNAIL_SIZE = 200
MIN_THUMBNAIL_SIZE = 100
MAX_THUMBNAIL_SIZE = 400
THUMBNAIL_SIZE_STEP = 50

DEFAULT_JPG_QUALITY = 95
DEFAULT_RENAME_DIGITS = 3
DEFAULT_RENAME_START = 1

# ログ
MAX_LOG_FILES = 30

# Undo/Redo
MAX_HISTORY = 50

# UI
WINDOW_DEFAULT_SIZE = (1920, 1080)
WINDOW_MIN_SIZE = (1280, 720)

# アニメーション
ANIMATION_CSV_PATH = "animations/animations.csv"
ANIMATION_FRAMES_DIR = "animations/frames"

4. データ構造
4.1 config.json
json{
  "version": "1.0.0",
  "mode": "folder",
  "last_input_folder": "C:\\Users\\Documents\\Photos",
  "last_output_folder": "C:\\Users\\Documents\\Output",
  "rename_template": "text_number",
  "rename_prefix": "MyImage",
  "rename_start_number": 1,
  "rename_digits": 3,
  "jpg_convert": false,
  "jpg_quality": 95,
  "show_save_confirmation": true,
  "thumbnail_size": 200,
  "window_size": [1920, 1080],
  "window_position": [100, 100],
  "enable_animations": true
}
4.2 animations.csv
csvanimation_id,name,frame_count,fps,loop,frame_prefix,description
splash,スプラッシュ,30,30,false,splash_,起動時のアニメーション
idle,待機中,60,24,true,idle_,画像未読み込み時のアニメーション
4.3 ログファイル形式
=====================================
SortSnap ログ
バージョン: 1.0.0
日時: 2025-10-06 14:30:15
OS: Windows 11 22H2
Python: 3.12.0
=====================================

[2025-10-06 14:30:15] [INFO] アプリケーション起動
[2025-10-06 14:30:15] [INFO] 設定ファイル読み込み: config.json
[2025-10-06 14:30:20] [INFO] フォルダ読み込み開始: C:\Users\Documents\Photos
[2025-10-06 14:30:22] [INFO] 対応画像: 1,234枚検出
[2025-10-06 14:35:00] [INFO] 保存処理開始
[2025-10-06 14:35:30] [ERROR] ファイル保存エラー
[2025-10-06 14:35:30] [ERROR] スタックトレース:
  File "main.py", line 123, in save_image
[2025-10-06 14:45:30] [INFO] アプリケーション終了

5. 主要クラス設計
5.1 クラス図（簡略版）
┌─────────────────┐
│   MainWindow    │
└────────┬────────┘
         │
         ├─────────────────┬──────────────────┐
         │                 │                  │
    ┌────▼────┐      ┌────▼────┐      ┌─────▼──────┐
    │Preview  │      │Settings │      │MenuBar     │
    │Area     │      │Panel    │      │            │
    └────┬────┘      └────┬────┘      └────────────┘
         │                │
         │                │
    ┌────▼────────────────▼────┐
    │   ImageController        │
    └────┬────────────────┬────┘
         │                │
    ┌────▼────┐      ┌────▼────┐
    │Image    │      │History  │
    │Model    │      │Model    │
    └─────────┘      └─────────┘

6. UI実装詳細
6.1 PyQt6 主要ウィジェット
機能使用ウィジェットメインウィンドウQMainWindowレイアウトQHBoxLayout, QVBoxLayout, QGridLayoutスクロールQScrollAreaサムネイル表示QLabel（QPixmap）ドラッグ&ドロップカスタムQWidget（ドラッグイベント実装）ラジオボタンQRadioButtonチェックボックスQCheckBoxドロップダウンQComboBoxテキスト入力QLineEdit数値入力QSpinBoxスライダーQSliderボタンQPushButtonプログレスバーQProgressBarダイアログQDialogメニューバーQMenuBarタイマーQTimer
6.2 スタイルシート（QSS）
css/* メインウィンドウ */
QMainWindow {
    background-color: #f5f5f5;
}

/* 設定パネル */
QWidget#SettingsPanel {
    background-color: #ffffff;
    border-left: 1px solid #e0e0e0;
}

/* 区切り線 */
QFrame[frameShape="4"] {
    color: #e0e0e0;
}

/* 入力欄 */
QLineEdit, QSpinBox {
    height: 32px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #2196F3;
}

/* ボタン */
QPushButton {
    height: 32px;
    border-radius: 4px;
    padding: 4px 16px;
}

QPushButton#SaveButton {
    height: 40px;
    background-color: #2196F3;
    color: white;
    font-size: 14pt;
}

QPushButton#SaveButton:hover {
    background-color: #1976D2;
}

/* サムネイル選択状態 */
QLabel.selected {
    border: 3px solid #2196F3;
}
6.3 ドラッグ&ドロップ実装
pythonclass ThumbnailWidget(QLabel):
    """ドラッグ可能なサムネイルウィジェット"""
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        
        # ドラッグ開始
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.index))
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        # ドロップ処理
        from_index = int(event.mimeData().text())
        to_index = self.index
        self.parent().reorder_images(from_index, to_index)

7. パフォーマンス最適化
7.1 サムネイル生成の最適化
pythondef generate_thumbnail(image_path: str, size: int = 200) -> QPixmap:
    """
    サムネイルを高速生成
    
    最適化ポイント:
    - Pillowでリサイズ（PyQt6より高速）
    - アスペクト比維持
    - キャッシュ利用
    """
    from PIL import Image
    
    img = Image.open(image_path)
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    
    # PIL Image → QPixmap
    img_qt = ImageQt.ImageQt(img)
    pixmap = QPixmap.fromImage(img_qt)
    
    return pixmap
7.2 非同期読み込み
pythonclass ImageLoader(QThread):
    """画像を非同期で読み込むスレッド"""
    
    progress = pyqtSignal(int, ImageModel)
    finished = pyqtSignal(list)
    
    def __init__(self, file_paths: list[str], thumbnail_size: int):
        super().__init__()
        self.file_paths = file_paths
        self.thumbnail_size = thumbnail_size
    
    def run(self):
        images = []
        total = len(self.file_paths)
        
        for i, path in enumerate(self.file_paths):
            try:
                image = ImageModel(path)
                image.load_thumbnail(self.thumbnail_size)
                images.append(image)
                self.progress.emit(i + 1, image)
            except Exception as e:
                logging.error(f"画像読み込みエラー: {path}", exc_info=True)
        
        self.finished.emit(images)
7.3 メモリ管理
pythondef clear_thumbnails():
    """不要なサムネイルをメモリから解放"""
    for image in self.images:
        if image.thumbnail:
            image.thumbnail = None
    
    import gc
    gc.collect()

8. ビルド・パッケージング
8.1 PyInstallerの設定
sortsnap.spec:
python# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('animations', 'animations'),
        ('README.md', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'tornado',
        'zmq'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SortSnap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリ
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/sortsnap.ico'  # アイコン
)
8.2 ビルドコマンド
Windows:
bashpyinstaller sortsnap.spec
macOS:
bashpyinstaller sortsnap.spec --osx-bundle-identifier com.yourname.sortsnap
8.3 ファイルサイズ削減
最適化手法:

不要なライブラリを除外（excludes）
UPX圧縮を有効化（upx=True）
アニメーションフレームを最適化（PNG圧縮）
PyQt6の不要なモジュールを除外

目標サイズ:

Windows: 40〜50MB
macOS: 50〜60MB


9. 開発環境
9.1 推奨開発環境

OS: Windows 11 / macOS 14+
Python: 3.10+ (推奨: 3.12)
IDE: Visual Studio Code / PyCharm
Git: バージョン管理

9.2 仮想環境セットアップ
bash# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
9.3 requirements.txt
PyQt6==6.6.1
PyQt6-Qt6==6.6.1
PyQt6-sip==13.6.0
Pillow==10.2.0
PyInstaller==6.3.0
9.4 開発ツール
bash# コードフォーマッター
pip install black

# リンター
pip install pylint flake8

# 型チェック
pip install mypy

10. テスト戦略
10.1 ユニットテスト
pytestを使用:
python# tests/test_rename_controller.py

import pytest
from src.controllers.rename_controller import RenameController

def test_generate_filename():
    controller = RenameController()
    
    # 連番のみ
    result = controller.generate_filename(
        template="sequential",
        number=1,
        digits=3,
        extension="jpg"
    )
    assert result == "001.jpg"
    
    # テキスト + 連番
    result = controller.generate_filename(
        template="text_number",
        prefix="MyImage",
        number=5,
        digits=3,
        extension="png"
    )
    assert result == "MyImage_005.png"

def test_validate_filename():
    controller = RenameController()
    
    # 有効なファイル名
    valid, errors = controller.validate_filename("image_001.jpg")
    assert valid == True
    assert len(errors) == 0
    
    # 不正文字を含む
    valid, errors = controller.validate_filename("image<001>.jpg")
    assert valid == False
    assert "不正な文字" in errors[0]
    
    # 予約語
    valid, errors = controller.validate_filename("CON.jpg")
    assert valid == False
    assert "予約語" in errors[0]
10.2 統合テスト
python# tests/test_integration.py

def test_folder_mode_workflow():
    """フォルダモードの完全なワークフロー"""
    
    # 1. フォルダから画像読み込み
    controller = ImageController()
    images = controller.load_from_folder("tests/fixtures/images")
    assert len(images) == 5
    
    # 2. 並べ替え
    controller.reorder(0, 2)
    assert images[2].index == 0
    
    # 3. Undo
    controller.undo()
    assert images[0].index == 0
    
    # 4. 保存
    file_controller = FileController()
    success, fail, errors = file_controller.save_images(
        images,
        output_path="tests/output",
        rename_settings={...}
    )
    assert success == 5
    assert fail == 0
10.3 UIテスト
pytest-qtを使用:
python# tests/test_ui.py

from pytestqt.qtbot import QtBot

def test_settings_panel(qtbot):
    """設定パネルのテスト"""
    
    panel = SettingsPanel(config)
    qtbot.addWidget(panel)
    
    # テンプレート変更
    panel.template_combo.setCurrentText("テキスト + 連番")
    assert panel.prefix_input.isVisible()
    
    # プレフィックス入力
    qtbot.keyClicks(panel.prefix_input, "MyImage")
    assert panel.get_rename_settings()["prefix"] == "MyImage"

11. セキュリティ考慮事項
11.1 ファイルパス検証
pythondef validate_path(path: str) -> bool:
    """パストラバーサル攻撃を防ぐ"""
    # 絶対パスに変換
    abs_path = os.path.abspath(path)
    
    # 許可されたディレクトリ内かチェック
    # ".." を含むパスを拒否
    if ".." in path:
        return False
    
    return True
11.2 入力サニタイズ
pythondef sanitize_input(text: str) -> str:
    """ユーザー入力をサニタイズ"""
    # HTMLタグを除去
    text = re.sub(r'<[^>]*>', '', text)
    
    # 制御文字を除去
    text = ''.join(char for char in text if ord(char) >= 32)
    
    return text
11.3 権限チェック
pythondef check_write_permission(path: str) -> bool:
    """書き込み権限をチェック"""
    try:
        test_file = os.path.join(path, '.sortsnap_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except:
        return False

12. デプロイメント
12.1 配布パッケージ構成
Windows版:
SortSnap_v1.0.0_Windows.zip
├── SortSnap.exe
├── README.md
└── animations/
    ├── animations.csv
    └── frames/
        ├── splash_*.png
        └── idle_*.png
macOS版:
SortSnap_v1.0.0_macOS.dmg
└── SortSnap.app
    ├── Contents/
    └── [README.md と animations は同梱]
12.2 リリースチェックリスト

 全てのユニットテストが通過
 統合テストが通過
 Windows版ビルド完了
 macOS版ビルド完了
 README.md 更新
 アニメーションサンプル同梱確認
 バージョン番号更新
 ログ機能動作確認
 実機テスト（Windows 10/11, macOS 11+）
 ファイルサイズ確認（50MB以下）

12.3 更新手順

バージョン番号を更新（constants.py, README.md）
CHANGELOG.md を更新
ビルド実行
テスト実行
GitHubリリース作成
配布ファイルをアップロード


付録
A. 開発規約
コーディングスタイル:

PEP 8 に準拠
関数・メソッドに型ヒントを使用
docstring を記述（Google Style）

コミットメッセージ:
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
refactor: リファクタリング
test: テスト追加
B. トラブルシューティング
ビルドエラー:

PyInstallerのバージョンを確認
仮想環境を再作成
キャッシュをクリア: pyinstaller --clean

起動エラー:

ログファイルを確認
依存ライブラリのバージョンを確認