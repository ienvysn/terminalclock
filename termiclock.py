
import curses
import time
import datetime
import argparse
import sys

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

DIGIT_W = 10   #
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


def safe_addstr(win, row, col, text):
    try:
        win.addstr(row, col, text)
    except curses.error:
        pass


def draw_bar(win, row, col, label, width=32):
    safe_addstr(win, row, col,
                f"─── {label} " + "─" * max(0, width - len(label) - 5))

# ---------------------------------------------------------------------------
# Clock mode
# ---------------------------------------------------------------------------

MODES = ['clock', 'stopwatch', 'timer']


def draw_clock(stdscr, mid_row):
    H, W = stdscr.getmaxyx()
    now      = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%a  %d %b %Y").upper()

    col = center_col(stdscr, time_str)
    top = mid_row - DIGIT_H // 2 - 2

    date_col = max(0, (W - len(date_str)) // 2)
    if top - 2 >= 0:
        safe_addstr(stdscr, top - 2, date_col, date_str)

    if top >= 0 and col >= 0:
        draw_string(stdscr, top, col, time_str)

    hint = "tab: stopwatch   q: quit"
    hcol = max(0, (W - len(hint)) // 2)
    if top + DIGIT_H + 2 < H:
        safe_addstr(stdscr, top + DIGIT_H + 2, hcol, hint)


def handle_timer_key(key, tm):
    if key == ord(' '):
        if tm['done']:
            tm.update(remaining=tm['total'], running=True,
                      start=time.perf_counter(), done=False)
        elif tm['running']:
            elapsed        = int((time.perf_counter() - tm['start']) * 1000)
            tm['remaining'] = max(0, tm['remaining'] - elapsed)
            tm['running']   = False
        elif tm['remaining'] > 0:
            tm['start']   = time.perf_counter()
            tm['running'] = True
    elif key in (ord('r'), ord('R')):
        tm.update(remaining=tm['total'], running=False, done=False)



def main(stdscr, initial_mode='clock', timer_total_ms=0):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(16)   # ~60 fps

    mode = initial_mode

    sw = dict(running=False, start=0, elapsed=0, laps=[], last_lap=0)
    tm = dict(total=timer_total_ms, remaining=timer_total_ms,
              running=False, start=0, done=False)

    while True:
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('\t'), ord('m')):
            idx  = MODES.index(mode) if mode in MODES else 0
            mode = MODES[(idx + 1) % len(MODES)]
            tm['done'] = False
        elif mode == 'stopwatch':
            handle_stopwatch_key(key, sw)
        elif mode == 'timer':
            handle_timer_key(key, tm)

        H, W   = stdscr.getmaxyx()
        mid    = H // 2
        stdscr.erase()

        if mode == 'clock':
            draw_clock(stdscr, mid)
        elif mode == 'stopwatch':
            draw_stopwatch(stdscr, mid, sw)
        elif mode == 'timer':
            draw_timer(stdscr, mid, tm)

        stdscr.refresh()

    curses.endwin()



def parse_duration(s):
    """Accept: 5m  90s  1h30m  1:30  1:30:00  120 → seconds (int)."""
    import re
    s = s.strip().lower()
    if ':' in s:
        parts = s.split(':')
        try:
            parts = [int(p) for p in parts]
            if len(parts) == 2: return parts[0] * 60 + parts[1]
            if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        except ValueError:
            return None
    total, found = 0, False
    for val, unit in re.findall(r'(\d+)\s*([hms])', s):
        found = True
        val   = int(val)
        if unit == 'h':   total += val * 3600
        elif unit == 'm': total += val * 60
        elif unit == 's': total += val
    if found:
        return total
    try:
        return int(s)
    except ValueError:
        return None

