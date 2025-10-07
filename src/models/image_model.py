"""画像データモデル"""
import os
from pathlib import Path
from PIL import Image
from PyQt6.QtGui import QPixmap, QImage


class ImageModel:
    """画像データを管理するモデル"""

    def __init__(self, file_path: str):
        self.file_path: str = str(Path(file_path).absolute())
        self.filename: str = os.path.basename(file_path)
        self.extension: str = os.path.splitext(self.filename)[1].lower()
        self.size: tuple = (0, 0)
        self.file_size: int = 0
        self.thumbnail: QPixmap = None
        self.index: int = 0
        self.selected: bool = False

        # サムネイルキャッシュ（サイズごとに保存）
        self._thumbnail_cache: dict[int, QPixmap] = {}

        # ファイル情報を取得
        self._load_file_info()

    def _load_file_info(self):
        """ファイル情報を読み込み"""
        try:
            # ファイルサイズ
            self.file_size = os.path.getsize(self.file_path)

            # 画像サイズ
            with Image.open(self.file_path) as img:
                self.size = img.size

        except Exception as e:
            print(f"ファイル情報の読み込みエラー: {self.file_path}, {e}")

    def load_thumbnail(self, size: int = 200) -> bool:
        """
        サムネイルを生成（キャッシュ対応）

        Args:
            size: サムネイルのサイズ

        Returns:
            成功したかどうか
        """
        # キャッシュ確認
        if size in self._thumbnail_cache:
            self.thumbnail = self._thumbnail_cache[size]
            return True

        try:
            # Pillowでリサイズ（高速）
            with Image.open(self.file_path) as img:
                # RGB変換（透過情報を削除）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # サムネイル生成（アスペクト比維持）
                # BILINEAR: LANCZOS より高速で十分な品質
                img.thumbnail((size, size), Image.Resampling.BILINEAR)

                # PIL Image → QPixmap
                img_bytes = img.tobytes('raw', 'RGB')
                qimage = QImage(img_bytes, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                self.thumbnail = QPixmap.fromImage(qimage)

                # キャッシュに保存
                self._thumbnail_cache[size] = self.thumbnail

            return True

        except Exception as e:
            print(f"サムネイル生成エラー: {self.file_path}, {e}")
            return False

    def get_new_filename(self, template: str, number: int, digits: int, extension: str = None) -> str:
        """
        リネーム後のファイル名を生成

        Args:
            template: テンプレート文字列
            number: 連番
            digits: 桁数
            extension: 拡張子（Noneの場合は元の拡張子を使用）

        Returns:
            新しいファイル名
        """
        if extension is None:
            extension = self.extension.lstrip('.')

        # 連番をゼロパディング
        number_str = str(number).zfill(digits)

        # テンプレートに応じてファイル名を生成
        filename = template.replace("{number}", number_str).replace("{ext}", extension)

        return filename

    def clear_thumbnail_cache(self, keep_size: int = None):
        """
        サムネイルキャッシュをクリア

        Args:
            keep_size: 保持するサイズ（Noneの場合は全削除）
        """
        if keep_size is None:
            self._thumbnail_cache.clear()
        else:
            # 指定サイズ以外を削除
            self._thumbnail_cache = {
                size: pixmap for size, pixmap in self._thumbnail_cache.items()
                if size == keep_size
            }

    def get_file_size_str(self) -> str:
        """
        ファイルサイズを人間が読みやすい形式で返す

        Returns:
            ファイルサイズ文字列（例: "2.5 MB"）
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def __repr__(self):
        return f"ImageModel(filename='{self.filename}', size={self.size}, index={self.index})"
