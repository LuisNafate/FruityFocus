"""
Pomodoro Timer Engine for FruityFocus.
Manages focus sessions, breaks, cycles, and emits Qt signals for UI and character state updates.
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.config import (
    DEFAULT_WORK_MINUTES,
    DEFAULT_BREAK_MINUTES,
    DEFAULT_LONG_BREAK_MINUTES,
    DEFAULT_SESSIONS_BEFORE_LONG_BREAK
)

class PomodoroState:
    IDLE = "IDLE"
    WORK = "WORK"
    BREAK = "BREAK"
    LONG_BREAK = "LONG_BREAK"
    CELEBRATING = "CELEBRATING"

class PomodoroEngine(QObject):
    """
    Core timer logic. Runs a QTimer ticking every 1 second.
    """
    tick = pyqtSignal(int, int, str)              # (remaining_seconds, total_seconds, state)
    state_changed = pyqtSignal(str, int)          # (new_state, session_count)
    work_completed = pyqtSignal()
    break_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.work_seconds = DEFAULT_WORK_MINUTES * 60
        self.break_seconds = DEFAULT_BREAK_MINUTES * 60
        self.long_break_seconds = DEFAULT_LONG_BREAK_MINUTES * 60
        self.sessions_before_long = DEFAULT_SESSIONS_BEFORE_LONG_BREAK

        self.current_state = PomodoroState.IDLE
        self.total_seconds = self.work_seconds
        self.remaining_seconds = self.work_seconds
        self.completed_sessions = 0
        self.is_paused = False

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

    def set_durations(self, work_min: int, break_min: int, long_break_min: int = 15):
        self.work_seconds = max(1, work_min) * 60
        self.break_seconds = max(1, break_min) * 60
        self.long_break_seconds = max(1, long_break_min) * 60

        if self.current_state == PomodoroState.IDLE:
            self.total_seconds = self.work_seconds
            self.remaining_seconds = self.work_seconds
            self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

    def start_work(self):
        self.current_state = PomodoroState.WORK
        self.total_seconds = self.work_seconds
        self.remaining_seconds = self.work_seconds
        self.is_paused = False
        self._timer.start()
        self.state_changed.emit(self.current_state, self.completed_sessions)
        self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

    def start_break(self, is_long: bool = False):
        if is_long:
            self.current_state = PomodoroState.LONG_BREAK
            self.total_seconds = self.long_break_seconds
            self.remaining_seconds = self.long_break_seconds
        else:
            self.current_state = PomodoroState.BREAK
            self.total_seconds = self.break_seconds
            self.remaining_seconds = self.break_seconds

        self.is_paused = False
        self._timer.start()
        self.state_changed.emit(self.current_state, self.completed_sessions)
        self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

    def toggle(self):
        if self.current_state == PomodoroState.IDLE:
            self.start_work()
        else:
            if self.is_paused:
                self.resume()
            else:
                self.pause()

    def pause(self):
        if self._timer.isActive() and not self.is_paused:
            self.is_paused = True
            self._timer.stop()
            self.tick.emit(self.remaining_seconds, self.total_seconds, f"{self.current_state}_PAUSED")

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            self._timer.start()
            self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

    def reset(self):
        self._timer.stop()
        self.is_paused = False
        self.current_state = PomodoroState.IDLE
        self.total_seconds = self.work_seconds
        self.remaining_seconds = self.work_seconds
        self.state_changed.emit(self.current_state, self.completed_sessions)
        self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

    def skip(self):
        if self.current_state in (PomodoroState.IDLE, PomodoroState.WORK):
            # Skip to break
            self.completed_sessions += 1
            is_long = (self.completed_sessions % self.sessions_before_long == 0)
            self.start_break(is_long)
        else:
            # Skip break to work
            self.start_work()

    def _on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

        if self.remaining_seconds <= 0:
            self._timer.stop()
            self._handle_period_end()

    def _handle_period_end(self):
        if self.current_state == PomodoroState.WORK:
            self.completed_sessions += 1
            self.current_state = PomodoroState.CELEBRATING
            self.state_changed.emit(self.current_state, self.completed_sessions)
            self.work_completed.emit()
        elif self.current_state in (PomodoroState.BREAK, PomodoroState.LONG_BREAK):
            self.current_state = PomodoroState.IDLE
            self.total_seconds = self.work_seconds
            self.remaining_seconds = self.work_seconds
            self.state_changed.emit(self.current_state, self.completed_sessions)
            self.break_completed.emit()
            self.tick.emit(self.remaining_seconds, self.total_seconds, self.current_state)

    @staticmethod
    def format_time(seconds: int) -> str:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
