"""
Settings Dialog for FruityFocus.
Allows customizing focus minutes, breaks, scale factor, and alert preferences.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox,
    QComboBox, QCheckBox, QPushButton, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from src.config import ICON_PATH, AVAILABLE_SCALES

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(int, int, int, int, bool, bool)

    def __init__(self, current_work=25, current_break=5, current_long_break=15,
                 current_scale=3, sound_enabled=True, always_show_bubble=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FruityFocus - Configuración")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setFixedSize(360, 380)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #3d405b;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #f77f00;
                padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QSpinBox, QComboBox {
                background-color: #2b2d42;
                color: #ffffff;
                border: 1px solid #4a4e69;
                border-radius: 5px;
                padding: 4px 8px;
                min-height: 22px;
            }
            QSpinBox:focus, QComboBox:focus {
                border-color: #f77f00;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 12px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid #4a4e69;
                background-color: #2b2d42;
            }
            QCheckBox::indicator:checked {
                background-color: #f77f00;
                border-color: #f77f00;
            }
            QPushButton {
                background-color: #2b2d42;
                color: #ffffff;
                border: 1px solid #4a4e69;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f77f00;
                border-color: #fcbf49;
            }
            QPushButton#btnSave {
                background-color: #f77f00;
                border-color: #f77f00;
                color: #ffffff;
            }
            QPushButton#btnSave:hover {
                background-color: #d62828;
                border-color: #d62828;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Timers Group
        timer_group = QGroupBox("⏱ Temporizador Pomodoro", self)
        timer_form = QFormLayout(timer_group)
        timer_form.setSpacing(10)

        self.spin_work = QSpinBox(self)
        self.spin_work.setRange(1, 120)
        self.spin_work.setValue(current_work)
        self.spin_work.setSuffix(" min")
        timer_form.addRow("Tiempo de Enfoque:", self.spin_work)

        self.spin_break = QSpinBox(self)
        self.spin_break.setRange(1, 45)
        self.spin_break.setValue(current_break)
        self.spin_break.setSuffix(" min")
        timer_form.addRow("Descanso Corto:", self.spin_break)

        self.spin_long_break = QSpinBox(self)
        self.spin_long_break.setRange(1, 60)
        self.spin_long_break.setValue(current_long_break)
        self.spin_long_break.setSuffix(" min")
        timer_form.addRow("Descanso Largo:", self.spin_long_break)

        layout.addWidget(timer_group)

        # Appearance & Pet Group
        pet_group = QGroupBox("🥭 Mascota Virtual y Sonido", self)
        pet_form = QFormLayout(pet_group)
        pet_form.setSpacing(10)

        self.combo_scale = QComboBox(self)
        for name, factor in AVAILABLE_SCALES.items():
            self.combo_scale.addItem(name, factor)
            if factor == current_scale:
                self.combo_scale.setCurrentText(name)
        pet_form.addRow("Tamaño del Mango:", self.combo_scale)

        self.chk_sound = QCheckBox("Alerta sonora al completar sesión", self)
        self.chk_sound.setChecked(sound_enabled)
        pet_form.addRow(self.chk_sound)

        self.chk_always_bubble = QCheckBox("Mantener bocadillo de tiempo visible", self)
        self.chk_always_bubble.setChecked(always_show_bubble)
        pet_form.addRow(self.chk_always_bubble)

        layout.addWidget(pet_group)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Guardar", self)
        self.btn_save.setObjectName("btnSave")
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _on_save(self):
        work_m = self.spin_work.value()
        break_m = self.spin_break.value()
        long_break_m = self.spin_long_break.value()
        scale = self.combo_scale.currentData()
        sound = self.chk_sound.isChecked()
        always_bubble = self.chk_always_bubble.isChecked()
        self.settings_saved.emit(work_m, break_m, long_break_m, scale, sound, always_bubble)
        self.accept()
