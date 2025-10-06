"""SortSnap メインエントリーポイント"""
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.views.main_window import MainWindow
from src.views.splash_screen import SplashScreen
from src.utils.constants import APP_NAME


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # スプラッシュスクリーン（一時的に無効化）
    # splash = SplashScreen()
    # splash.show()
    # splash.start_animation()

    # メインウィンドウを作成・表示
    window = MainWindow()
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
