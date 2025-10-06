"""非同期保存処理ワーカー"""
from PyQt6.QtCore import QThread, pyqtSignal
from src.models.image_model import ImageModel


class SaveWorker(QThread):
    """非同期で画像を保存するワーカースレッド"""

    # シグナル
    progress = pyqtSignal(int, str)  # (現在の処理数, ファイル名)
    finished = pyqtSignal(int, int, list)  # (成功数, 失敗数, エラーリスト)

    def __init__(
        self,
        file_controller,
        images: list[ImageModel],
        output_path: str,
        rename_settings: dict,
        jpg_convert: bool = False,
        jpg_quality: int = 95
    ):
        super().__init__()
        self.file_controller = file_controller
        self.images = images
        self.output_path = output_path
        self.rename_settings = rename_settings
        self.jpg_convert = jpg_convert
        self.jpg_quality = jpg_quality
        self.cancel_flag = {"cancel": False}

    def run(self):
        """保存処理を実行"""
        def progress_callback(current: int, filename: str):
            self.progress.emit(current, filename)

        success, fail, errors = self.file_controller.save_images(
            self.images,
            self.output_path,
            self.rename_settings,
            self.jpg_convert,
            self.jpg_quality,
            progress_callback=progress_callback,
            cancel_flag=self.cancel_flag
        )

        self.finished.emit(success, fail, errors)

    def cancel(self):
        """保存処理をキャンセル"""
        self.cancel_flag["cancel"] = True
