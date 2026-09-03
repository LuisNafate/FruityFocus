"""
Physics Engine for FruityFocus.
Handles gravity, ground landing on top of the Windows taskbar, bounce mechanics, and screen clamping.
"""
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QRect
from src.config import (
    GRAVITY,
    TERMINAL_VELOCITY,
    BOUNCE_DAMPING,
    MIN_BOUNCE_VELOCITY
)

class PhysicsEngine:
    def __init__(self):
        self.velocity_y = 0.0
        self.is_falling = False
        self.is_grounded = True

    @staticmethod
    def get_usable_screen_geometry() -> QRect:
        """
        Returns the desktop area available excluding the Windows taskbar.
        """
        screen = QGuiApplication.primaryScreen()
        if screen:
            return screen.availableGeometry()
        return QRect(0, 0, 1920, 1040)

    def get_ground_y(self, pet_height: int) -> int:
        """
        Calculates the Y coordinate such that the bottom of the pet aligns
        precisely with the top border of the Windows taskbar.
        """
        geom = self.get_usable_screen_geometry()
        # availableGeometry.bottom() is the last pixel row above the taskbar
        return geom.bottom() - pet_height + 1

    def start_fall(self, initial_vy: float = 0.0):
        self.velocity_y = initial_vy
        self.is_falling = True
        self.is_grounded = False

    def stop_fall(self):
        self.velocity_y = 0.0
        self.is_falling = False
        self.is_grounded = True

    def update_gravity(self, current_x: int, current_y: int, pet_width: int, pet_height: int) -> tuple[int, int, bool]:
        """
        Performs one physics step.
        Returns (new_x, new_y, just_landed_firmly).
        """
        if not self.is_falling:
            return current_x, current_y, False

        ground_y = self.get_ground_y(pet_height)
        self.velocity_y = min(self.velocity_y + GRAVITY, TERMINAL_VELOCITY)
        new_y = current_y + self.velocity_y

        just_landed = False

        if new_y >= ground_y:
            new_y = ground_y
            if abs(self.velocity_y) > MIN_BOUNCE_VELOCITY:
                # Elastic bounce
                self.velocity_y = -self.velocity_y * BOUNCE_DAMPING
            else:
                # Firm landing
                self.stop_fall()
                just_landed = True

        # Clamp horizontal position within usable screen
        geom = self.get_usable_screen_geometry()
        clamped_x = max(geom.left(), min(current_x, geom.right() - pet_width))

        return clamped_x, int(new_y), just_landed
