"""プレビューダイアログ（画像拡大表示）"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
from src.models.image_model import ImageModel


class PreviewDialog(QDialog):
    """画像拡大表示ダイアログ"""

    # シグナル
    image_deleted = pyqtSignal(int)  # 削除した画像のインデックス

    def __init__(self, images: list[ImageModel], current_index: int, parent=None):
        super().__init__(parent)
        self.images = images
        self.current_index = current_index
        self.zoom_level = 1.0
        self.fit_to_window = True

        self.init_ui()
        self.setup_shortcuts()
        self.load_image(current_index)

    def init_ui(self):
        """UIを初期化"""
        self.setWindowTitle("画像プレビュー")
        self.resize(1200, 800)
        self.setModal(False)

        # 背景を暗く
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)

        layout = QVBoxLayout()

        # 画像表示エリア
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        layout.addWidget(self.image_label, 1)

        # 情報表示
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 11pt; padding: 8px;")
        layout.addWidget(self.info_label)

        # コントロールボタン
        control_layout = QHBoxLayout()

        self.prev_btn = QPushButton("← 前へ")
        self.prev_btn.clicked.connect(self.previous_image)
        control_layout.addWidget(self.prev_btn)

        control_layout.addStretch()

        zoom_out_btn = QPushButton("縮小 (-)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_btn)

        self.fit_btn = QPushButton("ウィンドウに合わせる")
        self.fit_btn.clicked.connect(self.fit_to_window_size)
        control_layout.addWidget(self.fit_btn)

        zoom_100_btn = QPushButton("100%")
        zoom_100_btn.clicked.connect(self.zoom_100)
        control_layout.addWidget(zoom_100_btn)

        zoom_in_btn = QPushButton("拡大 (+)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_btn)

        control_layout.addStretch()

        delete_btn = QPushButton("削除 (Del)")
        delete_btn.clicked.connect(self.delete_current_image)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
        """)
        control_layout.addWidget(delete_btn)

        control_layout.addStretch()

        # 閉じるボタン
        close_btn = QPushButton("閉じる (Esc)")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2196F3;
            }
        """)
        control_layout.addWidget(close_btn)

        control_layout.addStretch()

        self.next_btn = QPushButton("次へ →")
        self.next_btn.clicked.connect(self.next_image)
        control_layout.addWidget(self.next_btn)

        layout.addLayout(control_layout)

        self.setLayout(layout)

    def setup_shortcuts(self):
        """ショートカットを設定"""
        # 矢印キー
        QShortcut(Qt.Key.Key_Left, self).activated.connect(self.previous_image)
        QShortcut(Qt.Key.Key_Right, self).activated.connect(self.next_image)

        # Esc で閉じる
        QShortcut(Qt.Key.Key_Escape, self).activated.connect(self.close)

        # Delete/Space で削除
        QShortcut(Qt.Key.Key_Delete, self).activated.connect(self.delete_current_image)
        QShortcut(Qt.Key.Key_Space, self).activated.connect(self.delete_current_image)

        # ズーム
        QShortcut(QKeySequence.StandardKey.ZoomIn, self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence.StandardKey.ZoomOut, self).activated.connect(self.zoom_out)

    def load_image(self, index: int):
        """画像を読み込んで表示"""
        if index < 0 or index >= len(self.images):
            return

        self.current_index = index
        image = self.images[index]

        # フルサイズで画像を読み込み
        pixmap = QPixmap(image.file_path)

        if self.fit_to_window:
            # ウィンドウサイズに合わせる
            pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.zoom_level = pixmap.width() / QPixmap(image.file_path).width()
        else:
            # 指定のズームレベル
            new_width = int(pixmap.width() * self.zoom_level)
            new_height = int(pixmap.height() * self.zoom_level)
            pixmap = pixmap.scaled(
                new_width, new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        self.image_label.setPixmap(pixmap)

        # 情報を更新
        self.update_info()

        # ボタンの有効/無効
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.images) - 1)

    def update_info(self):
        """情報表示を更新"""
        image = self.images[self.current_index]
        info_text = (
            f"{image.filename}  |  "
            f"{image.size[0]} × {image.size[1]}  |  "
            f"{image.get_file_size_str()}  |  "
            f"{self.current_index + 1} / {len(self.images)}  |  "
            f"ズーム: {int(self.zoom_level * 100)}%"
        )
        self.info_label.setText(info_text)

    def next_image(self):
        """次の画像へ"""
        if self.current_index < len(self.images) - 1:
            self.load_image(self.current_index + 1)

    def previous_image(self):
        """前の画像へ"""
        if self.current_index > 0:
            self.load_image(self.current_index - 1)

    def zoom_in(self):
        """ズームイン"""
        self.fit_to_window = False
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        self.load_image(self.current_index)

    def zoom_out(self):
        """ズームアウト"""
        self.fit_to_window = False
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.load_image(self.current_index)

    def zoom_100(self):
        """100%表示"""
        self.fit_to_window = False
        self.zoom_level = 1.0
        self.load_image(self.current_index)

    def fit_to_window_size(self):
        """ウィンドウサイズに合わせる"""
        self.fit_to_window = True
        self.load_image(self.current_index)

    def delete_current_image(self):
        """現在の画像を削除"""
        # シグナルを発行
        self.image_deleted.emit(self.current_index)

        # 次の画像を表示
        if self.current_index < len(self.images) - 1:
            # 次の画像へ
            self.load_image(self.current_index)
        elif self.current_index > 0:
            # 最後の画像の場合は前へ
            self.load_image(self.current_index - 1)
        else:
            # 画像がなくなったら閉じる
            self.close()

    def resizeEvent(self, event):
        """ウィンドウリサイズ時"""
        super().resizeEvent(event)
        if self.fit_to_window and hasattr(self, 'current_index'):
            self.load_image(self.current_index)
