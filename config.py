"""
Pixelbnnuy Configuration
========================
All tunable constants for the desktop pet bunny.
Adjust these to change behavior, appearance, and timing.
"""

# ── Display ──────────────────────────────────────────────
SPRITE_SIZE = 32          # Native art pixel resolution
DISPLAY_SCALE = 4         # Scale factor (32×4 = 128px on screen)
WINDOW_PADDING = 40       # Extra space around sprite for stretch animations

# ── Animation Timing ─────────────────────────────────────
FRAME_RATE = 30           # Target FPS
FRAME_INTERVAL_MS = 1000 // FRAME_RATE

# Idle behavior timing (seconds)
IDLE_SWITCH_MIN = 3.0     # Min seconds before switching idle variant
IDLE_SWITCH_MAX = 10.0    # Max seconds before switching idle variant
NIBBLE_DURATION = 4.0     # Seconds for eating animation
LOOK_DURATION = 2.0       # Seconds for looking around
STRETCH_DURATION = 3.0    # Seconds for click-stretch animation
WALK_DURATION = 5.0       # Seconds for walking animation
DIZZY_DURATION = 2.0      # Seconds for recovering from being shaken animation
HUNT_TIMEOUT = 3.0        # Seconds before hunt mode expires
TYPING_COOLDOWN = 1.5     # Seconds after last keypress before exiting typing state
SCROLL_REACT_DURATION = 0.6  # Seconds for scroll reaction
SETTLE_DURATION = 0.8     # Seconds for spring settle after drag
BLINK_INTERVAL_MIN = 2.0  # Min seconds between blinks
BLINK_INTERVAL_MAX = 6.0  # Max seconds between blinks
BLINK_DURATION = 0.15     # Seconds eyes stay closed

# ── Interaction ──────────────────────────────────────────
EYE_TRACK_RADIUS = 2.0    # Max pupil movement in art pixels
DRAG_STRETCH_FACTOR = 0.02  # Velocity multiplier for stretch amount
STRETCH_MAX = 0.6         # Max stretch/squish deformation ratio
SPRING_STIFFNESS = 0.18   # Settle spring stiffness
SPRING_DAMPING = 0.65     # Settle spring damping
HUNT_TRIGGER_DISTANCE = 180  # Pixel distance to trigger hunt
HUNT_TRIGGER_SPEED = 8.0  # Mouse speed threshold for hunt
HUNT_MIN_SAMPLES = 4      # Min mouse samples to detect teasing
TRIPLE_CLICK_WINDOW = 0.5 # Seconds window for triple-click detection
PET_HOVER_DELAY = 0.3     # Seconds of hover before petting state

# ── Bounce / Idle Motion ─────────────────────────────────
IDLE_BOUNCE_AMPLITUDE = 1.5   # Pixels of vertical bounce
IDLE_BOUNCE_SPEED = 1.2       # Cycles per second
BREATH_SCALE_AMOUNT = 0.015   # Subtle breathing scale

# ── Reminder System ─────────────────────────────────────
REMINDER_ENABLED = True
REMINDER_INTERVAL = 1800  # Seconds between reminders (30 min)
REMINDER_DURATION = 6.0   # Seconds reminder stays visible
REMINDER_MESSAGES = [
    "Stretch time!",
    "Take a break~",
    "Look away!",
    "Drink water!",
    "Stand up!",
]

# ── Palettes ─────────────────────────────────────────────
PALETTE_NAMES = ['white', 'brown', 'gray', 'pink']
DEFAULT_PALETTE = 'white'

PALETTES = {
    'white': {
        'name': 'Snow',
        'outline':    (60,  50,  45,  255),
        'body':       (245, 240, 238, 255),
        'shadow':     (218, 210, 206, 255),
        'highlight':  (255, 252, 250, 255),
        'inner_ear':  (255, 182, 182, 255),
        'nose':       (255, 155, 155, 255),
        'blush':      (255, 195, 195, 160),
        'eye_white':  (255, 255, 255, 255),
        'pupil':      (35,  25,  20,  255),
        'belly':      (255, 248, 244, 255),
        'paw_pad':    (255, 188, 188, 255),
        'carrot':     (255, 140, 50,  255),
        'carrot_tip': (100, 170, 60,  255),
    },
    'brown': {
        'name': 'Cocoa',
        'outline':    (70,  42,  22,  255),
        'body':       (198, 158, 118, 255),
        'shadow':     (168, 128, 92,  255),
        'highlight':  (222, 188, 152, 255),
        'inner_ear':  (232, 162, 148, 255),
        'nose':       (178, 118, 98,  255),
        'blush':      (228, 168, 158, 160),
        'eye_white':  (255, 255, 255, 255),
        'pupil':      (35,  25,  20,  255),
        'belly':      (228, 198, 168, 255),
        'paw_pad':    (232, 168, 152, 255),
        'carrot':     (255, 140, 50,  255),
        'carrot_tip': (100, 170, 60,  255),
    },
    'gray': {
        'name': 'Storm',
        'outline':    (48,  48,  55,  255),
        'body':       (188, 188, 198, 255),
        'shadow':     (158, 158, 170, 255),
        'highlight':  (212, 212, 222, 255),
        'inner_ear':  (218, 178, 192, 255),
        'nose':       (198, 158, 172, 255),
        'blush':      (218, 182, 198, 160),
        'eye_white':  (255, 255, 255, 255),
        'pupil':      (28,  28,  38,  255),
        'belly':      (208, 208, 218, 255),
        'paw_pad':    (212, 178, 188, 255),
        'carrot':     (255, 140, 50,  255),
        'carrot_tip': (100, 170, 60,  255),
    },
    'pink': {
        'name': 'Sakura',
        'outline':    (138, 78, 98,  255),
        'body':       (255, 208, 218, 255),
        'shadow':     (238, 182, 198, 255),
        'highlight':  (255, 232, 238, 255),
        'inner_ear':  (255, 168, 188, 255),
        'nose':       (238, 148, 168, 255),
        'blush':      (255, 178, 198, 160),
        'eye_white':  (255, 255, 255, 255),
        'pupil':      (78,  38,  52,  255),
        'belly':      (255, 225, 232, 255),
        'paw_pad':    (255, 172, 192, 255),
        'carrot':     (255, 140, 50,  255),
        'carrot_tip': (100, 170, 60,  255),
    },
}

# ── Eye Metadata (art pixel coordinates for each pose) ───
# (left_eye_center_x, left_eye_center_y, right_eye_center_x, right_eye_center_y)
EYE_POSITIONS = {
    'idle':    (12, 15, 21, 15),
    'nibble':  (12, 15, 21, 15),
    'nibble2': (12, 15, 21, 15),
    'happy':   None,  # Happy eyes are arcs, no pupils
    'stretch': None,  # Eyes closed during stretch
    'hunt':    (12, 15, 21, 15),
    'typing':  (12, 15, 21, 15),
    'typing2': (12, 15, 21, 15),
    'walk1':   (12, 16, 21, 16),
    'walk2':   (12, 16, 21, 16),
    'dizzy':   None,  # Dizzy eyes are drawn into the sprite
}

# ── Starting Position ────────────────────────────────────
START_X = None  # None = right third of screen
START_Y = None  # None = near bottom of screen
