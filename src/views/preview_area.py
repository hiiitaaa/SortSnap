"""画像プレビューエリア"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QGridLayout, QLabel, QPushButton, QApplication
)
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QMimeData
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QColor
from src.models.image_model import ImageModel
from src.utils.animation import AnimationPlayer


class PreviewArea(QWidget):
    """画像プレビューエリア"""

    # シグナル
    selection_changed = pyqtSignal(list)
    order_changed = pyqtSignal(int, int)  # (from_index, to_index)
    image_clicked = pyqtSignal(int)
    delete_requested = pyqtSignal(list)  # 削除する画像のインデックスリスト

    def __init__(self, parent=None):
        super().__init__(parent)
        self.images: list[ImageModel] = []
        self.thumbnail_widgets: list = []
        self.thumbnail_size: int = 200
        self.animation_player: AnimationPlayer = None
        self.selected_indices: list[int] = []
        self.last_selected_index: int = -1

        self.init_ui()

    def init_ui(self):
        """UIを初期化"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # スクロールエリア
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # グリッドコンテナ
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_widget.setLayout(self.grid_layout)

        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)

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
        self.selected_indices.clear()
        self.last_selected_index = -1

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
            thumbnail_widget = ThumbnailWidget(image, i, self)
            thumbnail_widget.clicked.connect(self._on_thumbnail_clicked)
            thumbnail_widget.drag_started.connect(self._on_drag_started)
            thumbnail_widget.drop_received.connect(self._on_drop_received)

            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(thumbnail_widget, row, col)
            self.thumbnail_widgets.append(thumbnail_widget)

        # 選択状態を復元
        for widget in self.thumbnail_widgets:
            widget.set_selected(widget.index in self.selected_indices)

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
            self.animation_player.setFixedSize(300, 300)

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

    def _on_thumbnail_clicked(self, index: int, modifiers):
        """サムネイルクリック時"""
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+クリック: トグル選択
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            else:
                self.selected_indices.append(index)
            self.last_selected_index = index

        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Shift+クリック: 範囲選択
            if self.last_selected_index >= 0:
                start = min(self.last_selected_index, index)
                end = max(self.last_selected_index, index)
                self.selected_indices = list(range(start, end + 1))
            else:
                self.selected_indices = [index]
                self.last_selected_index = index

        else:
            # 通常クリック: 単一選択
            self.selected_indices = [index]
            self.last_selected_index = index
            # ダブルクリックで拡大表示
            self.image_clicked.emit(index)

        # 選択状態を更新
        for widget in self.thumbnail_widgets:
            widget.set_selected(widget.index in self.selected_indices)

        self.selection_changed.emit(self.selected_indices)

    def _on_drag_started(self, index: int):
        """ドラッグ開始時"""
        # 選択されていない場合は選択
        if index not in self.selected_indices:
            self.selected_indices = [index]
            for widget in self.thumbnail_widgets:
                widget.set_selected(widget.index in self.selected_indices)

    def _on_drop_received(self, from_index: int, to_index: int):
        """ドロップ受信時"""
        if from_index != to_index:
            self.order_changed.emit(from_index, to_index)

    def keyPressEvent(self, event):
        """キーボードイベント"""
        # Delete/Space: 削除
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Space):
            if self.selected_indices:
                self.delete_requested.emit(self.selected_indices)

        # Ctrl+A: 全選択
        elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.selected_indices = list(range(len(self.images)))
            for widget in self.thumbnail_widgets:
                widget.set_selected(True)
            self.selection_changed.emit(self.selected_indices)

        # Ctrl+D / Esc: 選択解除
        elif (event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier) or \
             event.key() == Qt.Key.Key_Escape:
            self.selected_indices.clear()
            for widget in self.thumbnail_widgets:
                widget.set_selected(False)
            self.selection_changed.emit(self.selected_indices)

        super().keyPressEvent(event)


class ThumbnailWidget(QWidget):
    """ドラッグ可能なサムネイルウィジェット"""

    clicked = pyqtSignal(int, Qt.KeyboardModifier)
    drag_started = pyqtSignal(int)
    drop_received = pyqtSignal(int, int)  # (from_index, to_index)

    def __init__(self, image: ImageModel, index: int, parent=None):
        super().__init__(parent)
        self.image = image
        self.index = index
        self.drag_start_position = None
        self.is_selected = False

        # ドラッグ&ドロップを有効化
        self.setAcceptDrops(True)

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

        # デフォルトスタイル
        self.update_style()

    def update_style(self):
        """スタイルを更新"""
        if self.is_selected:
            self.setStyleSheet("""
                ThumbnailWidget {
                    border: 3px solid #2196F3;
                    border-radius: 4px;
                    background-color: #E3F2FD;
                }
            """)
        else:
            self.setStyleSheet("""
                ThumbnailWidget {
                    border: 2px solid transparent;
                    border-radius: 4px;
                    background-color: white;
                }
                ThumbnailWidget:hover {
                    border: 2px solid #BBDEFB;
                }
            """)

    def set_selected(self, selected: bool):
        """選択状態を設定"""
        self.is_selected = selected
        self.update_style()

    def mousePressEvent(self, event):
        """マウス押下時"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.clicked.emit(self.index, QApplication.keyboardModifiers())

    def mouseMoveEvent(self, event):
        """マウス移動時（ドラッグ）"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self.drag_start_position:
            return

        # ドラッグ距離チェック
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # ドラッグ開始
        self.drag_started.emit(self.index)

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.index))
        drag.setMimeData(mime_data)

        # ドラッグ時のプレビュー画像
        if self.image.thumbnail:
            pixmap = self.image.thumbnail.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        """ドラッグ侵入時"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """ドロップ時"""
        if event.mimeData().hasText():
            from_index = int(event.mimeData().text())
            to_index = self.index
            self.drop_received.emit(from_index, to_index)
            event.acceptProposedAction()
