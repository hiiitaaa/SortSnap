"""設定データモデル"""
import json
import os
from pathlib import Path


class ConfigModel:
    """設定データを管理するモデル"""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "mode": "folder",
        "last_input_folder": "",
        "last_output_folder": "",
        "rename_template": "sequential",
        "rename_prefix": "",
        "rename_start_number": 1,
        "rename_digits": 3,
        "jpg_convert": False,
        "jpg_quality": 95,
        "show_save_confirmation": True,
        "show_delete_confirmation": True,  # 削除確認ダイアログを表示するか
        "thumbnail_size": 200,
        "window_size": [1920, 1080],
        "window_position": None,
        "enable_animations": True
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load()

    def load(self) -> dict:
        """
        設定ファイルを読み込み

        Returns:
            設定辞書
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # デフォルト設定とマージ（新しいキーに対応）
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded_config)
                return config
            else:
                # 設定ファイルがない場合はデフォルトを返す
                return self.DEFAULT_CONFIG.copy()

        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            return self.DEFAULT_CONFIG.copy()

    def save(self) -> bool:
        """
        設定ファイルを保存

        Returns:
            成功したかどうか
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True

        except Exception as e:
            print(f"設定ファイルの保存エラー: {e}")
            return False

    def get(self, key: str, default=None):
        """
        設定値を取得

        Args:
            key: 設定キー
            default: デフォルト値

        Returns:
            設定値
        """
        return self.config.get(key, default)

    def set(self, key: str, value):
        """
        設定値を更新して即座に保存

        Args:
            key: 設定キー
            value: 設定値
        """
        self.config[key] = value
        self.save()

    def set_multiple(self, settings: dict):
        """
        複数の設定値を一度に更新して保存

        Args:
            settings: 設定辞書
        """
        self.config.update(settings)
        self.save()

    def reset(self):
        """設定をデフォルトにリセット"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
