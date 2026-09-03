"""
Speech Bubble / Floating Timer HUD for FruityFocus.
Displays timer countdown, state badge, and quick action buttons above the mango pet.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush

class SpeechBubble(QWidget):
    toggle_timer = pyqtSignal()
    reset_timer = pyqtSignal()
    skip_timer = pyqtSignal()
    open_settings = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Frameless, stays on top, tool window (doesn't show separate taskbar button)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(180, 110)

        self._init_ui()
        self.is_user_pinned = False

    def _init_ui(self):
        # Layout inside bubble
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 22) # bottom margin reserves space for bubble tail
        main_layout.setSpacing(4)

        # Header / Status Badge
        self.lbl_status = QLabel("✨ FruityFocus", self)
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("""
            QLabel {
                color: #ffb703;
                font-size: 11px;
                font-weight: bold;
                background-color: rgba(255, 183, 3, 0.15);
                border-radius: 4px;
                padding: 1px 4px;
            }
        """)
        main_layout.addWidget(self.lbl_status)

        # Time Display (retro digital / bold)
        self.lbl_time = QLabel("25:00", self)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: 900;
                font-family: 'Consolas', 'Courier New', monospace;
                letter-spacing: 1px;
            }
        """)
        main_layout.addWidget(self.lbl_time)

        # Button Controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        btn_style = """
            QPushButton {
                background-color: #2b2d42;
                color: #edf2f4;
                border: 1px solid #4a4e69;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                padding: 3px 6px;
                min-width: 24px;
                min-height: 22px;
            }
            QPushButton:hover {
                background-color: #f77f00;
                color: #ffffff;
                border-color: #fcbf49;
            }
            QPushButton:pressed {
                background-color: #d62828;
            }
        """

        self.btn_toggle = QPushButton("▶", self)
        self.btn_toggle.setToolTip("Iniciar / Pausar")
        self.btn_toggle.setStyleSheet(btn_style)
        self.btn_toggle.clicked.connect(self.toggle_timer.emit)
        btn_layout.addWidget(self.btn_toggle)

        self.btn_reset = QPushButton("🔄", self)
        self.btn_reset.setToolTip("Reiniciar")
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_reset.clicked.connect(self.reset_timer.emit)
        btn_layout.addWidget(self.btn_reset)

        self.btn_skip = QPushButton("⏭", self)
        self.btn_skip.setToolTip("Saltar período")
        self.btn_skip.setStyleSheet(btn_style)
        self.btn_skip.clicked.connect(self.skip_timer.emit)
        btn_layout.addWidget(self.btn_skip)

        self.btn_settings = QPushButton("⚙", self)
        self.btn_settings.setToolTip("Configurar")
        self.btn_settings.setStyleSheet(btn_style)
        self.btn_settings.clicked.connect(self.open_settings.emit)
        btn_layout.addWidget(self.btn_settings)

        main_layout.addLayout(btn_layout)

    def paintEvent(self, event):
        """Draws a smooth dark card with a speech bubble pointer at the bottom."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Bubble body rect
        w = self.width()
        h = self.height()
        tail_h = 10
        card_h = h - tail_h

        path = QPainterPath()
        path.addRoundedRect(1, 1, w - 2, card_h - 2, 10, 10)

        # Downward pointer tail
        center_x = w // 2
        tail_path = QPainterPath()
        tail_path.moveTo(center_x - 8, card_h - 2)
        tail_path.lineTo(center_x, h - 2)
        tail_path.lineTo(center_x + 8, card_h - 2)
        path.addPath(tail_path)

        # Fill background
        brush = QBrush(QColor(24, 24, 30, 235))
        painter.setBrush(brush)
        pen = QPen(QColor(247, 127, 0, 200), 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

    def update_display(self, time_str: str, state_name: str, is_paused: bool = False):
        self.lbl_time.setText(time_str)

        if "PAUSED" in state_name or is_paused:
            self.lbl_status.setText("⏸ Pausado")
            self.lbl_status.setStyleSheet("color: #ffca3a; background: rgba(255, 202, 58, 0.15); border-radius: 4px; padding: 1px 4px; font-weight: bold;")
            self.btn_toggle.setText("▶")
        elif state_name == "WORK":
            self.lbl_status.setText("🍅 Concentrado")
            self.lbl_status.setStyleSheet("color: #ff595e; background: rgba(255, 89, 94, 0.15); border-radius: 4px; padding: 1px 4px; font-weight: bold;")
            self.btn_toggle.setText("⏸")
        elif state_name in ("BREAK", "LONG_BREAK"):
            self.lbl_status.setText("☕ Descanso")
            self.lbl_status.setStyleSheet("color: #1982c4; background: rgba(25, 130, 196, 0.15); border-radius: 4px; padding: 1px 4px; font-weight: bold;")
            self.btn_toggle.setText("⏸")
        elif state_name == "CELEBRATING":
            self.lbl_status.setText("🎉 ¡Completado!")
            self.lbl_status.setStyleSheet("color: #8ac926; background: rgba(138, 201, 38, 0.15); border-radius: 4px; padding: 1px 4px; font-weight: bold;")
            self.btn_toggle.setText("▶")
        else:
            self.lbl_status.setText("✨ FruityFocus")
            self.lbl_status.setStyleSheet("color: #ffb703; background: rgba(255, 183, 3, 0.15); border-radius: 4px; padding: 1px 4px; font-weight: bold;")
            self.btn_toggle.setText("▶")

    def position_above_pet(self, pet_x: int, pet_y: int, pet_width: int):
        """Positions the bubble centered directly above the pet."""
        target_x = pet_x + (pet_width // 2) - (self.width() // 2)
        target_y = pet_y - self.height() + 4
        self.move(target_x, max(10, target_y))
