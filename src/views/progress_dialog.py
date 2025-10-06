"""プログレスバーダイアログ"""
import time
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt


class ProgressDialog(QDialog):
    """保存処理プログレスバー"""

    # シグナル
    cancel_requested = pyqtSignal()

    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self.cancelled = False

        self.init_ui()

    def init_ui(self):
        """UIを初期化"""
        self.setWindowTitle("保存中...")
        self.setModal(True)
        self.setFixedWidth(500)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # メインメッセージ
        self.message_label = QLabel("画像を保存しています...")
        self.message_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(self.message_label)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.total)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 詳細情報
        self.detail_label = QLabel("0 / 0")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.detail_label)

        # 現在のファイル名
        self.current_file_label = QLabel("")
        self.current_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_file_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.current_file_label)

        # 経過時間・残り時間
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #666;")
        layout.addWidget(self.time_label)

        # キャンセルボタン
        self.cancel_btn = QPushButton("キャンセル")
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 24px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        layout.addWidget(self.cancel_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def update_progress(self, current: int, filename: str = ""):
        """
        進捗を更新

        Args:
            current: 現在の処理数
            filename: 現在処理中のファイル名
        """
        self.current = current
        self.progress_bar.setValue(current)

        # 詳細情報
        percentage = int((current / self.total) * 100) if self.total > 0 else 0
        self.detail_label.setText(f"{current} / {self.total} ({percentage}%)")

        # 現在のファイル名
        if filename:
            self.current_file_label.setText(f"処理中: {filename}")

        # 経過時間・残り時間
        elapsed = time.time() - self.start_time
        if current > 0:
            avg_time = elapsed / current
            remaining = int(avg_time * (self.total - current))
            remaining_str = self._format_time(remaining)
            elapsed_str = self._format_time(int(elapsed))
            self.time_label.setText(f"経過: {elapsed_str} / 残り: 約{remaining_str}")
        else:
            self.time_label.setText("計算中...")

        # 完了時
        if current >= self.total:
            self.message_label.setText("保存が完了しました！")
            self.cancel_btn.setText("閉じる")
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 24px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)

    def _format_time(self, seconds: int) -> str:
        """
        秒数を読みやすい形式に変換

        Args:
            seconds: 秒数

        Returns:
            フォーマットされた時間文字列
        """
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}分{secs}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}時間{minutes}分"

    def _on_cancel_clicked(self):
        """キャンセルボタンクリック時"""
        if self.current >= self.total:
            # 完了後は閉じる
            self.accept()
        else:
            # キャンセル確認
            from PyQt6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                "キャンセル確認",
                f"保存処理をキャンセルしますか？\n\n"
                f"これまでに{self.current}枚の画像が保存されました。\n"
                f"保存済みのファイルはそのまま残ります。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.cancelled = True
                self.cancel_requested.emit()
                self.message_label.setText("キャンセルしています...")
                self.cancel_btn.setEnabled(False)

    def is_cancelled(self) -> bool:
        """キャンセルされたかどうか"""
        return self.cancelled
