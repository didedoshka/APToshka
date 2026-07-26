#!/usr/bin/env python3
"""Draw aptoshka.svg.

The K table below mirrors proXiao.keymap (white/blue/red layers) and Yasherty:
after changing the keymap, update K and rerun `python3 draw-layout.py`.
"""
import math
import os

# --- legends, keymap order: rows top to bottom, 5 left + 5 right, then thumbs ---
# (key, russian, red layer, blue layer, russian via blue layer) ; None = empty
K = [
    # row 1
    ('W', 'Ш', None, '!', None), ('G', 'Г', '#', ':', None), ('D', 'Д', '@', '"', None),
    ('F', 'Ф', '+', '-', None), ('B', 'Б', None, None, None),
    ('Q', 'Я', None, '`', 'Щ'), ('L', 'Л', '1', '→', None), ('U', 'У', '2', '\\', 'Ю'),
    ('O', 'О', '3', '/', None), ('Y', 'Ы', None, '|', None),
    # row 2
    ('R', 'Р', '●', '?', None), ('S', 'С', '^', '.', None), ('T', 'Т', '%', ',', None),
    ('H', 'Х', '$', '←', None), ('K', 'К', '=', '↑', None),
    ('J', 'Й', '0', '↓', None), ('N', 'Н', '4', '[', 'Ж'), ('E', 'Е', '5', '<', 'Ь'),
    ('A', 'А', '6', '(', None), ('I', 'И', None, '{', None),
    # row 3
    ('X', 'Ч', None, None, None), ('C', 'Ц', None, ';', None), ('M', 'М', '*', "'", None),
    ('P', 'П', '&', '_', None), ('V', 'В', None, None, None),
    ('Z', 'З', None, '~', None), ('⌘', None, '7', ']', 'Э'), ('⇧', None, '8', '>', 'Ъ'),
    ('⎋', None, '9', ')', None), ('Tab', None, None, '}', None),
    # thumbs
    ('⌃', None, None, '⌥⇧', None), ('␣', None, None, None, None), ('●R', None, None, '⌥', None),
    ('●B', None, None, None, None), ('⌫', None, None, None, None), ('↩', None, None, None, None),
]

# --- geometry: (x, y, rotation) in key units, measured from the physical board ---
STAGGER = [0.3, 0.15, 0, 0.15, 0.3]  # per column, pinky to pinky on both halves
MIRROR = 15.25                       # x + mirrored x == MIRROR - 1 (key width)
keys = []
for row in (1, 2, 3):
    for i, x in enumerate((1, 2, 3, 4, 5)):
        keys.append((x, row + STAGGER[i], 0))
    for i, x in enumerate((9.25, 10.25, 11.25, 12.25, 13.25)):
        keys.append((x, row + STAGGER[i], 0))
keys.extend([
    (3.65, 4.30, 0), (4.72, 4.42, 12), (5.85, 4.72, 28),      # left: ⌃ ␣ ●R
    (8.40, 4.72, -28), (9.53, 4.42, -12), (10.60, 4.30, 0),   # right: ●B ⌫ ↩
])

# case outline of the left half (staircase top following the columns, inner
# controller strip going down to the thumb wedge, chamfered pinky corner —
# traced from a photo of the actual case); the right one is mirrored
CASE_L = [
    (0.80, 1.10), (2.00, 1.10), (2.00, 0.95), (3.00, 0.95), (3.00, 0.80),
    (4.00, 0.80), (4.00, 0.95), (5.00, 0.95), (5.00, 1.10),
    (7.40, 1.10), (7.40, 5.60), (6.70, 6.25), (3.45, 5.50), (0.80, 4.50),
]
CASE_R = [(MIRROR - x, y) for x, y in CASE_L]

U, S, M = 54.0, 58.0, 16.0

def corners(x, y, rot):
    cx, cy = x * S + U / 2, y * S + U / 2
    a = math.radians(rot)
    pts = []
    for dx, dy in ((-U / 2, -U / 2), (U / 2, -U / 2), (U / 2, U / 2), (-U / 2, U / 2)):
        pts.append((cx + dx * math.cos(a) - dy * math.sin(a),
                    cy + dx * math.sin(a) + dy * math.cos(a)))
    return pts

allpts = [(x * S, y * S) for x, y in CASE_L + CASE_R]
for x, y, rot in keys:
    allpts += corners(x, y, rot)
minx, miny = min(p[0] for p in allpts), min(p[1] for p in allpts)
maxx, maxy = max(p[0] for p in allpts), max(p[1] for p in allpts)
W, H = maxx - minx + 2 * M, maxy - miny + 2 * M

esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f" font-family="Helvetica, Arial, sans-serif">' % (W, H)]
out.append('<style>'
           '.case{fill:#e7e7e5;stroke:#c4c4c2;stroke-width:5;stroke-linejoin:round;}'
           '.key{fill:#fdfdfd;stroke:#444;stroke-width:1.2;}'
           '.red-key{fill:#fdeceb;stroke:#c0392b;stroke-width:1.2;}'
           '.blue-key{fill:#eaf2fb;stroke:#2471a3;stroke-width:1.2;}'
           '.en{font-size:19px;fill:#111;}'
           '.ru{font-size:12px;fill:#666;}'
           '.red{font-size:12px;fill:#c0392b;}'
           '.blue{font-size:12px;fill:#2471a3;}'
           '.rublue{font-size:12px;fill:#1a5276;font-weight:bold;}'
           '</style>')
out.append('<g transform="translate(%.1f, %.1f)">' % (M - minx, M - miny))
for case in (CASE_L, CASE_R):
    out.append('<polygon class="case" points="%s"/>'
               % ' '.join('%.1f,%.1f' % (x * S, y * S) for x, y in case))
for (x, y, rot), (en, ru, red, blue, rublue) in zip(keys, K):
    px, py = x * S, y * S
    cls, label = 'key', en
    if en == '●R':
        cls, label = 'red-key', ''
    elif en == '●B':
        cls, label = 'blue-key', ''
    if rot:
        out.append('<g transform="rotate(%g, %.1f, %.1f)">' % (rot, px + U / 2, py + U / 2))
    out.append('<rect class="%s" x="%.1f" y="%.1f" width="%g" height="%g" rx="7"/>' % (cls, px, py, U, U))
    if label:
        out.append('<text class="en" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                   % (px + U / 2, py + U / 2 + 7, esc(label)))
    if red == '●':  # green layer access
        out.append('<text x="%.1f" y="%.1f" font-size="11" fill="#1e8449">●</text>' % (px + 5, py + 15))
    elif red:
        out.append('<text class="red" x="%.1f" y="%.1f">%s</text>' % (px + 5, py + 15, esc(red)))
    if blue:
        out.append('<text class="blue" x="%.1f" y="%.1f" text-anchor="end">%s</text>' % (px + U - 5, py + 15, esc(blue)))
    if ru:
        out.append('<text class="ru" x="%.1f" y="%.1f">%s</text>' % (px + 5, py + U - 6, esc(ru)))
    if rublue:
        out.append('<text class="rublue" x="%.1f" y="%.1f" text-anchor="end">%s</text>' % (px + U - 5, py + U - 6, esc(rublue)))
    if rot:
        out.append('</g>')
out.append('</g>')
out.append('</svg>')

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aptoshka.svg')
open(path, 'w', encoding='utf-8').write('\n'.join(out))
print('wrote %s (%.0fx%.0f)' % (path, W, H))
