#!/usr/bin/env python3
"""Pixel-art panels for the profile README. Usage: python3 build.py (writes ./assets)."""
import math
import random
from pathlib import Path

from pixel import Canvas, P, luminance

OUT = Path(__file__).resolve().parent / "assets"
BLINK = "@keyframes blink{50%{opacity:0}}"

TITLE = "SAMET GÖKTEPE"
ROLES = ["BACKEND ARCHITECT", "SYSTEM DESIGNER", "CLOUD ENGINEER"]
PROFILE = [
    ("location", "Turkey"),
    ("role", "Backend Developer & System Architect"),
    ("current work", "Scalable Microservices & Cloud Architecture"),
    ("learning", "Advanced System Design, Rust"),
    ("expertise", "Laravel, NestJS, Docker, DB Optimization"),
    ("philosophy", "I don't just write code. I architect ecosystems."),
    ("fun fact", "I treat logs like a detective treats evidence."),
]
GROUPS = [
    ("BACKEND & ARCHITECTURE", [("PHP", "#777BB4"), ("Laravel", "#FF2D20"), ("Node.js", "#5FA04E"), ("NestJS", "#E0234E"),
                                ("TypeScript", "#3178C6"), ("Python", "#3776AB"), ("Go", "#00ADD8"), ("Rust", "#DEA584")]),
    ("DATA & MESSAGING", [("MySQL", "#4479A1"), ("PostgreSQL", "#4169E1"), ("MongoDB", "#47A248"), ("Redis", "#DC382D"),
                          ("RabbitMQ", "#FF6600"), ("Kafka", "#3b3b3b"), ("Elasticsearch", "#FEC514"), ("GraphQL", "#E10098")]),
    ("DEVOPS & CLOUD", [("Docker", "#2496ED"), ("Kubernetes", "#326CE5"), ("AWS", "#FF9900"), ("GCP", "#4285F4"),
                        ("Linux", "#FCC624"), ("Nginx", "#009639"), ("GitHub", "#3b3b3b"), ("GitLab", "#FC6D26")]),
    ("FRONTEND & MOBILE", [("Vue", "#4FC08D"), ("React", "#61DAFB"), ("Next.js", "#3b3b3b"), ("Tailwind", "#06B6D4"),
                           ("Flutter", "#02569B"), ("HTML", "#E34F26"), ("CSS", "#1572B6"), ("JavaScript", "#F7DF1E")]),
    ("IDE & WORKFLOW", [("VS Code", "#007ACC"), ("PhpStorm", "#B345F6"), ("Postman", "#FF6C37"), ("Figma", "#F24E1E"),
                        ("Git", "#F05032"), ("Bash", "#4EAA25")]),
]
QUOTE = ("First, solve the problem. Then, write the code.", "John Johnson")
DIM = {P["amber"]: "#4a3416", P["cream"]: "#3e3d47", P["teal"]: "#174540", P["red"]: "#3f1c1c"}
SIL = "#070a18"
SKY = ("#0b1024", "#131a3c", "#1e2a5e")

ICON_IN = ["########", "#.#....#", "#..#.#.#", "#.##.#.#", "#.##.#.#", "#.##.#.#", "#......#", "########"]
ICON_X = ["#......#", ".#....#.", "..#..#..", "...##...", "...##...", "..#..#..", ".#....#.", "#......#"]
ICON_MAIL = ["##########", "##......##", "#.#....#.#", "#..#..#..#", "#...##...#", "#........#", "##########"]
DIAMOND = ["..#..", ".###.", "#####", ".###.", "..#.."]


def diamond(cv, x, y, color):
    cv.sprite(x, y, DIAMOND, color)


# ---------- hero: Istanbul night skyline over water ----------

def moon(cv, cx, cy):
    for y in range(cy - 12, cy + 13):
        for x in range(cx - 12, cx + 13):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 121 and (x - cx - 4) ** 2 + (y - cy + 2) ** 2 > 100:
                cv.px(x, y, P["cream"])


def skyline(cv, rng, x0, x1, ground, lit):
    x = x0
    while x < x1 - 8:
        w = min(rng.randrange(14, 40), x1 - x)
        h = rng.randrange(14, 36)
        top = ground - h
        cv.fill(x, top, w, h, SIL)
        if rng.random() < .3:
            ax = x + w // 2
            cv.fill(ax, top - 6, 1, 6, SIL)
            cv.px(ax, top - 7, P["red"], "beacon")
        if rng.random() < .4:
            cv.fill(x + 2, top - 3, max(2, min(8, w - 6)), 3, SIL)
        for wy in range(top + 3, ground - 3, 4):
            for wx in range(x + 2, x + w - 2, 3):
                if rng.random() < .2:
                    col = P["amber"] if rng.random() < .75 else P["cream"]
                    cv.px(wx, wy, col)
                    lit.append((wx, wy, col))
        x += w + rng.choice([0, 0, 1, 2])


def galata(cv, x, ground, lit):
    cv.fill(x, ground - 40, 12, 40, SIL)
    for k in range(8):                       # conical roof
        w = 2 + int(k * 10 / 7)
        cv.fill(x + (12 - w) // 2, ground - 48 + k, w, 1, SIL)
    cv.fill(x - 2, ground - 34, 16, 2, SIL)  # balcony ring
    for wx in (x + 2, x + 5, x + 8):
        cv.px(wx, ground - 37, P["amber"]); lit.append((wx, ground - 37, P["amber"]))
    for wy in (ground - 28, ground - 20, ground - 12):
        cv.px(x + 5, wy, P["cream"]); lit.append((x + 5, wy, P["cream"]))


def mosque(cv, x, ground, lit):
    base_top = ground - 14
    cv.fill(x, base_top, 72, 14, SIL)
    for cx, r in ((x + 36, 18), (x + 12, 8), (x + 60, 8)):
        for dy in range(-r, 1):
            hw = int(math.sqrt(r * r - dy * dy))
            cv.fill(cx - hw, base_top + dy, 2 * hw + 1, 1, SIL)
    cv.fill(x + 36, base_top - 22, 1, 4, SIL)   # alem on the main dome
    for mx in (x - 10, x + 79):                              # minarets
        cv.fill(mx, ground - 44, 3, 44, SIL)
        cv.fill(mx + 1, ground - 48, 1, 4, SIL)
        for by in (ground - 30, ground - 20):
            cv.fill(mx - 1, by, 5, 1, SIL)
        cv.px(mx + 1, ground - 25, P["amber"]); lit.append((mx + 1, ground - 25, P["amber"]))
    for wx in range(x + 4, x + 70, 6):
        cv.px(wx, ground - 8, P["amber"]); lit.append((wx, ground - 8, P["amber"]))


def bridge(cv, x0, x1, ground, lit):
    deck, top = ground - 10, ground - 46
    t1, t2 = x0 + 30, x1 - 34
    cv.fill(x0, deck, x1 - x0, 4, SIL)
    for tx in (t1, t2):
        cv.fill(tx, top, 6, ground - top, SIL)
    mid, half = (t1 + 6 + t2) / 2, (t2 - t1 - 6) / 2
    cable = []
    for x in range(t1 + 6, t2):
        t = (x - mid) / half
        cable.append((x, top + int(round(24 * (1 - t * t)))))
    for x in range(x0, t1):                      # side spans sag towards the deck ends
        t = (t1 - x) / (t1 - x0)
        cable.append((x, top + int(round((deck - 2 - top) * t * t))))
    for x in range(t2 + 6, x1):
        t = (x - t2 - 6) / (x1 - t2 - 6)
        cable.append((x, top + int(round((deck - 2 - top) * t * t))))
    for i, (x, y) in enumerate(sorted(cable)):
        cv.px(x, y, P["mute"])
        if x % 12 == 0 and y < deck - 3:
            cv.fill(x, y + 1, 1, deck - y - 1, SIL)
        if x % 6 == 3 and y < deck - 1:
            col = P["teal"] if x % 36 == 3 else P["amber"]
            cv.px(x, y - 1, col, "shim" if x % 36 == 3 else "base")
            lit.append((x, y - 1, col))
    for x in range(x0 + 4, x1, 10):
        cv.px(x, deck - 1, P["cream"]); lit.append((x, deck - 1, P["cream"]))


def water(cv, ground, lit, rng):
    cv.fill(0, ground, cv.w, 1, P["horizon"])
    for x, y, col in lit:
        if (x + y) % 2:
            continue
        ry = ground + (ground - y) // 2 + 1
        rx = x + (1 if ry % 2 else 0)
        cv.px(rx, ry, DIM.get(col, col), "shim" if rng.random() < .3 else "base")


def hero():
    W, H, G = 520, 140, 108
    cv = Canvas(W, H)
    cv.fill(0, 0, W, 40, SKY[0]); cv.fill(0, 40, W, 34, SKY[1])
    cv.fill(0, 74, W, G - 74, SKY[2]); cv.fill(0, G, W, H - G, P["deep"])
    rng = random.Random(7)
    lit = []
    keep = (8, 8, 24 + cv.text_width(TITLE, 3), 58)
    for _ in range(80):
        x, y = rng.randrange(W), rng.randrange(0, 60)
        if keep[0] <= x <= keep[2] and keep[1] <= y <= keep[3]:
            continue
        r = rng.random()
        cv.px(x, y, P["cream"] if rng.random() < .4 else P["mute"], "twa" if r < .12 else "twb" if r < .24 else "base")
    moon(cv, 462, 24)
    skyline(cv, rng, 0, 392, G, lit)
    galata(cv, 96, G, lit)
    mosque(cv, 300, G, lit)
    bridge(cv, 392, W, G, lit)
    water(cv, G, lit, rng)
    cv.text(16, 16, TITLE, P["night"], 3)
    cv.text(14, 14, TITLE, P["cream"], 3)
    x = 14
    for i, role in enumerate(ROLES):
        x = cv.text(x, 46, role, P["cream"])
        if i < len(ROLES) - 1:
            diamond(cv, x + 4, 47, P["teal"])
            x += 13
    assert x <= keep[2] + 120 and x < W, "roles line too wide"
    css = (".twa{animation:blink 2.6s steps(1,end) infinite}.twb{animation:blink 3.4s steps(1,end) 1.1s infinite}"
           ".beacon{animation:blink 1.4s steps(1,end) infinite}.shim{animation:blink 2.2s steps(1,end) .7s infinite}" + BLINK)
    return cv.svg(css, "Samet Göktepe. Backend architect, system designer, cloud engineer. Istanbul skyline at night.")


# ---------- terminal: whoami on a CRT ----------

def terminal():
    W, H = 520, 166
    sx, sy, sw, sh = 10, 10, 500, 134
    cv = Canvas(W, H)
    cv.fill(0, 0, W, H, P["steel"])
    cv.bevel(0, 0, W, H, P["steel_hi"], P["steel_lo"])
    cv.fill(sx - 1, sy - 1, sw + 2, sh + 2, P["steel_lo"])
    cv.fill(sx, sy, sw, sh, P["screen"])
    for y in range(sy + 1, sy + sh, 2):
        cv.fill(sx, y, sw, 1, P["scan"])
    lines = [("$", "whoami"), ("out", "samet.goktepe"), ("$", "cat profile.txt")]
    lines += [("kv", kv) for kv in PROFILE]
    lines.append(("$", None))
    key_w = max(cv.text_width(k) for k, _ in PROFILE) + 10
    for i, (kind, payload) in enumerate(lines):
        layer, y, x = f"ln{i}", sy + 8 + i * 11, sx + 8
        cv.styles[layer] = f"animation-delay:{.25 + i * .22:.2f}s"
        if kind == "$":
            x = cv.text(x, y, "$", P["teal"], layer=layer) + 4
            if payload is None:
                cv.rect(x, y, 6, 8, P["green"], "cur")
            else:
                cv.text(x, y, payload, P["cream"], layer=layer)
        elif kind == "out":
            cv.text(x, y, payload, P["green"], layer=layer)
        else:
            key, value = payload
            cv.text(x, y, key, P["green_dim"], layer=layer)
            end = cv.text(x + key_w, y, value, P["green"], layer=layer)
            assert end < sx + sw - 6, f"terminal line too wide: {value}"
    cv.rect(14, H - 8, 2, 2, P["green"], "led")
    cv.text_right(W - 14, H - 10, "TTY1", P["mute"])
    css = ("[class^=ln]{opacity:0;animation:show .1s steps(1,end) forwards}@keyframes show{to{opacity:1}}"
           ".cur{animation:blink 1s steps(1,end) infinite}.led{animation:blink 3s steps(1,end) infinite}" + BLINK)
    return cv.svg(css, "whoami: " + "; ".join(f"{k}: {v}" for k, v in PROFILE))


# ---------- shelf: the stack as cartridges on wooden shelves ----------

def cartridge(cv, x, y, name, color):
    w, h = 118, 16
    cv.fill(x, y, w, h, P["steel"])
    cv.bevel(x, y, w, h, P["steel_hi"], P["steel_lo"])
    cv.fill(x + 2, y, 2, 1, P["steel_lo"]); cv.fill(x + w - 4, y, 2, 1, P["steel_lo"])
    cv.fill(x + 6, y + 3, w - 12, h - 6, color)
    ink = P["night"] if luminance(color) > 0.3 else P["cream"]
    assert cv.text_width(name) <= w - 16, f"cartridge label too wide: {name}"
    cv.text_center(x + w // 2, y + 4, name, ink)


def shelf():
    W = 520
    block, H = 62, 10 + 62 * len(GROUPS)
    cv = Canvas(W, H)
    cv.fill(0, 0, W, H, P["night"])
    for g, (group, items) in enumerate(GROUPS):
        y = 10 + g * block
        cv.fill(8, y, W - 16, 12, P["wood"])
        cv.bevel(8, y, W - 16, 12, P["wood_hi"], P["wood_lo"])
        cv.text(16, y + 2, group, P["cream"])
        for i, (name, color) in enumerate(items):
            row, col = divmod(i, 4)
            cartridge(cv, 12 + col * 126, y + 14 + row * 23, name, color)
        for row in range(2):
            by = y + 14 + row * 23 + 16
            cv.fill(8, by, W - 16, 3, P["wood"])
            cv.fill(8, by + 3, W - 16, 1, P["wood_lo"])
    names = ", ".join(n for _, items in GROUPS for n, _ in items)
    return cv.svg("", "Tech stack shelves: " + names)


# ---------- footer sign and contact buttons ----------

def footer():
    W, H = 520, 56
    cv = Canvas(W, H)
    cv.fill(0, 0, W, H, P["steel"])
    cv.bevel(0, 0, W, H, P["steel_hi"], P["steel_lo"])
    cv.fill(6, 6, W - 12, H - 12, P["dusk"])
    cv.text_center(W // 2, 16, QUOTE[0], P["cream"])
    cv.text_center(W // 2, 32, QUOTE[1], P["mute"])
    diamond(cv, 16, 25, P["teal"]); diamond(cv, W - 21, 25, P["teal"])
    return cv.svg("", f"{QUOTE[0]} ({QUOTE[1]})")


def button(label, icon, icon_w):
    W, H = 130, 22
    cv = Canvas(W, H)
    cv.fill(0, 0, W, H, P["steel"])
    cv.bevel(0, 0, W, H, P["steel_hi"], P["steel_lo"], 2)
    cv.sprite(10, (H - len(icon)) // 2, icon, P["cream"])
    cv.text_center((10 + icon_w + W) // 2, 7, label, P["cream"])
    return cv.svg("", label)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    files = {"hero.svg": hero(), "terminal.svg": terminal(), "shelf.svg": shelf(), "footer.svg": footer(),
             "btn-linkedin.svg": button("LinkedIn", ICON_IN, 8), "btn-x.svg": button("X / Twitter", ICON_X, 8),
             "btn-email.svg": button("Email", ICON_MAIL, 10)}
    for name, svg in files.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"{name:18s} {len(svg) // 1024:4d} KB")
