"""
Global configuration and constants for FruityFocus.
"""
import os
import sys

# Directory paths
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
CHIME_SOUND_PATH = os.path.join(SOUNDS_DIR, "ding.wav")

# Default Pomodoro Timers (in minutes)
DEFAULT_WORK_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15
DEFAULT_SESSIONS_BEFORE_LONG_BREAK = 4

# Scale settings
# Base sprite is 32x32 pixels
DEFAULT_SCALE = 3  # 3x = 96x96 pixels
AVAILABLE_SCALES = {
    "Pequeño (64px)": 2,
    "Normal (96px)": 3,
    "Grande (128px)": 4,
}

# Physics settings
PHYSICS_FPS = 60
PHYSICS_INTERVAL_MS = int(1000 / PHYSICS_FPS)
GRAVITY = 1.15         # pixels per physics tick^2
TERMINAL_VELOCITY = 22.0
BOUNCE_DAMPING = 0.38  # elasticity of ground bounce
MIN_BOUNCE_VELOCITY = 2.5

# Walking settings
WALK_SPEED = 1.25      # pixels per tick
WANDER_MIN_WAIT_S = 3  # min idle seconds before walking
WANDER_MAX_WAIT_S = 8  # max idle seconds before walking
WANDER_MIN_WALK_S = 2  # min walk duration
WANDER_MAX_WALK_S = 6  # max walk duration

# Animation settings
ANIMATION_FPS = 10     # 10 frames per second
ANIMATION_INTERVAL_MS = int(1000 / ANIMATION_FPS)
CELEBRATION_DURATION_S = 6

# Styling constants
COLOR_PRIMARY = "#f77f00"
COLOR_PRIMARY_DARK = "#d62828"
COLOR_ACCENT = "#fcbf49"
COLOR_BG_CARD = "#1e1e24"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_MUTED = "#b0b0b0"
