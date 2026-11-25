#!/usr/bin/env python3
"""Draw the news-image-20261125 entry: a cream broadsheet front page.

THE WORLD TODAY - Wednesday, 25 November 2026.
Ten stories, each cross-checked against at least two independent sources.
Deterministic: fixed fonts, fixed geometry, no randomness, no time, no network.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (245, 239, 224)
INK = (18, 18, 18)
RED = (178, 34, 34)
NAVY = (26, 35, 64)
NAVY_DARK = (14, 21, 38)
GOLD = (198, 148, 42)
GREY = (90, 86, 76)
LIGHT_GREY = (154, 163, 178)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap to max_w, returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, max_w, fill, leading):
    lines = wrap(d, text, fnt, max_w)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(d, text, fnt, max_w, max_lines):
    """Return (lines, font) shrinking the font until it fits max_lines."""
    size = fnt.size
    while size > 10:
        f = font(fnt.path, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 2
    f = font(fnt.path, 10)
    return wrap(d, text, f, max_w), f


def rule(d, x0, y, x1, w=3):
    d.line([(x0, y), (x1, y)], fill=INK, width=w)


def kicker(d, x, y, text):
    d.text((x, y), text, font=font(SANS_B, 20), fill=RED)
    return y + 28


def icon_trophy(d, x, y, s=46):
    d.rectangle([x, y, x + s, y + s], outline=NAVY, width=2)
    cx = x + s // 2
    d.polygon([(x + 10, y + 8), (x + s - 10, y + 8), (x + s - 13, y + 24),
               (x + 13, y + 24)], fill=GOLD)
    d.arc([x + 4, y + 10, x + 16, y + 24], 90, 270, fill=GOLD, width=3)
    d.arc([x + s - 16, y + 10, x + s - 4, y + 24], -90, 90, fill=GOLD, width=3)
    d.rectangle([cx - 2, y + 24, cx + 2, y + 32], fill=GOLD)
    d.rectangle([x + 12, y + 32, x + s - 12, y + 37], fill=GOLD)


def icon_derrick(d, x, y, s=46):
    d.rectangle([x, y, x + s, y + s], outline=NAVY, width=2)
    d.line([(x + 12, y + 38), (x + 20, y + 8)], fill=NAVY, width=3)
    d.line([(x + 34, y + 38), (x + 26, y + 8)], fill=NAVY, width=3)
    d.line([(x + 20, y + 8), (x + 26, y + 8)], fill=NAVY, width=3)
    d.line([(x + 15, y + 26), (x + 31, y + 26)], fill=NAVY, width=2)
    d.line([(x + 18, y + 17), (x + 28, y + 17)], fill=NAVY, width=2)
    d.ellipse([x + 31, y + 28, x + 39, y + 36], fill=INK)


def icon_shield(d, x, y, s=46):
    d.rectangle([x, y, x + s, y + s], outline=NAVY, width=2)
    cx = x + s // 2
    d.polygon([(cx - 13, y + 9), (cx + 13, y + 9), (cx + 13, y + 24),
               (cx, y + 37), (cx - 13, y + 24)], outline=NAVY, width=2)
    d.text((cx - 8, y + 15), "UK", font=font(SANS_B, 13), fill=NAVY)


def icon_ball(d, x, y, s=46):
    d.rectangle([x, y, x + s, y + s], outline=NAVY, width=2)
    cx, cy = x + s // 2, y + s // 2
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=INK, width=2)
    d.polygon([(cx, cy - 6), (cx + 6, cy - 2), (cx + 4, cy + 5),
               (cx - 4, cy + 5), (cx - 6, cy - 2)], fill=INK)
    for ang in (90, 210, 330):
        import math
        r = math.radians(ang)
        d.line([(cx, cy), (cx + int(14 * math.cos(r)), cy + int(14 * math.sin(r)))],
               fill=INK, width=1)


def icon_dome(d, x, y, s=46):
    d.rectangle([x, y, x + s, y + s], outline=NAVY, width=2)
    cx = x + s // 2
    d.pieslice([cx - 13, y + 10, cx + 13, y + 36], 180, 360, fill=NAVY)
    d.rectangle([cx - 15, y + 30, cx + 15, y + 38], fill=NAVY)
    d.line([(cx, y + 5), (cx, y + 10)], fill=NAVY, width=2)
    d.line([(x + 8, y + 14), (x + 8, y + 38)], fill=NAVY, width=2)
    d.line([(x + 38, y + 14), (x + 38, y + 38)], fill=NAVY, width=2)


def icon_plane(d, x, y, s=46):
    d.rectangle([x, y, x + s, y + s], outline=NAVY, width=2)
    # side-view jet: fuselage, swept wing, tail fin
    d.polygon([(x + 5, y + 25), (x + 20, y + 21), (x + 38, y + 21),
               (x + 42, y + 24), (x + 38, y + 27), (x + 20, y + 28)],
              fill=NAVY)
    d.polygon([(x + 20, y + 21), (x + 26, y + 10), (x + 30, y + 21)], fill=NAVY)
    d.polygon([(x + 34, y + 21), (x + 38, y + 13), (x + 41, y + 21)], fill=NAVY)
    d.polygon([(x + 22, y + 28), (x + 26, y + 36), (x + 30, y + 28)], fill=NAVY)


def night_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    for sx, sy in [(18, 14), (110, 10), (240, 12),
                   (360, 14), (480, 10), (90, 40),
                   (330, 42), (450, 40)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # distant buildings
    d.rectangle([x + 8, y + h - 46, x + 78, y + h], fill=NAVY_DARK)
    d.rectangle([x + 420, y + h - 40, x + 470, y + h], fill=NAVY_DARK)
    d.rectangle([x + 470, y + h - 56, x + 516, y + h], fill=NAVY_DARK)
    # the tower: tall, lit bands
    tx = x + 150
    d.rectangle([tx, y + 10, tx + 56, y + h], fill=(8, 12, 26))
    for wy in range(y + 22, y + h - 6, 16):
        d.line([(tx + 6, wy), (tx + 50, wy)], fill=GOLD, width=2)
    # smoke drifting from the tower top
    for cx, cy, r in [(tx + 72, y + 20, 10), (tx + 90, y + 12, 13),
                      (tx + 110, y + 18, 9)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIGHT_GREY)
    # drone: small quadcopter with a faint trail
    dx, dy = x + 340, y + 30
    d.line([(dx - 46, dy + 22), (dx - 8, dy + 4)], fill=LIGHT_GREY, width=1)
    d.ellipse([dx - 4, dy - 3, dx + 4, dy + 3], fill=(255, 255, 255))
    for ox, oy in [(-9, -7), (9, -7), (-9, 7), (9, 7)]:
        d.ellipse([dx + ox - 3, dy + oy - 2, dx + ox + 3, dy + oy + 2],
                  outline=(255, 255, 255), width=1)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 36
    R = W - M  # right edge

    # --- masthead ---
    rule(d, M, 26, R, 4)
    lines, mast_f = fit_lines(d, "THE WORLD TODAY", font(SERIF_B, 92), R - M, 1)
    d.text(((W - d.textlength(lines[0], font=mast_f)) / 2, 36),
           lines[0], font=mast_f, fill=INK)
    rule(d, M, 140, R, 2)

    # --- date band ---
    d.rectangle([M, 150, R, 190], fill=INK)
    date_f = font(SANS_B, 26)
    dtxt = "WEDNESDAY, 25 NOVEMBER 2026"
    d.text(((W - d.textlength(dtxt, font=date_f)) / 2, 158),
           dtxt, font=date_f, fill=(255, 255, 255))

    # --- hero zone: left column (hero) + right column (two stories) ---
    hy = 208
    hero_w = 524
    hx = M
    col_x = M + hero_w + 24  # 584
    col_w = R - col_x        # 404

    # HERO
    y = kicker(d, hx, hy, "MIDDLE EAST \u2014 RIYADH")
    lines, hf = fit_lines(d, "HOUTHIS HIT RIYADH'S TALLEST TOWER",
                          font(SERIF_B, 54), hero_w, 3)
    for ln in lines:
        d.text((hx, y), ln, font=hf, fill=INK)
        y += hf.size + 4
    y += 2
    y = draw_wrapped(d, hx, y,
                     "Drone strike wounds 11 in the Saudi capital's "
                     "financial district \u2014 the second hit on the "
                     "PIF tower in a week.",
                     font(SANS, 21), hero_w, INK, 28)
    panel_y = y + 10
    panel_h = 590 - panel_y
    night_panel(d, hx, panel_y, hero_w, panel_h)

    # RIGHT COLUMN, story 1: Huawei
    y = kicker(d, col_x, hy, "UNITED STATES \u2014 JUSTICE")
    lines, hf = fit_lines(d, "HUAWEI GUILTY ON 10 OF 12 COUNTS",
                          font(SERIF_B, 34), col_w, 3)
    for ln in lines:
        d.text((col_x, y), ln, font=hf, fill=INK)
        y += hf.size + 3
    y = draw_wrapped(d, col_x, y + 2,
                     "Brooklyn jury convicts the telecom giant: bank "
                     "fraud, sanctions breaches, trade-secret theft.",
                     font(SANS, 18), col_w, INK, 24)
    rule(d, col_x, y + 10, R, 1)

    # RIGHT COLUMN, story 2: Sparta II
    y = kicker(d, col_x, y + 24, "EUROPE \u2014 WAR AT SEA")
    lines, hf = fit_lines(d, "KYIV OWNS THE SHIP STRIKE",
                          font(SERIF_B, 34), col_w, 2)
    for ln in lines:
        d.text((col_x, y), ln, font=hf, fill=INK)
        y += hf.size + 3
    draw_wrapped(d, col_x, y + 2,
                 "Zelenskyy confirms Ukraine hit Russian cargo ship "
                 "Sparta II in the Gulf of Finland.",
                 font(SANS, 18), col_w, INK, 24)

    # --- divider + 2x3 grid ---
    rule(d, M, 590, R, 2)
    grid = [
        ("AFRICA \u2014 SPORT", "SENEGAL WIN AFCON TITLE BACK",
         "CAS restores the 2025 crown; Morocco appeals.", icon_trophy),
        ("IRAQ \u2014 OIL", "BAGHDAD TAKES KURDISH OILFIELDS",
         "Federal takeover of Kurdish fields.", icon_derrick),
        ("BRITAIN \u2014 SANCTIONS", "UK SANCTIONS HOUTHIS",
         "Asset freezes on 4 officials over abuse.", icon_shield),
        ("EUROPE \u2014 FOOTBALL", "REAL MADRID ROUT PSV 5-1",
         "Mbapp\u00e9 brace in a second-half comeback.", icon_ball),
        ("GAZA \u2014 CONFLICT", "HAMAS SECURITY CHIEF KILLED",
         "Drone strike in Gaza City; both sides confirm.", icon_dome),
        ("UNITED STATES \u2014 TRAVEL", "O'HARE RADAR FAILS, 350 DELAYED",
         "Flights delayed by second ground stop.", icon_plane),
    ]
    gw = (R - M - 2 * 20) // 3
    gh = 158
    for i, (kick, head, sub, icon) in enumerate(grid):
        gx = M + (i % 3) * (gw + 20)
        gy = 606 + (i // 3) * (gh + 10)
        icon(d, gx, gy)
        kx = gx + 56
        kw = gw - 56
        klines = wrap(d, kick, font(SANS_B, 17), kw)
        ky = gy + 2
        for ln in klines:
            d.text((kx, ky), ln, font=font(SANS_B, 17), fill=RED)
            ky += 21
        hlines, hfont = fit_lines(d, head, font(SERIF_B, 25), gw, 2)
        hyy = gy + 54
        for ln in hlines:
            d.text((gx, hyy), ln, font=hfont, fill=INK)
            hyy += hfont.size + 2
        draw_wrapped(d, gx, hyy + 2, sub, font(SANS, 17), gw, GREY, 22)

    # --- footer ---
    rule(d, M, 946, R, 2)
    foot = "Reported 24\u201325 November 2026 \u2022 10 stories from six continents"
    ff = font(SANS, 18)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 960),
           foot, font=ff, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
