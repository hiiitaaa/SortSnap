"""リネームコントローラー"""
from datetime import datetime
from src.utils.validator import Validator


class RenameController:
    """リネーム処理を管理するコントローラー"""

    TEMPLATES = {
        "sequential": "{number}.{ext}",
        "text_number": "{prefix}_{number}.{ext}",
        "date_number": "{date}_{number}.{ext}"
    }

    def generate_filename(
        self,
        template: str,
        prefix: str = "",
        number: int = 1,
        digits: int = 3,
        extension: str = "jpg"
    ) -> str:
        """
        ファイル名を生成

        Args:
            template: テンプレート名
            prefix: プレフィックス
            number: 連番
            digits: 桁数
            extension: 拡張子

        Returns:
            生成されたファイル名
        """
        # 連番をゼロパディング
        number_str = str(number).zfill(digits)

        # 日付（YYMMDD形式）
        date_str = datetime.now().strftime("%y%m%d")

        # テンプレートを取得
        template_str = self.TEMPLATES.get(template, self.TEMPLATES["sequential"])

        # 置換
        filename = template_str.replace("{number}", number_str)
        filename = filename.replace("{ext}", extension)
        filename = filename.replace("{prefix}", prefix)
        filename = filename.replace("{date}", date_str)

        return filename

    def validate_filename(self, filename: str) -> tuple[bool, list[str]]:
        """
        ファイル名を検証

        Args:
            filename: ファイル名

        Returns:
            (有効かどうか, エラーリスト)
        """
        return Validator.validate_filename(filename)

    def sanitize_filename(self, filename: str) -> str:
        """
        ファイル名を安全な形式に変換

        Args:
            filename: 元のファイル名

        Returns:
            安全なファイル名
        """
        return Validator.sanitize_filename(filename)

    def generate_sample_names(
        self,
        template: str,
        prefix: str,
        start: int,
        digits: int,
        extension: str = "jpg",
        count: int = 3
    ) -> list[str]:
        """
        サンプルファイル名を生成

        Args:
            template: テンプレート名
            prefix: プレフィックス
            start: 開始番号
            digits: 桁数
            extension: 拡張子
            count: 生成数

        Returns:
            サンプルファイル名のリスト
        """
        samples = []
        for i in range(count):
            filename = self.generate_filename(
                template=template,
                prefix=prefix,
                number=start + i,
                digits=digits,
                extension=extension
            )
            samples.append(filename)

        return samples

    def validate_prefix(self, prefix: str) -> tuple[bool, str]:
        """
        プレフィックスを検証

        Args:
            prefix: プレフィックス

        Returns:
            (有効かどうか, エラーメッセージ)
        """
        if not prefix:
            return (True, "")

        # 不正文字チェック
        invalid_chars = [c for c in Validator.INVALID_CHARS if c in prefix]
        if invalid_chars:
            return (False, f"不正な文字が含まれています: {', '.join(invalid_chars)}")

        # 予約語チェック
        if prefix.upper() in Validator.RESERVED_NAMES:
            return (False, f"予約語は使用できません: {prefix}")

        return (True, "")
