"""スプラッシュスクリーン"""
from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
from src.utils.animation import AnimationPlayer
from src.utils.constants import APP_NAME, APP_VERSION


class SplashScreen(QSplashScreen):
    """起動時のスプラッシュスクリーン"""

    def __init__(self):
        # 透明な背景で初期化
        pixmap = QPixmap(400, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)

        self.init_ui()

    def init_ui(self):
        """UIを初期化"""
        # 中央ウィジェット
        widget = QWidget(self)
        widget.setGeometry(0, 0, 400, 400)
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # アニメーション
        try:
            self.animation_player = AnimationPlayer("splash", widget)
            self.animation_player.setFixedSize(300, 300)
            layout.addWidget(self.animation_player, alignment=Qt.AlignmentFlag.AlignCenter)
        except:
            # アニメーション読み込み失敗時はテキストのみ
            pass

        # アプリ名
        app_label = QLabel(APP_NAME)
        app_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        app_label.setFont(font)
        layout.addWidget(app_label)

        # バージョン
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666; font-size: 11pt;")
        layout.addWidget(version_label)

        # メッセージラベル
        self.message_label = QLabel("起動中...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #999; font-size: 10pt;")
        layout.addWidget(self.message_label)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: #f5f5f5;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        widget.setLayout(layout)

    def show_message(self, message: str, progress: int = None):
        """
        メッセージと進捗を表示

        Args:
            message: 表示するメッセージ
            progress: 進捗率（0-100）
        """
        self.message_label.setText(message)
        if progress is not None:
            self.progress_bar.setValue(progress)

        # UIを更新
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

    def start_animation(self):
        """アニメーションを開始"""
        if hasattr(self, 'animation_player'):
            self.animation_player.play()

    def stop_animation(self):
        """アニメーションを停止"""
        if hasattr(self, 'animation_player'):
            self.animation_player.stop()
