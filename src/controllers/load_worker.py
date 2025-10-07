"""非同期画像読み込みワーカー"""
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from src.models.image_model import ImageModel
from src.utils.constants import SUPPORTED_FORMATS


class LoadWorker(QThread):
    """非同期で画像を読み込むワーカースレッド"""

    # シグナル
    progress = pyqtSignal(int, str)  # (現在の処理数, ファイル名)
    finished = pyqtSignal(list)  # (ImageModelのリスト)
    error = pyqtSignal(str)  # エラーメッセージ

    def __init__(self, folder_path: str = None, file_paths: list[str] = None, thumbnail_size: int = 200):
        """
        Args:
            folder_path: フォルダパス（フォルダモード）
            file_paths: ファイルパスのリスト（ファイルモード）
            thumbnail_size: サムネイルサイズ
        """
        super().__init__()
        self.folder_path = folder_path
        self.file_paths = file_paths
        self.thumbnail_size = thumbnail_size

    def run(self):
        """読み込み処理を実行"""
        try:
            images = []

            # フォルダモード
            if self.folder_path:
                folder = Path(self.folder_path)

                # フォルダの存在確認
                if not folder.exists():
                    self.error.emit(f"フォルダが見つかりません: {self.folder_path}")
                    return

                # ディレクトリ確認
                if not folder.is_dir():
                    self.error.emit(f"指定されたパスはフォルダではありません: {self.folder_path}")
                    return

                # 画像ファイルを検出
                image_files = []
                try:
                    for file_path in folder.iterdir():
                        if file_path.is_file():
                            ext = file_path.suffix.lower()
                            if ext in SUPPORTED_FORMATS:
                                image_files.append(str(file_path))
                except PermissionError as e:
                    self.error.emit(f"フォルダへのアクセス権限がありません: {self.folder_path}")
                    return

                # ソート
                image_files = sorted(image_files)

            # ファイルモード
            elif self.file_paths:
                image_files = []
                for file_path in self.file_paths:
                    ext = Path(file_path).suffix.lower()
                    if ext in SUPPORTED_FORMATS:
                        image_files.append(file_path)

            else:
                self.error.emit("フォルダパスまたはファイルパスが指定されていません")
                return

            # 画像がない場合
            if not image_files:
                self.finished.emit([])
                return

            # ImageModelを作成し、サムネイルを事前生成
            for i, file_path in enumerate(image_files):
                try:
                    # ImageModel作成
                    image = ImageModel(file_path)
                    image.index = i

                    # サムネイル生成（ここで時間がかかる）
                    image.load_thumbnail(self.thumbnail_size)

                    images.append(image)

                    # プログレス更新
                    self.progress.emit(i + 1, image.filename)

                except Exception as e:
                    print(f"画像読み込みエラー: {file_path}, {e}")
                    continue

            # 完了
            self.finished.emit(images)

        except Exception as e:
            self.error.emit(f"予期しないエラー: {str(e)}")
