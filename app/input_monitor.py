"""
Global Input Monitor
====================
Monitors keyboard activity and mouse scroll events using pynput.
Emits Qt signals so the main window can react safely from the UI thread.
"""

import time
import threading
from collections import deque

from PySide6.QtCore import QObject, Signal

try:
    from pynput import keyboard as pynput_keyboard
    from pynput import mouse as pynput_mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("[Warning] pynput not installed - keyboard/scroll reactions disabled.")
    print("  Install with: pip install pynput")


class InputMonitor(QObject):
    """Monitors global keyboard and mouse scroll events.

    Signals:
        keyboard_active: Emitted when keyboard activity is detected.
        keyboard_idle: Emitted after typing cooldown expires.
        scroll_detected(int): Emitted on scroll with direction (+1 up, -1 down).
    """

    keyboard_active = Signal()
    keyboard_idle = Signal()
    scroll_detected = Signal(int)

    def __init__(self, typing_cooldown: float = 1.5):
        super().__init__()
        self._typing_cooldown = typing_cooldown
        self._is_typing = False
        self._last_key_time = 0.0
        self._lock = threading.Lock()
        self._running = False

        # Mouse movement tracking for hunt detection
        self._mouse_positions: deque = deque(maxlen=20)
        self._mouse_speed = 0.0

        self._kb_listener = None
        self._mouse_listener = None

    def start(self):
        """Start the global input listeners."""
        if not PYNPUT_AVAILABLE:
            return

        self._running = True

        try:
            self._kb_listener = pynput_keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._kb_listener.daemon = True
            self._kb_listener.start()
        except Exception as e:
            print(f"[Warning] Keyboard listener failed: {e}")
            self._kb_listener = None

        try:
            self._mouse_listener = pynput_mouse.Listener(
                on_scroll=self._on_scroll,
                on_move=self._on_mouse_move
            )
            self._mouse_listener.daemon = True
            self._mouse_listener.start()
        except Exception as e:
            print(f"[Warning] Mouse listener failed: {e}")
            self._mouse_listener = None

    def stop(self):
        """Stop all listeners cleanly."""
        self._running = False
        if self._kb_listener:
            try:
                self._kb_listener.stop()
            except Exception:
                pass
        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass

    def _on_key_press(self, key):
        """Called on any key press (runs in pynput thread)."""
        if not self._running:
            return False
        now = time.time()
        with self._lock:
            self._last_key_time = now
            if not self._is_typing:
                self._is_typing = True
                try:
                    self.keyboard_active.emit()
                except RuntimeError:
                    pass

    def _on_key_release(self, key):
        """Called on key release (runs in pynput thread)."""
        pass  # Cooldown handled by check_typing_cooldown

    def _on_scroll(self, x, y, dx, dy):
        """Called on mouse scroll (runs in pynput thread)."""
        if not self._running:
            return False
        direction = 1 if dy > 0 else -1
        try:
            self.scroll_detected.emit(direction)
        except RuntimeError:
            pass

    def _on_mouse_move(self, x, y):
        """Track mouse movement for hunt speed calculation."""
        if not self._running:
            return False
        now = time.time()
        self._mouse_positions.append((x, y, now))

    def check_typing_cooldown(self):
        """Check if typing has stopped (call from UI timer).

        Returns True if typing just ended.
        """
        if not self._is_typing:
            return False

        with self._lock:
            now = time.time()
            if now - self._last_key_time > self._typing_cooldown:
                self._is_typing = False
                try:
                    self.keyboard_idle.emit()
                except RuntimeError:
                    pass
                return True
        return False

    @property
    def is_typing(self) -> bool:
        with self._lock:
            return self._is_typing

    def get_mouse_speed(self) -> float:
        """Calculate recent mouse movement speed (pixels/second)."""
        positions = list(self._mouse_positions)
        if len(positions) < 2:
            return 0.0

        # Use last few samples
        recent = positions[-5:]
        if len(recent) < 2:
            return 0.0

        total_dist = 0.0
        for i in range(1, len(recent)):
            x1, y1, _ = recent[i - 1]
            x2, y2, _ = recent[i]
            total_dist += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        time_span = recent[-1][2] - recent[0][2]
        if time_span < 0.01:
            return 0.0

        return total_dist / time_span

    def get_mouse_direction_changes(self) -> int:
        """Count horizontal direction changes in recent movement (for teasing detection)."""
        positions = list(self._mouse_positions)
        if len(positions) < 3:
            return 0

        recent = positions[-10:]
        changes = 0
        prev_dir = 0
        for i in range(1, len(recent)):
            dx = recent[i][0] - recent[i - 1][0]
            current_dir = 1 if dx > 0 else (-1 if dx < 0 else 0)
            if current_dir != 0 and current_dir != prev_dir and prev_dir != 0:
                changes += 1
            if current_dir != 0:
                prev_dir = current_dir

        return changes
