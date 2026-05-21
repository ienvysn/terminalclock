#!/usr/bin/env python3
import curses

B = "▓▓"
_ = "  "
DIGITS = {
    '0': [_+B+B+B+_, B+_+_+_+B, B+_+_+_+B, B+_+_+_+B, B+_+_+_+B, B+_+_+_+B, _+B+B+B+_],
    '1': [_+_+B+_+_, _+B+B+_+_, _+_+B+_+_, _+_+B+_+_, _+_+B+_+_, _+_+B+_+_, _+B+B+B+_],
    '2': [_+B+B+B+_, B+_+_+_+B, _+_+_+_+B, _+_+_+B+_, _+_+B+_+_, _+B+_+_+_, B+B+B+B+B],
    '3': [_+B+B+B+_, B+_+_+_+B, _+_+_+_+B, _+_+B+B+_, _+_+_+_+B, B+_+_+_+B, _+B+B+B+_],
    '4': [_+_+_+B+_, _+_+B+B+_, _+B+_+B+_, B+_+_+B+_, B+B+B+B+B, _+_+_+B+_, _+_+_+B+_],
    '5': [B+B+B+B+B, B+_+_+_+_, B+B+B+B+_, _+_+_+_+B, _+_+_+_+B, B+_+_+_+B, _+B+B+B+_],
    '6': [_+B+B+B+_, B+_+_+_+_, B+_+_+_+_, B+B+B+B+_, B+_+_+_+B, B+_+_+_+B, _+B+B+B+_],
    '7': [B+B+B+B+B, _+_+_+_+B, _+_+_+B+_, _+_+_+B+_, _+_+B+_+_, _+_+B+_+_, _+_+B+_+_],
    '8': [_+B+B+B+_, B+_+_+_+B, B+_+_+_+B, _+B+B+B+_, B+_+_+_+B, B+_+_+_+B, _+B+B+B+_],
    '9': [_+B+B+B+_, B+_+_+_+B, B+_+_+_+B, _+B+B+B+B, _+_+_+_+B, _+_+_+_+B, _+B+B+B+_],
    ':': [_+_+_+_+_, _+_+B+_+_, _+_+B+_+_, _+_+_+_+_, _+_+B+_+_, _+_+B+_+_, _+_+_+_+_],
    '.': [_+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+B+_+_, _+_+B+_+_],
    ' ': [_+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+_+_+_, _+_+_+_+_],
}

DIGIT_W = 10
DIGIT_H = 7
GAP     = 2


def draw_string(win, row, col, text):
    for r in range(DIGIT_H):
        x = col
        for ch in text:
            glyph = DIGITS.get(ch, DIGITS[' '])
            win.addstr(row + r, x, glyph[r])
            x += DIGIT_W + GAP


def string_width(text):
    return len(text) * (DIGIT_W + GAP) - GAP


def center_col(win, text):
    _, W = win.getmaxyx()
    return max(0, (W - string_width(text)) // 2)


def fmt_ms(ms):
    """HH:MM:SS.cs"""
    cs = (ms // 10) % 100
    s  = (ms // 1000) % 60
    m  = (ms // 60000) % 60
    h  = ms // 3600000
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"
    return f"{m:02d}:{s:02d}.{cs:02d}"


def fmt_countdown(ms):
    """HH:MM:SS or MM:SS"""
    s = (ms + 999) // 1000
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def draw_bar(win, row, col, label, width=32):
    try:
        win.addstr(row, col, f"─── {label} " + "─" * max(0, width - len(label) - 5))
    except curses.error:
        pass

