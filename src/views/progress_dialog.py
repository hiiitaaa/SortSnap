"""プログレスバーダイアログ"""
import time
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QMovie


class ProgressDialog(QDialog):
    """保存処理プログレスバー"""

    # シグナル
    cancel_requested = pyqtSignal()

    def __init__(self, total: int, parent=None, mode: str = "save"):
        """
        Args:
            total: 全体の処理数
            parent: 親ウィジェット
            mode: "save" (保存) または "load" (読み込み)
        """
        super().__init__(parent)
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self.cancelled = False
        self.mode = mode

        self.init_ui()

    def init_ui(self):
        """UIを初期化"""
        if self.mode == "load":
            self.setWindowTitle("読み込み中...")
            message_text = "画像を読み込んでいます..."
        else:
            self.setWindowTitle("保存中...")
            message_text = "画像を保存しています..."

        self.setModal(True)
        self.setFixedWidth(550)

        # メインレイアウト
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # コンテンツレイアウト（上部）
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # メインメッセージとアニメーションの横並びレイアウト
        message_layout = QHBoxLayout()

        # メインメッセージ
        self.message_label = QLabel(message_text)
        self.message_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        message_layout.addWidget(self.message_label)

        message_layout.addSpacing(20)

        # アニメーション表示（100x100）
        self.animation_label = QLabel()
        self.animation_label.setFixedSize(100, 100)
        self.animation_label.setScaledContents(True)
        message_layout.addWidget(self.animation_label)

        message_layout.addStretch()

        layout.addLayout(message_layout)

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

        # 上部のコンテンツを追加
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

        # アニメーション再生開始
        self._setup_animation()

    def _setup_animation(self):
        """アニメーションを設定して再生"""
        # idle.gifのパスを取得
        animation_path = Path(__file__).parent.parent.parent / "animations" / "idle.gif"

        if not animation_path.exists():
            print(f"Warning: Animation file not found: {animation_path}")
            return

        # GIFアニメーション設定
        self.movie = QMovie(str(animation_path))
        self.movie.setScaledSize(self.animation_label.size())

        # 再生速度を1.5倍に設定（66.7%のスピード = 1.5倍速）
        self.movie.setSpeed(150)  # 100が通常速度、150で1.5倍速

        self.animation_label.setMovie(self.movie)

        # ループ再生開始
        self.movie.start()

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
            if self.mode == "load":
                self.message_label.setText("読み込みが完了しました！")
            else:
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

    def closeEvent(self, event):
        """ダイアログを閉じる時"""
        # アニメーションを停止
        if hasattr(self, 'movie'):
            self.movie.stop()
        event.accept()
