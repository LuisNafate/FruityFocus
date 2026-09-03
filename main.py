"""
FruityFocus - Desktop Pomodoro Virtual Pet
Main entry point.
"""
import sys
import os

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.config import ICON_PATH
from src.pet_window import PetWindow

def main():
    # Ensure process attaches to interactive 'default' desktop on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            DESKTOP_ALL = 0x01FF
            h_default = user32.OpenDesktopW("default", 0, False, DESKTOP_ALL)
            if h_default:
                user32.SetThreadDesktop(h_default)
        except Exception as e:
            print(f"Notice: Could not switch desktop: {e}")

    # Enable high-DPI rounding policy for pixel-crisp rendering
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("FruityFocus")
    app.setApplicationDisplayName("FruityFocus - Pomodoro Pet")
    app.setQuitOnLastWindowClosed(False)

    if os.path.exists(ICON_PATH):
        app_icon = QIcon(ICON_PATH)
        app.setWindowIcon(app_icon)
    else:
        app_icon = None

    # Instantiate desktop pet
    pet = PetWindow()

    # System Tray Icon integration
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray_icon = QSystemTrayIcon(app)
        if app_icon:
            tray_icon.setIcon(app_icon)
        tray_icon.setToolTip("FruityFocus - Temporizador Pomodoro")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #f77f00;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 5px 18px;
            }
            QMenu::item:selected {
                background-color: #f77f00;
            }
        """)

        act_toggle_timer = tray_menu.addAction("▶ Iniciar / Pausar")
        act_toggle_timer.triggered.connect(pet.timer_engine.toggle)

        act_toggle_pet = tray_menu.addAction("🥭 Mostrar / Ocultar Mascota")
        def toggle_pet_visible():
            if pet.isVisible():
                pet.hide()
                pet.speech_bubble.hide()
            else:
                pet.show()
                if pet.always_show_bubble:
                    pet.speech_bubble.show()
        act_toggle_pet.triggered.connect(toggle_pet_visible)

        act_settings = tray_menu.addAction("⚙ Configuración...")
        act_settings.triggered.connect(pet.open_settings_dialog)

        tray_menu.addSeparator()

        act_exit = tray_menu.addAction("❌ Salir")
        act_exit.triggered.connect(pet.quit_app)

        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()

    # Run application main loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
