"""Undo/Redo履歴管理モデル"""
from datetime import datetime
from src.utils.constants import MAX_HISTORY


class HistoryModel:
    """Undo/Redo履歴を管理するモデル"""

    def __init__(self):
        self.undo_stack: list = []
        self.redo_stack: list = []

    def push(self, action: dict):
        """
        アクションを履歴に追加

        Args:
            action: アクション辞書
                {
                    "type": "delete" | "reorder" | "sort",
                    "timestamp": "2025-10-06 14:30:15",
                    "data": {...}
                }
        """
        # タイムスタンプを追加
        action["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Undoスタックに追加
        self.undo_stack.append(action)

        # 最大履歴数を超えたら古いものを削除
        if len(self.undo_stack) > MAX_HISTORY:
            self.undo_stack.pop(0)

        # Redoスタックをクリア（新しいアクションが追加されたら）
        self.redo_stack.clear()

    def undo(self) -> dict:
        """
        Undoを実行して前の状態を返す

        Returns:
            アクション辞書（Noneの場合はUndoできない）
        """
        if not self.can_undo():
            return None

        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        return action

    def redo(self) -> dict:
        """
        Redoを実行

        Returns:
            アクション辞書（Noneの場合はRedoできない）
        """
        if not self.can_redo():
            return None

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        return action

    def can_undo(self) -> bool:
        """
        Undo可能か

        Returns:
            Undo可能かどうか
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """
        Redo可能か

        Returns:
            Redo可能かどうか
        """
        return len(self.redo_stack) > 0

    def clear(self):
        """履歴をクリア"""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_undo_count(self) -> int:
        """Undo可能な回数を取得"""
        return len(self.undo_stack)

    def get_redo_count(self) -> int:
        """Redo可能な回数を取得"""
        return len(self.redo_stack)
