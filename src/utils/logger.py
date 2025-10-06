"""ログ管理クラス"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path


class Logger:
    """ログ管理クラス"""

    LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.logger = None
        self.setup_logger()
        self.rotate_logs()

    def setup_logger(self):
        """ロガーをセットアップ"""
        try:
            # ログディレクトリ作成
            self.log_dir.mkdir(exist_ok=True)

            # ログファイル名生成
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            log_file = self.log_dir / f"sortsnap_log_{timestamp}.txt"

            # ロガー設定
            self.logger = logging.getLogger("SortSnap")
            self.logger.setLevel(logging.INFO)

            # ファイルハンドラー
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))

            # コンソールハンドラー（デバッグ用）
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

            # ヘッダー情報を記録
            self._write_header()

        except Exception as e:
            print(f"ログシステムの初期化に失敗しました: {e}")
            self.logger = None

    def _write_header(self):
        """ログファイルのヘッダー情報を書き込み"""
        if not self.logger:
            return

        import platform
        from src.utils.constants import APP_NAME, APP_VERSION

        header = f"""{'='*60}
{APP_NAME} ログ
バージョン: {APP_VERSION}
日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
OS: {platform.system()} {platform.release()}
Python: {platform.python_version()}
{'='*60}
"""
        for line in header.strip().split('\n'):
            self.logger.info(line)

    def rotate_logs(self, max_logs: int = 30):
        """ログローテーション（最新30件まで保持）"""
        try:
            if not self.log_dir.exists():
                return

            # ログファイル一覧を取得
            log_files = sorted(
                self.log_dir.glob("sortsnap_log_*.txt"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )

            # 古いログを削除
            for old_log in log_files[max_logs:]:
                old_log.unlink()

        except Exception as e:
            print(f"ログローテーションに失敗しました: {e}")

    def info(self, message: str):
        """INFOログ"""
        if self.logger:
            self.logger.info(message)

    def warning(self, message: str):
        """WARNINGログ"""
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str, exc_info: bool = True):
        """ERRORログ（スタックトレース含む）"""
        if self.logger:
            self.logger.error(message, exc_info=exc_info)

    def open_log_folder(self):
        """ログフォルダを開く"""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(self.log_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(self.log_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(self.log_dir)])
        except Exception as e:
            self.error(f"ログフォルダを開けませんでした: {e}")
