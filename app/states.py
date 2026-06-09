"""
Bunny State Machine
===================
Defines all behavioral states and manages transitions with priorities.
"""

from enum import Enum, auto
import time


class BunnyState(Enum):
    """All possible bunny behavioral states, ordered by display priority."""
    IDLE = auto()
    LOOK = auto()
    NIBBLE = auto()
    WALK = auto()
    SCROLL_REACT = auto()
    DIZZY = auto()
    REMIND = auto()
    HUNT = auto()
    TYPING = auto()
    STRETCH = auto()
    PET = auto()
    SETTLE = auto()
    DRAG = auto()

    @property
    def priority(self) -> int:
        """Higher priority states override lower ones."""
        return {
            BunnyState.IDLE: 0,
            BunnyState.LOOK: 1,
            BunnyState.NIBBLE: 1,
            BunnyState.WALK: 1,
            BunnyState.SCROLL_REACT: 2,
            BunnyState.DIZZY: 2,
            BunnyState.REMIND: 2,
            BunnyState.HUNT: 3,
            BunnyState.TYPING: 4,
            BunnyState.STRETCH: 5,
            BunnyState.PET: 6,
            BunnyState.SETTLE: 7,
            BunnyState.DRAG: 10,
        }[self]


# Map states to their sprite base name
STATE_SPRITE_MAP = {
    BunnyState.IDLE:          'idle',
    BunnyState.LOOK:          'idle',     # Uses eye tracking for look direction
    BunnyState.NIBBLE:        'nibble',
    BunnyState.WALK:          'walk1',
    BunnyState.SCROLL_REACT:  'idle',     # Uses transform for bounce
    BunnyState.DIZZY:         'dizzy',
    BunnyState.REMIND:        'idle',
    BunnyState.HUNT:          'hunt',
    BunnyState.TYPING:        'typing',
    BunnyState.STRETCH:       'stretch',
    BunnyState.PET:           'happy',
    BunnyState.SETTLE:        'idle',     # Uses spring transform
    BunnyState.DRAG:          'idle',     # Uses stretch transform
}


class StateManager:
    """Manages bunny state transitions with priority and cooldown logic."""

    def __init__(self):
        self._state = BunnyState.IDLE
        self._state_start_time = time.time()
        self._previous_state = BunnyState.IDLE
        self._locked = False  # True during non-interruptible animations

    @property
    def state(self) -> BunnyState:
        return self._state

    @property
    def previous_state(self) -> BunnyState:
        return self._previous_state

    @property
    def state_elapsed(self) -> float:
        """Seconds since current state began."""
        return time.time() - self._state_start_time

    @property
    def is_idle_family(self) -> bool:
        """True if in any idle-like state (idle, look, nibble, walk)."""
        return self._state in (BunnyState.IDLE, BunnyState.LOOK, BunnyState.NIBBLE, BunnyState.WALK)

    def can_transition_to(self, new_state: BunnyState) -> bool:
        """Check if transition to new_state is allowed."""
        if new_state == self._state:
            return False

        # Drag always wins
        if new_state == BunnyState.DRAG:
            return True

        # Cannot interrupt drag
        if self._state == BunnyState.DRAG:
            return False

        # Settle can only be interrupted by drag or pet
        if self._state == BunnyState.SETTLE:
            return new_state in (BunnyState.DRAG, BunnyState.PET)

        # Stretch animation plays fully unless dragged
        if self._state == BunnyState.STRETCH:
            return new_state == BunnyState.DRAG

        # Higher or equal priority can override
        return new_state.priority >= self._state.priority

    def transition_to(self, new_state: BunnyState, force: bool = False) -> bool:
        """Attempt transition. Returns True if transition occurred."""
        if not force and not self.can_transition_to(new_state):
            return False

        self._previous_state = self._state
        self._state = new_state
        self._state_start_time = time.time()
        return True

    def reset_to_idle(self):
        """Return to idle state."""
        self.transition_to(BunnyState.IDLE, force=True)

    def get_sprite_name(self) -> str:
        """Get the sprite base name for the current state."""
        return STATE_SPRITE_MAP.get(self._state, 'idle')
