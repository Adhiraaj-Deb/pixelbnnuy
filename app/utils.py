"""
Utility functions for Pixelbnnuy.
Math helpers, interpolation, clamping, and coordinate utilities.
"""

import math
import random


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to [min_val, max_val] range."""
    return max(min_val, min(max_val, value))


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def normalize(x: float, y: float) -> tuple[float, float]:
    """Normalize a 2D vector. Returns (0, 0) for zero-length vectors."""
    length = math.sqrt(x * x + y * y)
    if length < 0.0001:
        return (0.0, 0.0)
    return (x / length, y / length)


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out for spring-like recovery animations."""
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    p = 0.4
    return math.pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1.0


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out for smooth deceleration."""
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out_sine(t: float) -> float:
    """Sine ease-in-out for gentle oscillation."""
    return -(math.cos(math.pi * t) - 1.0) / 2.0


def random_range(min_val: float, max_val: float) -> float:
    """Random float in [min_val, max_val]."""
    return random.uniform(min_val, max_val)


def direction_to(from_x: float, from_y: float, to_x: float, to_y: float) -> tuple[float, float]:
    """Unit direction vector from one point to another."""
    dx = to_x - from_x
    dy = to_y - from_y
    return normalize(dx, dy)


def smooth_damp(current: float, target: float, velocity: float,
                smooth_time: float, dt: float) -> tuple[float, float]:
    """Critically-damped spring smoothing (like Unity's SmoothDamp).

    Returns:
        (new_current, new_velocity)
    """
    smooth_time = max(0.0001, smooth_time)
    omega = 2.0 / smooth_time
    x = omega * dt
    exp_factor = 1.0 / (1.0 + x + 0.48 * x * x + 0.235 * x * x * x)
    delta = current - target
    temp = (velocity + omega * delta) * dt
    new_velocity = (velocity - omega * temp) * exp_factor
    new_current = target + (delta + temp) * exp_factor
    return new_current, new_velocity
