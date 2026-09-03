"""
Unit & Component Tests for FruityFocus.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.config import SPRITES_DIR
from src.sprites import SpriteManager
from src.physics_engine import PhysicsEngine
from src.animation_engine import AnimationController, AnimationState
from src.timer_engine import PomodoroEngine, PomodoroState

def run_tests():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    print("=== Testing SpriteManager ===")
    sprite_mgr = SpriteManager()
    for state in ['idle', 'walk', 'focus', 'break', 'celebrate']:
        count = sprite_mgr.get_frame_count(state)
        assert count > 0, f"State {state} has no frames loaded!"
        frame = sprite_mgr.get_frame(state, 0, scale=3, flipped=False)
        assert not frame.isNull(), f"Frame {state}_0 is null!"
        mask = frame.mask()
        assert not mask.isNull(), f"Frame {state}_0 mask is null!"
        print(f"  [OK] State '{state}': {count} frames loaded. Size: {frame.width()}x{frame.height()}")

    print("\n=== Testing PhysicsEngine ===")
    physics = PhysicsEngine()
    ground_y = physics.get_ground_y(96)
    print(f"  [OK] Ground Y for 96px pet: {ground_y}")
    assert ground_y > 0

    physics.start_fall(initial_vy=0.0)
    curr_y = ground_y - 200
    new_x, new_y, landed = physics.update_gravity(500, curr_y, 96, 96)
    assert new_y > curr_y, "Gravity should accelerate downwards!"
    print(f"  [OK] Gravity step: {curr_y} -> {new_y} (landed={landed})")

    print("\n=== Testing PomodoroEngine ===")
    timer = PomodoroEngine()
    assert timer.current_state == PomodoroState.IDLE
    timer.set_durations(work_min=25, break_min=5, long_break_min=15)
    assert timer.remaining_seconds == 25 * 60

    timer.start_work()
    assert timer.current_state == PomodoroState.WORK
    assert not timer.is_paused

    timer.pause()
    assert timer.is_paused

    timer.resume()
    assert not timer.is_paused

    timer.reset()
    assert timer.current_state == PomodoroState.IDLE
    assert timer.remaining_seconds == 25 * 60
    print("  [OK] Pomodoro state transitions verified.")

    print("\n=== Testing AnimationController ===")
    anim = AnimationController(sprite_mgr)
    assert anim.current_state == AnimationState.IDLE
    anim.step_animation()
    assert anim.frame_idx == 1
    anim.set_state(AnimationState.WALK)
    assert anim.current_state == AnimationState.WALK
    print("  [OK] AnimationController cycles frames.")

    print("\n>>> ALL TESTS PASSED! <<<")

if __name__ == "__main__":
    run_tests()
