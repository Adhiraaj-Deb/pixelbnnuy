"""
Pixelbnnuy Asset Generator
==========================
Procedurally generates all pixel-art sprite PNGs for the desktop pet bunny.
Run this module directly or call generate_all_assets() from code.
All art is created at 32×32 native resolution using Pillow drawing primitives.
"""

import os
import sys

from PIL import Image, ImageDraw

# Add parent to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PALETTES, PALETTE_NAMES, SPRITE_SIZE

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SIZE = SPRITE_SIZE  # 32


class BunnyArtist:
    """Draws pixel-art bunny sprites using Pillow primitives."""

    def __init__(self, palette_name: str):
        self.pal = PALETTES[palette_name]
        self.palette_name = palette_name

    def _new_canvas(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        return img, draw

    # ── Component Drawing Methods ────────────────────────

    def _draw_ears(self, draw, left_shift=0, right_shift=0,
                   left_tilt=0, right_tilt=0, relaxed=False, y_offset=0):
        """Draw bunny ears. Shifts move ear bases, tilt isn't used at pixel scale."""
        c = self.pal
        ear_top = (0 if not relaxed else 1) + y_offset

        # Left ear (outer)
        lx = 9 + left_shift
        draw.ellipse([lx, ear_top, lx + 4, 12], fill=c['body'], outline=c['outline'])
        # Left inner ear
        draw.ellipse([lx + 1, ear_top + 2, lx + 3, 11], fill=c['inner_ear'])

        # Right ear (outer)
        rx = 19 + right_shift
        draw.ellipse([rx, ear_top, rx + 4, 12], fill=c['body'], outline=c['outline'])
        # Right inner ear
        draw.ellipse([rx + 1, ear_top + 2, rx + 3, 11], fill=c['inner_ear'])

    def _draw_body(self, draw, y_offset=0, squish=False):
        """Draw the main body oval."""
        c = self.pal
        top = 19 + y_offset
        bot = 29 + y_offset
        if squish:
            top += 1
            bot += 1
        # Body outline + fill
        draw.ellipse([9, top, 23, bot], fill=c['body'], outline=c['outline'])
        # Belly highlight
        draw.ellipse([11, top + 2, 21, bot - 1], fill=c['belly'])

    def _draw_head(self, draw, y_offset=0):
        """Draw the head circle, covering ear bases and body top."""
        c = self.pal
        top = 9 + y_offset
        draw.ellipse([7, top, 25, top + 13], fill=c['body'], outline=c['outline'])
        # Shadow on lower head
        draw.ellipse([9, top + 8, 23, top + 12], fill=c['shadow'])
        # Redraw body color over shadow center to make it subtle
        draw.ellipse([10, top + 8, 22, top + 11], fill=c['body'])

    def _draw_eyes_neutral(self, draw, y_offset=0, wide=False):
        """Draw neutral open eyes (white part only; pupils rendered at runtime)."""
        c = self.pal
        ey = 14 + y_offset
        h = 4 if wide else 3
        # Left eye
        draw.rectangle([10, ey, 13, ey + h], fill=c['eye_white'], outline=c['outline'])
        # Right eye
        draw.rectangle([19, ey, 22, ey + h], fill=c['eye_white'], outline=c['outline'])

    def _draw_eyes_happy(self, draw, y_offset=0):
        """Draw happy squinting eyes (^_^) — no pupil area needed."""
        c = self.pal
        ey = 15 + y_offset
        # Left happy eye: small arc shape using pixels
        for i in range(3):
            draw.point((10 + i, ey), fill=c['outline'])
        draw.point((10, ey - 1), fill=c['outline'])
        draw.point((12, ey - 1), fill=c['outline'])

        # Right happy eye
        for i in range(3):
            draw.point((19 + i, ey), fill=c['outline'])
        draw.point((19, ey - 1), fill=c['outline'])
        draw.point((21, ey - 1), fill=c['outline'])

    def _draw_eyes_closed(self, draw, y_offset=0):
        """Draw closed eyes (horizontal lines) for stretch/blink."""
        c = self.pal
        ey = 15 + y_offset
        draw.line([(10, ey), (13, ey)], fill=c['outline'], width=1)
        draw.line([(19, ey), (22, ey)], fill=c['outline'], width=1)

    def _draw_nose(self, draw, y_offset=0):
        """Draw the small nose."""
        c = self.pal
        ny = 19 + y_offset
        draw.point((15, ny), fill=c['nose'])
        draw.point((16, ny), fill=c['nose'])
        # Tiny mouth curve
        draw.point((15, ny + 1), fill=c['outline'])
        draw.point((17, ny + 1), fill=c['outline'])
        draw.point((16, ny + 2), fill=c['outline'])

    def _draw_blush(self, draw, y_offset=0):
        """Draw cute blush marks on cheeks."""
        c = self.pal
        by = 17 + y_offset
        draw.point((8, by), fill=c['blush'])
        draw.point((9, by), fill=c['blush'])
        draw.point((8, by + 1), fill=c['blush'])
        draw.point((23, by), fill=c['blush'])
        draw.point((24, by), fill=c['blush'])
        draw.point((24, by + 1), fill=c['blush'])

    def _draw_feet(self, draw, y_offset=0):
        """Draw feet with paw pads."""
        c = self.pal
        fy = 27 + y_offset
        # Left foot
        draw.ellipse([9, fy, 14, fy + 3], fill=c['body'], outline=c['outline'])
        draw.ellipse([10, fy + 1, 13, fy + 3], fill=c['paw_pad'])
        # Right foot
        draw.ellipse([18, fy, 23, fy + 3], fill=c['body'], outline=c['outline'])
        draw.ellipse([19, fy + 1, 22, fy + 3], fill=c['paw_pad'])

    def _draw_carrot(self, draw, x=14, y=20):
        """Draw a small carrot near the bunny's mouth."""
        c = self.pal
        # Carrot body (orange triangle-ish)
        draw.polygon([(x, y), (x + 4, y + 1), (x + 4, y + 3), (x, y + 2)],
                      fill=c['carrot'], outline=c['outline'])
        # Carrot leaf/top
        draw.point((x - 1, y), fill=c['carrot_tip'])
        draw.point((x - 1, y + 1), fill=c['carrot_tip'])
        draw.point((x - 2, y), fill=c['carrot_tip'])

    def _draw_typing_paws(self, draw, frame=0):
        """Draw forward-extended typing paws."""
        c = self.pal
        left_y = 23 + (frame % 2)
        right_y = 23 + ((frame + 1) % 2)
        # Left paw
        draw.ellipse([8, left_y, 12, left_y + 3], fill=c['body'], outline=c['outline'])
        draw.ellipse([9, left_y + 1, 11, left_y + 3], fill=c['paw_pad'])
        # Right paw
        draw.ellipse([20, right_y, 24, right_y + 3], fill=c['body'], outline=c['outline'])
        draw.ellipse([21, right_y + 1, 23, right_y + 3], fill=c['paw_pad'])

    # ── Full Pose Methods ────────────────────────────────

    def draw_idle(self) -> Image.Image:
        """Standard idle bunny pose."""
        img, draw = self._new_canvas()
        self._draw_ears(draw)
        self._draw_body(draw)
        self._draw_head(draw)
        self._draw_eyes_neutral(draw)
        self._draw_nose(draw)
        self._draw_feet(draw)
        return img

    def draw_nibble(self, frame: int = 0) -> Image.Image:
        """Bunny eating a carrot."""
        img, draw = self._new_canvas()
        self._draw_ears(draw)
        self._draw_body(draw)
        self._draw_head(draw)
        
        if frame == 1:
            # Munching frame: eyes squint, carrot moves, mouth moves
            self._draw_eyes_happy(draw, y_offset=0)
            self._draw_nose(draw, y_offset=1)
            self._draw_carrot(draw, x=6, y=19)
        else:
            self._draw_eyes_neutral(draw)
            self._draw_nose(draw)
            self._draw_carrot(draw, x=5, y=20)
            
        self._draw_feet(draw)
        return img

    def draw_happy(self) -> Image.Image:
        """Being petted — happy expression with blush and relaxed ears."""
        img, draw = self._new_canvas()
        self._draw_ears(draw, left_shift=-1, right_shift=1, relaxed=True)
        self._draw_body(draw, squish=True)
        self._draw_head(draw)
        self._draw_eyes_happy(draw)
        self._draw_nose(draw)
        self._draw_blush(draw)
        self._draw_feet(draw)
        return img

    def draw_stretch(self) -> Image.Image:
        """Stretching/waking up — arms up, eyes closed, body elongated."""
        img, draw = self._new_canvas()
        c = self.pal
        # Stretched ears (higher)
        draw.ellipse([9, 0, 13, 10], fill=c['body'], outline=c['outline'])
        draw.ellipse([10, 1, 12, 9], fill=c['inner_ear'])
        draw.ellipse([19, 0, 23, 10], fill=c['body'], outline=c['outline'])
        draw.ellipse([20, 1, 22, 9], fill=c['inner_ear'])

        # Body (elongated)
        draw.ellipse([9, 17, 23, 30], fill=c['body'], outline=c['outline'])
        draw.ellipse([11, 19, 21, 29], fill=c['belly'])

        # Head (slightly higher)
        draw.ellipse([7, 7, 25, 20], fill=c['body'], outline=c['outline'])

        # Raised paws/arms
        draw.ellipse([6, 8, 10, 13], fill=c['body'], outline=c['outline'])
        draw.ellipse([7, 9, 9, 12], fill=c['paw_pad'])
        draw.ellipse([22, 8, 26, 13], fill=c['body'], outline=c['outline'])
        draw.ellipse([23, 9, 25, 12], fill=c['paw_pad'])

        self._draw_eyes_closed(draw, y_offset=-2)
        self._draw_nose(draw, y_offset=-2)

        # Yawn mouth
        draw.ellipse([14, 19, 18, 21], fill=c['inner_ear'], outline=c['outline'])

        self._draw_feet(draw)
        return img

    def draw_hunt(self) -> Image.Image:
        """Alert/crouching hunt posture — body low, ears forward, wide eyes."""
        img, draw = self._new_canvas()
        c = self.pal

        # Ears tilted forward (inward at top)
        draw.ellipse([10, 0, 14, 11], fill=c['body'], outline=c['outline'])
        draw.ellipse([11, 2, 13, 10], fill=c['inner_ear'])
        draw.ellipse([18, 0, 22, 11], fill=c['body'], outline=c['outline'])
        draw.ellipse([19, 2, 21, 10], fill=c['inner_ear'])

        # Crouched body (lower, wider)
        draw.ellipse([7, 21, 25, 30], fill=c['body'], outline=c['outline'])
        draw.ellipse([9, 23, 23, 29], fill=c['belly'])

        # Head (slightly lower)
        draw.ellipse([7, 10, 25, 23], fill=c['body'], outline=c['outline'])

        # Wide alert eyes
        self._draw_eyes_neutral(draw, y_offset=0, wide=True)
        self._draw_nose(draw)

        # Crouched feet (wider stance)
        draw.ellipse([7, 28, 13, 31], fill=c['body'], outline=c['outline'])
        draw.ellipse([8, 29, 12, 31], fill=c['paw_pad'])
        draw.ellipse([19, 28, 25, 31], fill=c['body'], outline=c['outline'])
        draw.ellipse([20, 29, 24, 31], fill=c['paw_pad'])
        return img

    def draw_typing2(self) -> Image.Image:
        """Typing frame 2 — right paw down, left paw up."""
        img, draw = self._new_canvas()
        self._draw_ears(draw, left_tilt=1)
        self._draw_body(draw, squish=True)
        self._draw_head(draw)
        self._draw_eyes_neutral(draw)
        self._draw_nose(draw)

        c = self.pal
        # Left paw up
        draw.ellipse([6, 12, 10, 17], fill=c['body'], outline=c['outline'])
        draw.ellipse([7, 13, 9, 16], fill=c['paw_pad'])
        # Right paw down on keyboard
        draw.ellipse([21, 16, 25, 21], fill=c['body'], outline=c['outline'])
        draw.ellipse([22, 17, 24, 20], fill=c['paw_pad'])
        return img

    def draw_dizzy(self) -> Image.Image:
        """Dizzy pose: Laying flat with X eyes after being shaken."""
        img, draw = self._new_canvas()
        c = self.pal
        
        # Flattened body
        draw.ellipse([5, 24, 27, 31], fill=c['body'], outline=c['outline'])
        draw.ellipse([7, 26, 25, 30], fill=c['belly'])
        
        # Drooping ears
        draw.ellipse([1, 25, 8, 30], fill=c['body'], outline=c['outline'])
        draw.ellipse([2, 26, 7, 29], fill=c['inner_ear'])
        draw.ellipse([24, 25, 31, 30], fill=c['body'], outline=c['outline'])
        draw.ellipse([25, 26, 30, 29], fill=c['inner_ear'])

        # Head lowered
        hy = 17
        draw.ellipse([8, hy, 24, hy + 11], fill=c['body'], outline=c['outline'])
        # Cheeks
        draw.ellipse([6, hy + 5, 12, hy + 10], fill=c['body'], outline=c['outline'])
        draw.ellipse([20, hy + 5, 26, hy + 10], fill=c['body'], outline=c['outline'])
        
        # X Eyes
        ey = hy + 4
        # Left X
        draw.line([(10, ey), (13, ey + 3)], fill=c['outline'], width=1)
        draw.line([(10, ey + 3), (13, ey)], fill=c['outline'], width=1)
        # Right X
        draw.line([(19, ey), (22, ey + 3)], fill=c['outline'], width=1)
        draw.line([(19, ey + 3), (22, ey)], fill=c['outline'], width=1)

        # Nose
        ny = hy + 8
        draw.point((15, ny), fill=c['nose'])
        draw.point((16, ny), fill=c['nose'])
        draw.line([(14, ny + 1), (17, ny + 1)], fill=c['outline'], width=1)

        # Cute little blush
        self._draw_blush(draw, y_offset=hy - 17 + 2)

        return img

    def draw_walk1(self) -> Image.Image:
        """Walking frame 1 — body slightly bobbed down, left foot up."""
        img, draw = self._new_canvas()
        c = self.pal
        self._draw_ears(draw, y_offset=1)
        self._draw_body(draw, y_offset=1)
        self._draw_head(draw, y_offset=1)
        self._draw_eyes_neutral(draw, y_offset=1)
        self._draw_nose(draw, y_offset=1)
        
        # Left foot up, Right foot down
        fy = 27 + 1
        draw.ellipse([9, fy - 2, 14, fy + 1], fill=c['body'], outline=c['outline']) # Left foot raised
        draw.ellipse([10, fy - 1, 13, fy + 1], fill=c['paw_pad'])
        draw.ellipse([18, fy, 23, fy + 3], fill=c['body'], outline=c['outline']) # Right foot planted
        draw.ellipse([19, fy + 1, 22, fy + 3], fill=c['paw_pad'])
        return img

    def draw_walk2(self) -> Image.Image:
        """Walking frame 2 — body slightly bobbed down, right foot up."""
        img, draw = self._new_canvas()
        c = self.pal
        self._draw_ears(draw, y_offset=1)
        self._draw_body(draw, y_offset=1)
        self._draw_head(draw, y_offset=1)
        self._draw_eyes_neutral(draw, y_offset=1)
        self._draw_nose(draw, y_offset=1)
        
        # Left foot down, Right foot up
        fy = 27 + 1
        draw.ellipse([9, fy, 14, fy + 3], fill=c['body'], outline=c['outline']) # Left foot planted
        draw.ellipse([10, fy + 1, 13, fy + 3], fill=c['paw_pad'])
        draw.ellipse([18, fy - 2, 23, fy + 1], fill=c['body'], outline=c['outline']) # Right foot raised
        draw.ellipse([19, fy - 1, 22, fy + 1], fill=c['paw_pad'])
        return img

    def draw_typing(self, frame: int = 0) -> Image.Image:
        """Typing pose — paws extended, focused expression."""
        img, draw = self._new_canvas()
        self._draw_ears(draw)
        self._draw_body(draw)
        self._draw_head(draw)
        self._draw_eyes_neutral(draw, y_offset=0)
        self._draw_nose(draw)
        self._draw_typing_paws(draw, frame=frame)
        # Don't draw normal feet since typing paws replace them visually
        return img


def generate_carrot() -> Image.Image:
    """Generate a standalone carrot sprite."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pal = PALETTES['white']
    # Big centered carrot
    cx, cy = SIZE // 2, SIZE // 2
    # Carrot body
    draw.polygon([(cx - 3, cy - 4), (cx + 5, cy), (cx + 5, cy + 3), (cx - 3, cy + 1)],
                  fill=pal['carrot'], outline=(80, 50, 20, 255))
    # Carrot stripes
    draw.line([(cx, cy - 2), (cx, cy + 1)], fill=(230, 120, 40, 255))
    draw.line([(cx + 2, cy - 1), (cx + 2, cy + 2)], fill=(230, 120, 40, 255))
    # Leaf top
    draw.polygon([(cx - 4, cy - 5), (cx - 2, cy - 8), (cx - 1, cy - 4)],
                  fill=pal['carrot_tip'])
    draw.polygon([(cx - 5, cy - 4), (cx - 4, cy - 7), (cx - 3, cy - 4)],
                  fill=(80, 150, 50, 255))
    return img


def generate_speech_bubble() -> Image.Image:
    """Generate a small speech bubble sprite for reminders."""
    # Wider bubble for text
    bw, bh = 48, 20
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Bubble body
    draw.rounded_rectangle([1, 1, bw - 2, bh - 6], radius=4,
                           fill=(255, 255, 255, 230), outline=(100, 90, 85, 255))
    # Tail triangle pointing down-left
    draw.polygon([(10, bh - 6), (14, bh - 6), (8, bh - 1)],
                  fill=(255, 255, 255, 230))
    draw.line([(10, bh - 6), (8, bh - 1)], fill=(100, 90, 85, 255))
    draw.line([(8, bh - 1), (14, bh - 6)], fill=(100, 90, 85, 255))
    # Small heart inside bubble
    draw.point((20, 6), fill=(255, 120, 120, 255))
    draw.point((21, 6), fill=(255, 120, 120, 255))
    draw.point((23, 6), fill=(255, 120, 120, 255))
    draw.point((24, 6), fill=(255, 120, 120, 255))
    draw.point((19, 7), fill=(255, 120, 120, 255))
    draw.point((22, 7), fill=(255, 120, 120, 255))
    draw.point((25, 7), fill=(255, 120, 120, 255))
    draw.point((20, 8), fill=(255, 120, 120, 255))
    draw.point((21, 8), fill=(255, 120, 120, 255))
    draw.point((23, 8), fill=(255, 120, 120, 255))
    draw.point((24, 8), fill=(255, 120, 120, 255))
    draw.point((21, 9), fill=(255, 120, 120, 255))
    draw.point((23, 9), fill=(255, 120, 120, 255))
    draw.point((22, 10), fill=(255, 120, 120, 255))
    # Exclamation mark
    for y in range(5, 9):
        draw.point((30, y), fill=(255, 160, 80, 255))
    draw.point((30, 10), fill=(255, 160, 80, 255))
    return img


def generate_heart() -> Image.Image:
    """Generate a standalone heart sprite."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Heart centered around 16, 16
    draw.point((14, 14), fill=(255, 120, 120, 255))
    draw.point((15, 14), fill=(255, 120, 120, 255))
    draw.point((17, 14), fill=(255, 120, 120, 255))
    draw.point((18, 14), fill=(255, 120, 120, 255))
    draw.point((13, 15), fill=(255, 120, 120, 255))
    draw.point((16, 15), fill=(255, 120, 120, 255))
    draw.point((19, 15), fill=(255, 120, 120, 255))
    draw.point((14, 16), fill=(255, 120, 120, 255))
    draw.point((15, 16), fill=(255, 120, 120, 255))
    draw.point((17, 16), fill=(255, 120, 120, 255))
    draw.point((18, 16), fill=(255, 120, 120, 255))
    draw.point((15, 17), fill=(255, 120, 120, 255))
    draw.point((17, 17), fill=(255, 120, 120, 255))
    draw.point((16, 18), fill=(255, 120, 120, 255))
    return img


def generate_all_assets():
    """Generate all sprite assets into the assets directory."""
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print("[Bunny] Generating Pixelbnnuy sprites...")

    # Generate bunny poses for each palette
    for palette_name in PALETTE_NAMES:
        artist = BunnyArtist(palette_name)
        prefix = palette_name

        poses = {
            'idle':    artist.draw_idle(),
            'nibble':  artist.draw_nibble(frame=0),
            'nibble2': artist.draw_nibble(frame=1),
            'happy':   artist.draw_happy(),
            'stretch': artist.draw_stretch(),
            'hunt':    artist.draw_hunt(),
            'typing':  artist.draw_typing(frame=0),
            'typing2': artist.draw_typing(frame=1),
            'walk1':   artist.draw_walk1(),
            'walk2':   artist.draw_walk2(),
            'dizzy':   artist.draw_dizzy()
        }

        for pose_name, img in poses.items():
            filename = f"{prefix}_{pose_name}.png"
            filepath = os.path.join(ASSETS_DIR, filename)
            img.save(filepath)
            print(f"  [OK] {filename}")

            # Also save the white idle pose as the main icon
            if palette_name == 'white' and pose_name == 'idle':
                # .ico needs multiple sizes for best scaling in windows
                icon_path = os.path.join(ASSETS_DIR, "icon.ico")
                img.save(icon_path, format="ICO", sizes=[(128, 128), (64, 64), (32, 32)])
                print("  [OK] icon.ico")

    # Universal assets
    carrot = generate_carrot()
    carrot.save(os.path.join(ASSETS_DIR, "carrot.png"))
    print("  [OK] carrot.png")

    bubble = generate_speech_bubble()
    bubble.save(os.path.join(ASSETS_DIR, "speech_bubble.png"))
    print("  [OK] speech_bubble.png")

    heart = generate_heart()
    heart.save(os.path.join(ASSETS_DIR, "heart.png"))
    print("  [OK] heart.png")

    print(f"\n[Done] All assets generated in {ASSETS_DIR}")
    return ASSETS_DIR


if __name__ == "__main__":
    generate_all_assets()
