"""メインウィンドウ"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFileDialog,
    QMessageBox, QMenuBar, QMenu
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
from src.models.config_model import ConfigModel
from src.controllers.image_controller import ImageController
from src.controllers.rename_controller import RenameController
from src.controllers.file_controller import FileController
from src.views.settings_panel import SettingsPanel
from src.views.preview_area import PreviewArea
from src.utils.constants import WINDOW_DEFAULT_SIZE, WINDOW_MIN_SIZE
from src.utils.logger import Logger


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.config = ConfigModel()
        self.image_controller = ImageController()
        self.rename_controller = RenameController()
        self.file_controller = FileController(self.logger)

        self.init_ui()
        self.setup_menu_bar()
        self.setup_shortcuts()
        self.restore_state()

        self.logger.info("アプリケーション起動")

    def init_ui(self):
        """UIを初期化"""
        self.setWindowTitle("SortSnap")
        self.setMinimumSize(*WINDOW_MIN_SIZE)

        # ドラッグ&ドロップを有効化
        self.setAcceptDrops(True)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト（左右分割）
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左: プレビューエリア（4/5）
        self.preview_area = PreviewArea()
        self.preview_area.image_clicked.connect(self._on_image_clicked)
        self.preview_area.sort_requested.connect(self._on_sort_requested)
        self.preview_area.restore_requested.connect(self._on_restore_order)
        self.preview_area.order_changed.connect(self._on_order_changed)
        self.preview_area.delete_requested.connect(self._on_delete_requested)
        layout.addWidget(self.preview_area, 4)

        # 右: 設定パネル（1/5）
        self.settings_panel = SettingsPanel(self.config)
        self.settings_panel.mode_changed.connect(self._on_mode_changed)
        self.settings_panel.save_requested.connect(self._on_save_requested)
        self.settings_panel.open_folder_requested.connect(self.open_folder)
        layout.addWidget(self.settings_panel, 1)

        central_widget.setLayout(layout)

    def setup_menu_bar(self):
        """メニューバーを構築"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")

        open_action = QAction("フォルダを開く(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_requested)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        quit_action = QAction("終了(&X)", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # 編集メニュー
        edit_menu = menubar.addMenu("編集(&E)")

        undo_action = QAction("元に戻す(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("やり直し(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(redo_action)

        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")

        log_action = QAction("ログフォルダを開く(&L)", self)
        log_action.triggered.connect(self.logger.open_log_folder)
        help_menu.addAction(log_action)

        help_menu.addSeparator()

        about_action = QAction("バージョン情報(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def setup_shortcuts(self):
        """キーボードショートカットを設定"""
        pass  # メニューバーで設定済み

    def open_folder(self):
        """フォルダを開く"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "フォルダを選択",
            self.config.get("last_input_folder", "")
        )

        if folder:
            self.load_folder(folder)

    def _on_mode_changed(self, mode: str):
        """モード変更時"""
        self.logger.info(f"モード変更: {mode}")

    def _on_save_requested(self):
        """保存リクエスト時"""
        if not self.image_controller.images:
            QMessageBox.warning(self, "警告", "保存する画像がありません。")
            return

        # 設定を取得
        rename_settings = self.settings_panel.get_rename_settings()
        jpg_convert = self.settings_panel.jpg_convert_check.isChecked()
        jpg_quality = self.settings_panel.quality_slider.value()
        output_path = self.settings_panel.output_path_input.text()

        if not output_path:
            QMessageBox.warning(self, "警告", "出力先フォルダを指定してください。")
            return

        # 新規フォルダ作成モードの場合
        mode = self.config.get("mode", "folder")
        if mode == "new_folder":
            new_folder_name = self.settings_panel.new_folder_input.text().strip()
            if not new_folder_name:
                from datetime import datetime
                new_folder_name = datetime.now().strftime("%y%m%d")

            try:
                # 新規フォルダを作成
                output_path = self.file_controller.create_folder(output_path, new_folder_name)
                self.logger.info(f"新規フォルダ作成: {output_path}")
            except FileExistsError:
                QMessageBox.warning(
                    self,
                    "エラー",
                    f"フォルダ '{new_folder_name}' は既に存在します。\n別の名前を指定してください。"
                )
                return
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"フォルダの作成に失敗しました。\n\n{str(e)}"
                )
                return

        # 保存確認ダイアログ
        if self.config.get("show_save_confirmation", True):
            reply = QMessageBox.question(
                self,
                "保存確認",
                f"以下の設定で保存しますか?\n\n"
                f"処理枚数: {len(self.image_controller.images)}枚\n"
                f"出力先: {output_path}\n"
                f"リネーム形式: {rename_settings['template']}\n"
                f"JPG変換: {'あり' if jpg_convert else 'なし'}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        # 保存処理（非同期 + プログレスバー）
        self.logger.info(f"保存処理開始: {len(self.image_controller.images)}枚")

        from src.views.progress_dialog import ProgressDialog
        from src.controllers.save_worker import SaveWorker

        # プログレスダイアログを表示
        progress_dialog = ProgressDialog(len(self.image_controller.images), self)

        # ワーカースレッド作成
        self.save_worker = SaveWorker(
            self.file_controller,
            self.image_controller.images,
            output_path,
            rename_settings,
            jpg_convert,
            jpg_quality
        )

        # シグナル接続
        self.save_worker.progress.connect(progress_dialog.update_progress)
        self.save_worker.finished.connect(
            lambda success, fail, errors: self._on_save_finished(
                success, fail, errors, progress_dialog
            )
        )
        progress_dialog.cancel_requested.connect(self.save_worker.cancel)

        # 保存開始
        self.save_worker.start()
        progress_dialog.exec()

    def _on_save_finished(self, success: int, fail: int, errors: list, progress_dialog):
        """保存完了時"""
        # プログレスダイアログを閉じる
        if not progress_dialog.is_cancelled():
            import time
            time.sleep(1)  # 完了メッセージを1秒表示
        progress_dialog.accept()

        # 結果表示
        if fail == 0:
            QMessageBox.information(
                self,
                "完了",
                f"{success}枚の画像を保存しました。"
            )
        else:
            QMessageBox.warning(
                self,
                "完了（一部失敗）",
                f"成功: {success}枚\n失敗: {fail}枚\n\n詳細はログを確認してください。"
            )

    def _on_image_clicked(self, index: int):
        """画像クリック時"""
        from src.views.preview_dialog import PreviewDialog

        dialog = PreviewDialog(self.image_controller.images, index, self)
        dialog.image_deleted.connect(lambda idx: self._on_delete_requested([idx]))
        dialog.exec()

    def _on_sort_requested(self, ascending: bool):
        """ソートリクエスト時"""
        self.image_controller.sort_by_name(ascending)
        self.preview_area.load_images(self.image_controller.images)

    def _on_restore_order(self):
        """元の順序に戻す"""
        self.image_controller.restore_original_order()
        self.preview_area.load_images(self.image_controller.images)

    def _on_undo(self):
        """Undo"""
        if self.image_controller.undo():
            self.preview_area.load_images(self.image_controller.images)

    def _on_redo(self):
        """Redo"""
        if self.image_controller.redo():
            self.preview_area.load_images(self.image_controller.images)

    def _on_order_changed(self, from_index: int, to_index: int):
        """順序変更時（ドラッグ&ドロップ）"""
        self.image_controller.reorder(from_index, to_index)
        self.preview_area.load_images(self.image_controller.images)
        self.logger.info(f"画像を並べ替え: {from_index} → {to_index}")

    def _on_delete_requested(self, indices: list[int]):
        """削除リクエスト時"""
        if not indices:
            return

        # 確認ダイアログ
        reply = QMessageBox.question(
            self,
            "削除確認",
            f"{len(indices)}枚の画像を削除しますか？\n\n"
            "この操作はUndo可能です。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.image_controller.delete_images(indices)
            self.preview_area.load_images(self.image_controller.images)
            self.logger.info(f"{len(indices)}枚の画像を削除")

    def _show_about(self):
        """バージョン情報を表示"""
        from src.utils.constants import APP_NAME, APP_VERSION, BUILD_DATE

        QMessageBox.about(
            self,
            f"{APP_NAME} について",
            f"<h2>{APP_NAME}</h2>"
            f"<p>バージョン: {APP_VERSION}</p>"
            f"<p>ビルド日: {BUILD_DATE}</p>"
            f"<p>画像並べ替え・リネームツール</p>"
        )

    def restore_state(self):
        """ウィンドウ状態を復元"""
        # ウィンドウサイズ
        size = self.config.get("window_size", WINDOW_DEFAULT_SIZE)
        self.resize(*size)

        # ウィンドウ位置
        pos = self.config.get("window_position")
        if pos:
            self.move(*pos)

    def dragEnterEvent(self, event):
        """ドラッグ侵入時"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """ドロップ時（ファイル/フォルダ）"""
        urls = event.mimeData().urls()
        if not urls:
            return

        from pathlib import Path

        # ドロップされたファイル/フォルダを取得
        paths = [Path(url.toLocalFile()) for url in urls]

        # フォルダが含まれている場合
        folders = [p for p in paths if p.is_dir()]
        if folders:
            # 最初のフォルダを開く
            self.load_folder(str(folders[0]))
            return

        # 画像ファイルのみの場合
        image_files = []
        for path in paths:
            if path.is_file():
                ext = path.suffix.lower()
                from src.utils.constants import SUPPORTED_FORMATS
                if ext in SUPPORTED_FORMATS:
                    image_files.append(str(path))

        if image_files:
            # 新規フォルダ作成モードに切り替え
            self.settings_panel.new_folder_mode_radio.setChecked(True)
            self.logger.info(f"{len(image_files)}枚の画像ファイルをドロップ受信")

            # 画像を読み込み
            images = self.image_controller.load_from_files(image_files)
            self.preview_area.load_images(images)

            # デフォルトの出力先を設定
            if image_files:
                first_file = Path(image_files[0])
                default_output = str(first_file.parent)
                self.settings_panel.output_path_input.setText(default_output)
                self.config.set("last_output_folder", default_output)

    def load_folder(self, folder_path: str):
        """フォルダを読み込む（内部メソッド）"""
        self.logger.info(f"フォルダ読み込み開始: {folder_path}")
        images = self.image_controller.load_from_folder(folder_path)

        if not images:
            QMessageBox.warning(
                self,
                "警告",
                "対応する画像ファイルが見つかりませんでした。"
            )
            self.logger.warning(f"対応画像なし: {folder_path}")
            return

        self.logger.info(f"対応画像: {len(images)}枚検出")

        # 設定を保存
        self.config.set("last_input_folder", folder_path)
        self.settings_panel.output_path_input.setText(folder_path)
        self.config.set("last_output_folder", folder_path)

        # プレビュー表示
        self.preview_area.load_images(images)

    def closeEvent(self, event):
        """ウィンドウを閉じる時"""
        # ウィンドウ状態を保存
        self.config.set("window_size", [self.width(), self.height()])
        self.config.set("window_position", [self.x(), self.y()])

        # 設定を保存
        self.settings_panel.save_settings()

        self.logger.info("アプリケーション終了")
        event.accept()
