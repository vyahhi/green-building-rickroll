#!/usr/bin/env python3
"""Play a tiny, procedural Rickroll on the MIT Green Building simulator."""

from __future__ import annotations

import argparse
import itertools
import json
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

BLACK: RGB = (1, 1, 3)
HAIR: RGB = (125, 43, 12)
HAIR_LIGHT: RGB = (155, 72, 18)
SKIN: RGB = (145, 78, 48)
SKIN_SHADOW: RGB = (90, 38, 26)
SHIRT: RGB = (4, 6, 10)
COAT: RGB = (118, 90, 56)
COAT_LIGHT: RGB = (145, 112, 68)
MIC: RGB = (105, 112, 125)


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


FONT = {
    "A": ("010", "101", "111", "101", "101"),
    "E": ("111", "100", "110", "100", "111"),
    "G": ("111", "100", "101", "101", "111"),
    "I": ("111", "010", "010", "010", "111"),
    # N is deliberately four columns wide so its diagonal remains legible.
    "N": ("1001", "1101", "1101", "1011", "1001"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("110", "101", "110", "100", "100"),
    "R": ("110", "101", "110", "101", "101"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "Y": ("101", "101", "010", "010", "010"),
}

WORD_CARDS = (
    ("NEVER", (22, 2, 6)),
    ("GONNA", (2, 8, 24)),
    ("GIVE", (17, 2, 22)),
    ("YOU", (2, 20, 16)),
    ("UP", (24, 8, 2)),
)


def solid(color: RGB) -> Frame:
    return blank(color)


def draw_text_line(frame: Frame, text: str, y: int) -> None:
    glyph_widths = [len(FONT[letter][0]) for letter in text]
    spacing = 1
    width = sum(glyph_widths) + max(0, len(text) - 1) * spacing
    if width > WIDTH:
        spacing = 0
        width = sum(glyph_widths)
    if width > WIDTH:
        raise ValueError(f"text line {text!r} is wider than the display")
    x = (WIDTH - width) // 2
    # Bright enough to read, but below the simulator's heavy bloom threshold.
    colors = ((135, 135, 135), (140, 108, 20), (38, 108, 132))
    for letter_index, letter in enumerate(text):
        color = colors[letter_index % len(colors)]
        for row, pattern in enumerate(FONT[letter]):
            for column, value in enumerate(pattern):
                if value == "1":
                    pixel(frame, x + column, y + row, color)
        x += glyph_widths[letter_index] + spacing


def word_card(word: str, background: RGB) -> Frame:
    frame = solid(background)
    lines = {
        "NEVER": ("NE", "VER"),
        "GONNA": ("GO", "NN", "A"),
        "GIVE": ("GI", "VE"),
        "YOU": ("YOU",),
        "UP": ("UP",),
    }[word]
    positions = {1: (6,), 2: (2, 10), 3: (0, 6, 12)}[len(lines)]
    for text, y in zip(lines, positions):
        draw_text_line(frame, text, y)
    return frame


def stage(frame_number: int) -> Frame:
    # A nearly solid background survives the building renderer much better than
    # subtle gradients. The side bars provide visible motion without visual noise.
    frame = solid((2, 10, 20))
    accent = (6, 42, 65) if frame_number % 2 else (7, 28, 46)
    for y in range(HEIGHT):
        pixel(frame, 0, y, accent)
        pixel(frame, 8, y, accent)
    return frame


def draw_rick(frame: Frame, phase: int) -> None:
    # Oversized head: orange quiff, face, eyes, nose, and smile.
    for x in range(3, 6):
        pixel(frame, x, 0, HAIR_LIGHT)
    for x in range(2, 7):
        pixel(frame, x, 1, HAIR)
        pixel(frame, x, 2, HAIR if x in (2, 3, 6) else SKIN)
    for y in range(3, 8):
        for x in range(2, 7):
            pixel(frame, x, y, SKIN)
    pixel(frame, 2, 3, HAIR)
    pixel(frame, 3, 4, (20, 18, 25))
    pixel(frame, 5, 4, (20, 18, 25))
    pixel(frame, 4, 5, SKIN_SHADOW)
    pixel(frame, 3, 6, SKIN_SHADOW)
    pixel(frame, 4, 7, (145, 137, 120))
    pixel(frame, 5, 6, SKIN_SHADOW)
    for x in range(3, 6):
        pixel(frame, x, 8, SKIN)

    # Broad tan jacket and black shirt fill the lower half of the facade.
    for y in range(9, HEIGHT):
        for x in range(2, 7):
            pixel(frame, x, y, COAT)
    for y, half_width in ((9, 2), (10, 1), (11, 1), (12, 0), (13, 0)):
        for x in range(4 - half_width, 5 + half_width):
            pixel(frame, x, y, SHIRT)
    line(frame, 3, 9, 3, 16, COAT_LIGHT)

    # Exaggerated arms are readable at a distance and create the dance motion.
    if phase in (0, 2):
        line(frame, 2, 10, 0, 7 if phase == 0 else 13, COAT_LIGHT)
        line(frame, 6, 10, 7, 13 if phase == 0 else 8, COAT)
    else:
        line(frame, 2, 10, 1, 13 if phase == 1 else 8, COAT)
        line(frame, 6, 10, 8, 7 if phase == 1 else 13, COAT_LIGHT)


def draw_microphone(frame: Frame, phase: int) -> None:
    x = 7
    pixel(frame, x, 4, MIC)
    pixel(frame, x + 1, 4, MIC)
    pixel(frame, x, 5, MIC)
    line(frame, x, 6, x, 15, (85, 92, 110))
    line(frame, x - 1, 16, x + 1, 16, (85, 92, 110))


def frames(fps: float) -> Iterator[Frame]:
    frame_number = 0
    while True:
        dance_frames = max(4, round(fps * 2.0))
        card_frames = max(2, round(fps * 1.0))
        cycle_frames = dance_frames + card_frames * len(WORD_CARDS)
        cycle_position = frame_number % cycle_frames
        if cycle_position < dance_frames:
            result = stage(frame_number)
            phase = (frame_number // max(1, round(fps * 0.28))) % 4
            draw_microphone(result, phase)
            draw_rick(result, phase)
        else:
            card_index = (cycle_position - dance_frames) // card_frames
            word, background = WORD_CARDS[card_index]
            result = word_card(word, background)
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


def play(endpoint: str, fps: float, seconds: float, dry_run: bool, loop: bool = False) -> int:
    display = WebDisplay(endpoint)
    total = max(1, round(seconds * fps))
    frame_numbers = itertools.count() if loop else range(total)
    deadline = time.monotonic()
    for index, frame in zip(frame_numbers, frames(fps)):
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
    parser.add_argument("--loop", action="store_true", help="play continuously until interrupted")
    parser.add_argument("--dry-run", action="store_true", help="preview in the terminal without POSTing")
    args = parser.parse_args()
    if not 1 <= args.fps <= 30:
        parser.error("--fps must be between 1 and 30")
    if args.seconds <= 0:
        parser.error("--seconds must be greater than zero")
    return args


if __name__ == "__main__":
    options = parse_args()
    try:
        exit_code = play(options.endpoint, options.fps, options.seconds, options.dry_run, options.loop)
    except KeyboardInterrupt:
        exit_code = 0
    raise SystemExit(exit_code)
