import badger2040
from badger2040 import WIDTH
import random
import os

# -----------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------
FORTUNE_DIR = "/fortunes"
MARGIN = 5
HEADER_H = 16
TEXT_TOP = HEADER_H + MARGIN


# -----------------------------------------------------------------------
# Discover fortune files
# Skips anything that looks like an OS/editor artefact (.dat, .DS_Store…)
# -----------------------------------------------------------------------
def find_fortune_files(directory):
    try:
        entries = os.listdir(directory)
    except OSError:
        return []
    return sorted(
        e for e in entries
        if not e.startswith(".") and not e.endswith(".dat")
    )


# -----------------------------------------------------------------------
# Fortune parser — reservoir sampling, single pass, O(1) RAM
# -----------------------------------------------------------------------
def get_fortune(path):
    chosen = None
    current = []
    count = 0

    try:
        with open(path) as f:
            for line in f:
                if line.strip() == "%":
                    if current:
                        count += 1
                        if random.randint(1, count) == 1:
                            chosen = list(current)
                        current = []
                else:
                    current.append(line.rstrip())

        # Handle final fortune with no trailing %
        if current:
            count += 1
            if random.randint(1, count) == 1:
                chosen = current

    except OSError:
        return f"Could not open:\n{path}"

    if chosen is None:
        return "Fortune file is empty."

    # Strip surrounding blank lines
    while chosen and not chosen[0].strip():
        chosen.pop(0)
    while chosen and not chosen[-1].strip():
        chosen.pop()

    return "\n".join(chosen)


# -----------------------------------------------------------------------
# Display
# -----------------------------------------------------------------------
def draw_fortune(text, filename, file_index, file_count):
    display.set_pen(15)
    display.clear()

    # Header bar
    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, HEADER_H)
    display.set_pen(15)
    display.set_font("bitmap8")

    # Show current filename, truncated if needed
    display.text(filename, MARGIN, 4, WIDTH // 2, 1)

    # Right side: file position and button hints
    hint = f"\u2191\u2193:file  A/C:new  {file_index + 1}/{file_count}"
    display.text(hint, WIDTH - display.measure_text(hint, 1) - MARGIN, 4, WIDTH, 1)

    # Fortune text — scale=2 suits short cookies; use scale=1 for longer files
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text(text, MARGIN, TEXT_TOP, WIDTH - (MARGIN * 2), 2)

    display.update()


def draw_no_files():
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, HEADER_H)
    display.set_pen(15)
    display.set_font("bitmap8")
    display.text("* fortune *", MARGIN, 4, WIDTH, 1)
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text(
        f"No fortune files found in {FORTUNE_DIR}\n\n"
        "Copy plain-text fortune files there\n"
        "(without the .dat extension).",
        MARGIN, TEXT_TOP, WIDTH - (MARGIN * 2), 1
    )
    display.update()


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------
display = badger2040.Badger2040()
display.led(128)

files = find_fortune_files(FORTUNE_DIR)

if not files:
    draw_no_files()
    while True:
        display.keepalive()
        display.halt()

file_index = 0


def current_path():
    return FORTUNE_DIR + "/" + files[file_index]


draw_fortune(get_fortune(current_path()), files[file_index], file_index, len(files))

# On battery, halt() cuts power until a button wakes the device.
# On USB, the launcher catches A+C to exit the app.
while True:
    display.keepalive()

    if display.pressed(badger2040.BUTTON_A) or display.pressed(badger2040.BUTTON_C):
        draw_fortune(get_fortune(current_path()), files[file_index], file_index, len(files))

    elif display.pressed(badger2040.BUTTON_UP):
        file_index = (file_index - 1) % len(files)
        draw_fortune(get_fortune(current_path()), files[file_index], file_index, len(files))

    elif display.pressed(badger2040.BUTTON_DOWN):
        file_index = (file_index + 1) % len(files)
        draw_fortune(get_fortune(current_path()), files[file_index], file_index, len(files))

    display.halt()
