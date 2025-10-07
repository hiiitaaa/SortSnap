"""設定パネル"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QComboBox, QLineEdit, QSpinBox, QCheckBox, QSlider,
    QPushButton, QButtonGroup, QFileDialog, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from datetime import datetime
from src.models.config_model import ConfigModel
from src.controllers.rename_controller import RenameController


class SettingsPanel(QWidget):
    """設定パネル"""

    # シグナル
    mode_changed = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)
    save_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()
    reset_requested = pyqtSignal()  # リセットシグナル

    def __init__(self, config: ConfigModel, parent=None):
        super().__init__(parent)
        self.config = config
        self.rename_controller = RenameController()

        self.init_ui()
        self.restore_settings()

        # 初期表示用のサンプル更新
        self._update_sample_names()

    def init_ui(self):
        """UIを初期化"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(24)

        # セクション1: モード選択
        layout.addWidget(self._create_mode_section())
        layout.addWidget(self._create_separator())

        # セクション2: リネーム設定
        layout.addWidget(self._create_rename_section())
        layout.addWidget(self._create_separator())

        # セクション3: JPG変換設定
        layout.addWidget(self._create_jpg_section())
        layout.addWidget(self._create_separator())

        # セクション4: 出力先設定
        layout.addWidget(self._create_output_section())

        # スペーサー
        layout.addStretch()

        # セクション5: リセットボタン
        layout.addWidget(self._create_reset_button())

        # セクション6: 保存ボタン
        layout.addWidget(self._create_save_button())

        self.setLayout(layout)
        self.setMinimumWidth(300)

    def _create_separator(self) -> QFrame:
        """区切り線を作成"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("QFrame { color: #e0e0e0; }")
        return line

    def _create_mode_section(self) -> QWidget:
        """モード選択セクション"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # タイトル
        title = QLabel("動作モード")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # ラジオボタングループ
        self.mode_group = QButtonGroup()

        # フォルダモード
        self.folder_mode_radio = QRadioButton("フォルダモード")
        self.folder_mode_radio.setChecked(True)
        self.mode_group.addButton(self.folder_mode_radio, 0)
        layout.addWidget(self.folder_mode_radio)

        desc1 = QLabel("既存フォルダの画像を読み込み")
        desc1.setStyleSheet("font-size: 9pt; color: #666; margin-left: 20px;")
        layout.addWidget(desc1)

        # フォルダを開くボタン
        self.open_folder_btn = QPushButton("📁 フォルダを開く (Ctrl+O)")
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin-left: 20px;
                margin-top: 5px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.open_folder_btn)

        # 新規フォルダモード
        self.new_folder_mode_radio = QRadioButton("新規フォルダ作成モード")
        self.mode_group.addButton(self.new_folder_mode_radio, 1)
        layout.addWidget(self.new_folder_mode_radio)

        desc2 = QLabel("画像ファイルをドラッグ&ドロップ")
        desc2.setStyleSheet("font-size: 9pt; color: #666; margin-left: 20px;")
        layout.addWidget(desc2)

        # シグナル接続
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        self.open_folder_btn.clicked.connect(self._on_open_folder_clicked)

        widget.setLayout(layout)
        return widget

    def _create_rename_section(self) -> QWidget:
        """リネーム設定セクション"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # タイトル
        title = QLabel("リネーム設定")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # テンプレート選択
        layout.addWidget(QLabel("命名規則:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "連番のみ",
            "テキスト + 連番",
            "日付 + 連番"
        ])
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        layout.addWidget(self.template_combo)

        # プレフィックス入力
        self.prefix_label = QLabel("プレフィックス:")
        layout.addWidget(self.prefix_label)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("例: MyImage")
        self.prefix_input.textChanged.connect(self._update_sample_names)
        layout.addWidget(self.prefix_input)

        # 連番開始番号
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("開始番号:"))
        self.start_number_spin = QSpinBox()
        self.start_number_spin.setRange(0, 9999)
        self.start_number_spin.setValue(1)
        self.start_number_spin.valueChanged.connect(self._update_sample_names)
        start_layout.addWidget(self.start_number_spin)
        layout.addLayout(start_layout)

        # 連番桁数
        digits_layout = QHBoxLayout()
        digits_layout.addWidget(QLabel("桁数:"))
        self.digits_spin = QSpinBox()
        self.digits_spin.setRange(1, 6)
        self.digits_spin.setValue(3)
        self.digits_spin.valueChanged.connect(self._update_sample_names)
        digits_layout.addWidget(self.digits_spin)
        layout.addLayout(digits_layout)

        # サンプル表示
        layout.addWidget(QLabel("サンプル:"))
        self.sample_label = QLabel("001.jpg")  # デフォルト表示
        self.sample_label.setStyleSheet(
            "background-color: #f5f5f5; padding: 8px; border-radius: 4px; font-family: monospace; color: #000;"
        )
        layout.addWidget(self.sample_label)

        widget.setLayout(layout)
        return widget

    def _create_jpg_section(self) -> QWidget:
        """JPG変換設定セクション"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # JPG変換チェックボックス
        self.jpg_convert_check = QCheckBox("JPGに変換（PNG → JPG）")
        self.jpg_convert_check.stateChanged.connect(self._on_jpg_convert_changed)
        layout.addWidget(self.jpg_convert_check)

        # 品質スライダー
        quality_layout = QVBoxLayout()
        quality_label_layout = QHBoxLayout()
        quality_label_layout.addWidget(QLabel("品質:"))
        self.quality_value_label = QLabel("95%")
        quality_label_layout.addWidget(self.quality_value_label)
        quality_label_layout.addStretch()
        quality_layout.addLayout(quality_label_layout)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(95)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        self.quality_slider.valueChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(self.quality_slider)

        layout.addLayout(quality_layout)

        widget.setLayout(layout)
        return widget

    def _create_output_section(self) -> QWidget:
        """出力先設定セクション"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # タイトル
        title = QLabel("出力先設定")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # 出力先パス
        layout.addWidget(QLabel("出力先フォルダ:"))
        path_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setReadOnly(True)
        path_layout.addWidget(self.output_path_input)

        self.browse_button = QPushButton("参照...")
        self.browse_button.clicked.connect(self._on_browse_output)
        path_layout.addWidget(self.browse_button)

        layout.addLayout(path_layout)

        # 新規フォルダ名（新規フォルダモード時のみ表示）
        self.new_folder_label = QLabel("新規フォルダ名:")
        layout.addWidget(self.new_folder_label)

        self.new_folder_input = QLineEdit()
        self.new_folder_input.setPlaceholderText(datetime.now().strftime("%y%m%d"))
        layout.addWidget(self.new_folder_input)

        widget.setLayout(layout)
        return widget

    def _create_reset_button(self) -> QPushButton:
        """リセットボタン"""
        reset_btn = QPushButton("🔄 リセット")
        reset_btn.setObjectName("ResetButton")
        reset_btn.setStyleSheet("""
            QPushButton#ResetButton {
                height: 36px;
                background-color: #FF9800;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton#ResetButton:hover {
                background-color: #F57C00;
            }
            QPushButton#ResetButton:pressed {
                background-color: #E65100;
            }
        """)
        reset_btn.clicked.connect(self._on_reset_clicked)
        return reset_btn

    def _create_save_button(self) -> QPushButton:
        """保存ボタン"""
        save_btn = QPushButton("💾 保存")
        save_btn.setObjectName("SaveButton")
        save_btn.setStyleSheet("""
            QPushButton#SaveButton {
                height: 40px;
                background-color: #2196F3;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton#SaveButton:hover {
                background-color: #1976D2;
            }
            QPushButton#SaveButton:pressed {
                background-color: #0D47A1;
            }
        """)
        save_btn.clicked.connect(self._on_save_clicked)
        return save_btn

    def _on_mode_changed(self):
        """モード変更時"""
        mode = "folder" if self.folder_mode_radio.isChecked() else "new_folder"
        self.config.set("mode", mode)

        # 新規フォルダ名の表示切替
        is_new_folder = mode == "new_folder"
        self.new_folder_label.setVisible(is_new_folder)
        self.new_folder_input.setVisible(is_new_folder)

        self.mode_changed.emit(mode)

    def _on_template_changed(self):
        """テンプレート変更時"""
        template_index = self.template_combo.currentIndex()

        # プレフィックス入力欄の表示切替
        show_prefix = (template_index == 1)  # "テキスト + 連番"
        self.prefix_label.setVisible(show_prefix)
        self.prefix_input.setVisible(show_prefix)

        self._update_sample_names()

    def _on_jpg_convert_changed(self, state):
        """JPG変換チェックボックス変更時"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.quality_slider.setEnabled(enabled)
        self.quality_value_label.setEnabled(enabled)

    def _on_quality_changed(self, value):
        """品質スライダー変更時"""
        self.quality_value_label.setText(f"{value}%")

    def _on_browse_output(self):
        """参照ボタンクリック時"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "出力先フォルダを選択",
            self.output_path_input.text()
        )
        if folder:
            self.output_path_input.setText(folder)
            self.config.set("last_output_folder", folder)

    def _on_reset_clicked(self):
        """リセットボタンクリック時"""
        self.reset_requested.emit()

    def _on_save_clicked(self):
        """保存ボタンクリック時"""
        self.save_requested.emit()

    def _on_open_folder_clicked(self):
        """フォルダを開くボタンクリック時"""
        self.open_folder_requested.emit()

    def _update_sample_names(self):
        """サンプル名をリアルタイム更新"""
        template_names = ["sequential", "text_number", "date_number"]
        template = template_names[self.template_combo.currentIndex()]

        # JPG変換が有効な場合は.jpg、それ以外はサンプルとして.jpgを表示
        # （実際の保存時は元ファイルの拡張子が使用される）
        extension = "jpg"

        samples = self.rename_controller.generate_sample_names(
            template=template,
            prefix=self.prefix_input.text(),
            start=self.start_number_spin.value(),
            digits=self.digits_spin.value(),
            extension=extension,
            count=1  # 1行のみ表示
        )

        self.sample_label.setText(samples[0] if samples else "")

    def restore_settings(self):
        """設定を復元"""
        # モード
        mode = self.config.get("mode", "folder")
        if mode == "new_folder":
            self.new_folder_mode_radio.setChecked(True)
        else:
            self.folder_mode_radio.setChecked(True)

        # テンプレート
        template = self.config.get("rename_template", "sequential")
        template_map = {"sequential": 0, "text_number": 1, "date_number": 2}
        self.template_combo.setCurrentIndex(template_map.get(template, 0))

        # プレフィックス
        self.prefix_input.setText(self.config.get("rename_prefix", ""))

        # 連番設定
        self.start_number_spin.setValue(self.config.get("rename_start_number", 1))
        self.digits_spin.setValue(self.config.get("rename_digits", 3))

        # JPG変換
        jpg_convert = self.config.get("jpg_convert", False)
        self.jpg_convert_check.setChecked(jpg_convert)
        jpg_quality = self.config.get("jpg_quality", 95)
        self.quality_slider.setValue(jpg_quality)

        # 出力先
        self.output_path_input.setText(self.config.get("last_output_folder", ""))

        # UI更新
        self._on_mode_changed()
        self._on_template_changed()
        self._on_jpg_convert_changed(Qt.CheckState.Checked.value if jpg_convert else Qt.CheckState.Unchecked.value)
        # サンプル更新は_on_template_changed()内で呼ばれるので不要

    def get_rename_settings(self) -> dict:
        """リネーム設定を取得"""
        template_names = ["sequential", "text_number", "date_number"]

        return {
            "template": template_names[self.template_combo.currentIndex()],
            "prefix": self.prefix_input.text(),
            "start_number": self.start_number_spin.value(),
            "digits": self.digits_spin.value()
        }

    def save_settings(self):
        """設定を保存"""
        template_names = ["sequential", "text_number", "date_number"]

        self.config.set_multiple({
            "rename_template": template_names[self.template_combo.currentIndex()],
            "rename_prefix": self.prefix_input.text(),
            "rename_start_number": self.start_number_spin.value(),
            "rename_digits": self.digits_spin.value(),
            "jpg_convert": self.jpg_convert_check.isChecked(),
            "jpg_quality": self.quality_slider.value(),
            "last_output_folder": self.output_path_input.text()
        })
