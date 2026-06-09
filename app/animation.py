"""
Animation Controller
====================
Manages animation timing, transforms (squish/stretch/bounce), eye tracking,
and smooth state transitions for the bunny.
"""

import math
import time
import random

from PySide6.QtCore import QPointF

from config import (
    DISPLAY_SCALE, EYE_TRACK_RADIUS, DRAG_STRETCH_FACTOR, STRETCH_MAX,
    SPRING_STIFFNESS, SPRING_DAMPING, IDLE_BOUNCE_AMPLITUDE, IDLE_BOUNCE_SPEED,
    BREATH_SCALE_AMOUNT, BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX, BLINK_DURATION,
    STRETCH_DURATION, SCROLL_REACT_DURATION
)
from app.states import BunnyState
from app.utils import clamp, lerp, ease_out_quad


class AnimationController:
    """Controls all animation transforms and timing for the bunny."""

    def __init__(self):
        self._time = time.time()
        self._dt = 0.0

        # Transform state
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.rotation = 0.0  # Degrees

        # Eye tracking
        self.pupil_offset_x = 0.0
        self.pupil_offset_y = 0.0

        # Spring physics for settle
        self._spring_sx = 1.0
        self._spring_sy = 1.0
        self._spring_vx = 0.0
        self._spring_vy = 0.0
        self._spring_rot = 0.0
        self._spring_rot_v = 0.0

        # Drag velocity tracking
        self._drag_vx = 0.0
        self._drag_vy = 0.0
        self._last_drag_x = 0.0
        self._last_drag_y = 0.0

        # Blink
        self._next_blink = time.time() + random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
        self._blink_active = False
        self._blink_end = 0.0

        # Idle bounce phase
        self._bounce_phase = random.uniform(0, 2 * math.pi)

        # Typing frame counter
        self.typing_frame = 0
        self._typing_timer = 0.0

        # Nibble animation phase
        self._nibble_phase = 0.0
        self.nibble_frame = 0
        self._nibble_last_switch = 0.0

        # Walk frame
        self.walk_frame = 0
        self._walk_last_switch = 0.0

        # Scroll bounce
        self._scroll_bounce = 0.0
        self._scroll_dir = 1

    def update(self, state: BunnyState, state_elapsed: float,
               cursor_pos: QPointF, bunny_center: QPointF):
        """Update all animation parameters for the current frame."""
        now = time.time()
        self._dt = min(now - self._time, 0.1)  # Cap to avoid jumps
        self._time = now

        # Update eye tracking (works in most states)
        self._update_eye_tracking(state, cursor_pos, bunny_center)

        # Update blink
        self._update_blink(now, state)

        # Update state-specific transforms
        if state == BunnyState.IDLE:
            self._update_idle()
        elif state == BunnyState.LOOK:
            self._update_idle()  # Same bounce, eyes do the looking
        elif state == BunnyState.NIBBLE:
            self._update_nibble(state_elapsed)
        elif state == BunnyState.PET:
            self._update_pet(state_elapsed)
        elif state == BunnyState.DRAG:
            self._update_drag()
        elif state == BunnyState.SETTLE:
            self._update_settle(state_elapsed)
        elif state == BunnyState.STRETCH:
            self._update_stretch(state_elapsed)
        elif state == BunnyState.HUNT:
            self._update_hunt(state_elapsed, cursor_pos, bunny_center)
        elif state == BunnyState.TYPING:
            self._update_typing(now)
        elif state == BunnyState.WALK:
            self._update_walk(now)
        elif state == BunnyState.SCROLL_REACT:
            self._update_scroll_react(state_elapsed)
        elif state == BunnyState.REMIND:
            self._update_idle()  # Gentle idle during reminder
        else:
            self._reset_transforms()

    def _update_eye_tracking(self, state: BunnyState, cursor: QPointF, center: QPointF):
        """Update pupil offset based on cursor position."""
        if state in (BunnyState.STRETCH, BunnyState.PET):
            # No eye tracking during these states
            self.pupil_offset_x = lerp(self.pupil_offset_x, 0, 0.2)
            self.pupil_offset_y = lerp(self.pupil_offset_y, 0, 0.2)
            return

        dx = cursor.x() - center.x()
        dy = cursor.y() - center.y()
        dist = max(1.0, math.sqrt(dx * dx + dy * dy))

        # Normalize and scale to eye radius (in display pixels)
        max_offset = EYE_TRACK_RADIUS * DISPLAY_SCALE
        target_x = clamp((dx / dist) * max_offset, -max_offset, max_offset)
        target_y = clamp((dy / dist) * max_offset, -max_offset, max_offset)

        # Smooth lerp
        self.pupil_offset_x = lerp(self.pupil_offset_x, target_x, 0.15)
        self.pupil_offset_y = lerp(self.pupil_offset_y, target_y, 0.15)

    def _update_blink(self, now: float, current_state: BunnyState):
        """Handle periodic blinking."""
        if current_state in (BunnyState.PET, BunnyState.STRETCH):
            self._blink_active = False
            return

        if self._blink_active:
            if now >= self._blink_end:
                self._blink_active = False
                self._next_blink = now + random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
        else:
            if now >= self._next_blink:
                self._blink_active = True
                self._blink_end = now + BLINK_DURATION

    @property
    def is_blinking(self) -> bool:
        return self._blink_active

    def _update_idle(self):
        """Gentle breathing and bounce during idle."""
        self._bounce_phase += self._dt * IDLE_BOUNCE_SPEED * 2 * math.pi
        bounce = math.sin(self._bounce_phase) * IDLE_BOUNCE_AMPLITUDE
        breath = math.sin(self._bounce_phase * 0.5) * BREATH_SCALE_AMOUNT

        self.offset_x = 0.0
        self.offset_y = bounce
        self.scale_x = 1.0 + breath
        self.scale_y = 1.0 - breath * 0.5

    def _update_nibble(self, elapsed: float):
        """Nibbling animation with slight bobbing."""
        self._nibble_phase += self._dt * 12.0
        bounce = math.sin(self._nibble_phase) * 1.5
        self.offset_y = bounce

        now = time.time()
        if now - self._nibble_last_switch > 0.2:
            self.nibble_frame = 1 if self.nibble_frame == 0 else 0
            self._nibble_last_switch = now
        self.scale_x = 1.0
        self.scale_y = 1.0

    def _update_pet(self, elapsed: float):
        """Happy petting reaction — gentle squish bounce."""
        phase = elapsed * 4.0
        squish = math.sin(phase) * 0.04
        self.scale_x = 1.0 + squish
        self.scale_y = 1.0 - squish
        self.offset_x = 0.0
        self.offset_y = math.sin(phase * 0.7) * 1.0

    def _update_drag(self):
        """Squish/stretch based on drag velocity."""
        # Velocity is set externally by the window
        speed_y = abs(self._drag_vy)
        stretch_y = clamp(speed_y * DRAG_STRETCH_FACTOR, 0, STRETCH_MAX)
        
        # When dragged up/down, stretch vertically
        if self._drag_vy < 0:
            # Dragged up: stretch long
            self.scale_x = 1.0 - stretch_y * 0.6
            self.scale_y = 1.0 + stretch_y
        elif self._drag_vy > 0:
            # Dragged down: squish slightly
            self.scale_x = 1.0 + stretch_y * 0.6
            self.scale_y = 1.0 - stretch_y * 0.3
        else:
            self.scale_x = 1.0
            self.scale_y = 1.0

        # When dragged side to side, wave (rotate)
        # _drag_vx is in pixels per frame roughly. Multiply by a factor for degrees.
        target_rotation = clamp(self._drag_vx * 0.8, -45.0, 45.0)
        # Smooth the rotation slightly
        self.rotation = lerp(self.rotation, target_rotation, 0.3)

        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # Apply heavy friction so that if the mouse stops moving but is still held,
        # the stretch immediately dissipates.
        self._drag_vx *= 0.5
        self._drag_vy *= 0.5

    def set_drag_velocity(self, vx: float, vy: float):
        """Called by the window to update drag velocity."""
        self._drag_vx = vx
        self._drag_vy = vy

    def start_settle(self):
        """Initialize spring physics from current stretch state."""
        self._spring_sx = self.scale_x
        self._spring_sy = self.scale_y
        self._spring_vx = self._drag_vx * 0.02
        self._spring_vy = self._drag_vy * 0.02
        self._spring_rot = self.rotation
        self._spring_rot_v = self._drag_vx * 0.1

    def _update_settle(self, elapsed: float):
        """Spring recovery after drag release."""
        # Spring toward scale (1.0, 1.0)
        self._spring_vx += (1.0 - self._spring_sx) * SPRING_STIFFNESS
        self._spring_vy += (1.0 - self._spring_sy) * SPRING_STIFFNESS
        self._spring_vx *= SPRING_DAMPING
        self._spring_vy *= SPRING_DAMPING
        self._spring_sx += self._spring_vx
        self._spring_sy += self._spring_vy
        
        # Spring toward rotation 0
        self._spring_rot_v += (0.0 - self._spring_rot) * (SPRING_STIFFNESS * 0.5)
        self._spring_rot_v *= 0.85  # slightly more damping for rotation
        self._spring_rot += self._spring_rot_v

        self.scale_x = self._spring_sx
        self.scale_y = self._spring_sy
        self.rotation = self._spring_rot
        self.offset_x = 0.0
        self.offset_y = 0.0

    def is_settle_complete(self) -> bool:
        """Check if spring has mostly settled."""
        return (abs(self.scale_x - 1.0) < 0.005 and
                abs(self.scale_y - 1.0) < 0.005 and
                abs(self._spring_vx) < 0.005 and
                abs(self._spring_vy) < 0.005)

    def _update_stretch(self, elapsed: float):
        """Click-triggered stretch animation."""
        t = clamp(elapsed / STRETCH_DURATION, 0, 1)
        if t < 0.3:
            # Crouch down first
            p = t / 0.3
            self.scale_x = 1.0 + p * 0.1
            self.scale_y = 1.0 - p * 0.12
        elif t < 0.7:
            # Stretch up
            p = (t - 0.3) / 0.4
            self.scale_x = 1.1 - p * 0.15
            self.scale_y = 0.88 + p * 0.22
        else:
            # Return to normal
            p = ease_out_quad((t - 0.7) / 0.3)
            self.scale_x = lerp(0.95, 1.0, p)
            self.scale_y = lerp(1.1, 1.0, p)

        self.offset_x = 0.0
        self.offset_y = 0.0

    def _update_hunt(self, elapsed: float, cursor: QPointF, center: QPointF):
        """Alert crouch with body tracking cursor."""
        sway = math.sin(elapsed * 3.0) * 0.02
        self.scale_x = 1.0 + sway
        self.scale_y = 0.95 - abs(sway) * 0.3
        self.offset_x = 0.0
        self.offset_y = 2.0  # Crouched down

    def _update_typing(self, now: float):
        """Fast arm switching for typing state."""
        if now - self._typing_timer > 0.1:  # 100ms per frame
            self.typing_frame = 1 if self.typing_frame == 0 else 0
            self._typing_timer = now
        self.offset_x = 0.0
        self.offset_y = 0.0

    def _update_walk(self, now: float):
        """Walk animation using walk_frame swapping."""
        if now - self._walk_last_switch > 0.1:  # 100ms per step for a running look
            self.walk_frame = 1 if self.walk_frame == 0 else 0
            self._walk_last_switch = now
        # Subtle bob
        self.offset_y = -1.0 if self.walk_frame == 1 else 0.0
        self.offset_x = 0.0

    def start_scroll_react(self, direction: int):
        """Initialize scroll reaction."""
        self._scroll_bounce = 1.0
        self._scroll_dir = direction

    def _update_scroll_react(self, elapsed: float):
        """Brief bounce reaction to scrolling."""
        t = clamp(elapsed / SCROLL_REACT_DURATION, 0, 1)
        bounce = math.sin(t * math.pi * 2) * (1.0 - t) * 4.0
        self.offset_y = bounce * self._scroll_dir
        self.scale_x = 1.0
        self.scale_y = 1.0 + math.sin(t * math.pi) * 0.05
        self.offset_x = 0.0

    def _reset_transforms(self):
        """Reset all transforms to neutral."""
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
