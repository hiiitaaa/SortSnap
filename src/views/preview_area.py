"""画像プレビューエリア"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from src.models.image_model import ImageModel
from src.utils.animation import AnimationPlayer


class PreviewArea(QWidget):
    """画像プレビューエリア"""

    # シグナル
    selection_changed = pyqtSignal(list)
    order_changed = pyqtSignal()
    image_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.images: list[ImageModel] = []
        self.thumbnail_widgets: list[QLabel] = []
        self.thumbnail_size: int = 200
        self.animation_player: AnimationPlayer = None

        self.init_ui()

    def init_ui(self):
        """UIを初期化"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # グリッドコンテナ
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_widget.setLayout(self.grid_layout)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        # コントロールボタン
        control_layout = QHBoxLayout()

        # サムネイルサイズ調整
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_btn)

        reset_btn = QPushButton("リセット")
        reset_btn.clicked.connect(self.reset_zoom)
        control_layout.addWidget(reset_btn)

        control_layout.addWidget(QLabel("|"))

        # ソートボタン
        sort_asc_btn = QPushButton("名前▲")
        sort_asc_btn.clicked.connect(lambda: self.sort_requested.emit(True))
        control_layout.addWidget(sort_asc_btn)

        sort_desc_btn = QPushButton("名前▼")
        sort_desc_btn.clicked.connect(lambda: self.sort_requested.emit(False))
        control_layout.addWidget(sort_desc_btn)

        restore_btn = QPushButton("元の順序")
        restore_btn.clicked.connect(self.restore_requested.emit)
        control_layout.addWidget(restore_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        self.setLayout(layout)

        # 初期表示：idleアニメーション
        self.show_idle_animation()

    # シグナル定義
    sort_requested = pyqtSignal(bool)
    restore_requested = pyqtSignal()

    def load_images(self, images: list[ImageModel]):
        """画像を読み込んで表示"""
        self.images = images
        self.clear_grid()

        if not images:
            self.show_idle_animation()
            return

        # アニメーション停止
        if self.animation_player:
            self.animation_player.stop()
            self.animation_player.hide()

        # サムネイルを生成して表示
        cols = max(1, self.width() // (self.thumbnail_size + 20))

        for i, image in enumerate(images):
            # サムネイル生成
            if not image.thumbnail:
                image.load_thumbnail(self.thumbnail_size)

            # サムネイルウィジェット作成
            thumbnail_widget = ThumbnailWidget(image, i)
            thumbnail_widget.clicked.connect(self._on_thumbnail_clicked)

            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(thumbnail_widget, row, col)
            self.thumbnail_widgets.append(thumbnail_widget)

    def clear_grid(self):
        """グリッドをクリア"""
        for widget in self.thumbnail_widgets:
            widget.deleteLater()
        self.thumbnail_widgets.clear()

        # グリッドレイアウトをクリア
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_idle_animation(self):
        """idleアニメーションを表示"""
        self.clear_grid()

        if not self.animation_player:
            self.animation_player = AnimationPlayer("idle", self.grid_widget)

        self.animation_player.show()
        self.animation_player.play()

        # 中央配置
        self.grid_layout.addWidget(self.animation_player, 0, 0, Qt.AlignmentFlag.AlignCenter)

    def update_thumbnail_size(self, size: int):
        """サムネイルサイズを変更"""
        from src.utils.constants import MIN_THUMBNAIL_SIZE, MAX_THUMBNAIL_SIZE

        size = max(MIN_THUMBNAIL_SIZE, min(MAX_THUMBNAIL_SIZE, size))
        self.thumbnail_size = size

        # 再描画
        self.load_images(self.images)

    def zoom_in(self):
        """拡大"""
        from src.utils.constants import THUMBNAIL_SIZE_STEP
        self.update_thumbnail_size(self.thumbnail_size + THUMBNAIL_SIZE_STEP)

    def zoom_out(self):
        """縮小"""
        from src.utils.constants import THUMBNAIL_SIZE_STEP
        self.update_thumbnail_size(self.thumbnail_size - THUMBNAIL_SIZE_STEP)

    def reset_zoom(self):
        """リセット"""
        from src.utils.constants import DEFAULT_THUMBNAIL_SIZE
        self.update_thumbnail_size(DEFAULT_THUMBNAIL_SIZE)

    def _on_thumbnail_clicked(self, index: int):
        """サムネイルクリック時"""
        self.image_clicked.emit(index)


class ThumbnailWidget(QWidget):
    """サムネイルウィジェット"""

    clicked = pyqtSignal(int)

    def __init__(self, image: ImageModel, index: int, parent=None):
        super().__init__(parent)
        self.image = image
        self.index = index

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # サムネイル画像
        self.thumbnail_label = QLabel()
        if image.thumbnail:
            self.thumbnail_label.setPixmap(image.thumbnail)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.thumbnail_label)

        # ファイル名表示
        name_label = QLabel(image.filename)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-size: 9pt;")
        layout.addWidget(name_label)

        # 連番表示
        number_label = QLabel(f"{index + 1:03d}")
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setStyleSheet("font-size: 8pt; color: #666;")
        layout.addWidget(number_label)

        self.setLayout(layout)

        # 選択状態のスタイル
        self.setStyleSheet("""
            ThumbnailWidget {
                border: 2px solid transparent;
                border-radius: 4px;
            }
            ThumbnailWidget:hover {
                border: 2px solid #BBDEFB;
            }
        """)

    def mousePressEvent(self, event):
        """マウスクリック時"""
        self.clicked.emit(self.index)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        """選択状態を設定"""
        if selected:
            self.setStyleSheet("""
                ThumbnailWidget {
                    border: 3px solid #2196F3;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                ThumbnailWidget {
                    border: 2px solid transparent;
                    border-radius: 4px;
                }
                ThumbnailWidget:hover {
                    border: 2px solid #BBDEFB;
                }
            """)
