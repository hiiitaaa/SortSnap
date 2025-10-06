"""ファイル名検証ユーティリティ"""
import re


class Validator:
    """ファイル名検証ユーティリティ"""

    INVALID_CHARS = r'<>:"/\|?*'
    RESERVED_NAMES = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 260

    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, list[str]]:
        """
        ファイル名を検証

        Returns:
            (有効かどうか, エラーリスト)
        """
        errors = []

        if not filename:
            errors.append("ファイル名が空です")
            return (False, errors)

        # 不正文字チェック
        invalid_chars_found = [c for c in Validator.INVALID_CHARS if c in filename]
        if invalid_chars_found:
            errors.append(f"不正な文字が含まれています: {', '.join(invalid_chars_found)}")

        # 予約語チェック（拡張子を除いたベース名で判定）
        base_name = filename.rsplit('.', 1)[0].upper()
        if base_name in Validator.RESERVED_NAMES:
            errors.append(f"予約語は使用できません: {base_name}")

        # 長さチェック
        if len(filename) > Validator.MAX_FILENAME_LENGTH:
            errors.append(f"ファイル名が長すぎます（最大{Validator.MAX_FILENAME_LENGTH}文字）")

        # 先頭・末尾チェック
        if filename.endswith(' ') or filename.endswith('.'):
            errors.append("ファイル名の末尾にスペースまたはピリオドは使用できません")

        if filename.startswith(' '):
            errors.append("ファイル名の先頭にスペースは使用できません")

        return (len(errors) == 0, errors)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        ファイル名を安全に変換

        Args:
            filename: 元のファイル名

        Returns:
            安全なファイル名
        """
        # 不正文字を _ に置換
        for char in Validator.INVALID_CHARS:
            filename = filename.replace(char, '_')

        # 先頭のスペースを削除
        filename = filename.lstrip(' ')

        # 末尾のスペース・ピリオドを削除
        filename = filename.rstrip(' .')

        # 空になった場合はデフォルト名
        if not filename:
            filename = "untitled"

        return filename

    @staticmethod
    def validate_path_length(path: str) -> bool:
        """
        パス全体の長さを検証

        Args:
            path: 検証するパス

        Returns:
            有効かどうか
        """
        return len(path) <= Validator.MAX_PATH_LENGTH
