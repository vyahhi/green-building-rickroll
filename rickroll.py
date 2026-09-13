#!/usr/bin/env python3
"""Play a tiny, procedural Rickroll on the MIT Green Building simulator."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterator


WIDTH = 9
HEIGHT = 17
DEFAULT_ENDPOINT = "https://sundai.willsarg.com/api/i/quiet-fox/frame"

RGB = tuple[int, int, int]
Frame = list[list[list[int]]]

BLACK: RGB = (3, 3, 8)
HAIR: RGB = (205, 75, 30)
HAIR_LIGHT: RGB = (255, 132, 51)
SKIN: RGB = (255, 174, 122)
SKIN_SHADOW: RGB = (190, 93, 68)
SHIRT: RGB = (18, 24, 35)
COAT: RGB = (224, 191, 145)
COAT_LIGHT: RGB = (255, 225, 174)
TROUSERS: RGB = (30, 38, 60)
SHOE: RGB = (5, 5, 10)
MIC: RGB = (215, 223, 235)


def blank(color: RGB = BLACK) -> Frame:
    return [[list(color) for _ in range(WIDTH)] for _ in range(HEIGHT)]


def pixel(frame: Frame, x: int, y: int, color: RGB) -> None:
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        frame[y][x] = list(color)


def line(frame: Frame, x0: int, y0: int, x1: int, y1: int, color: RGB) -> None:
    """Draw a clipped Bresenham line."""
    dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
    dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
    error = dx + dy
    while True:
        pixel(frame, x0, y0, color)
        if x0 == x1 and y0 == y1:
            return
        twice = 2 * error
        if twice >= dy:
            error += dy
            x0 += sx
        if twice <= dx:
            error += dx
            y0 += sy


def stage(frame_number: int) -> Frame:
    frame = blank()
    pulse = (math.sin(frame_number * 0.45) + 1.0) / 2.0
    blue = int(20 + 42 * pulse)

    # Blue video-set backdrop, a warm window, and alternating spotlights.
    for y in range(HEIGHT - 2):
        for x in range(WIDTH):
            frame[y][x] = [7 + x * 2, 14 + y, blue + y * 2]
    for y in range(2, 7):
        for x in range(1, 4):
            pixel(frame, x, y, (115 + y * 8, 72 + y * 5, 40))
    beam_x = 1 + (frame_number // 2) % 7
    for y in range(HEIGHT - 2):
        pixel(frame, max(0, min(WIDTH - 1, beam_x + (y - 7) // 5)), y, (28, 45, 88))
    for x in range(WIDTH):
        pixel(frame, x, HEIGHT - 2, (46, 35, 48))
        pixel(frame, x, HEIGHT - 1, (18, 15, 25))
    return frame


def draw_rick(frame: Frame, phase: int) -> None:
    sway = (-1, 0, 1, 0)[phase]
    cx = 4 + sway
    bob = 1 if phase == 2 else 0

    # Hair and face: the orange quiff is the key silhouette at this scale.
    pixel(frame, cx - 1, 1 + bob, HAIR_LIGHT)
    pixel(frame, cx, 1 + bob, HAIR)
    pixel(frame, cx + 1, 2 + bob, HAIR)
    for x in range(cx - 1, cx + 2):
        pixel(frame, x, 2 + bob, HAIR)
        pixel(frame, x, 3 + bob, SKIN)
        pixel(frame, x, 4 + bob, SKIN_SHADOW)
    pixel(frame, cx, 3 + bob, (255, 218, 174))
    pixel(frame, cx - 1, 3 + bob, (35, 25, 28))

    # Black turtleneck, tan coat, and highlights.
    pixel(frame, cx, 5 + bob, SHIRT)
    for y in range(6 + bob, 11 + bob):
        for x in range(cx - 1, cx + 2):
            pixel(frame, x, y, COAT)
    line(frame, cx, 6 + bob, cx, 10 + bob, COAT_LIGHT)
    pixel(frame, cx, 7 + bob, SHIRT)
    pixel(frame, cx, 8 + bob, SHIRT)

    # Four poses create Rick's familiar side-to-side dance.
    if phase == 0:
        line(frame, cx - 1, 6 + bob, cx - 3, 9 + bob, COAT)
        line(frame, cx + 1, 6 + bob, cx + 2, 8 + bob, COAT)
        pixel(frame, cx - 3, 10 + bob, SKIN)
        pixel(frame, cx + 2, 9 + bob, SKIN)
    elif phase == 1:
        line(frame, cx - 1, 6 + bob, cx - 3, 6 + bob, COAT)
        line(frame, cx + 1, 6 + bob, cx + 2, 9 + bob, COAT)
        pixel(frame, cx - 3, 6 + bob, SKIN)
        pixel(frame, cx + 2, 10 + bob, SKIN)
    elif phase == 2:
        line(frame, cx - 1, 6 + bob, cx - 2, 9 + bob, COAT)
        line(frame, cx + 1, 6 + bob, cx + 3, 7 + bob, COAT)
        pixel(frame, cx - 2, 10 + bob, SKIN)
        pixel(frame, cx + 3, 7 + bob, SKIN)
    else:
        line(frame, cx - 1, 6 + bob, cx - 3, 8 + bob, COAT)
        line(frame, cx + 1, 6 + bob, cx + 3, 10 + bob, COAT)
        pixel(frame, cx - 3, 9 + bob, SKIN)
        pixel(frame, cx + 3, 11 + bob, SKIN)

    hip_y = 11 + bob
    pixel(frame, cx - 1, hip_y, TROUSERS)
    pixel(frame, cx, hip_y, TROUSERS)
    pixel(frame, cx + 1, hip_y, TROUSERS)
    if phase in (0, 3):
        line(frame, cx - 1, hip_y, cx - 2, 15, TROUSERS)
        line(frame, cx + 1, hip_y, cx + 2, 15, TROUSERS)
        pixel(frame, cx - 3, 16, SHOE)
        pixel(frame, cx - 2, 16, SHOE)
        pixel(frame, cx + 2, 16, SHOE)
    else:
        line(frame, cx - 1, hip_y, cx, 15, TROUSERS)
        line(frame, cx + 1, hip_y, cx + 3, 14, TROUSERS)
        pixel(frame, cx, 16, SHOE)
        pixel(frame, cx + 3, 15, SHOE)
        pixel(frame, cx + 4, 15, SHOE)


def draw_microphone(frame: Frame, phase: int) -> None:
    x = 7 if phase in (0, 1) else 6
    pixel(frame, x, 5, MIC)
    pixel(frame, x + 1, 5, (85, 92, 110))
    line(frame, x, 6, x, 14, (70, 75, 90))
    line(frame, x - 1, 15, x + 1, 15, (70, 75, 90))


def frames(fps: float) -> Iterator[Frame]:
    frame_number = 0
    while True:
        result = stage(frame_number)
        phase = (frame_number // max(1, round(fps * 0.28))) % 4
        draw_microphone(result, phase)
        draw_rick(result, phase)
        yield result
        frame_number += 1


def validate(frame: Frame) -> None:
    if len(frame) != HEIGHT or any(len(row) != WIDTH for row in frame):
        raise ValueError(f"frame must be {HEIGHT} rows by {WIDTH} columns")
    for row in frame:
        for color in row:
            if len(color) != 3 or any(type(value) is not int or not 0 <= value <= 255 for value in color):
                raise ValueError("every pixel must be an [r, g, b] triplet from 0 to 255")


@dataclass
class WebDisplay:
    endpoint: str
    timeout: float = 5.0

    def send(self, frame: Frame) -> None:
        validate(frame)
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(frame, separators=(",", ":")).encode("utf-8"),
            # Cloudflare rejects urllib's default Python-urllib user agent even
            # though the endpoint is public; identify this small client plainly.
            headers={
                "Content-Type": "application/json",
                "User-Agent": "green-building-rickroll/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            response.read()


def preview(frame: Frame) -> str:
    reset = "\x1b[0m"
    return "\n".join(
        "".join(f"\x1b[48;2;{r};{g};{b}m  " for r, g, b in row) + reset
        for row in frame
    )


def play(endpoint: str, fps: float, seconds: float, dry_run: bool) -> int:
    display = WebDisplay(endpoint)
    total = max(1, round(seconds * fps))
    deadline = time.monotonic()
    for index, frame in zip(range(total), frames(fps)):
        if dry_run:
            sys.stdout.write("\x1b[H\x1b[2J" + preview(frame) + "\n")
            sys.stdout.flush()
        else:
            try:
                display.send(frame)
            except (urllib.error.URLError, TimeoutError) as error:
                print(f"Could not send frame {index + 1}: {error}", file=sys.stderr)
                return 1
        deadline += 1.0 / fps
        time.sleep(max(0.0, deadline - time.monotonic()))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="frame POST endpoint")
    parser.add_argument("--fps", type=float, default=6.0, help="frames per second (default: 6)")
    parser.add_argument("--seconds", type=float, default=30.0, help="duration (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="preview in the terminal without POSTing")
    args = parser.parse_args()
    if not 1 <= args.fps <= 30:
        parser.error("--fps must be between 1 and 30")
    if args.seconds <= 0:
        parser.error("--seconds must be greater than zero")
    return args


if __name__ == "__main__":
    options = parse_args()
    raise SystemExit(play(options.endpoint, options.fps, options.seconds, options.dry_run))
