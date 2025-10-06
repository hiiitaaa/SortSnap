"""ファイル操作コントローラー"""
import os
import shutil
from pathlib import Path
from PIL import Image
from src.models.image_model import ImageModel


class FileController:
    """ファイル操作を管理するコントローラー"""

    def __init__(self, logger=None):
        self.logger = logger

    def save_images(
        self,
        images: list[ImageModel],
        output_path: str,
        rename_settings: dict,
        jpg_convert: bool = False,
        jpg_quality: int = 95,
        progress_callback=None,
        cancel_flag=None
    ) -> tuple[int, int, list[dict]]:
        """
        画像を保存

        Args:
            images: 画像モデルのリスト
            output_path: 出力先パス
            rename_settings: リネーム設定
            jpg_convert: JPG変換するかどうか
            jpg_quality: JPG品質
            progress_callback: 進捗コールバック関数
            cancel_flag: キャンセルフラグ（辞書 {"cancel": bool}）

        Returns:
            (成功数, 失敗数, エラーリスト)
        """
        success_count = 0
        fail_count = 0
        errors = []

        output_dir = Path(output_path)

        for i, image in enumerate(images):
            # キャンセルチェック
            if cancel_flag and cancel_flag.get("cancel", False):
                if self.logger:
                    self.logger.warning(f"保存処理がキャンセルされました（{success_count}/{len(images)}枚処理済み）")
                break

            try:
                # 新しいファイル名を生成
                new_filename = image.get_new_filename(
                    template=rename_settings["template"],
                    number=rename_settings["start_number"] + i,
                    digits=rename_settings["digits"],
                    extension=rename_settings.get("extension")
                )

                # 出力先パス
                output_file = output_dir / new_filename

                # JPG変換が必要かチェック
                if jpg_convert and image.extension.lower() in ['.png']:
                    # PNG → JPG変換
                    success = self._convert_png_to_jpg(
                        image.file_path,
                        str(output_file),
                        jpg_quality
                    )
                    if not success:
                        # 変換失敗時はPNGのままコピー
                        shutil.copy2(image.file_path, output_file)
                        if self.logger:
                            self.logger.warning(f"JPG変換失敗、PNG形式で保存: {new_filename}")
                else:
                    # 通常のコピー
                    shutil.copy2(image.file_path, output_file)

                success_count += 1

                # 進捗コールバック
                if progress_callback:
                    progress_callback(i + 1, new_filename)

            except Exception as e:
                fail_count += 1
                error_info = {
                    "filename": image.filename,
                    "error": str(e)
                }
                errors.append(error_info)

                if self.logger:
                    self.logger.error(f"ファイル保存エラー: {image.filename}", exc_info=True)

        if self.logger:
            self.logger.info(f"保存処理完了: 成功 {success_count}枚, 失敗 {fail_count}枚")

        return (success_count, fail_count, errors)

    def create_folder(self, parent_path: str, folder_name: str) -> str:
        """
        新規フォルダを作成

        Args:
            parent_path: 親ディレクトリパス
            folder_name: 新規フォルダ名

        Returns:
            作成したフォルダのパス（失敗時はNone）
        """
        try:
            new_folder = Path(parent_path) / folder_name

            if new_folder.exists():
                raise FileExistsError(f"フォルダが既に存在します: {folder_name}")

            new_folder.mkdir(parents=True, exist_ok=False)

            if self.logger:
                self.logger.info(f"フォルダ作成: {new_folder}")

            return str(new_folder)

        except Exception as e:
            if self.logger:
                self.logger.error(f"フォルダ作成エラー: {folder_name}", exc_info=True)
            raise

    def _convert_png_to_jpg(
        self,
        image_path: str,
        output_path: str,
        quality: int = 95
    ) -> bool:
        """
        PNG → JPG変換

        Args:
            image_path: 入力画像パス
            output_path: 出力画像パス
            quality: JPG品質

        Returns:
            成功したかどうか
        """
        try:
            with Image.open(image_path) as img:
                # RGB変換（透過情報を白背景に合成）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # JPG保存（拡張子を.jpgに変更）
                output_path = str(Path(output_path).with_suffix('.jpg'))
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

            return True

        except Exception as e:
            print(f"PNG→JPG変換エラー: {e}")
            return False

    def check_write_permission(self, path: str) -> bool:
        """
        書き込み権限をチェック

        Args:
            path: チェックするパス

        Returns:
            書き込み可能かどうか
        """
        try:
            test_file = Path(path) / '.sortsnap_test'
            test_file.write_text('test')
            test_file.unlink()
            return True
        except:
            return False

    def get_disk_space(self, path: str) -> tuple[int, int]:
        """
        ディスクの空き容量を取得

        Args:
            path: チェックするパス

        Returns:
            (空き容量, 全体容量) バイト単位
        """
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return (free, total)
        except Exception as e:
            if self.logger:
                self.logger.error(f"ディスク容量取得エラー: {e}")
            return (0, 0)
