"""
Sprite Manager for FruityFocus.
Loads, caches, scales (nearest-neighbor) and provides flipped variants of sprites.
"""
import os
from PyQt6.QtGui import QPixmap, QTransform, QImage
from PyQt6.QtCore import Qt
from src.config import SPRITES_DIR

class SpriteManager:
    """Manages sprite frames and masks for the Mango character."""
    def __init__(self, sprites_dir=SPRITES_DIR):
        self.sprites_dir = sprites_dir
        self.raw_pixmaps = {}  # state -> list of QPixmap (32x32)
        self.cache = {}        # (state, frame_idx, scale, flipped) -> QPixmap
        self._load_all_sprites()

    def _load_all_sprites(self):
        states = ['idle', 'walk', 'focus', 'break', 'celebrate']
        for state in states:
            self.raw_pixmaps[state] = []
            frame_idx = 0
            while True:
                filename = f"{state}_{frame_idx}.png"
                path = os.path.join(self.sprites_dir, filename)
                if not os.path.exists(path):
                    break
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.raw_pixmaps[state].append(pixmap)
                frame_idx += 1

    def get_frame(self, state: str, frame_idx: int, scale: int = 3, flipped: bool = False) -> QPixmap:
        """
        Returns a scaled QPixmap for the requested state, frame, scale factor, and orientation.
        Uses FastTransformation (Nearest Neighbor) to maintain sharp pixel art aesthetics.
        """
        frames = self.raw_pixmaps.get(state, [])
        if not frames:
            # Fallback to idle if state not found
            frames = self.raw_pixmaps.get('idle', [])
        if not frames:
            # Create a 32x32 blank pixmap if nothing loaded
            return QPixmap(32 * scale, 32 * scale)

        safe_idx = frame_idx % len(frames)
        cache_key = (state, safe_idx, scale, flipped)
        if cache_key in self.cache:
            return self.cache[cache_key]

        base_pixmap = frames[safe_idx]
        target_w = base_pixmap.width() * scale
        target_h = base_pixmap.height() * scale

        scaled_pixmap = base_pixmap.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        if flipped:
            transform = QTransform()
            transform.scale(-1, 1)
            final_pixmap = scaled_pixmap.transformed(transform)
        else:
            final_pixmap = scaled_pixmap

        self.cache[cache_key] = final_pixmap
        return final_pixmap

    def get_frame_count(self, state: str) -> int:
        return len(self.raw_pixmaps.get(state, []))
