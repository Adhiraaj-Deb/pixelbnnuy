"""
Bunny Window
=============
The main transparent always-on-top window that renders and animates the bunny.
Handles all mouse interaction, state management, and rendering.
"""

import time
import random
import math

from PySide6.QtWidgets import QMainWindow, QApplication, QMenu
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRect
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor,
    QFont, QTransform, QRegion, QAction
)

_active_bunnies = []

from config import (
    SPRITE_SIZE, DISPLAY_SCALE, WINDOW_PADDING, FRAME_INTERVAL_MS,
    IDLE_SWITCH_MIN, IDLE_SWITCH_MAX, NIBBLE_DURATION, LOOK_DURATION,
    STRETCH_DURATION, HUNT_TIMEOUT, TYPING_COOLDOWN, SCROLL_REACT_DURATION,
    SETTLE_DURATION, HUNT_TRIGGER_DISTANCE, HUNT_TRIGGER_SPEED, HUNT_MIN_SAMPLES,
    WALK_DURATION,
    TRIPLE_CLICK_WINDOW, PET_HOVER_DELAY, REMINDER_ENABLED, REMINDER_INTERVAL,
    REMINDER_DURATION, REMINDER_MESSAGES, PALETTES, PALETTE_NAMES,
    START_X, START_Y
)
from app.states import BunnyState, StateManager
from app.sprite import SpriteManager
from app.animation import AnimationController
from app.input_monitor import InputMonitor
from app.utils import distance, clamp


class BunnyWindow(QMainWindow):
    """Transparent frameless always-on-top window hosting the pixel bunny."""

    def __init__(self, assets_dir: str):
        super().__init__()

        # ── Window Setup ──
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |                # Hide from taskbar
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Calculate window size
        self._sprite_display_size = SPRITE_SIZE * DISPLAY_SCALE
        self._win_size = self._sprite_display_size + WINDOW_PADDING * 2
        self.setFixedSize(self._win_size, self._win_size)

        # ── Core Systems ──
        self.sprites = SpriteManager(assets_dir)
        self.state_mgr = StateManager()
        self.anim = AnimationController()
        self.input_monitor = InputMonitor(typing_cooldown=TYPING_COOLDOWN)

        # ── Interaction State ──
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._drag_start_window = QPoint()
        self._dragging = False
        self._shake_count = 0
        self._last_drag_dx = 0
        
        self.walk_velocity = QPointF(0.0, 0.0)
        self._exact_pos = QPointF(float(self.x()), float(self.y()))

        self._hover = False
        self._hover_start = 0.0

        self._click_times: list[float] = []

        self._idle_timer = time.time() + random.uniform(IDLE_SWITCH_MIN, IDLE_SWITCH_MAX)

        # Reminder
        self._reminder_timer = time.time() + REMINDER_INTERVAL if REMINDER_ENABLED else float('inf')
        self._reminder_visible = False
        self._reminder_end = 0.0
        self._reminder_message = ""
        
        # Stretch tracking
        self._last_stretch_time = time.time()
        self._last_walk_time = time.time()
        
        # ── Position Window ──
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = START_X if START_X is not None else geo.width() * 2 // 3
            y = START_Y if START_Y is not None else geo.height() - self._win_size - 50
        else:
            x, y = 400, 400
        self.move(int(x), int(y))

        # ── Connect Input Signals ──
        self.input_monitor.keyboard_active.connect(self._on_keyboard_active)
        self.input_monitor.keyboard_idle.connect(self._on_keyboard_idle)
        self.input_monitor.scroll_detected.connect(self._on_scroll)

        # ── Main Update Timer ──
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(FRAME_INTERVAL_MS)

        # ── Start Input Monitoring ──
        self.input_monitor.start()

        _active_bunnies.append(self)
        self.show()

    # ── Update Loop ──────────────────────────────────────

    def _update(self):
        """Main update tick — runs at FRAME_RATE fps."""
        now = time.time()
        state = self.state_mgr.state
        elapsed = self.state_mgr.state_elapsed

        # Check typing cooldown
        self.input_monitor.check_typing_cooldown()

        # Handle state durations and auto-transitions
        self._handle_state_timeouts(now, state, elapsed)

        # Check for hunt trigger (cursor near bunny + teasing motion)
        if self.state_mgr.is_idle_family:
            self._check_hunt_trigger()

        # Check idle behavior changes
        if self.state_mgr.is_idle_family and state == BunnyState.IDLE:
            if now >= self._idle_timer:
                self._trigger_random_idle()

        # Check reminder
        if REMINDER_ENABLED and now >= self._reminder_timer and not self._reminder_visible:
            self._trigger_reminder(now)
        if self._reminder_visible and now >= self._reminder_end:
            self._reminder_visible = False
            if self.state_mgr.state == BunnyState.REMIND:
                self.state_mgr.reset_to_idle()
        
        if state == BunnyState.WALK:
            # Move window
            self._exact_pos += self.walk_velocity
            new_pos = self._exact_pos.toPoint()
            
            screen = QApplication.primaryScreen().availableGeometry()
            win_w = self.width()
            win_h = self.height()
            
            # Bounce off walls
            if new_pos.x() < screen.left():
                self._exact_pos.setX(float(screen.left()))
                self.walk_velocity.setX(abs(self.walk_velocity.x()))
            elif new_pos.x() > screen.right() - win_w:
                self._exact_pos.setX(float(screen.right() - win_w))
                self.walk_velocity.setX(-abs(self.walk_velocity.x()))
                
            if new_pos.y() < screen.top():
                self._exact_pos.setY(float(screen.top()))
                self.walk_velocity.setY(abs(self.walk_velocity.y()))
            elif new_pos.y() > screen.bottom() - win_h:
                self._exact_pos.setY(float(screen.bottom() - win_h))
                self.walk_velocity.setY(-abs(self.walk_velocity.y()))
                
            self.move(self._exact_pos.toPoint())

        # Update animation
        cursor_global = QCursor.pos()
        bunny_center = self._get_bunny_center_global()
        self.anim.update(
            state, elapsed,
            QPointF(cursor_global.x(), cursor_global.y()),
            QPointF(bunny_center.x(), bunny_center.y())
        )

        # Check settle completion
        if state == BunnyState.SETTLE and self.anim.is_settle_complete():
            self.state_mgr.reset_to_idle()

        self.update()  # Trigger repaint

    def _handle_state_timeouts(self, now: float, state: BunnyState, elapsed: float):
        """Auto-return to idle when timed states expire."""
        timeouts = {
            BunnyState.NIBBLE: NIBBLE_DURATION,
            BunnyState.LOOK: LOOK_DURATION,
            BunnyState.STRETCH: STRETCH_DURATION,
            BunnyState.SCROLL_REACT: SCROLL_REACT_DURATION,
            BunnyState.HUNT: HUNT_TIMEOUT,
            BunnyState.WALK: WALK_DURATION,
        }

        if state in timeouts and elapsed >= timeouts[state]:
            if state == BunnyState.WALK:
                # After finishing a walk, always stop and eat a carrot
                self.state_mgr.transition_to(BunnyState.NIBBLE)
            elif state == BunnyState.DIZZY:
                self._schedule_next_idle()
                self.state_mgr.reset_to_idle()
            else:
                self._schedule_next_idle()
                self.state_mgr.reset_to_idle()

    def _trigger_random_idle(self):
        """Randomly pick an idle animation. Stretch occurs roughly every 30s."""
        now = time.time()
        
        # Check if it's been ~30 seconds since the last stretch
        if now - self._last_stretch_time >= 30.0:
            self.state_mgr.transition_to(BunnyState.STRETCH)
            self._last_stretch_time = now
        # Trigger walk very frequently (every 5-10 seconds)
        elif now - self._last_walk_time >= random.uniform(5.0, 10.0):
            self.state_mgr.transition_to(BunnyState.WALK)
            self._last_walk_time = now
            # Faster walk/run speed (3 to 6 pixels per frame)
            speed = random.uniform(3.0, 6.0)
            angle = random.uniform(0, 2 * 3.14159)
            self.walk_velocity = QPointF(speed * math.cos(angle), speed * math.sin(angle))
            self._exact_pos = QPointF(float(self.x()), float(self.y()))
        else:
            # Otherwise just pick between eating and looking
            if random.random() < 0.5:
                self.state_mgr.transition_to(BunnyState.NIBBLE)
            else:
                self.state_mgr.transition_to(BunnyState.LOOK)

    def _schedule_next_idle(self):
        """Schedule the next idle behavior switch."""
        self._idle_timer = time.time() + random.uniform(IDLE_SWITCH_MIN, IDLE_SWITCH_MAX)

    def _check_hunt_trigger(self):
        """Check if cursor movement warrants hunt mode."""
        cursor = QCursor.pos()
        center = self._get_bunny_center_global()
        dist = distance(cursor.x(), cursor.y(), center.x(), center.y())

        if dist < HUNT_TRIGGER_DISTANCE:
            speed = self.input_monitor.get_mouse_speed()
            dir_changes = self.input_monitor.get_mouse_direction_changes()

            if speed > HUNT_TRIGGER_SPEED and dir_changes >= 2:
                self.state_mgr.transition_to(BunnyState.HUNT)

    def _trigger_reminder(self, now: float):
        """Activate a stretch/break reminder."""
        self._reminder_visible = True
        self._reminder_end = now + REMINDER_DURATION
        self._reminder_message = random.choice(REMINDER_MESSAGES)
        self._reminder_timer = now + REMINDER_INTERVAL
        if self.state_mgr.is_idle_family:
            self.state_mgr.transition_to(BunnyState.REMIND)

    def _get_bunny_center_global(self) -> QPoint:
        """Get the bunny's center in global screen coordinates."""
        local_center = QPoint(self._win_size // 2, self._win_size // 2)
        return self.mapToGlobal(local_center)

    # ── Mouse Events ─────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            now = time.time()

            # Track clicks for triple-click detection
            self._click_times.append(now)
            # Keep only recent clicks
            self._click_times = [t for t in self._click_times
                                 if now - t < TRIPLE_CLICK_WINDOW]

            if len(self._click_times) >= 3:
                # Triple click — cycle palette
                new_palette = self.sprites.cycle_palette()
                pal_data = PALETTES[new_palette]
                print(f"[Palette] Changed to: {pal_data.get('name', new_palette)}")
                self._click_times.clear()
                self.update()
                return

            # Start drag tracking
            self._dragging = True
            self._shake_count = 0
            self._last_drag_dx = 0
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_start_window = self.pos()
            self._drag_last_pos = self._drag_start_pos
            self.state_mgr.transition_to(BunnyState.DRAG)

    def mouseMoveEvent(self, event):
        if self._dragging:
            current = event.globalPosition().toPoint()
            delta = current - self._drag_start_pos
            self.move(self._drag_start_window + delta)

            # Calculate velocity for stretch and shake
            vx = current.x() - self._drag_last_pos.x()
            vy = current.y() - self._drag_last_pos.y()
            self.anim.set_drag_velocity(vx, vy)
            
            # Shake detection logic
            if abs(vx) > 2:  # Just moving it left and right a little bit
                if self._last_drag_dx != 0 and (vx > 0) != (self._last_drag_dx > 0):
                    self._shake_count += 1
                self._last_drag_dx = vx
                
            self._drag_last_pos = current

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False

            # Check if it was a click (minimal drag distance)
            total_drag = distance(
                self._drag_start_pos.x(), self._drag_start_pos.y(),
                event.globalPosition().toPoint().x(),
                event.globalPosition().toPoint().y()
            )

            if total_drag < 5:
                # It was a click, not a drag — trigger stretch
                self.anim.set_drag_velocity(0, 0)
                self.state_mgr.transition_to(BunnyState.STRETCH, force=True)
            elif self._shake_count > 3:
                # It was moved side to side — make it dizzy
                self.anim.set_drag_velocity(0, 0)
                self.state_mgr.transition_to(BunnyState.DIZZY, force=True)
            else:
                # Was a drag — settle with spring
                self.anim.start_settle()
                self.state_mgr.transition_to(BunnyState.SETTLE, force=True)

    def contextMenuEvent(self, event):
        """Right-click context menu."""
        menu = QMenu(self)
        
        new_bunny_action = QAction("New Bunny", self)
        new_bunny_action.triggered.connect(self._spawn_new_bunny)
        menu.addAction(new_bunny_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec(QCursor.pos())

    def _spawn_new_bunny(self):
        new_bunny = BunnyWindow(self.sprites.assets_dir)
        # It adds itself to _active_bunnies and shows itself in __init__

    def enterEvent(self, event):
        """Mouse enters the window — potential pet interaction."""
        self._hover = True
        self._hover_start = time.time()
        # Delayed pet trigger handled in update

    def leaveEvent(self, event):
        """Mouse leaves the window."""
        self._hover = False
        if self.state_mgr.state == BunnyState.PET:
            self.state_mgr.reset_to_idle()

    def _check_pet(self):
        """Check if hover has lasted long enough for petting."""
        if (self._hover and not self._dragging and
                self.state_mgr.state != BunnyState.PET and
                time.time() - self._hover_start >= PET_HOVER_DELAY):
            if self.state_mgr.can_transition_to(BunnyState.PET):
                self.state_mgr.transition_to(BunnyState.PET)

    # ── Input Signal Handlers ────────────────────────────

    def _on_keyboard_active(self):
        """Global keyboard activity detected."""
        if self.state_mgr.state != BunnyState.DRAG:
            self.state_mgr.transition_to(BunnyState.TYPING)

    def _on_keyboard_idle(self):
        """Typing cooldown expired."""
        if self.state_mgr.state == BunnyState.TYPING:
            self.state_mgr.reset_to_idle()

    def _on_scroll(self, direction: int):
        """Mouse scroll detected."""
        if self.state_mgr.is_idle_family or self.state_mgr.state == BunnyState.TYPING:
            self.anim.start_scroll_react(direction)
            self.state_mgr.transition_to(BunnyState.SCROLL_REACT)

    # ── Rendering ────────────────────────────────────────

    def paintEvent(self, event):
        """Render the bunny with current animation state."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        painter.setRenderHint(QPainter.Antialiasing, False)

        state = self.state_mgr.state

        # Also check hover -> pet
        self._check_pet()

        # Get current sprite
        sprite_name = self.state_mgr.get_sprite_name()

        # Handle typing frame alternation
        if state == BunnyState.TYPING and self.anim.typing_frame == 1:
            sprite_name = 'typing2'
            
        # Handle nibble frame alternation
        if state == BunnyState.NIBBLE and self.anim.nibble_frame == 1:
            sprite_name = 'nibble2'

        # Handle walk frame alternation
        if state == BunnyState.WALK and self.anim.walk_frame == 1:
            sprite_name = 'walk2'

        sprite = self.sprites.get_sprite(sprite_name)
        if sprite is None:
            sprite = self.sprites.get_sprite('idle')
        if sprite is None:
            painter.end()
            return

        # Calculate draw position (centered in window with offsets)
        cx = self._win_size / 2.0
        cy = self._win_size / 2.0
        half_w = self._sprite_display_size / 2.0
        half_h = self._sprite_display_size / 2.0

        # Apply transforms
        transform = QTransform()
        transform.translate(cx, cy)
        transform.scale(self.anim.scale_x, self.anim.scale_y)
        transform.rotate(self.anim.rotation)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)

        # Draw sprite
        draw_x = int(cx - half_w + self.anim.offset_x)
        draw_y = int(cy - half_h + self.anim.offset_y)
        painter.drawPixmap(draw_x, draw_y, sprite)

        # Draw pupils (eye tracking) if applicable
        eye_pos = self.sprites.get_eye_positions(sprite_name)
        if eye_pos is not None and not self.anim.is_blinking:
            self._draw_pupils(painter, draw_x, draw_y, eye_pos)
        elif eye_pos is not None and self.anim.is_blinking:
            self._draw_blink_lines(painter, draw_x, draw_y, eye_pos)

        # Reset transform for UI overlays
        painter.resetTransform()

        # Draw speech bubble if reminder is active
        if self._reminder_visible:
            self._draw_reminder(painter, cx, draw_y)

        if state == BunnyState.PET:
            self._draw_hearts(painter, cx, draw_y, self.state_mgr.state_elapsed)

        painter.end()

        # Update window mask for click-through on transparent areas
        self._update_mask()

    def _draw_pupils(self, painter: QPainter, sprite_x: int, sprite_y: int,
                     eye_pos: tuple[int, int, int, int]):
        """Draw dynamic pupils at eye positions with tracking offset."""
        lx, ly, rx, ry = eye_pos
        scale = DISPLAY_SCALE
        pupil_size = max(1, scale)  # Pupil is 1 art pixel

        # Offset
        ox = int(self.anim.pupil_offset_x)
        oy = int(self.anim.pupil_offset_y)

        palette_name = self.sprites.palette_name
        pupil_color = QColor(*PALETTES[palette_name]['pupil'])

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(pupil_color))

        # Left pupil (2×2 art pixels = 2*scale display pixels)
        painter.drawRect(
            sprite_x + lx + ox, sprite_y + ly + oy,
            pupil_size * 2, pupil_size * 2
        )
        # Right pupil
        painter.drawRect(
            sprite_x + rx + ox, sprite_y + ry + oy,
            pupil_size * 2, pupil_size * 2
        )

    def _draw_blink_lines(self, painter: QPainter, sprite_x: int, sprite_y: int,
                          eye_pos: tuple[int, int, int, int]):
        """Draw closed-eye lines during blink."""
        lx, ly, rx, ry = eye_pos
        scale = DISPLAY_SCALE
        palette_name = self.sprites.palette_name
        color = QColor(*PALETTES[palette_name]['outline'])

        pen = QPen(color, scale)
        painter.setPen(pen)

        # Left eye blink line
        painter.drawLine(
            sprite_x + lx - scale, sprite_y + ly + scale,
            sprite_x + lx + scale * 2, sprite_y + ly + scale
        )
        # Right eye blink line
        painter.drawLine(
            sprite_x + rx - scale, sprite_y + ry + scale,
            sprite_x + rx + scale * 2, sprite_y + ry + scale
        )

    def _draw_reminder(self, painter: QPainter, center_x: float, sprite_top_y: int):
        """Draw the reminder speech bubble above the bunny."""
        bubble = self.sprites.get_universal('speech_bubble')
        if bubble:
            bx = int(center_x - bubble.width() / 2)
            by = sprite_top_y - bubble.height() - 5
            painter.drawPixmap(bx, max(2, by), bubble)

        # Draw text in bubble
        font = QFont("Segoe UI", 7, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(100, 85, 75)))
        text_x = int(center_x - 30)
        text_y = max(10, sprite_top_y - 30)
        painter.drawText(QRect(text_x, text_y, 60, 16), Qt.AlignCenter, self._reminder_message)

    def _draw_hearts(self, painter: QPainter, center_x: float, sprite_top_y: int, elapsed: float):
        """Draw pulsating hearts above the bunny while being petted."""
        heart_sprite = self.sprites.get_universal('heart')
        if not heart_sprite:
            return

        import math
        scale1 = 1.0 + math.sin(elapsed * 6.0) * 0.25
        scale2 = 1.0 + math.sin(elapsed * 6.0 + 1.5) * 0.25

        w = heart_sprite.width()
        h = heart_sprite.height()

        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Draw left heart
        painter.save()
        painter.translate(center_x - 25, sprite_top_y - 10)
        painter.scale(scale1, scale1)
        painter.drawPixmap(int(-w/2), int(-h/2), heart_sprite)
        painter.restore()

        # Draw right heart
        painter.save()
        painter.translate(center_x + 25, sprite_top_y - 25)
        painter.scale(scale2, scale2)
        painter.drawPixmap(int(-w/2), int(-h/2), heart_sprite)
        painter.restore()

        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)

    def _update_mask(self):
        """Update window mask so transparent areas pass through clicks."""
        # Create a simple rectangular mask with some padding
        # This keeps the bunny area clickable but doesn't block the whole window
        pad = WINDOW_PADDING // 2
        sprite_area = QRect(
            pad, pad,
            self._win_size - pad * 2,
            self._win_size - pad * 2
        )
        self.setMask(QRegion(sprite_area))

    # ── Cleanup ──────────────────────────────────────────

    def closeEvent(self, event):
        """Clean shutdown."""
        if self in _active_bunnies:
            _active_bunnies.remove(self)
        self._timer.stop()
        self.input_monitor.stop()
        event.accept()
