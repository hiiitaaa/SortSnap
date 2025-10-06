"""アニメーション再生クラス"""
import csv
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap


class AnimationPlayer(QLabel):
    """アニメーション再生クラス"""

    def __init__(self, animation_id: str, parent=None):
        super().__init__(parent)
        self.animation_id = animation_id
        self.animation_data = None
        self.frames = []
        self.current_frame = 0
        self.is_playing = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # アニメーションデータを読み込み
        self.load_animation()

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
                return False

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['animation_id'] == self.animation_id:
                        self.animation_data = {
                            'name': row['name'],
                            'frame_count': int(row['frame_count']),
                            'fps': int(row['fps']),
                            'loop': row['loop'].lower() == 'true',
                            'frame_prefix': row['frame_prefix'],
                            'description': row['description']
                        }
                        break

            if not self.animation_data:
                return False

            # フレーム画像を読み込み
            self.load_frames()

            return len(self.frames) > 0

        except Exception as e:
            print(f"アニメーション読み込みエラー: {e}")
            return False

    def load_frames(self):
        """全フレームをプリロード"""
        self.frames = []

        frames_dir = Path("animations/frames")
        if not frames_dir.exists():
            return

        frame_count = self.animation_data['frame_count']
        frame_prefix = self.animation_data['frame_prefix']

        for i in range(1, frame_count + 1):
            frame_path = frames_dir / f"{frame_prefix}{i:03d}.png"
            if frame_path.exists():
                pixmap = QPixmap(str(frame_path))
                self.frames.append(pixmap)
            else:
                print(f"フレームが見つかりません: {frame_path}")

    def play(self):
        """再生開始"""
        if not self.frames or self.is_playing:
            return

        self.is_playing = True
        self.current_frame = 0

        # フレームレートに基づいてタイマー間隔を設定
        frame_duration = int(1000 / self.animation_data['fps'])
        self.timer.start(frame_duration)

        # 最初のフレームを表示
        self.show_current_frame()

    def stop(self):
        """再生停止"""
        self.is_playing = False
        self.timer.stop()

    def update_frame(self):
        """フレームを更新"""
        if not self.frames:
            return

        self.current_frame += 1

        # ループ判定
        if self.current_frame >= len(self.frames):
            if self.animation_data['loop']:
                self.current_frame = 0
            else:
                self.stop()
                return

        self.show_current_frame()

    def show_current_frame(self):
        """現在のフレームを表示"""
        if 0 <= self.current_frame < len(self.frames):
            self.setPixmap(self.frames[self.current_frame])
