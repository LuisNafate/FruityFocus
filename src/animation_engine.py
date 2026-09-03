"""
Animation and Behavior Controller for FruityFocus.
Manages animation states, frame timing, facing direction, and autonomous taskbar wandering.
"""
import random
import time
from PyQt6.QtCore import QObject, pyqtSignal
from src.config import (
    WALK_SPEED,
    WANDER_MIN_WAIT_S,
    WANDER_MAX_WAIT_S,
    WANDER_MIN_WALK_S,
    WANDER_MAX_WALK_S,
    CELEBRATION_DURATION_S
)

class AnimationState:
    IDLE = "idle"
    WALK = "walk"
    FOCUS = "focus"
    BREAK = "break"
    CELEBRATE = "celebrate"

class AnimationController(QObject):
    frame_changed = pyqtSignal(str, int, bool)  # (state, frame_idx, flipped)
    position_delta = pyqtSignal(int, int)       # (dx, dy)

    def __init__(self, sprite_manager, parent=None):
        super().__init__(parent)
        self.sprite_manager = sprite_manager
        
        self.current_state = AnimationState.IDLE
        self.frame_idx = 0
        self.direction = 1   # 1 = right, -1 = left (flipped)
        self.is_walking = False

        # Autonomous wandering timers
        self._next_wander_time = time.time() + random.uniform(WANDER_MIN_WAIT_S, WANDER_MAX_WAIT_S)
        self._wander_stop_time = 0.0
        self._celebration_end_time = 0.0

        # State lock (e.g. while in Focus or Break or Celebrate or Dragging)
        self.manual_override = False

    def set_state(self, new_state: str, force_reset_frame: bool = True):
        if self.current_state != new_state:
            self.current_state = new_state
            if force_reset_frame:
                self.frame_idx = 0
            if new_state == AnimationState.CELEBRATE:
                self._celebration_end_time = time.time() + CELEBRATION_DURATION_S
            self._notify_frame()

    def start_celebration(self):
        self.set_state(AnimationState.CELEBRATE)

    def step_animation(self):
        """Called by the animation QTimer (approx 10-12 FPS)."""
        count = self.sprite_manager.get_frame_count(self.current_state)
        if count > 0:
            self.frame_idx = (self.frame_idx + 1) % count

        # Check celebration timeout
        now = time.time()
        if self.current_state == AnimationState.CELEBRATE:
            if now >= self._celebration_end_time:
                # Transition back to break or idle
                self.set_state(AnimationState.BREAK)

        self._notify_frame()

    def step_behavior(self, current_x: int, min_x: int, max_x: int):
        """
        Called regularly to process movement and autonomous wandering.
        """
        now = time.time()

        # Autonomous wandering only happens in IDLE or WALK state (when not manually overridden)
        if not self.manual_override and self.current_state in (AnimationState.IDLE, AnimationState.WALK):
            if not self.is_walking:
                if now >= self._next_wander_time:
                    # Start walking
                    self.is_walking = True
                    self.direction = random.choice([-1, 1])
                    self._wander_stop_time = now + random.uniform(WANDER_MIN_WALK_S, WANDER_MAX_WALK_S)
                    self.set_state(AnimationState.WALK, force_reset_frame=False)
            else:
                if now >= self._wander_stop_time:
                    # Stop walking, return to idle
                    self.is_walking = False
                    self._next_wander_time = now + random.uniform(WANDER_MIN_WAIT_S, WANDER_MAX_WAIT_S)
                    self.set_state(AnimationState.IDLE, force_reset_frame=False)

        # If currently walking, calculate movement
        if self.current_state == AnimationState.WALK:
            dx = int(self.direction * WALK_SPEED)
            new_x = current_x + dx

            # Screen bounds check: bounce back if hitting borders
            if new_x <= min_x:
                self.direction = 1
                dx = abs(dx)
            elif new_x >= max_x:
                self.direction = -1
                dx = -abs(dx)

            if dx != 0:
                self.position_delta.emit(dx, 0)

    def _notify_frame(self):
        # When facing left (direction == -1), flip the sprite horizontally
        flipped = (self.direction == -1)
        self.frame_changed.emit(self.current_state, self.frame_idx, flipped)
