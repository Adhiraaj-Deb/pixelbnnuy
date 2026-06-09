"""
Sprite Manager
==============
Loads and manages all bunny sprites, handles palette swapping and scaling.
"""

import os
from PySide6.QtGui import QPixmap, QImage, Qt
from PySide6.QtCore import QSize

from config import (
    SPRITE_SIZE, DISPLAY_SCALE, PALETTE_NAMES, DEFAULT_PALETTE,
    EYE_POSITIONS
)


class SpriteManager:
    """Loads sprites from disk, scales them, and manages palette cycling."""

    POSE_NAMES = ['idle', 'nibble', 'nibble2', 'happy', 'stretch', 'hunt', 'typing', 'typing2', 'walk1', 'walk2', 'dizzy']

    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self._palette_index = PALETTE_NAMES.index(DEFAULT_PALETTE)
        self._sprites: dict[str, dict[str, QPixmap]] = {}  # palette -> pose -> pixmap
        self._universal: dict[str, QPixmap] = {}
        self._display_size = SPRITE_SIZE * DISPLAY_SCALE

        self._load_all()

    def _load_all(self):
        """Load all sprite PNGs and scale to display size."""
        for palette_name in PALETTE_NAMES:
            self._sprites[palette_name] = {}
            for pose in self.POSE_NAMES:
                filename = f"{palette_name}_{pose}.png"
                filepath = os.path.join(self.assets_dir, filename)
                if os.path.exists(filepath):
                    pixmap = QPixmap(filepath)
                    # Scale up with nearest-neighbor for pixel-art crispness
                    scaled = pixmap.scaled(
                        QSize(self._display_size, self._display_size),
                        Qt.KeepAspectRatio,
                        Qt.FastTransformation
                    )
                    self._sprites[palette_name][pose] = scaled

        # Universal assets
        for name in ['carrot', 'speech_bubble', 'heart']:
            filepath = os.path.join(self.assets_dir, f"{name}.png")
            if os.path.exists(filepath):
                pixmap = QPixmap(filepath)
                # Speech bubble gets different scaling
                if name == 'speech_bubble':
                    scaled = pixmap.scaled(
                        pixmap.size() * DISPLAY_SCALE,
                        Qt.KeepAspectRatio,
                        Qt.FastTransformation
                    )
                else:
                    scaled = pixmap.scaled(
                        QSize(self._display_size, self._display_size),
                        Qt.KeepAspectRatio,
                        Qt.FastTransformation
                    )
                self._universal[name] = scaled

    @property
    def palette_name(self) -> str:
        return PALETTE_NAMES[self._palette_index]

    @property
    def display_size(self) -> int:
        return self._display_size

    def get_sprite(self, pose_name: str) -> QPixmap | None:
        """Get the scaled sprite for current palette and given pose."""
        palette = PALETTE_NAMES[self._palette_index]
        return self._sprites.get(palette, {}).get(pose_name)

    def get_universal(self, name: str) -> QPixmap | None:
        """Get a universal (non-palette) sprite."""
        return self._universal.get(name)

    def cycle_palette(self) -> str:
        """Advance to next palette. Returns new palette name."""
        self._palette_index = (self._palette_index + 1) % len(PALETTE_NAMES)
        return self.palette_name

    def get_eye_positions(self, pose_name: str) -> tuple[int, int, int, int] | None:
        """Get eye center coordinates (art pixels) for a pose, scaled to display.

        Returns (left_x, left_y, right_x, right_y) in display pixels, or None.
        """
        raw = EYE_POSITIONS.get(pose_name)
        if raw is None:
            return None
        scale = DISPLAY_SCALE
        return (raw[0] * scale, raw[1] * scale, raw[2] * scale, raw[3] * scale)
