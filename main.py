# news-image-20261123: a one-page newspaper front page summing up
# Monday 23 November 2026. Pure Python 3 stdlib: draws the whole page
# procedurally (5x7 bitmap font, flat vector shapes) and writes a
# deterministic PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
# No network, no randomness, no clock: two runs are byte-identical.

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (24, 24, 24)
GREY = (96, 92, 82)
RULE = (196, 188, 170)
RED = (176, 32, 28)
BLUE = (28, 62, 118)
TEAL = (18, 110, 108)
ORANGE = (214, 88, 18)
GOLD = (186, 138, 20)
LIGHT = (232, 226, 212)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells, '#' = ink.
FONT = {
"A": (" .###. ",),  # placeholder replaced below
}
# The font table is built row by row in _FONT_ROWS for readability.
_FONT_ROWS = {
"A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
"C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
"D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
"E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
"F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
"G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
"H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
"J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
"L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
"M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
"N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
"X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
"b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
"c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
"d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
"e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
"f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
"g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
"i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
"j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", "##..."),
"k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
"l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
"n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
"o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
"p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
"q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
"s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
"t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
"u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
"v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
"x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
"y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
"z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
"0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
"2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
"3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
",": (".....", ".....", ".....", ".....", "..##.", "..#..", ".#..."),
":": (".....", ".##..", ".....", ".....", ".##..", ".....", "....."),
";": (".....", ".##..", ".....", ".##..", "..#..", ".#...", "....."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
"-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
"(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
"/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
"&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
"%": ("#...#", "#..#.", "..#..", ".#...", "#..#.", "#...#", "....."),
"+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
"=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
"*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}
# Fix the two glyphs that need an 8th row (descenders).
_FONT_ROWS["g"] = (".....", ".....", ".####", "#...#", "#...#", ".####", "....#")
_FONT_ROWS["j"] = ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.")
# Normalise every glyph to exactly 7 rows (truncate extras).
FONT = {ch: tuple(rows[:7]) for ch, rows in _FONT_ROWS.items()}
FONT["A"] = _FONT_ROWS["A"]


def glyph(ch):
    return FONT.get(ch, FONT["?"])


def text_width(s, scale):
    return len(s) * 6 * scale


def wrap(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x0, y0, x1, y1, c):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            for x in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, c)
        self.fill_rect(x0, y1 - t, x1, y1, c)
        self.fill_rect(x0, y0, x0 + t, y1, c)
        self.fill_rect(x1 - t, y0, x1, y1, c)

    def hline(self, x0, x1, y, c, t=1):
        self.fill_rect(x0, y, x1, y + t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.fill_rect(x, y0, x + t, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(x, y, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(x, y, c)

    def fill_triangle(self, p0, p1, p2, c):
        xs = sorted([p0, p1, p2], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = xs
        if y0 == y2:
            return
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(max(0, y0), min(self.h, y2 + 1)):
            if y < y1:
                xa = edge(x0, y0, x1, y1, y)
                xb = edge(x0, y0, x2, y2, y)
            else:
                xa = edge(x1, y1, x2, y2, y)
                xb = edge(x0, y0, x2, y2, y)
            lo, hi = sorted((int(xa), int(xb)))
            self.fill_rect(lo, y, hi + 1, y + 1, c)

    def text(self, s, x, y, scale=2, c=INK):
        cx = x
        for ch in s:
            g = glyph(ch)
            for r, row in enumerate(g):
                for col, cell in enumerate(row):
                    if cell == "#":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       cx + (col + 1) * scale,
                                       y + (r + 1) * scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, s, cx, y, scale=2, c=INK):
        return self.text(s, cx - text_width(s, scale) // 2, y, scale, c)

    def para(self, s, x, y, max_w, scale=2, c=INK, leading=None):
        lh = leading if leading is not None else 7 * scale + 4
        for ln in wrap(s, max_w, scale):
            self.text(ln, x, y, scale, c)
            y += lh
        return y

    def png_bytes(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]
        def chunk(typ, data):
            out = struct.pack(">I", len(data)) + typ + data
            return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))

def chord(cv, cx, cy, r, dy, c):
    """Horizontal chord of a circle at vertical offset dy."""
    if abs(dy) >= r:
        return
    hw = int((r * r - dy * dy) ** 0.5)
    cv.hline(cx - hw, cx + hw, cy + dy, c, 2)


def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, BLUE, fill=True)
    cv.circle(cx, cy, r, INK, fill=False)
    for dy in (-r // 2, 0, r // 2):
        chord(cv, cx, cy, r, dy, PAPER)
    for dx in (-r // 2, r // 2):
        if abs(dx) < r:
            hw = int((r * r - dx * dx) ** 0.5)
            cv.vline(cx + dx, cy - hw, cy + hw, PAPER, 2)
    # Red crack zigzag across the globe.
    pts = [(cx - r + 8, cy - 18), (cx - 20, cy - 4), (cx - 4, cy + 12),
           (cx + 16, cy - 2), (cx + r - 10, cy + 16)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)


def draw_ship_scene(cv, x, y, w, h):
    cv.fill_rect(x, y, x + w, y + h, LIGHT)
    cv.rect(x, y, x + w, y + h, RULE, 1)
    sea_y = y + h - 14
    cv.fill_rect(x, sea_y, x + w, y + h, BLUE)
    # Smoke puffs.
    for sx, sy, sr in ((x + w - 78, y + 10, 6), (x + w - 62, y + 6, 8),
                       (x + w - 46, y + 10, 5)):
        cv.circle(sx, sy, sr, GREY, fill=True)
    # Small flame on deck.
    cv.fill_triangle((x + w - 66, y + 24), (x + w - 59, y + 12),
                     (x + w - 52, y + 24), ORANGE)
    # Containers.
    cv.fill_rect(x + 18, y + 24, x + 48, y + 38, RED)
    cv.fill_rect(x + 52, y + 24, x + 82, y + 38, TEAL)
    cv.fill_rect(x + 86, y + 24, x + 116, y + 38, GOLD)
    # Hull with a bow that stays inside the box.
    cv.fill_rect(x + 10, y + 38, x + w - 34, y + 50, INK)
    cv.fill_triangle((x + w - 34, y + 38), (x + w - 34, y + 50),
                     (x + w - 8, y + 50), INK)


def draw_flame_scene(cv, x, y, w, h):
    cv.fill_rect(x, y, x + w, y + h, LIGHT)
    cv.rect(x, y, x + w, y + h, RULE, 1)
    for sx, sy, sr in ((x + 40, y + 12, 8), (x + 62, y + 7, 10),
                       (x + 84, y + 13, 7)):
        cv.circle(sx, sy, sr, GREY, fill=True)
    cx = x + w // 2
    cv.fill_triangle((cx - 46, y + h - 6), (cx - 6, y + 8),
                     (cx + 22, y + h - 6), ORANGE)
    cv.fill_triangle((cx - 26, y + h - 6), (cx + 2, y + 22),
                     (cx + 34, y + h - 6), RED)
    cv.fill_triangle((cx - 10, y + h - 6), (cx + 4, y + 34),
                     (cx + 16, y + h - 6), GOLD)
    cv.fill_rect(x, y + h - 6, x + w, y + h, INK)


def kicker(cv, s, x, y):
    cv.fill_rect(x, y + 2, x + 10, y + 12, RED)
    return cv.text(s, x + 16, y, 2, RED)


def headline(cv, s, x, y, max_w, scale=3):
    for ln in wrap(s, max_w, scale):
        cv.text(ln, x, y, scale, INK)
        y += 7 * scale + 4
    return y


def draw_page(cv):
    MX, RX = 28, 996
    # --- Masthead ---
    cv.hline(MX, RX, 20, INK, 2)
    cv.text_center("THE WORLD TODAY", 512, 32, 6, INK)
    cv.fill_rect(MX, 86, RX, 90, RED)
    cv.text("MONDAY, 23 NOVEMBER 2026", MX, 100, 2, INK)
    rw = text_width("ONE DAY IN THE WORLD", 2)
    cv.text("ONE DAY IN THE WORLD", RX - rw, 100, 2, GREY)
    cv.hline(MX, RX, 120, INK, 2)

    # --- Lead story: COP31 collapses ---
    kicker(cv, "CLIMATE - ANTALYA, TURKIYE", MX, 134)
    cv.text("CLIMATE TALKS COLLAPSE", MX, 156, 5, INK)
    cv.text("No deal as 194 nations split over fossil fuels", MX, 200, 2, GREY)
    y = cv.para(
        "The COP31 climate summit in Antalya ended on Sunday with no "
        "agreement, the longest UN climate conference ever and the first "
        "to collapse since Copenhagen in 2009. The final draft dropped "
        "every mention of fossil fuels, and the EU, Britain and island "
        "states refused to back it.",
        MX, 228, 572, 2, INK)
    y = cv.para(
        "Just 142m dollars in new funding was pledged. Talks chair "
        "Chris Bowen called the outcome very disappointing.",
        MX, y + 8, 572, 2, INK)
    # Art panel: globe + NO DEAL stamp.
    cv.fill_rect(620, 224, RX, 400, LIGHT)
    cv.rect(620, 224, RX, 400, RULE, 1)
    cv.text_center("ANTALYA, TURKIYE", 808, 232, 2, GREY)
    draw_globe(cv, 808, 300, 54)
    cv.fill_rect(640, 358, 976, 392, RED)
    cv.text_center("NO DEAL", 808, 366, 3, PAPER)
    cv.hline(MX, RX, 414, INK, 2)

    # --- Three columns ---
    col_y = 430
    col_w = 312
    # Column A: war in Europe.
    x = MX
    kicker(cv, "WAR IN EUROPE", x, col_y)
    y = headline(cv, "BURNING SHIP OFF FINLAND", x, col_y + 22,
                 col_w, 3)
    draw_ship_scene(cv, x, y + 4, col_w, 56)
    y = cv.para(
        "The Sparta II, a Russian cargo ship hit by drones in the Baltic "
        "on Saturday, was still smouldering on Sunday. All 16 crew were "
        "evacuated.",
        x, y + 68, col_w, 2, INK)
    y = headline(cv, "14 MISSING AFTER KYIV STRIKE", x, y + 10, col_w, 3)
    cv.para(
        "A Russian drone hit a block near Kyiv on Sunday. One killed, "
        "14 missing, Zelenskiy said.",
        x, y + 4, col_w, 2, INK)
    cv.vline(352, col_y, 806, RULE, 1)
    # Column B: Asia.
    x = 364
    kicker(cv, "ASIA", x, col_y)
    y = headline(cv, "FACTORY FIRE: 50 MISSING IN JAVA", x, col_y + 22,
                 col_w, 3)
    draw_flame_scene(cv, x, y + 4, col_w, 56)
    y = cv.para(
        "Seven body bags were recovered; about 50 workers were missing "
        "after fire tore through a Milkita candy factory in Cikande, "
        "Banten.",
        x, y + 68, col_w, 2, INK)
    y = headline(cv, "NEPAL PM MEETS MODI IN DELHI", x, y + 10, col_w, 3)
    cv.para(
        "Nepal's PM Balendra Shah held talks with PM Narendra Modi in "
        "New Delhi on Monday.",
        x, y + 4, col_w, 2, INK)
    cv.vline(688, col_y, 806, RULE, 1)
    # Column C: briefs.
    x = 700
    kicker(cv, "IN BRIEF", x, col_y)
    briefs = [
        ("KILLER ROBOTS TALKS GO ON",
         "UN talks on lethal AI weapons will continue."),
        ("SEOUL MINISTER QUITS",
         "Education minister quits over AI exam cheating."),
        ("LISBON MARCH",
         "Thousands marched in Lisbon over living costs."),
        ("MYANMAR HITS BACK",
         "Called ASEAN's decision unfair and imbalanced."),
        ("DEMOCRATS AT 258",
         "At least 258 House seats, the most since 1992."),
    ]
    y = col_y + 22
    for head, body in briefs:
        y = headline(cv, head, x, y, RX - x, 2)
        y = cv.para(body, x, y + 2, RX - x, 2, INK)
        y += 8
    cv.hline(MX, RX, 818, INK, 2)

    # --- Sport strip ---
    kicker(cv, "SPORT", MX, 832)
    sport = [
        ("LIVERPOOL 4-0 MAN UTD",
         "Ten-man Man Utd lost 4-0 at Liverpool."),
        ("INDIA 720/9d IN WELLINGTON",
         "India declared on a record 720 for 9 v New Zealand."),
        ("WEMBANYAMA 50 POINTS",
         "Wembanyama scored 50 as Spurs won 114-91."),
    ]
    for i, (head, body) in enumerate(sport):
        x = MX + i * 336
        y = headline(cv, head, x, 862, 312, 2)
        cv.para(body, x, y + 4, 312, 2, INK)
    cv.hline(MX, RX, 940, INK, 2)
    cv.text_center(
        "Sources: Reuters, CNN, AP, BBC, Le Monde - Monday 23 November 2026",
        512, 954, 2, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas()
    draw_page(cv)
    data = cv.png_bytes()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
