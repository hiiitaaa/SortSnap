"""SortSnap メインエントリーポイント"""
import sys
from PyQt6.QtWidgets import QApplication
from src.views.main_window import MainWindow
from src.utils.constants import APP_NAME


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # メインウィンドウを作成・表示
    window = MainWindow()
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
