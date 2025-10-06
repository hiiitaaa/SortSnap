"""アニメーション再生クラス（MP4対応）"""
import csv
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class AnimationPlayer(QWidget):
    """MP4動画を再生するクラス"""

    def __init__(self, animation_id: str, parent=None):
        super().__init__(parent)
        self.animation_id = animation_id
        self.animation_data = None
        self.is_playing = False

        # メディアプレイヤーの設定
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0)  # ミュート
        self.player.setAudioOutput(self.audio_output)

        # ビデオウィジェット
        self.video_widget = QVideoWidget(self)
        self.player.setVideoOutput(self.video_widget)

        # レイアウト
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        # アニメーションデータを読み込み
        if self.load_animation():
            # ループ設定
            if self.animation_data.get('loop', False):
                self.player.mediaStatusChanged.connect(self._on_media_status_changed)

    def load_animation(self) -> bool:
        """
        アニメーションデータを読み込み

        Returns:
            成功したかどうか
        """
        try:
            # CSVファイルを読み込み
            csv_path = Path("animations/animations.csv")
            if not csv_path.exists():
                print(f"CSVファイルが見つかりません: {csv_path}")
                return False

            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['animation_id'] == self.animation_id:
                        self.animation_data = {
                            'name': row['name'],
                            'video_path': row['video_path'],
                            'loop': row['loop'].lower() == 'true',
                            'description': row['description']
                        }
                        break

            if not self.animation_data:
                print(f"アニメーションID '{self.animation_id}' が見つかりません")
                return False

            # 動画ファイルのパスを確認
            video_path = Path(self.animation_data['video_path'])
            if not video_path.exists():
                print(f"動画ファイルが見つかりません: {video_path}")
                return False

            # メディアソースを設定
            self.player.setSource(QUrl.fromLocalFile(str(video_path.absolute())))

            return True

        except Exception as e:
            print(f"アニメーション読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            return False

    def play(self):
        """再生開始"""
        if not self.animation_data:
            return

        self.is_playing = True
        self.player.play()

    def stop(self):
        """再生停止"""
        self.is_playing = False
        self.player.stop()

    def pause(self):
        """一時停止"""
        self.player.pause()

    def _on_media_status_changed(self, status):
        """メディアステータス変更時（ループ処理）"""
        from PyQt6.QtMultimedia import QMediaPlayer

        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.animation_data.get('loop', False) and self.is_playing:
                # ループ再生
                self.player.setPosition(0)
                self.player.play()

    def setFixedSize(self, width, height):
        """サイズ固定"""
        super().setFixedSize(width, height)
        self.video_widget.setFixedSize(width, height)
