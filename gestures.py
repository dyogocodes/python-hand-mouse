"""Dependency-free gesture state and coordinate mapping."""
from dataclasses import dataclass
from math import hypot


def map_point(x, y, width, height, margin=0.15):
    """Map the central camera region to the primary display, avoiding corners."""
    def axis(value, size):
        unit = max(0.0, min(1.0, (value - margin) / (1 - 2 * margin)))
        return round(1 + unit * (size - 3))
    return axis(x, width), axis(y, height)


def pinch_ratio(points, width, height):
    """Thumb-index distance relative to palm width, in aspect-correct pixels."""
    def distance(a, b):
        return hypot((points[a].x - points[b].x) * width,
                     (points[a].y - points[b].y) * height)
    return distance(4, 8) / max(distance(5, 17), 1e-6)


@dataclass
class PinchClick:
    close: float = 0.30
    release: float = 0.50
    dwell: float = 0.08
    cooldown: float = 0.35
    armed: bool = False
    since: float | None = None
    last_click: float = float('-inf')

    def reset(self):
        # Require an open hand after startup, pause or tracking loss.
        self.armed = False
        self.since = None

    def update(self, ratio, now):
        if ratio >= self.release:
            self.armed = True
            self.since = None
        elif self.armed and ratio <= self.close:
            if self.since is None:
                self.since = now
            if now - self.since >= self.dwell and now - self.last_click >= self.cooldown:
                self.last_click = now
                self.armed = False
                self.since = None
                return True
        else:
            self.since = None
        return False
