"""画像プレビューエリア"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QGridLayout, QLabel, QPushButton, QApplication
)
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QMimeData, QTimer, QRect, QSize
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QColor, QPen, QBrush, QFont
from src.models.image_model import ImageModel
from src.utils.animation import AnimationPlayer


class PreviewArea(QWidget):
    """画像プレビューエリア"""

    # シグナル
    selection_changed = pyqtSignal(list)
    order_changed = pyqtSignal(int, int)  # (from_index, to_index)
    order_changed_multiple = pyqtSignal(list, int)  # (from_indices, to_index) - 複数選択時
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
        # フォーカスを受け取れるように設定
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
            # サムネイル生成（常に現在のサイズで再生成）
            image.load_thumbnail(self.thumbnail_size)

            # サムネイルウィジェット作成
            thumbnail_widget = ThumbnailWidget(image, i, self, self.thumbnail_size, preview_area=self)
            thumbnail_widget.set_preview_area(self)  # 遅延バインディング：明示的に設定
            thumbnail_widget.clicked.connect(self._on_thumbnail_clicked)
            thumbnail_widget.double_clicked.connect(self._on_thumbnail_double_clicked)
            thumbnail_widget.preview_requested.connect(self._on_preview_requested)
            thumbnail_widget.drag_started.connect(self._on_drag_started)
            thumbnail_widget.drop_received.connect(self._on_drop_received)
            thumbnail_widget.drop_received_multiple.connect(self._on_drop_received_multiple)

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

        # アニメーション一時無効化
        placeholder = QLabel("画像をドラッグ&ドロップ\nまたは\nCtrl+O でフォルダを開く")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                color: #999;
                padding: 50px;
            }
        """)
        self.grid_layout.addWidget(placeholder, 0, 0, Qt.AlignmentFlag.AlignCenter)

    def update_thumbnail_size(self, size: int):
        """サムネイルサイズを変更"""
        from src.utils.constants import MIN_THUMBNAIL_SIZE, MAX_THUMBNAIL_SIZE

        size = max(MIN_THUMBNAIL_SIZE, min(MAX_THUMBNAIL_SIZE, size))
        if self.thumbnail_size == size:
            return  # サイズ変更なし

        self.thumbnail_size = size

        # ウィジェットが既に存在する場合は更新のみ（再作成しない）
        if self.thumbnail_widgets:
            self._update_existing_thumbnails(size)
        else:
            # 初回は通常の読み込み
            self.load_images(self.images)

    def _update_existing_thumbnails(self, size: int):
        """既存のサムネイルウィジェットを更新（超高速：Qt側でリサイズ）"""
        # レイアウト更新を一時停止（高速化）
        self.grid_widget.setUpdatesEnabled(False)

        # 新しい列数を計算
        cols = max(1, self.scroll.viewport().width() // (size + 20))

        # グリッドをクリアして再配置
        for i, widget in enumerate(self.thumbnail_widgets):
            # 古い位置から削除
            self.grid_layout.removeWidget(widget)

            # ウィジェットのサムネイル更新（Qtの scaled() を使用）
            widget.update_thumbnail_size(size)

            # 【重要】既存ウィジェットにもpreview_area参照を設定（遅延バインディング）
            widget.set_preview_area(self)

            # 新しい位置に配置
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(widget, row, col)

        # レイアウト更新を再開
        self.grid_widget.setUpdatesEnabled(True)
        self.grid_widget.update()

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
        """サムネイルクリック時（シングルクリック）"""
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
            # 通常クリック: 単一選択のみ（拡大表示はダブルクリックまたは虫眼鏡で）
            self.selected_indices = [index]
            self.last_selected_index = index

        # 選択状態を更新（ウィジェットとImageModelの両方）
        for i, widget in enumerate(self.thumbnail_widgets):
            is_selected = widget.index in self.selected_indices
            widget.set_selected(is_selected)
            # ImageModel.selectedも同期
            if i < len(self.images):
                self.images[i].selected = is_selected

        self.selection_changed.emit(self.selected_indices)

    def _on_thumbnail_double_clicked(self, index: int):
        """サムネイルダブルクリック時"""
        # 拡大表示
        self.image_clicked.emit(index)

    def _on_preview_requested(self, index: int):
        """虫眼鏡アイコンクリック時"""
        # 拡大表示
        self.image_clicked.emit(index)

    def _on_drag_started(self, index: int):
        """ドラッグ開始時"""
        # 選択されていない場合は選択
        if index not in self.selected_indices:
            self.selected_indices = [index]
            for i, widget in enumerate(self.thumbnail_widgets):
                is_selected = widget.index in self.selected_indices
                widget.set_selected(is_selected)
                # ImageModel.selectedも同期
                if i < len(self.images):
                    self.images[i].selected = is_selected

    def _on_drop_received(self, from_index: int, to_index: int):
        """ドロップ受信時（単一）"""
        if from_index != to_index:
            self.order_changed.emit(from_index, to_index)

    def _on_drop_received_multiple(self, from_indices: list[int], to_index: int):
        """ドロップ受信時（複数）"""
        self.order_changed_multiple.emit(from_indices, to_index)

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
    double_clicked = pyqtSignal(int)  # ダブルクリックシグナル
    preview_requested = pyqtSignal(int)  # 虫眼鏡クリックシグナル
    drag_started = pyqtSignal(int)
    drop_received = pyqtSignal(int, int)  # (from_index, to_index)
    drop_received_multiple = pyqtSignal(list, int)  # (from_indices, to_index) - 複数選択時

    def __init__(self, image: ImageModel, index: int, parent=None, thumbnail_size: int = 200, preview_area=None):
        super().__init__(parent)
        self.image = image
        self.index = index
        self.drag_start_position = None
        self.is_selected = False
        self.thumbnail_size = thumbnail_size
        self.preview_area = preview_area  # PreviewAreaへの参照を保持

        # 元のサムネイル（初回読み込み時のもの）を保持
        self.original_thumbnail = image.thumbnail

        # ダブルクリック検出用
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._handle_single_click)
        self.pending_click_event = None

        # ドラッグ&ドロップを有効化
        self.setAcceptDrops(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # サムネイル画像エリア（虫眼鏡ボタンを含む）
        self.thumbnail_container = QWidget()
        # サムネイルサイズに基づいてコンテナサイズを設定
        container_size = image.thumbnail.size() if image.thumbnail else QSize(thumbnail_size, thumbnail_size)
        self.thumbnail_container.setFixedSize(container_size)

        # 画像ラベル
        self.thumbnail_label = QLabel(self.thumbnail_container)
        if image.thumbnail:
            self.thumbnail_label.setPixmap(image.thumbnail)
            self.thumbnail_label.setFixedSize(image.thumbnail.size())
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.move(0, 0)

        # 虫眼鏡ボタン（右下にオーバーレイ）
        self.magnifier_btn = QPushButton("🔍", self.thumbnail_container)
        self.magnifier_btn.setFixedSize(36, 36)
        self.magnifier_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 180);
                color: white;
                border: 2px solid rgba(255, 255, 255, 200);
                border-radius: 18px;
                font-size: 16px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 220);
                border: 2px solid white;
            }
        """)

        # 虫眼鏡ボタンを右下に配置（コンテナサイズに基づく）
        self._update_magnifier_position()

        # ホバー時にプレビュー表示
        self.magnifier_btn.enterEvent = lambda e: self._on_magnifier_hover_enter()
        self.magnifier_btn.leaveEvent = lambda e: self._on_magnifier_hover_leave()
        self.magnifier_btn.clicked.connect(lambda: self.preview_requested.emit(self.index))

        layout.addWidget(self.thumbnail_container, alignment=Qt.AlignmentFlag.AlignCenter)

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

        # ホバータイマー（ホバー時に拡大表示）
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(lambda: self.preview_requested.emit(self.index))

        # デフォルトスタイル
        self.update_style()

    def _update_magnifier_position(self):
        """虫眼鏡ボタンの位置を更新"""
        btn_margin = 5
        btn_x = self.thumbnail_container.width() - self.magnifier_btn.width() - btn_margin
        btn_y = self.thumbnail_container.height() - self.magnifier_btn.height() - btn_margin
        self.magnifier_btn.move(btn_x, btn_y)

    def _on_magnifier_hover_enter(self):
        """虫眼鏡ホバー開始"""
        self.hover_timer.start(500)  # 500ms後にプレビュー表示

    def _on_magnifier_hover_leave(self):
        """虫眼鏡ホバー終了"""
        self.hover_timer.stop()

    def update_style(self):
        """スタイルを更新"""
        if self.is_selected:
            # 選択時：画像に太い青枠、背景も青系
            self.thumbnail_label.setStyleSheet("""
                QLabel {
                    border: 5px solid #2196F3;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
            self.setStyleSheet("""
                ThumbnailWidget {
                    background-color: #E3F2FD;
                    border-radius: 8px;
                }
            """)
        else:
            # 非選択時：画像に薄いグレー枠
            self.thumbnail_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #E0E0E0;
                    border-radius: 2px;
                    background-color: white;
                }
            """)
            self.setStyleSheet("""
                ThumbnailWidget {
                    background-color: white;
                }
                ThumbnailWidget:hover {
                    background-color: #F5F5F5;
                }
            """)

    def set_selected(self, selected: bool):
        """選択状態を設定"""
        self.is_selected = selected
        self.update_style()

    def set_preview_area(self, preview_area):
        """PreviewArea参照を設定（遅延バインディング）"""
        self.preview_area = preview_area

    def update_thumbnail_size(self, size: int):
        """サムネイルサイズを変更（超高速：Qt側でリサイズ）"""
        self.thumbnail_size = size

        if not self.original_thumbnail:
            return

        # 元のサムネイルをQt側でリサイズ（Pillowでの再生成なし）
        scaled_pixmap = self.original_thumbnail.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation  # 高品質リサイズ
        )

        # コンテナとラベルのサイズを更新
        new_size = scaled_pixmap.size()
        self.thumbnail_container.setFixedSize(new_size)
        self.thumbnail_label.setPixmap(scaled_pixmap)
        self.thumbnail_label.setFixedSize(new_size)

        # 虫眼鏡ボタンの位置を更新
        self._update_magnifier_position()

    def mouseMoveEvent(self, event):
        """マウス移動時（ドラッグ）"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self.drag_start_position:
            return

        # ドラッグ距離チェック
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # ダブルクリック待機中ならキャンセル
        if self.click_timer.isActive():
            self.click_timer.stop()

        # ドラッグ開始
        self.drag_started.emit(self.index)

        drag = QDrag(self)
        mime_data = QMimeData()

        # 複数選択されている場合は選択されたインデックスをすべて渡す
        if not hasattr(self, 'preview_area') or self.preview_area is None:
            # 防御的プログラミング: preview_area未設定時は単一ドラッグにフォールバック
            mime_data.setText(str(self.index))
        else:
            selected_indices = [i for i, img in enumerate(self.preview_area.images) if img.selected]
            if len(selected_indices) > 1 and self.index in selected_indices:
                # 複数選択されており、ドラッグ元も選択されている
                indices_str = ",".join(map(str, selected_indices))
                mime_data.setText(indices_str)
            else:
                # 単一のドラッグ
                mime_data.setText(str(self.index))

        drag.setMimeData(mime_data)

        # ドラッグ時のプレビュー画像
        if self.image.thumbnail:
            pixmap = self.image.thumbnail.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        drag.exec(Qt.DropAction.MoveAction)

    def mousePressEvent(self, event):
        """マウス押下時"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

            # ダブルクリック検出のため、シングルクリックを遅延処理
            if self.click_timer.isActive():
                # 既にタイマーが動いている = ダブルクリック
                self.click_timer.stop()
                self.double_clicked.emit(self.index)
                self.pending_click_event = None
            else:
                # シングルクリックの可能性
                self.pending_click_event = (self.index, QApplication.keyboardModifiers())
                self.click_timer.start(QApplication.doubleClickInterval())

    def _handle_single_click(self):
        """シングルクリック処理（ダブルクリックでなかった場合）"""
        if self.pending_click_event:
            index, modifiers = self.pending_click_event
            self.clicked.emit(index, modifiers)
            self.pending_click_event = None

    def dragEnterEvent(self, event):
        """ドラッグ侵入時"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """ドロップ時"""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            to_index = self.index

            # カンマ区切りの場合は複数選択
            if "," in text:
                from_indices = [int(idx) for idx in text.split(",")]
                self.drop_received_multiple.emit(from_indices, to_index)
            else:
                from_index = int(text)
                self.drop_received.emit(from_index, to_index)

            event.acceptProposedAction()
