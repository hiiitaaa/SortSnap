"""画像操作コントローラー"""
import os
from pathlib import Path
from src.models.image_model import ImageModel
from src.models.history_model import HistoryModel
from src.utils.constants import SUPPORTED_FORMATS


class ImageController:
    """画像操作を管理するコントローラー"""

    def __init__(self):
        self.images: list[ImageModel] = []
        self.history: HistoryModel = HistoryModel()
        self.original_order: list[ImageModel] = []

    def load_from_folder(self, folder_path: str) -> list[ImageModel]:
        """
        フォルダから画像を読み込み

        Args:
            folder_path: フォルダパス

        Returns:
            画像モデルのリスト

        Raises:
            FileNotFoundError: フォルダが存在しない場合
            NotADirectoryError: 指定されたパスがディレクトリでない場合
            PermissionError: フォルダへのアクセス権限がない場合
        """
        self.images.clear()
        self.history.clear()
        self.original_order.clear()

        folder = Path(folder_path)

        # フォルダの存在確認
        if not folder.exists():
            raise FileNotFoundError(f"フォルダが見つかりません: {folder_path}")

        # ディレクトリ確認
        if not folder.is_dir():
            raise NotADirectoryError(f"指定されたパスはフォルダではありません: {folder_path}")

        try:
            # glob使用時は角括弧などをエスケープする必要がある
            # より確実な方法として、iterdir()で全ファイルを取得してフィルタリング
            image_files = []
            for file_path in folder.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in SUPPORTED_FORMATS:
                        image_files.append(str(file_path))

            # ソート
            image_files = sorted(image_files)

            # ImageModelを作成
            for i, file_path in enumerate(image_files):
                try:
                    image = ImageModel(file_path)
                    image.index = i
                    self.images.append(image)
                except Exception as e:
                    print(f"画像読み込みエラー: {file_path}, {e}")

            # 元の順序を保存
            self.original_order = self.images.copy()

            return self.images

        except PermissionError as e:
            raise PermissionError(f"フォルダへのアクセス権限がありません: {folder_path}") from e

    def load_from_files(self, file_paths: list[str]) -> list[ImageModel]:
        """
        ファイルリストから画像を読み込み

        Args:
            file_paths: ファイルパスのリスト

        Returns:
            画像モデルのリスト
        """
        self.images.clear()
        self.history.clear()
        self.original_order.clear()

        # 対応形式のみフィルタ
        valid_files = []
        for file_path in file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in SUPPORTED_FORMATS:
                valid_files.append(file_path)

        # ImageModelを作成
        for i, file_path in enumerate(valid_files):
            try:
                image = ImageModel(file_path)
                image.index = i
                self.images.append(image)
            except Exception as e:
                print(f"画像読み込みエラー: {file_path}, {e}")

        # 元の順序を保存
        self.original_order = self.images.copy()

        return self.images

    def reorder(self, from_index: int, to_index: int):
        """
        画像の順序を変更（履歴に記録）

        Args:
            from_index: 移動元のインデックス
            to_index: 移動先のインデックス
        """
        if from_index < 0 or from_index >= len(self.images):
            return
        if to_index < 0 or to_index >= len(self.images):
            return
        if from_index == to_index:
            return

        # 履歴に記録
        self.history.push({
            "type": "reorder",
            "data": {
                "from_index": from_index,
                "to_index": to_index,
                "order": [img.file_path for img in self.images]
            }
        })

        # 順序を変更
        image = self.images.pop(from_index)
        self.images.insert(to_index, image)

        # インデックスを更新
        self._update_indices()

    def reorder_multiple(self, indices: list[int], to_index: int):
        """
        複数の画像の順序を一括変更（履歴に記録）

        Args:
            indices: 移動する画像のインデックスリスト（昇順ソート済みを想定）
            to_index: 移動先のインデックス
        """
        if not indices:
            return

        # インデックスを昇順ソート
        sorted_indices = sorted(set(indices))

        # 履歴に記録
        self.history.push({
            "type": "reorder_multiple",
            "data": {
                "indices": sorted_indices,
                "to_index": to_index,
                "order": [img.file_path for img in self.images]
            }
        })

        # 移動する画像を取得
        moving_images = [self.images[i] for i in sorted_indices]

        # 降順で削除（インデックスがずれないように）
        for i in reversed(sorted_indices):
            self.images.pop(i)

        # 挿入位置を調整（削除した画像の数だけずれる）
        # to_indexより前にいくつ削除したかをカウント
        deleted_before = sum(1 for i in sorted_indices if i < to_index)
        adjusted_to_index = to_index - deleted_before

        # 移動する画像を一括挿入
        for i, image in enumerate(moving_images):
            self.images.insert(adjusted_to_index + i, image)

        # インデックスを更新
        self._update_indices()

    def delete_images(self, indices: list[int]):
        """
        画像を削除（履歴に記録）

        Args:
            indices: 削除するインデックスのリスト
        """
        if not indices:
            return

        # 削除する画像を記録
        deleted_images = [(i, self.images[i]) for i in sorted(indices, reverse=True)]

        # 履歴に記録
        self.history.push({
            "type": "delete",
            "data": {
                "deleted_images": [(i, img.file_path) for i, img in deleted_images]
            }
        })

        # 削除実行
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self.images):
                self.images.pop(i)

        # インデックスを更新
        self._update_indices()

    def sort_by_name(self, ascending: bool = True):
        """
        ファイル名順にソート（履歴に記録）

        Args:
            ascending: 昇順かどうか
        """
        # 履歴に記録
        self.history.push({
            "type": "sort",
            "data": {
                "order": [img.file_path for img in self.images],
                "ascending": ascending
            }
        })

        # 自然順ソート
        import re
        def natural_sort_key(img: ImageModel):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split(r'(\d+)', img.filename)]

        self.images.sort(key=natural_sort_key, reverse=not ascending)

        # インデックスを更新
        self._update_indices()

    def restore_original_order(self):
        """元の順序に戻す"""
        if not self.original_order:
            return

        # 履歴に記録
        self.history.push({
            "type": "sort",
            "data": {
                "order": [img.file_path for img in self.images],
                "restore": True
            }
        })

        # 元の順序に復元
        self.images = self.original_order.copy()
        self._update_indices()

    def undo(self) -> bool:
        """
        Undoを実行

        Returns:
            成功したかどうか
        """
        action = self.history.undo()
        if not action:
            return False

        action_type = action["type"]
        data = action["data"]

        if action_type == "reorder":
            # 順序を復元
            self._restore_order(data["order"])

        elif action_type == "reorder_multiple":
            # 複数画像の順序を復元
            self._restore_order(data["order"])

        elif action_type == "delete":
            # 削除された画像を復元
            for i, file_path in data["deleted_images"]:
                try:
                    image = ImageModel(file_path)
                    self.images.insert(i, image)
                except Exception as e:
                    print(f"画像復元エラー: {file_path}, {e}")

        elif action_type == "sort":
            # 順序を復元
            self._restore_order(data["order"])

        self._update_indices()
        return True

    def redo(self) -> bool:
        """
        Redoを実行

        Returns:
            成功したかどうか
        """
        action = self.history.redo()
        if not action:
            return False

        action_type = action["type"]
        data = action["data"]

        if action_type == "reorder":
            # 元のfrom_indexとto_indexを使って再度並べ替え
            # ただし、履歴に追加しないように直接操作
            from_index = data["from_index"]
            to_index = data["to_index"]
            image = self.images.pop(from_index)
            self.images.insert(to_index, image)

        elif action_type == "reorder_multiple":
            # 複数画像の順序変更を再実行
            indices = data["indices"]
            to_index = data["to_index"]

            # 移動する画像を取得
            moving_images = [self.images[i] for i in indices]

            # 降順で削除
            for i in reversed(indices):
                self.images.pop(i)

            # 挿入位置を調整
            deleted_before = sum(1 for i in indices if i < to_index)
            adjusted_to_index = to_index - deleted_before

            # 移動する画像を一括挿入
            for i, image in enumerate(moving_images):
                self.images.insert(adjusted_to_index + i, image)

        elif action_type == "delete":
            # 再度削除
            for i, file_path in sorted(data["deleted_images"], reverse=True):
                if 0 <= i < len(self.images):
                    self.images.pop(i)

        elif action_type == "sort":
            if "restore" in data:
                self.images = self.original_order.copy()
            elif "ascending" in data:
                self.sort_by_name(data["ascending"])
                return True  # sort_by_nameが既にインデックス更新する

        self._update_indices()
        return True

    def _update_indices(self):
        """インデックスを更新"""
        for i, img in enumerate(self.images):
            img.index = i

    def _restore_order(self, file_paths: list[str]):
        """
        順序を復元

        Args:
            file_paths: ファイルパスのリスト
        """
        # ファイルパスでソート
        path_to_image = {img.file_path: img for img in self.images}
        self.images = [path_to_image[path] for path in file_paths if path in path_to_image]

    def get_selected_images(self) -> list[ImageModel]:
        """選択された画像のリストを取得"""
        return [img for img in self.images if img.selected]

    def get_selected_indices(self) -> list[int]:
        """選択された画像のインデックスリストを取得"""
        return [i for i, img in enumerate(self.images) if img.selected]

    def select_all(self):
        """全選択"""
        for img in self.images:
            img.selected = True

    def deselect_all(self):
        """選択解除"""
        for img in self.images:
            img.selected = False

    def select_range(self, start: int, end: int):
        """範囲選択"""
        start, end = min(start, end), max(start, end)
        for i in range(start, end + 1):
            if 0 <= i < len(self.images):
                self.images[i].selected = True
