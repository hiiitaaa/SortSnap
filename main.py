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

    # スプラッシュスクリーン表示
    splash = SplashScreen()
    splash.show()
    splash.start_animation()

    # 初期化処理をシミュレート
    splash.show_message("設定を読み込んでいます...", 20)
    QApplication.processEvents()
    time.sleep(0.3)

    splash.show_message("リソースを読み込んでいます...", 40)
    QApplication.processEvents()
    time.sleep(0.3)

    splash.show_message("UIを初期化しています...", 60)
    QApplication.processEvents()

    # メインウィンドウを作成
    window = MainWindow()

    splash.show_message("起動準備完了", 90)
    QApplication.processEvents()
    time.sleep(0.2)

    splash.show_message("起動中...", 100)
    QApplication.processEvents()
    time.sleep(0.3)

    # スプラッシュスクリーンを閉じてメインウィンドウを表示
    splash.stop_animation()
    splash.finish(window)
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
