"""
PetWindow for FruityFocus.
Frameless, transparent, always-on-top desktop pet with physics, drag & drop,
click-through transparency via dynamic window masking, context menu, and Pomodoro integration.
"""
import sys
import os
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QAction, QIcon, QCursor

from src.config import (
    DEFAULT_SCALE,
    ANIMATION_INTERVAL_MS,
    PHYSICS_INTERVAL_MS,
    CHIME_SOUND_PATH,
    ICON_PATH,
    AVAILABLE_SCALES
)
from src.sprites import SpriteManager
from src.physics_engine import PhysicsEngine
from src.animation_engine import AnimationController, AnimationState
from src.timer_engine import PomodoroEngine, PomodoroState
from src.speech_bubble import SpeechBubble
from src.settings_dialog import SettingsDialog

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Window configuration: Frameless, Always on Top, Tool (overlay without taskbar clutter)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Core Engines
        self.sprite_manager = SpriteManager()
        self.physics = PhysicsEngine()
        self.anim_ctrl = AnimationController(self.sprite_manager, self)
        self.timer_engine = PomodoroEngine(self)
        self.scale_factor = DEFAULT_SCALE
        self.sound_enabled = True
        self.always_show_bubble = True

        # Internal state
        self.current_pixmap = None
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.drag_offset = QPoint()
        self.drag_moved_distance = 0

        # Create Speech Bubble HUD
        self.speech_bubble = SpeechBubble()
        self._connect_bubble_signals()

        # Connect Timer Engine signals
        self.timer_engine.tick.connect(self._on_timer_tick)
        self.timer_engine.state_changed.connect(self._on_timer_state_changed)
        self.timer_engine.work_completed.connect(self._on_work_completed)
        self.timer_engine.break_completed.connect(self._on_break_completed)

        # Connect Animation signals
        self.anim_ctrl.frame_changed.connect(self._on_frame_changed)
        self.anim_ctrl.position_delta.connect(self._on_position_delta)

        # Timers: Animation and Physics
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(ANIMATION_INTERVAL_MS)
        self.anim_timer.timeout.connect(self._on_anim_tick)

        self.physics_timer = QTimer(self)
        self.physics_timer.setInterval(PHYSICS_INTERVAL_MS)
        self.physics_timer.timeout.connect(self._on_physics_tick)

        # Initial frame & size setup
        self._update_current_pixmap("idle", 0, False)
        self._init_position_on_taskbar()

        # Start timers and show
        self.anim_timer.start()
        self.physics_timer.start()
        self.show()
        self.raise_()

        if self.always_show_bubble:
            self.speech_bubble.show()
            self.speech_bubble.raise_()
            self._update_bubble_position()

    def _connect_bubble_signals(self):
        self.speech_bubble.toggle_timer.connect(self.timer_engine.toggle)
        self.speech_bubble.reset_timer.connect(self.timer_engine.reset)
        self.speech_bubble.skip_timer.connect(self.timer_engine.skip)
        self.speech_bubble.open_settings.connect(self.open_settings_dialog)

    def _init_position_on_taskbar(self):
        """Places the mango initially centered resting right on the taskbar."""
        geom = self.physics.get_usable_screen_geometry()
        init_x = geom.center().x() - (self.width() // 2)
        init_y = self.physics.get_ground_y(self.height())
        self.move(init_x, init_y)

    def _update_current_pixmap(self, state: str, frame_idx: int, flipped: bool):
        self.current_pixmap = self.sprite_manager.get_frame(
            state, frame_idx, scale=self.scale_factor, flipped=flipped
        )
        self.setFixedSize(self.current_pixmap.size())

        # CRITICAL FOR QA FASE 1: Set window mask so mouse clicks pass through transparent areas!
        # Only the opaque pixels of the mango register mouse events.
        mask = self.current_pixmap.mask()
        self.setMask(mask)
        self.update()

    def _update_bubble_position(self):
        if self.speech_bubble.isVisible():
            self.speech_bubble.position_above_pet(self.x(), self.y(), self.width())

    # --- Paint Event ---
    def paintEvent(self, event):
        if self.current_pixmap and not self.current_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.current_pixmap)

    # --- Mouse & Interaction Events ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPosition().toPoint()
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.drag_moved_distance = 0
            self.anim_ctrl.manual_override = True
            self.physics.stop_fall()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            curr_pos = event.globalPosition().toPoint()
            move_delta = curr_pos - self.drag_start_pos
            self.drag_moved_distance += abs(move_delta.x()) + abs(move_delta.y())
            new_pos = curr_pos - self.drag_offset
            self.move(new_pos)
            self._update_bubble_position()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.anim_ctrl.manual_override = False

            # If user barely moved mouse, treat as click to toggle Speech Bubble
            if self.drag_moved_distance < 8:
                if self.speech_bubble.isVisible():
                    self.speech_bubble.hide()
                else:
                    self.speech_bubble.show()
                    self._update_bubble_position()

            # Check if dropped in the air above taskbar
            ground_y = self.physics.get_ground_y(self.height())
            if self.y() < ground_y:
                self.physics.start_fall()
            else:
                self.move(self.x(), ground_y)
                self.physics.stop_fall()

            event.accept()

    # --- Animation & Physics Tick Handlers ---
    def _on_anim_tick(self):
        self.anim_ctrl.step_animation()

    def _on_physics_tick(self):
        geom = self.physics.get_usable_screen_geometry()
        min_x = geom.left()
        max_x = geom.right() - self.width()

        # Update autonomous wandering if on ground and not dragging
        if not self.is_dragging and not self.physics.is_falling:
            self.anim_ctrl.step_behavior(self.x(), min_x, max_x)

        # Update gravity if in free fall
        if self.physics.is_falling:
            new_x, new_y, just_landed = self.physics.update_gravity(
                self.x(), self.y(), self.width(), self.height()
            )
            self.move(new_x, new_y)
            self._update_bubble_position()
            if just_landed:
                # Returned firmly to ground
                self.anim_ctrl.set_state(AnimationState.IDLE)

    def _on_frame_changed(self, state: str, frame_idx: int, flipped: bool):
        self._update_current_pixmap(state, frame_idx, flipped)

    def _on_position_delta(self, dx: int, dy: int):
        if not self.is_dragging:
            self.move(self.x() + dx, self.y() + dy)
            self._update_bubble_position()

    # --- Pomodoro Handlers ---
    def _on_timer_tick(self, remaining_sec: int, total_sec: int, state_name: str):
        formatted = PomodoroEngine.format_time(remaining_sec)
        self.speech_bubble.update_display(formatted, state_name, self.timer_engine.is_paused)

    def _on_timer_state_changed(self, new_state: str, session_count: int):
        if new_state == PomodoroState.WORK:
            self.anim_ctrl.set_state(AnimationState.FOCUS)
            self.anim_ctrl.manual_override = True
        elif new_state in (PomodoroState.BREAK, PomodoroState.LONG_BREAK):
            self.anim_ctrl.set_state(AnimationState.BREAK)
            self.anim_ctrl.manual_override = True
        elif new_state == PomodoroState.IDLE:
            self.anim_ctrl.manual_override = False
            self.anim_ctrl.set_state(AnimationState.IDLE)
        elif new_state == PomodoroState.CELEBRATING:
            self.anim_ctrl.start_celebration()

        formatted = PomodoroEngine.format_time(self.timer_engine.remaining_seconds)
        self.speech_bubble.update_display(formatted, new_state, self.timer_engine.is_paused)

    def _on_work_completed(self):
        self._play_sound_alert()
        self.anim_ctrl.start_celebration()
        # After celebration, automatically prompt or transition to break
        QTimer.singleShot(6000, self._auto_advance_after_celebration)

    def _auto_advance_after_celebration(self):
        if self.timer_engine.current_state == PomodoroState.CELEBRATING:
            is_long = (self.timer_engine.completed_sessions % self.timer_engine.sessions_before_long == 0)
            self.timer_engine.start_break(is_long)

    def _on_break_completed(self):
        self._play_sound_alert()
        self.anim_ctrl.manual_override = False
        self.anim_ctrl.set_state(AnimationState.IDLE)

    def _play_sound_alert(self):
        if self.sound_enabled and HAS_WINSOUND and os.path.exists(CHIME_SOUND_PATH):
            try:
                winsound.PlaySound(CHIME_SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Audio playback error: {e}")

    # --- Context Menu ---
    def show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #f77f00;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f77f00;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: #3d405b;
                margin: 4px 8px;
            }
        """)

        # Timer Actions
        if self.timer_engine.current_state == PomodoroState.IDLE:
            act_start = menu.addAction("▶ Iniciar Temporizador")
            act_start.triggered.connect(self.timer_engine.start_work)
        elif self.timer_engine.is_paused:
            act_resume = menu.addAction("▶ Reanudar Temporizador")
            act_resume.triggered.connect(self.timer_engine.resume)
        else:
            act_pause = menu.addAction("⏸ Pausar Temporizador")
            act_pause.triggered.connect(self.timer_engine.pause)

        act_reset = menu.addAction("🔄 Reiniciar Temporizador")
        act_reset.triggered.connect(self.timer_engine.reset)

        act_skip = menu.addAction("⏭ Saltar Período")
        act_skip.triggered.connect(self.timer_engine.skip)

        menu.addSeparator()

        # Bubble visibility toggle
        bubble_text = "👁 Ocultar Contador" if self.speech_bubble.isVisible() else "👁 Mostrar Contador"
        act_bubble = menu.addAction(bubble_text)
        act_bubble.triggered.connect(self._toggle_bubble_visibility)

        # Scale Submenu
        scale_menu = menu.addMenu("🔍 Tamaño del Mango")
        for name, factor in AVAILABLE_SCALES.items():
            act_scale = scale_menu.addAction(name)
            act_scale.setCheckable(True)
            act_scale.setChecked(self.scale_factor == factor)
            act_scale.triggered.connect(lambda checked, f=factor: self.set_scale(f))

        act_settings = menu.addAction("⏱ Configurar Tiempos...")
        act_settings.triggered.connect(self.open_settings_dialog)

        menu.addSeparator()

        act_exit = menu.addAction("❌ Salir de FruityFocus")
        act_exit.triggered.connect(self.quit_app)

        menu.exec(global_pos)

    def _toggle_bubble_visibility(self):
        if self.speech_bubble.isVisible():
            self.speech_bubble.hide()
        else:
            self.speech_bubble.show()
            self._update_bubble_position()

    def set_scale(self, new_scale: int):
        self.scale_factor = new_scale
        # Recalculate ground position with new height
        self._update_current_pixmap(self.anim_ctrl.current_state, self.anim_ctrl.frame_idx, self.anim_ctrl.direction == -1)
        ground_y = self.physics.get_ground_y(self.height())
        self.move(self.x(), ground_y)
        self._update_bubble_position()

    def open_settings_dialog(self):
        dlg = SettingsDialog(
            current_work=self.timer_engine.work_seconds // 60,
            current_break=self.timer_engine.break_seconds // 60,
            current_long_break=self.timer_engine.long_break_seconds // 60,
            current_scale=self.scale_factor,
            sound_enabled=self.sound_enabled,
            always_show_bubble=self.always_show_bubble,
            parent=self
        )
        dlg.settings_saved.connect(self._on_settings_saved)
        dlg.exec()

    def _on_settings_saved(self, work_m, break_m, long_m, scale, sound, always_bubble):
        self.timer_engine.set_durations(work_m, break_m, long_m)
        self.sound_enabled = sound
        self.always_show_bubble = always_bubble
        if self.scale_factor != scale:
            self.set_scale(scale)
        if always_bubble and not self.speech_bubble.isVisible():
            self.speech_bubble.show()
            self._update_bubble_position()

    def quit_app(self):
        self.speech_bubble.close()
        self.close()
        sys.exit(0)
