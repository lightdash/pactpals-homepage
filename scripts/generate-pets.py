"""Generate the 64x96 pixel-art pets in public/pets (same grid and egg cup as Sprout/Puff/Pebble)."""
import colorsys, math, os, struct, sys, zlib

W, H = 64, 96
INK = "#111a35"
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "pets")


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def tohex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02x}" for v in rgb)


def tone(c, dl=0.0, ds=0.0, dh=0.0):
    h, l, s = colorsys.rgb_to_hls(*hx(c))
    return tohex(colorsys.hls_to_rgb((h + dh) % 1, max(0, min(1, l + dl)), max(0, min(1, s + ds))))


def ramp(c):
    """hi, base, mid, dark: the four-step shading used by the original pets."""
    return (tone(c, 0.12, -0.05), c, tone(c, -0.1, 0.02, -0.01), tone(c, -0.2, 0.0, -0.02))


# ---------- masks ----------
def ellipse(cx, cy, rx, ry):
    return {(x, y) for y in range(H) for x in range(W)
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}


def poly(pts):
    out = set()
    for y in range(H):
        for x in range(W):
            px, py, inside = x + 0.5, y + 0.5, False
            for i in range(len(pts)):
                (x1, y1), (x2, y2) = pts[i], pts[i - 1]
                if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
                    inside = not inside
            if inside:
                out.add((x, y))
    return out


def rect(x, y, w, h):
    return {(i, j) for i in range(x, x + w) for j in range(y, y + h)}


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def sym(m):
    return m | mirror(m)


def dilate(m, r=2):
    return {(x + dx, y + dy) for x, y in m for dx in range(-r, r + 1) for dy in range(-r, r + 1)
            if abs(dx) + abs(dy) <= r + (1 if r > 1 else 0)}


class Pet:
    def __init__(self):
        self.g = {}

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.g[(x, y)] = c

    def part(self, mask, color, outline=True, shade=True, clip=None):
        if clip is not None:
            mask = mask & clip
        if outline:
            for p in dilate(mask) - mask:
                self.put(*p, INK)
        hi, base, mid, dark = ramp(color) if shade else (color,) * 4
        for x, y in mask:
            c = base
            if shade:
                if (x + 1, y) not in mask or (x, y + 1) not in mask:
                    c = dark
                elif (x + 2, y) not in mask or (x + 3, y) not in mask or (x, y + 2) not in mask:
                    c = mid
                elif (x - 1, y) not in mask or (x, y - 1) not in mask:
                    c = hi
            self.put(x, y, c)
        return mask

    def stamp(self, x0, y0, art, colors):
        for j, row in enumerate(art):
            for i, ch in enumerate(row):
                if ch in colors:
                    self.put(x0 + i, y0 + j, colors[ch])


# ---------- shared pieces ----------
def rim_top(x):
    return 61.5 + abs((x % 10) - 5) * 0.9


CUP = {(x, y) for x, y in ellipse(32, 64, 25.5, 29) if y >= rim_top(x)}
CUP_MOUTH = ellipse(32, 64, 24, 4.5)

EYES = {
    "sparkle": [".####.", "#ww###", "#ww###", "######", "####w#", "######", ".####."],
    "big": [".#####.", "#ww####", "#ww####", "#######", "#####w#", "#######", ".#####."],
    "happy": [".####.", "##..##", "#....#"],
    "wink": [".####.", "##..##", "#....#"],
    "sleepy": ["#....#", ".####."],
}
MOUTHS = {
    "smile": ["#....#", ".####."],
    "cat": ["#..#..#", ".##.##."],
    "open": ["#....#", "#pppp#", ".#pp#.", "..##.."],
    "tiny": ["#..#", ".##."],
    "tongue": ["#....#", ".####.", "..pp.."],
    "o": [".##.", "#..#", ".##."],
    "fang": ["#.....#", ".#####.", ".w...w."],
}


def face(p, cx=32, cy=50, eyes="sparkle", mouth="smile", gap=7, blush="#ff8fb3", body=None):
    """Stamp eyes, blush and mouth; mouth=None leaves it off (e.g. under a snout)."""
    art = EYES[eyes]
    ew = len(art[0])
    lx, rx = cx - gap - ew + 1, cx + gap
    if eyes == "wink":
        p.stamp(lx, cy - 3, EYES["sparkle"], {"#": INK, "w": "#ffffff"})
        p.stamp(rx, cy, art, {"#": INK})
    else:
        ey = cy - 3 if eyes in ("sparkle", "big") else cy
        p.stamp(lx, ey, art, {"#": INK, "w": "#ffffff"})
        p.stamp(rx, ey, art, {"#": INK, "w": "#ffffff"})
    if blush:
        for bx in (lx - 2, rx + ew - 3):
            p.stamp(bx, cy + 5, ["#####", ".###."], {"#": blush})
    if not mouth:
        return
    m = MOUTHS[mouth]
    p.stamp(cx - len(m[0]) // 2, cy + 4, m, {"#": INK, "p": "#ff6f91", "w": "#ffffff"})


def gloss(p, x, y):
    for dx, dy in ((0, 1), (0, 2), (1, 0), (0, 3), (1, 1)):
        p.put(x + dx, y + dy, "#ffffff")


def finish(p, name, cup, before=None, body_color=None, body=None, after=None, face_kw=None, gloss_at=(20, 37),
           over=None):
    p.part(CUP_MOUTH, tone(cup, -0.28, -0.35), shade=False)
    if before:
        before(p)
    b = p.part(body or ellipse(32, 48, 18.5, 18), body_color)
    if after:
        after(p, b)
    if gloss_at:
        gloss(p, *gloss_at)
    face(p, **(face_kw or {}))
    if over:
        over(p, b)
    p.part(CUP, cup)
    # rim highlight + a few speckles so it reads as eggshell
    for x in range(8, 57):
        y = math.ceil(rim_top(x))
        if all((x + dx, y) in CUP for dx in (-1, 1)) and (x, y + 1) in CUP:
            p.put(x, y, tone(cup, 0.08))
    for sx, sy in ((17, 74), (21, 80), (40, 76), (45, 71), (30, 85), (35, 72)):
        p.put(sx, sy, tone(cup, -0.08))
    return name, p


# ---------- the twenty ----------
def mochi():  # bunny
    p = Pet()
    def ears(p):
        for cx in (24, 40):
            p.part(ellipse(cx, 18, 4.5, 13), "#ffe3ee")
            p.part(ellipse(cx, 19, 2, 9), "#ff9fc1", outline=False, shade=False)
    return finish(p, "mochi", "#ffc2d9", ears, "#ffe3ee")


def biscuit():  # kitten
    p = Pet()
    def ears(p):
        p.part(sym(poly([(14, 40), (17, 20), (31, 32)])), "#ffb55e")
        p.part(sym(poly([(17.5, 34), (19, 25), (26, 31)])), "#ffd1dc", outline=False, shade=False)
    def stripes(p, b):
        for y in (33, 36):
            p.part(rect(30, y, 4, 2), "#e8893a", outline=False, shade=False, clip=b)
        for x, y in ((15, 46), (15, 50), (47, 46), (47, 50)):
            p.part(rect(x, y, 3, 1), INK, outline=False, shade=False)
    return finish(p, "biscuit", "#fff1d6", ears, "#ffb55e", after=stripes, face_kw={"mouth": "cat"})


def bun():  # bear cub
    p = Pet()
    def ears(p):
        for cx in (18, 46):
            p.part(ellipse(cx, 32, 6.5, 6.5), "#c99a6e")
            p.part(ellipse(cx, 32, 3, 3), "#f2c9a8", outline=False, shade=False)
    def muzzle(p, b):
        p.part(ellipse(32, 55, 7, 4.5), "#f2dcc3", outline=False, shade=False, clip=b)
    return finish(p, "bun", "#e7f2ff", ears, "#c99a6e", after=muzzle,
                  face_kw={"mouth": "tiny", "cy": 49})


def fizz():  # axolotl
    p = Pet()
    def gills(p):
        for side in (0, 1):
            for gx, gy, rx, ry in ((13, 37, 5, 2.6), (11, 44, 5.5, 2.6), (13, 51, 5, 2.6)):
                m = ellipse(gx, gy, rx, ry)
                p.part(mirror(m) if side else m, "#ff7fb0")
    return finish(p, "fizz", "#b9f3ff", gills, "#ffc6dd", face_kw={"eyes": "big", "mouth": "smile", "gap": 9})


def pip():  # chick
    p = Pet()
    def tuft(p):
        p.part(ellipse(30, 26, 2, 5), "#ffd84a")
        p.part(ellipse(34.5, 25, 2, 6), "#ffd84a")
    def wings(p, b):
        p.part(ellipse(32, 60, 10, 5), "#fff3b0", outline=False, shade=False, clip=b)
    face_kw = {"mouth": "tiny", "blush": "#ffa36b"}
    name, p = finish(p, "pip", "#d6f5ff", tuft, "#ffe680", after=wings, face_kw=face_kw)
    p.part(poly([(28.5, 53), (35.5, 53), (32, 57.5)]), "#ff9a3c")  # beak over mouth
    p.part(CUP, "#d6f5ff")
    return name, p


def shroomie():  # mushroom
    p = Pet()
    def cap(p, b):
        c = {(x, y) for x, y in ellipse(32, 41, 26, 17) if y <= 42}
        p.part(c, "#ff5a6e")
        for sx, sy, r in ((20, 34, 3.5), (32, 29, 3), (44, 34, 3.5), (27, 38, 2), (38, 38, 2)):
            p.part(ellipse(sx, sy, r, r * 0.9), "#fff6ee", outline=False, shade=False, clip=c)
    return finish(p, "shroomie", "#c9f0b8", None, "#fff0dd", body=ellipse(32, 52, 16, 14),
                  after=cap, face_kw={"cy": 52, "gap": 6}, gloss_at=(21, 47))


def twinkle():  # unicorn
    p = Pet()
    def horn(p):
        h = poly([(28.5, 32), (35.5, 32), (32, 12)])
        p.part(h, "#ffd75e")
        for y in (17, 22, 27):
            p.part({(x, yy) for x, yy in h if yy in (y, y + 1) and x + (y - yy) < 34}, "#ffb13b",
                   outline=False, shade=False)
    def mane(p, b):
        for (mx, my, r), col in zip(((38, 31, 4.5), (44, 34, 4), (48.5, 39.5, 3.5)),
                                    ("#ff9ad5", "#c7a2ff", "#8fd8ff")):
            p.part(ellipse(mx, my, r, r), col)
    return finish(p, "twinkle", "#e8dcff", horn, "#fff8ff", after=mane)


def ember():  # flame sprite
    p = Pet()
    def flame(p):
        f = poly([(18, 38), (19, 24), (24, 30), (27, 16), (32, 26), (37, 13), (40, 28), (45, 22), (46, 38)])
        p.part(f, "#ff8a3d")
        p.part(poly([(25, 36), (28, 24), (32, 31), (37, 21), (39, 36)]), "#ffd04a", outline=False, shade=False)
    return finish(p, "ember", "#ffe0c2", flame, "#ffb36b", face_kw={"eyes": "happy", "mouth": "open"})


def blossom():  # flower
    p = Pet()
    def flower(p):
        p.part(rect(31, 22, 2, 9), "#47b86b")
        for a in range(5):
            t = a * 2 * math.pi / 5 - math.pi / 2
            p.part(ellipse(32 + 5.5 * math.cos(t), 18 + 5.5 * math.sin(t), 3.8, 3.8), "#ff8fc4")
        p.part(ellipse(32, 18, 2.8, 2.8), "#ffe05a", shade=False)
    return finish(p, "blossom", "#d8f7c8", flower, "#ffd7ea", face_kw={"eyes": "wink"})


def waddle():  # penguin
    p = Pet()
    def belly(p, b):
        p.part(ellipse(32, 53, 13.5, 13), "#f5fbff", outline=False, shade=False, clip=b)
        p.part(ellipse(33, 29, 2, 3.5), "#4a6aa6")
    face_kw = {"cy": 50, "mouth": "tiny", "gap": 6}
    name, p = finish(p, "waddle", "#c7ecff", None, "#4a6aa6", after=belly, face_kw=face_kw)
    p.part(poly([(29, 53), (35, 53), (32, 56.5)]), "#ffb03b")
    p.part(CUP, "#c7ecff")
    return name, p


def ribbit():  # frog
    p = Pet()
    def bumps(p):
        p.part(ellipse(22, 33, 7, 7), "#7fd67a")
        p.part(ellipse(42, 33, 7, 7), "#7fd67a")
    def belly(p, b):
        p.part(ellipse(32, 58, 12, 6), "#d9f5b8", outline=False, shade=False, clip=b)
    name, p = finish(p, "ribbit", "#fff3c4", bumps, "#7fd67a", body=ellipse(32, 50, 19.5, 16),
                     after=belly, face_kw={"cy": 36, "gap": 6, "mouth": "smile", "blush": None}, gloss_at=None)
    p.stamp(28, 51, ["#......#", ".######."], {"#": INK})
    for bx in (15, 44):
        p.stamp(bx, 46, ["#####", ".###."], {"#": "#ff8fb3"})
    p.part(CUP, "#fff3c4")
    return name, p


def plum():  # baby bat
    p = Pet()
    def wings(p):
        w = poly([(17, 42), (3, 32), (6, 44), (1, 50), (8, 52), (6, 58), (17, 54)])
        p.part(sym(w), "#6c4fb8")
        p.part(sym(poly([(17, 34), (18, 24), (27, 31)])), "#9b7be0")
    return finish(p, "plum", "#ffd9ec", wings, "#9b7be0", face_kw={"mouth": "fang"})


def coral():  # fish
    p = Pet()
    def fins(p):
        p.part(poly([(26, 32), (33, 18), (40, 31)]), "#ff8c69")
        p.part(sym(poly([(15, 46), (5, 40), (8, 52), (15, 52)])), "#ff8c69")
    def scales(p, b):
        for x, y in ((24, 59), (32, 61), (40, 59)):
            p.stamp(x - 2, y, ["#...#", ".###."], {"#": "#ff9a7a"})
    return finish(p, "coral", "#bdf2ee", fins, "#ffb8a0", after=scales, face_kw={"eyes": "big", "gap": 8, "mouth": "open"})


def smol():  # baby dragon
    p = Pet()
    def horns(p):
        p.part(sym(poly([(20, 33), (19, 20), (27, 31)])), "#ffe39a")
        p.part(sym(poly([(15, 44), (2, 34), (5, 46), (14, 52)])), "#57c48f")
    def belly(p, b):
        p.part(ellipse(32, 60, 11, 7), "#d6f7c7", outline=False, shade=False, clip=b)
        for y in (55, 58, 61):
            p.part(rect(26, y, 12, 1), "#b5e8a6", outline=False, shade=False, clip=ellipse(32, 60, 11, 7))
        for x in (26, 32, 38):
            p.part(poly([(x - 2, 31), (x + 2, 31), (x, 27)]), "#3fa874")
    return finish(p, "smol", "#fff0c2", horns, "#7ee0a8", after=belly)


def buzzy():  # bee
    p = Pet()
    def wings(p):
        p.part(ellipse(14, 33, 6, 8), "#e6f7ff")
        p.part(ellipse(50, 33, 6, 8), "#e6f7ff")
        for x in (25, 39):
            p.part(rect(x, 22, 2, 9), INK, outline=False, shade=False)
            p.part(ellipse(x + 1, 21, 3, 3), INK, outline=False, shade=False)
    def stripes(p, b):
        for y in (34, 60):
            p.part(rect(0, y, W, 3), "#3a2a3d", outline=False, shade=False, clip=b)
    return finish(p, "buzzy", "#ffe1b8", wings, "#ffd23f", after=stripes, gloss_at=(20, 39))


def peachy():  # peach
    p = Pet()
    def leaf(p):
        p.part(rect(31, 25, 2, 6), "#7a5a3a")
        p.part(poly([(33, 27), (39, 20), (47, 20), (42, 27)]), "#6cc46a")
    def crease(p, b):
        p.part(rect(32, 31, 1, 7), "#ff9a7e", outline=False, shade=False)
    return finish(p, "peachy", "#d9f4c4", leaf, "#ffc2a6", after=crease, face_kw={"eyes": "happy"})


def halo():  # little angel ghost
    p = Pet()
    def back(p):
        p.part(sym(ellipse(12, 44, 6, 8.5)), "#ffffff")
    def ring(p, b):
        r = ellipse(32, 24, 10, 3.5) - ellipse(32, 24, 6.5, 1.6)
        p.part(r, "#ffe066")
    return finish(p, "halo", "#e3e9ff", back, "#e6dcff", after=ring, face_kw={"eyes": "sparkle", "mouth": "tiny"})


def mango():  # fox kit
    p = Pet()
    def ears(p):
        e = poly([(15, 40), (16, 18), (31, 31)])
        p.part(sym(e), "#ff9a3d")
        p.part(sym({(x, y) for x, y in e if y < 25}), "#5a3427", outline=False, shade=False)
        p.part(sym(poly([(18.5, 33), (18.5, 25), (25, 31)])), "#ffe1c4", outline=False, shade=False)
    def cheeks(p, b):
        p.part(sym(ellipse(22, 59, 10, 7)), "#fff3e3", outline=False, shade=False, clip=b)
    return finish(p, "mango", "#e0f1ff", ears, "#ff9a3d", after=cheeks, face_kw={"mouth": "cat"})


def wobble():  # jelly
    p = Pet()
    def bulb(p):
        p.part(rect(31, 21, 2, 9), "#7fd8e8")
        p.part(ellipse(32, 18, 4, 4), "#fff38a")
    def bubbles(p, b):
        for bx, by, r in ((41, 37, 2.2), (45, 43, 1.4), (19, 58, 1.6)):
            p.part(ellipse(bx, by, r, r), "#e9fdff", outline=False, shade=False, clip=b)
    return finish(p, "wobble", "#ffe0f0", bulb, "#8ee8f2", after=bubbles, face_kw={"eyes": "big", "mouth": "open"})


def cocoa():  # puppy
    p = Pet()
    def ears(p, b):
        p.part(sym(poly([(17, 32), (8, 36), (7, 52), (12, 56), (19, 44)])), "#8a5a3c")
    def patch(p, b):
        p.part(ellipse(23, 47, 6, 5.5), "#b0784f", outline=False, shade=False, clip=b)
        p.part(ellipse(32, 55, 3, 2), INK, outline=False, shade=False)
        ears(p, b)
    def after(p, b):
        patch(p, b)
    name, p = finish(p, "cocoa", "#fff0d1", None, "#d9a77c", after=after,
                     face_kw={"mouth": "open", "cy": 50})
    p.part(ellipse(32, 53.5, 2.5, 1.6), INK, outline=False, shade=False)  # nose
    p.part(CUP, "#fff0d1")
    return name, p


PETS = [mochi, biscuit, bun, fizz, pip, shroomie, twinkle, ember, blossom, waddle,
        ribbit, plum, coral, smol, buzzy, peachy, halo, mango, wobble, cocoa]


# ---------- mix-and-match kit for the bigger roster ----------
import random


def line(x0, y0, x1, y1, w=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return {(round(x0 + (x1 - x0) * t / n) + i, round(y0 + (y1 - y0) * t / n))
            for t in range(n + 1) for i in range(w)}


def ring(cx, cy, rx, ry, t):
    return ellipse(cx, cy, rx, ry) - ellipse(cx, cy, rx - t, ry - t * ry / rx)


def flat(p, m, c, b=None):
    p.part(m, c, outline=False, shade=False, clip=b)


# back layer: drawn before the body
def ears_round(p, b, c, inner=None, x=18, y=32, r=6.5):
    for cx in (x, W - x):
        p.part(ellipse(cx, y, r, r), c)
        if inner:
            flat(p, ellipse(cx, y, r * 0.5, r * 0.5), inner)


def ears_cat(p, b, c, inner=None, tip=None, big=0):
    e = poly([(15 - big, 40), (16 - big, 18 - big * 2), (31, 31)])
    p.part(sym(e), c)
    if tip:
        flat(p, sym({(x, y) for x, y in e if y < 24 - big}), tip)
    if inner:
        flat(p, sym(poly([(18.5 - big, 33), (18.5 - big, 25 - big * 2), (25, 31)])), inner)


def ears_bunny(p, b, c, inner="#ff9fc1"):
    for cx in (24, 40):
        p.part(ellipse(cx, 18, 4.5, 13), c)
        flat(p, ellipse(cx, 19, 2, 9), inner)


def ears_pig(p, b, c):
    p.part(sym(poly([(17, 34), (19, 24), (27, 31)])), c)


def ears_big(p, b, c, inner=None):  # elephant / mouse-style side ears
    p.part(sym(ellipse(12, 42, 9, 11)), c)
    if inner:
        flat(p, sym(ellipse(12, 42, 5.5, 7.5)), inner)


def horns(p, b, c, x=22, h=20):
    p.part(sym(poly([(x - 3, 33), (x - 4, h), (x + 4, 31)])), c)


def horns_ram(p, b, c):
    for cx in (16, 48):
        p.part(ellipse(cx, 38, 7, 7), c)
        flat(p, ring(cx, 38, 4.5, 4.5, 1), tone(c, -0.18))


def antlers(p, b, c):
    m = (line(22, 32, 18, 18, 2) | line(20, 25, 13, 21, 2) | line(19, 20, 22, 14, 2))
    p.part(sym(m), c, shade=False)


def antennae(p, b, c=INK, ball=None, x=25):
    for ax in (x, W - x - 2):
        flat(p, line(ax, 31, ax + (-3 if ax < 32 else 3), 21, 2), c)
    for ax in (x - 3, W - x + 1):
        p.part(ellipse(ax + 1, 20, 3, 3), ball or c, outline=ball is not None)


def wings(p, b, c, kind="bat", c2=None):
    if kind == "bat":
        p.part(sym(poly([(17, 42), (3, 32), (6, 44), (1, 50), (8, 52), (6, 58), (17, 54)])), c)
    elif kind == "angel":
        p.part(sym(poly([(16, 40), (6, 32), (2, 38), (4, 46), (8, 52), (16, 52)])), c)
    elif kind == "bug":
        p.part(sym(ellipse(13, 32, 6.5, 8.5)), c)
    elif kind == "butterfly":
        p.part(sym(ellipse(11, 34, 9, 10)), c)
        p.part(sym(ellipse(12, 52, 6, 6)), c2 or c)
        flat(p, sym(ellipse(10, 33, 3.5, 3.5)), "#ffffff")
    elif kind == "dragon":
        p.part(sym(poly([(15, 44), (2, 34), (5, 46), (14, 52)])), c)


def fins(p, b, c, side=True, top=True):
    if top:
        p.part(poly([(26, 32), (33, 18), (40, 31)]), c)
    if side:
        p.part(sym(poly([(15, 46), (5, 40), (8, 52), (15, 52)])), c)


def rays(p, b, c, n=12, r=25, w=0.22, a0=0.0, a1=2 * math.pi, cy=48, petal=False):
    for i in range(n):
        t = a0 + (a1 - a0) * (i + 0.5) / n
        if petal:
            p.part(ellipse(32 + (r - 4) * math.cos(t), cy + (r - 4) * math.sin(t), 4.5, 4.5), c)
        else:
            pts = [(32 + 14 * math.cos(t - w), cy + 14 * math.sin(t - w)),
                   (32 + r * math.cos(t), cy + r * math.sin(t)),
                   (32 + 14 * math.cos(t + w), cy + 14 * math.sin(t + w))]
            p.part(poly(pts), c)


def tufts(p, b, c):
    p.part(sym(poly([(16, 36), (14, 24), (25, 31)])), c)


def plates(p, b, c, n=4):
    for i in range(n):
        t = math.pi * (1.15 + 0.7 * (i + 0.5) / n)
        x, y = 32 + 18 * math.cos(t), 48 + 18 * math.sin(t)
        p.part(poly([(x - 3, y + 2), (x + 3 * math.cos(t), y + 7 * math.sin(t)), (x + 3, y + 2)]), c)


def claws(p, b, c):
    for side in (0, 1):
        m = ellipse(9, 40, 6, 7) - poly([(9, 40), (2, 31), (12, 31)])
        p.part(mirror(m) if side else m, c)


def mane(p, b, c, n=12, r=19):
    for i in range(n):
        t = 2 * math.pi * i / n
        p.part(ellipse(32 + r * math.cos(t), 47 + r * math.sin(t), 6, 6), c)


def puffs_top(p, b, c, y=31):
    for cx, cy, r in ((22, y + 2, 6), (32, y - 2, 7), (42, y + 2, 6)):
        p.part(ellipse(cx, cy, r, r * 0.9), c)


def stem(p, b, c="#7a5a3a", leaf="#6cc46a", y=25, flip=False):
    p.part(rect(31, y, 2, 31 - y), c, shade=False)
    if leaf:
        lf = poly([(33, 27), (39, 20), (47, 20), (42, 27)])
        p.part(mirror(lf) if flip else lf, leaf)


def sprout(p, b, c="#47b86b"):
    p.part(rect(31, 22, 2, 9), c, shade=False)
    p.part(ellipse(26, 20, 5, 3), c)
    p.part(ellipse(38, 20, 5, 3), c)


def flower(p, b, c, center="#ffe05a", y=18, n=5):
    p.part(rect(31, y + 4, 2, 31 - y - 4), "#47b86b", shade=False)
    for a in range(n):
        t = a * 2 * math.pi / n - math.pi / 2
        p.part(ellipse(32 + 5.5 * math.cos(t), y + 5.5 * math.sin(t), 3.8, 3.8), c)
    p.part(ellipse(32, y, 2.8, 2.8), center, shade=False)


def tulip(p, b, c):
    p.part(rect(31, 22, 2, 9), "#47b86b", shade=False)
    p.part(poly([(25, 12), (28, 16), (32, 11), (36, 16), (39, 12), (38, 21), (32, 24), (26, 21)]), c)


def bulb(p, b, c="#fff38a", stalk="#7fd8e8"):
    p.part(rect(31, 21, 2, 9), stalk)
    p.part(ellipse(32, 18, 4, 4), c)


def flame(p, b, c="#ff8a3d", inner="#ffd04a"):
    p.part(poly([(18, 38), (19, 24), (24, 30), (27, 16), (32, 26), (37, 13), (40, 28), (45, 22), (46, 38)]), c)
    flat(p, poly([(25, 36), (28, 24), (32, 31), (37, 21), (39, 36)]), inner)


def crystals(p, b, c):
    for x, h, w in ((24, 18, 3), (32, 12, 4), (40, 18, 3)):
        p.part(poly([(x - w, 33), (x - w, h + 4), (x, h), (x + w, h + 4), (x + w, 33)]), c)


def tail_curl(p, b, c):
    p.part(ring(52, 34, 8, 8, 3) - rect(44, 34, 8, 10), c)


# deco layer: drawn after the body (clip to the body with b)
def belly(p, b, c, cy=56, rx=12, ry=9):
    flat(p, ellipse(32, cy, rx, ry), c, b)


def muzzle(p, b, c, cy=55, rx=7, ry=4.5):
    flat(p, ellipse(32, cy, rx, ry), c, b)


def cheeks(p, b, c):
    flat(p, sym(ellipse(22, 59, 10, 7)), c, b)


def snout(p, b, c):
    p.part(ellipse(32, 55, 5.5, 3.5), c)
    for x in (30, 34):
        p.put(x, 55, INK)
        p.put(x - (1 if x < 32 else 0), 55, INK)


def nose(p, b, c=INK, y=53.5):
    flat(p, ellipse(32, y, 2.5, 1.6), c)


def spots(p, b, c, n=6, seed=1, r=(2, 3.5), top=False):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(15, 49), rnd.uniform(31, 44 if top else 62)
        if 18 < x < 46 and 45 < y < 58:  # keep the face clear
            y = rnd.uniform(31, 40)
        rr = rnd.uniform(*r)
        flat(p, ellipse(x, y, rr, rr * 0.9), c, b)


def stripes(p, b, c, rows=(34, 60), h=3):
    for y in rows:
        flat(p, rect(0, y, W, h), c, b)


def side_stripes(p, b, c):
    for y in (40, 46, 52):
        flat(p, rect(12, y, 6, 2) | rect(46, y, 6, 2), c, b)
    flat(p, rect(30, 32, 4, 2) | rect(30, 36, 4, 2), c, b)


def eye_patches(p, b, c):
    flat(p, ellipse(22.5, 50, 5.5, 5.5) | ellipse(41.5, 50, 5.5, 5.5), c, b)


def eye_patch_one(p, b, c):
    flat(p, ellipse(23, 47, 6, 5.5), c, b)


def bandit_mask(p, b, c):
    flat(p, ellipse(32, 50, 17, 5) - ellipse(32, 52, 3, 3), c, b)


def face_patch(p, b, c):
    flat(p, ellipse(26, 50, 7, 7) | ellipse(38, 50, 7, 7) | ellipse(32, 55, 9, 5), c, b)


def whiskers(p, b, c=INK):
    for x, y in ((15, 52), (15, 55), (46, 52), (46, 55)):
        flat(p, rect(x, y, 3, 1), c)


def freckles(p, b, c):
    for x, y in ((18, 54), (20, 55), (22, 54), (41, 54), (43, 55), (45, 54)):
        p.put(x, y, c)


def mark(p, b, c, kind="heart", y=38):
    art = {"heart": [".#.#.", "#####", ".###.", "..#.."],
           "star": ["..#..", "#####", ".###.", ".#.#."],
           "gem": [".###.", "#####", ".###.", "..#.."],
           "moon": [".##..", "##...", "##...", ".##.."]}[kind]
    p.stamp(30, y, art, {"#": c})


def seeds(p, b, c="#fff3a8"):
    for i, (x, y) in enumerate(((19, 38), (26, 34), (38, 34), (45, 38), (17, 45), (47, 45), (24, 41), (40, 41), (32, 38))):
        p.put(x, y, c)
        p.put(x, y + 1, tone(c, -0.15))


def creases(p, b, c):
    for x in (22, 32, 42):
        flat(p, rect(x, 31, 1, 10), c, b)


def pleats(p, b, c):
    for x in (26, 30, 34, 38):
        flat(p, line(x, 31, 32 if x < 32 else 32, 36), c, b)


def sprinkles(p, b, cols=("#ff6f91", "#5ec8ff", "#ffe066", "#7be08b", "#c39bff")):
    rnd = random.Random(7)
    for i in range(14):
        x, y = rnd.randint(16, 47), rnd.randint(24, 34)
        c = cols[i % len(cols)]
        p.put(x, y, c)
        p.put(x + 1, y, c)


def spines(p, b, c=INK):
    for x, y in ((17, 40), (22, 34), (42, 34), (47, 40), (15, 48), (49, 48), (32, 32), (27, 38), (37, 38)):
        p.put(x, y, c)
        p.put(x, y - 1, "#fff6c8")


def drip(p, b, c):
    flat(p, {(x, y) for x, y in ellipse(32, 30, 22, 12) if y <= 34} |
         ellipse(21, 35, 2.5, 3) | ellipse(30, 37, 2.5, 4) | ellipse(42, 36, 2.5, 3), c, b)


def bow(p, b, c="#ff6b9a", x=22, y=30):
    p.part(poly([(x - 7, y - 4), (x - 7, y + 4), (x, y)]) | poly([(x + 7, y - 4), (x + 7, y + 4), (x, y)]), c)
    p.part(ellipse(x, y, 2.2, 2.2), tone(c, -0.12), shade=False)


def crown(p, b, c="#ffd23f", gem="#ff5a8a"):
    p.part(poly([(23, 32), (23, 21), (27.5, 26), (32, 18), (36.5, 26), (41, 21), (41, 32)]), c)
    p.put(32, 28, gem); p.put(32, 29, gem); p.put(26, 29, "#5ec8ff"); p.put(38, 29, "#5ec8ff")


def party_hat(p, b, c, c2="#ffffff"):
    h = poly([(24, 33), (40, 33), (32, 12)])
    p.part(h, c)
    for y in (18, 24, 30):
        flat(p, {(x, yy) for x, yy in h if y <= yy < y + 2}, c2)
    p.part(ellipse(32, 11, 2.6, 2.6), c2, shade=False)


def top_hat(p, b, c, band="#ff5a6e"):
    p.part(rect(25, 14, 14, 16) | rect(21, 28, 22, 3), c)
    flat(p, rect(25, 25, 14, 3), band)


def beanie(p, b, c, c2="#ffffff"):
    cap = {(x, y) for x, y in ellipse(32, 36, 18, 12) if y <= 32}
    p.part(cap, c)
    flat(p, rect(14, 30, 36, 3), tone(c, -0.12), cap | rect(14, 30, 36, 3))
    p.part(ellipse(32, 23, 4, 4), c2)


def wizard_hat(p, b, c, star="#ffe066"):
    p.part(poly([(21, 32), (43, 32), (37, 11), (28, 7), (32, 13)]), c)
    p.part(ellipse(32, 32, 19, 2.5), c, shade=False)
    p.stamp(30, 20, ["..#..", "#####", ".#.#."], {"#": star})


def witch_hat(p, b, c, band="#a6ff5a"):
    p.part(ellipse(32, 31, 19, 3) | poly([(24, 31), (40, 31), (38, 10)]), c)
    flat(p, rect(25, 26, 14, 2), band)


def chef_hat(p, b, c="#ffffff"):
    p.part(rect(24, 24, 16, 8), c)
    for cx, r in ((25, 6), (32, 7), (39, 6)):
        p.part(ellipse(cx, 20, r, r * 0.85), c)
    p.part(rect(24, 24, 16, 8), c)


def cap(p, b, c, dots="#fff6ee", y=42, ry=17, n=5, seed=3):
    m = {(x, yy) for x, yy in ellipse(32, y, 26, ry) if yy <= y + 1}
    p.part(m, c)
    rnd = random.Random(seed)
    for sx, sy, r in ((20, 34, 3.5), (32, 29, 3), (44, 34, 3.5), (27, 38, 2), (38, 38, 2))[:n]:
        flat(p, ellipse(sx, sy + y - 42, r, r * 0.9), dots, m)


def acorn_cap(p, b, c):
    m = {(x, y) for x, y in ellipse(32, 39, 21, 12) if y <= 38}
    p.part(m, c)
    for x in range(14, 50, 4):
        flat(p, line(x, 28, x + 4, 38), tone(c, -0.12), m)
    p.part(rect(31, 24, 2, 4), "#6b4a2b", shade=False)


def frosting(p, b, c, cherry=True):
    m = {(x, y) for x, y in ellipse(32, 38, 21, 12) if y <= 35} | ellipse(18, 36, 3, 3) | ellipse(27, 37, 3, 4) | \
        ellipse(37, 36.5, 3, 3.5) | ellipse(46, 36, 3, 3)
    p.part(m, c)
    if cherry:
        p.part(ellipse(32, 23, 3.5, 3.5), "#ff3d5a")
        flat(p, line(33, 20, 36, 15), "#4a7a3a")


def calyx(p, b, c="#4fbf5a"):
    p.part(poly([(20, 31), (24, 26), (27, 29), (32, 23), (37, 29), (40, 26), (44, 31), (32, 34)]), c)
    p.part(rect(31, 19, 2, 6), c, shade=False)


def crescent(p, b, c="#ffe066"):
    p.part(ellipse(32, 20, 7, 7) - ellipse(36, 17, 6, 6), c)


def raindrop(p, b, c="#6cc8ff"):
    p.part(ellipse(32, 21, 4, 4) | poly([(28.5, 20), (35.5, 20), (32, 12)]), c)


def spout(p, b, c="#8fdcff"):
    for x0, x1 in ((31, 25), (32, 32), (33, 39)):
        p.part(line(32, 30, x1, 20, 2) | ellipse(x1 + 0.5, 18, 2.5, 2.5), c, shade=False)


def halo_ring(p, b, c="#ffe066"):
    p.part(ellipse(32, 24, 10, 3.5) - ellipse(32, 24, 6.5, 1.6), c)


def tuft(p, b, c):
    p.part(ellipse(30, 26, 2, 5) | ellipse(34.5, 25, 2, 6), c)


def flower_clip(p, b, c, x=42, y=32):
    for a in range(5):
        t = a * 2 * math.pi / 5
        p.part(ellipse(x + 3 * math.cos(t), y + 3 * math.sin(t), 2.4, 2.4), c)
    flat(p, ellipse(x, y, 1.6, 1.6), "#ffe05a")


def pumpkin_stem(p, b, c="#6b8a3a"):
    p.part(poly([(30, 31), (30, 24), (35, 21), (36, 24), (34, 25), (34, 31)]), c)


def lop_ears(p, b, c):
    p.part(sym(poly([(17, 32), (10, 36), (9, 58), (14, 61), (19, 46)])), c)


def floppy_ears(p, b, c):
    p.part(sym(poly([(17, 32), (8, 36), (7, 52), (12, 56), (19, 44)])), c)


def flippers(p, b, c):
    p.part(sym(ellipse(13, 56, 3, 5)), c)


def beak(p, b, c="#ff9a3c", wide=False):
    if wide:
        p.part(ellipse(32, 55, 6, 2.6), c)
    else:
        p.part(poly([(28.5, 53), (35.5, 53), (32, 57.5)]), c)


def gem(p, b, c):
    p.part(poly([(32, 33), (36, 37), (32, 42), (28, 37)]), c)
    p.put(31, 36, "#ffffff")


def bolts(p, b, c="#c7cfdb"):
    for x in (13, 51):
        p.part(rect(x - 2, 45, 4, 5), c)


def visor_antenna(p, b, c="#ff5a6e"):
    p.part(rect(31, 22, 2, 9), "#8a95a8", shade=False)
    p.part(ellipse(32, 20, 3, 3), c)


def scarf(p, b, c):  # sits just above the shell rim
    p.part({(x, y) for x, y in rect(14, 59, 36, 4) if (x, y) in dilate(b, 1)}, c)


# over layer: drawn after the face
def pirate_patch(p, b, c=INK):
    flat(p, line(16, 41, 47, 46) | line(16, 42, 47, 47), c)
    flat(p, ellipse(41.5, 50, 4.5, 4.5), c)
    p.put(40, 48, "#3a4566")


def glasses(p, b, c=INK):
    for cx in (22.5, 41.5):
        flat(p, ring(cx, 50, 5.5, 5.5, 1), c)
    flat(p, rect(28, 49, 8, 1), c)


def sweat(p, b, c="#9fe0ff"):
    p.stamp(46, 41, [".#.", "###", "###", ".#."], {"#": c})


def zzz(p, b, c="#c39bff"):
    p.stamp(46, 31, ["####", "..#.", ".#..", "####"], {"#": c})
    p.stamp(52, 25, ["###", ".#.", "###"], {"#": c})


KIT = {f.__name__: f for f in (
    ears_round, ears_cat, ears_bunny, ears_pig, ears_big, horns, horns_ram, antlers, antennae, wings, fins, rays,
    tufts, plates, claws, mane, puffs_top, stem, sprout, flower, tulip, bulb, flame, crystals, tail_curl,
    belly, muzzle, cheeks, snout, nose, spots, stripes, side_stripes, eye_patches, eye_patch_one, bandit_mask,
    face_patch, whiskers, freckles, mark, seeds, creases, pleats, sprinkles, spines, drip, bow, crown, party_hat,
    top_hat, beanie, wizard_hat, witch_hat, chef_hat, cap, acorn_cap, frosting, calyx, crescent, raindrop, spout,
    halo_ring, tuft, flower_clip, pumpkin_stem, lop_ears, floppy_ears, flippers, beak, gem, bolts, visor_antenna,
    scarf, pirate_patch, glasses, sweat, zzz)}


def run(p, b, items):
    for item in items:
        name, kw = (item, {}) if isinstance(item, str) else (item[0], item[1] if len(item) > 1 else {})
        if isinstance(kw, str):
            kw = {"c": kw}
        KIT[name](p, b, **kw)


def build(spec):
    name, body, cup = spec[0], spec[1], spec[2]
    opts = spec[3] if len(spec) > 3 else {}
    p = Pet()
    shape = opts.get("shape", (32, 48, 18.5, 18))
    return finish(
        p, name, cup,
        before=lambda p: run(p, None, opts.get("back", [])),
        body_color=body, body=ellipse(*shape),
        after=lambda p, b: run(p, b, opts.get("deco", [])),
        over=lambda p, b: run(p, b, opts.get("over", [])),
        face_kw=opts.get("face"), gloss_at=opts.get("gloss", (20, 37)),
    )


# name, body, cup, {back, deco, over, face, shape, gloss}
ROSTER = [
    # --- critters ---
    ("bamboo", "#f7f7fb", "#cdeccf", {"back": [("ears_round", {"c": "#4a4658"})], "deco": [("eye_patches", "#4a4658")]}),
    ("gumtree", "#b8bcc9", "#d9f1d0", {"back": [("ears_round", {"c": "#b8bcc9", "inner": "#f1e6ee", "x": 15, "y": 36, "r": 8})],
                                      "deco": [("muzzle", {"c": "#dcdfe7", "cy": 57}), ("nose", {"y": 53})], "face": {"mouth": None}}),
    ("squeak", "#cfd3dd", "#ffe4b8", {"back": [("ears_round", {"c": "#cfd3dd", "inner": "#ffb3c9", "x": 17, "y": 30, "r": 8.5})],
                                     "deco": ["whiskers"], "face": {"mouth": "tiny"}}),
    ("nibbles", "#f2c48d", "#e6dcff", {"back": [("ears_round", {"c": "#f2c48d", "inner": "#ffc7d3", "x": 20, "y": 31, "r": 4.5})],
                                      "deco": [("cheeks", "#fff4e6"), ("mark", {"c": "#ffffff", "kind": "gem", "y": 33})],
                                      "face": {"mouth": "cat"}}),
    ("fluff", "#fffaf3", "#c9ecff", {"back": [("floppy_ears", "#ffd8c6")], "deco": [("puffs_top", "#ffffff")],
                                    "face": {"eyes": "happy"}}),
    ("curly", "#fff3dd", "#d6f2c4", {"back": [("horns_ram", "#e2b98a")], "deco": [("puffs_top", {"c": "#fffaf0", "y": 32})]}),
    ("fawn", "#d99a62", "#e3f5d6", {"back": [("antlers", "#8a5a3c"), ("ears_cat", {"c": "#d99a62", "inner": "#ffd9c4"})],
                                   "deco": [("spots", {"c": "#fff1df", "n": 5, "seed": 4, "r": (1.2, 1.8), "top": True})]}),
    ("peanut", "#a9c0e6", "#ffe0ec", {"back": [("ears_big", {"c": "#a9c0e6", "inner": "#ffc7dd"})],
                                     "deco": [("muzzle", {"c": "#c2d4f0", "cy": 57, "rx": 3, "ry": 5})], "face": {"mouth": None}}),
    ("hoot", "#b98a63", "#fff0c8", {"back": [("tufts", "#b98a63")], "deco": [("belly", {"c": "#f2dcc0", "cy": 58})],
                                   "face": {"eyes": "big", "mouth": None},
                                   "over": [("beak", {"c": "#ffb33b"})]}),
    ("oink", "#ffc4d3", "#c9f0e0", {"back": [("ears_pig", "#ffc4d3")], "deco": [("snout", "#ff9fb8")], "face": {"mouth": None}}),
    ("moo", "#fbfbfd", "#d6f5c4", {"back": [("horns", {"c": "#fff0c2", "x": 19, "h": 24}), ("ears_round", {"c": "#4a4658", "x": 14, "y": 38, "r": 4.5})],
                                  "deco": [("spots", {"c": "#4a4658", "n": 5, "seed": 2, "r": (3, 4.5)}),
                                           ("muzzle", {"c": "#ffc4d3", "cy": 57, "rx": 8, "ry": 4})]}),
    ("roary", "#ffcf6b", "#ffe0c8", {"back": [("mane", "#e8873a")], "deco": [("muzzle", {"c": "#fff2d6"})], "face": {"mouth": "cat"}}),
    ("stripes", "#ff9f4a", "#d9f4ff", {"back": [("ears_cat", {"c": "#ff9f4a", "inner": "#ffe0c4"})],
                                      "deco": [("side_stripes", "#5a3427"), ("muzzle", {"c": "#fff3e3"})], "face": {"mouth": "cat"}}),
    ("bandit", "#b3b7c4", "#ffe6c2", {"back": [("ears_cat", {"c": "#b3b7c4", "inner": "#f1e6ee"})],
                                     "deco": [("bandit_mask", "#4a4658"), ("muzzle", {"c": "#f1f2f6", "cy": 56})]}),
    ("maple", "#e8693c", "#ffe9c8", {"back": [("ears_cat", {"c": "#e8693c", "inner": "#ffffff", "tip": "#5a3427"})],
                                    "deco": [("face_patch", "#fff1e3")], "face": {"mouth": "tiny"}}),
    ("splash", "#c9d3e3", "#bdf2ee", {"deco": ["whiskers", ("muzzle", {"c": "#e3e9f2", "cy": 56})],
                                     "face": {"eyes": "big", "mouth": "tiny"}}),
    ("paddle", "#a8754f", "#c9ecff", {"back": [("ears_round", {"c": "#a8754f", "x": 17, "y": 36, "r": 4})],
                                     "deco": [("muzzle", {"c": "#e8cba8", "cy": 56, "rx": 9}), ("nose", {"y": 53})]}),
    ("spike", "#e8c9a0", "#d6f2c4", {"back": [("rays", {"c": "#8a6248", "n": 9, "r": 27, "a0": math.pi * 0.95, "a1": math.pi * 2.05})],
                                    "deco": [("nose", {"y": 53})], "face": {"mouth": None}}),
    ("banana", "#a8754f", "#fff2b8", {"back": [("ears_round", {"c": "#e8cba8", "x": 13, "y": 46, "r": 5})],
                                     "deco": [("face_patch", "#f2dcc0")]}),
    ("snooze", "#c9b6a0", "#d6f2c4", {"deco": [("eye_patches", "#8a7462")], "over": ["zzz"],
                                     "face": {"eyes": "sleepy", "mouth": "o"}}),
    # --- spooky & space ---
    ("imp", "#ff6b6b", "#ffe0c2", {"back": [("horns", {"c": "#5a3427"}), ("wings", {"c": "#c43b4a", "kind": "bat"})],
                                  "face": {"mouth": "fang"}}),
    ("zorp", "#9ef07a", "#e6dcff", {"back": [("antennae", {"c": "#58b84a", "ball": "#ff8fd0"})],
                                   "face": {"eyes": "big", "gap": 8, "mouth": "o"}}),
    ("bleep", "#c7cfdb", "#ffe6c2", {"back": ["visor_antenna", "bolts"], "deco": [("mark", {"c": "#5ec8ff", "kind": "heart"})],
                                    "face": {"mouth": "smile", "blush": "#ff9fb8"}}),
    ("boo", "#ffffff", "#e3e9ff", {"face": {"eyes": "big", "mouth": "o"}, "over": [("sweat", "#c7e6ff")]}),
    ("gourd", "#ffa04a", "#d6f2c4", {"back": ["pumpkin_stem"], "deco": [("creases", "#e07a2e")], "face": {"eyes": "happy", "mouth": "open"}}),
    ("luna", "#9fa8e8", "#d6dcff", {"back": [("crescent", "#ffe066")], "deco": [("mark", {"c": "#ffe066", "kind": "star"})],
                                   "face": {"eyes": "sleepy"}}),
    ("sunny", "#ffe066", "#ffd2a6", {"back": [("rays", {"c": "#ffb33b", "n": 12})], "face": {"eyes": "happy", "mouth": "open"}}),
    ("starla", "#fff3a8", "#d6dcff", {"back": [("rays", {"c": "#ffd23f", "n": 5, "r": 29, "w": 0.45, "a0": -math.pi / 2 - math.pi / 5, "a1": 2 * math.pi - math.pi / 2 - math.pi / 5})],
                                     "face": {"eyes": "wink"}}),
    ("drizzle", "#d9e2ee", "#c9ecff", {"back": [("puffs_top", "#d9e2ee"), ("raindrop", "#6cc8ff")],
                                      "face": {"eyes": "sleepy", "mouth": "tiny"}}),
    ("prism", "#fff8ff", "#e8dcff", {"back": [("rays", {"c": "#ff8fc4", "n": 3, "r": 26, "a0": math.pi, "a1": math.pi * 1.33, "petal": True}),
                                              ("rays", {"c": "#ffd75e", "n": 3, "r": 26, "a0": math.pi * 1.33, "a1": math.pi * 1.67, "petal": True}),
                                              ("rays", {"c": "#8fd8ff", "n": 3, "r": 26, "a0": math.pi * 1.67, "a1": math.pi * 2, "petal": True})]}),
    # --- snacks ---
    ("berry", "#ff5a6e", "#ffe3ee", {"back": ["calyx"], "deco": ["seeds"]}),
    ("cherry", "#e8344e", "#fff0d6", {"back": [("stem", {"c": "#4a7a3a", "leaf": "#6cc46a"})], "face": {"eyes": "happy"}}),
    ("crisp", "#a6e05a", "#ffe0e6", {"back": [("stem", {"flip": True})], "face": {"mouth": "open"}}),
    ("zest", "#fff06a", "#d6f2c4", {"back": [("stem", {"c": "#6b8a3a", "leaf": "#7bd06a", "y": 27})], "shape": (32, 48, 20, 17),
                                   "face": {"eyes": "wink", "mouth": "tongue"}}),
    ("bloop", "#7f9cff", "#e3e9ff", {"back": [("calyx", "#4a5fc4")], "face": {"mouth": "o"}}),
    ("sprinkles", "#ffd9b0", "#ffd2ea", {"deco": [("frosting", "#ff9fc8"), "sprinkles"], "face": {"cy": 51}}),
    ("glaze", "#e8b07a", "#d9f4ff", {"deco": [("drip", "#ff8fc4"), "sprinkles"], "face": {"cy": 51, "mouth": "tongue"}}),
    ("flurry", "#ffffff", "#c9ecff", {"deco": [("beanie", {"c": "#ff6b8a"}), ("scarf", "#5ec8ff")], "face": {"mouth": "open"}}),
    ("nutmeg", "#e0a46a", "#d6f2c4", {"deco": [("acorn_cap", "#8a5a3c")], "face": {"cy": 51}}),
    ("flan", "#ffd56b", "#fff0d6", {"deco": [("drip", "#b8642e"), ("frosting", {"c": "#fffaf3", "cherry": True})],
                                   "face": {"cy": 51}}),
    ("scoop", "#c8f0d8", "#ffd9b0", {"deco": [("drip", "#ff9fc8"), ("spots", {"c": "#7a4a32", "n": 6, "seed": 9, "r": (0.8, 1.2), "top": True})],
                                    "face": {"mouth": "tongue"}}),
    ("boba", "#d9b38c", "#ffe3ee", {"deco": [("spots", {"c": "#4a3428", "n": 7, "seed": 5, "r": (1.6, 2.2)})], "face": {"mouth": "open"}}),
    ("bao", "#fffaf3", "#ffe0c8", {"deco": ["chef_hat", ("pleats", "#ead9c4")], "face": {"mouth": "open"}}),
    ("soda", "#9fe8ff", "#ffe0ec", {"deco": [("spots", {"c": "#e9fdff", "n": 7, "seed": 11, "r": (0.8, 2)})],
                                   "back": [("bulb", {"c": "#ff6b8a", "stalk": "#ffffff"})], "face": {"mouth": "tongue"}}),
    # --- plants & bugs ---
    ("prickles", "#7bd06a", "#ffc8a6", {"back": [("flower", {"c": "#ff8fc4", "y": 22})], "deco": ["spines"],
                                       "shape": (32, 48, 17, 19)}),
    ("rosette", "#9fe0c0", "#ffe0ec", {"back": [("rays", {"c": "#6cc8a0", "n": 7, "r": 26, "a0": math.pi, "a1": 2 * math.pi, "petal": True})],
                                      "face": {"eyes": "happy"}}),
    ("sunflower", "#c9894a", "#d6f2c4", {"back": [("rays", {"c": "#ffd23f", "n": 14, "r": 27, "petal": True})],
                                        "deco": [("spots", {"c": "#a8693a", "n": 6, "seed": 6, "r": (0.8, 1.2)})]}),
    ("tulip", "#ffe0e6", "#d6f2c4", {"back": [("tulip", "#ff5a6e")], "face": {"eyes": "wink"}}),
    ("sakura", "#fff0f5", "#d9f4ff", {"back": [("flower", {"c": "#ffb3d1", "center": "#ff7aa0"})],
                                     "deco": [("flower_clip", {"c": "#ffb3d1", "x": 20, "y": 34})]}),
    ("clover", "#a6e88a", "#fff3c4", {"back": ["sprout"], "deco": [("mark", {"c": "#ffffff", "kind": "heart"})]}),
    ("dotty", "#ff4f5e", "#d6f2c4", {"back": [("antennae", {})], "deco": [("spots", {"c": "#3a2a3d", "n": 6, "seed": 8, "r": (2, 3)})],
                                    "face": {"blush": "#ffb3c1"}}),
    ("flutter", "#ffe9a8", "#e6dcff", {"back": [("wings", {"c": "#c39bff", "kind": "butterfly", "c2": "#ff9ad5"}), ("antennae", {})]}),
    ("fuzz", "#f2e6d3", "#d9f4ff", {"back": [("wings", {"c": "#d6c6ae", "kind": "bug"}), ("antennae", {"c": "#b8a48a", "ball": "#fff6e3"})],
                                   "deco": [("puffs_top", "#fffaf0")], "face": {"eyes": "sleepy"}}),
    ("inchy", "#a6e05a", "#ffe0c8", {"back": [("antennae", {"c": "#4a7a3a", "ball": "#ffd23f"})],
                                    "deco": [("stripes", {"c": "#8cc84a", "rows": (38, 59), "h": 2})], "face": {"mouth": "open"}}),
    ("honeybun", "#ffc93b", "#fff3c4", {"back": [("wings", {"c": "#e6f7ff", "kind": "bug"}), ("antennae", {})],
                                       "deco": [("stripes", {"c": "#3a2a3d", "rows": (35, 59)}), "bow"],
                                       "face": {"eyes": "wink"}, "gloss": (20, 39)}),
    # --- ocean ---
    ("pinch", "#ff7a5c", "#c9ecff", {"back": [("claws", "#ff7a5c"), ("antennae", {"c": "#e8553a", "ball": "#ffffff", "x": 26})],
                                    "face": {"mouth": "open"}}),
    ("spout", "#7fb8ff", "#e3f5ff", {"back": ["spout"], "deco": [("belly", {"c": "#e3f0ff", "cy": 60, "rx": 14, "ry": 6})],
                                    "shape": (32, 49, 20, 17)}),
    ("chomp", "#a9b8cc", "#c9ecff", {"back": [("fins", {"c": "#8a9cb8"})], "deco": [("belly", {"c": "#f1f4f8", "cy": 59, "rx": 13, "ry": 7})],
                                    "face": {"mouth": "fang"}}),
    ("puffle", "#ffe38a", "#bdf2ee", {"back": [("rays", {"c": "#e8b83a", "n": 14, "r": 25, "w": 0.15})],
                                     "face": {"eyes": "big", "mouth": "o"}}),
    ("nemo", "#ff9a3d", "#c9ecff", {"back": [("fins", {"c": "#ffffff"})], "deco": [("stripes", {"c": "#ffffff", "rows": (38,), "h": 3})],
                                   "face": {"eyes": "big", "gap": 8}}),
    # --- dinos & dragons & myth ---
    ("stego", "#8ce0a8", "#fff3c4", {"back": [("plates", "#ff9a7a")], "deco": [("belly", {"c": "#d6f7c7", "cy": 60, "rx": 11, "ry": 7})]}),
    ("frosty", "#bfe6ff", "#e3e9ff", {"back": [("horns", {"c": "#ffffff"}), ("wings", {"c": "#8fc8f0", "kind": "dragon"})],
                                     "deco": [("belly", {"c": "#e9f6ff", "cy": 60, "rx": 11, "ry": 7})], "face": {"eyes": "wink"}}),
    ("rosie", "#ffb3d1", "#fff3c4", {"back": [("horns", {"c": "#fff3c4"}), ("wings", {"c": "#ff8fc0", "kind": "dragon"})],
                                    "deco": [("belly", {"c": "#ffe3ee", "cy": 60, "rx": 11, "ry": 7})], "face": {"mouth": "open"}}),
    ("blaze", "#ffb36b", "#ffe0c2", {"back": [("flame", {"c": "#ff5a3d", "inner": "#ffb33b"}), ("wings", {"c": "#ff7a3d", "kind": "angel"})],
                                    "face": {"eyes": "big"}, "over": [("beak", {"c": "#ffd23f"})]}),
    ("yeti", "#ffffff", "#c9ecff", {"back": [("puffs_top", "#ffffff")], "deco": [("face_patch", "#a6c8f0")], "face": {"mouth": "fang"}}),
    ("kitsune", "#fff6ee", "#ffd2ea", {"back": [("ears_cat", {"c": "#fff6ee", "inner": "#ffb3d1", "tip": "#ff5a6e", "big": 1})],
                                      "deco": [("mark", {"c": "#ff5a6e", "kind": "moon", "y": 36})], "face": {"eyes": "happy", "mouth": "cat"}}),
    ("gemmy", "#c4b5ff", "#e3e9ff", {"back": [("crystals", "#8ff0e8")], "deco": [("gem", "#ff8fd0")]}),
    ("quartz", "#ffd0e8", "#e6dcff", {"back": [("crystals", "#c39bff")], "face": {"eyes": "wink"}}),
    # --- pets (dogs & cats & birds & bunnies) ---
    ("toffee", "#c99a6e", "#ffe0ec", {"back": [("lop_ears", "#a8754f")], "deco": [("muzzle", {"c": "#f2dcc3"})],
                                     "face": {"mouth": "tiny"}}),
    ("midnight", "#4a4462", "#e6dcff", {"back": [("ears_cat", {"c": "#4a4462", "inner": "#ff9fc1"})],
                                       "deco": [("whiskers", {"c": "#c4bede"})], "face": {"eyes": "big", "mouth": "cat"}}),
    ("snowball", "#ffffff", "#d9f4ff", {"back": [("ears_cat", {"c": "#ffffff", "inner": "#ffc7d9"})],
                                       "deco": [("bow", {"c": "#ff6b9a", "x": 42, "y": 32})], "face": {"mouth": "cat"}}),
    ("patches", "#fffaf3", "#d6f2c4", {"back": [("ears_cat", {"c": "#ff9f4a", "inner": "#ffd8c4"})],
                                      "deco": [("spots", {"c": "#ff9f4a", "n": 3, "seed": 14, "r": (3.5, 5)}),
                                               ("spots", {"c": "#4a4658", "n": 3, "seed": 15, "r": (2.5, 3.5)})],
                                      "face": {"mouth": "cat"}}),
    ("goldie", "#ffc96b", "#e3f0ff", {"back": [("floppy_ears", "#e8a04a")], "deco": [("nose", {})], "face": {"mouth": "tongue"}}),
    ("domino", "#ffffff", "#ffe0e6", {"back": [("floppy_ears", "#4a4658")], "deco": [("spots", {"c": "#4a4658", "n": 7, "seed": 16, "r": (1.2, 2)}), "nose"],
                                     "face": {"mouth": "open"}}),
    ("blizzard", "#8a95a8", "#d9f4ff", {"back": [("ears_cat", {"c": "#8a95a8", "inner": "#f1f2f6"})],
                                       "deco": [("face_patch", "#f1f4f8"), ("mark", {"c": "#f1f4f8", "kind": "gem", "y": 33}), "nose"]}),
    ("waffles", "#ffad5c", "#fff3c4", {"back": [("ears_cat", {"c": "#ffad5c", "inner": "#ffe0c4", "big": 2})],
                                      "deco": [("cheeks", "#fff6ee"), "nose"], "face": {"mouth": "tongue"}}),
    ("frostbite", "#f5fbff", "#c9ecff", {"back": [("ears_cat", {"c": "#f5fbff", "inner": "#c9e6ff"})], "face": {"mouth": "cat", "blush": "#ffb3d1"}}),
    ("sandy", "#f2d2a0", "#ffe0e6", {"back": [("ears_cat", {"c": "#f2d2a0", "inner": "#ffd0c4", "big": 4})],
                                    "deco": [("cheeks", "#fff6e6")], "face": {"mouth": "cat"}}),
    ("howl", "#9aa2b4", "#e6dcff", {"back": [("ears_cat", {"c": "#9aa2b4", "inner": "#5a6278"})],
                                   "deco": [("muzzle", {"c": "#e3e6ee", "cy": 56, "rx": 8, "ry": 5}), ("nose", {"y": 53})],
                                   "face": {"mouth": None}}),
    ("polar", "#fbfdff", "#bdf2ee", {"back": [("ears_round", {"c": "#fbfdff", "inner": "#e3e9f2"})], "deco": [("nose", {"y": 54})],
                                    "face": {"mouth": None, "eyes": "happy"}}),
    ("grizzly", "#8a5a3c", "#fff3c4", {"back": [("ears_round", {"c": "#8a5a3c", "inner": "#c99a6e"})],
                                      "deco": [("muzzle", {"c": "#c99a6e"}), ("mark", {"c": "#ffd23f", "kind": "heart", "y": 34})],
                                      "face": {"mouth": "tiny"}}),
    ("puddle", "#ffe066", "#c9ecff", {"back": [("tuft", "#ffd23f")], "face": {"mouth": None}, "over": [("beak", {"c": "#ff9a3c", "wide": True})]}),
    ("flamingo", "#ffa6c8", "#c9f0e0", {"back": [("tuft", "#ff7aa8")], "face": {"mouth": None},
                                       "over": [("beak", {"c": "#3a2a3d"})]}),
    ("kiwi", "#7be08b", "#fff0c8", {"back": [("tuft", "#ff6b6b")], "deco": [("cheeks", "#ffe066")], "face": {"mouth": None},
                                   "over": [("beak", {"c": "#4a4658"})]}),
    ("chirp", "#7fb8ff", "#ffe6c2", {"back": [("tufts", "#7fb8ff")], "deco": [("belly", {"c": "#ffd8b0", "cy": 59})],
                                    "face": {"mouth": None}, "over": ["beak"]}),
    ("fuzzball", "#b8bcc9", "#d9f4ff", {"deco": [("face_patch", "#fbfbfd"), ("puffs_top", "#c9cdd8")], "face": {"mouth": None},
                                       "over": [("beak", {"c": "#4a4658"})]}),
    ("snowy", "#fbfbfd", "#e3e9ff", {"back": [("tufts", "#fbfbfd")], "deco": [("spots", {"c": "#b8bcc9", "n": 6, "seed": 17, "r": (0.8, 1.2)})],
                                    "face": {"eyes": "big", "mouth": None}, "over": [("beak", {"c": "#ffd23f"})]}),
    ("dusk", "#5c5a8a", "#ffd9ec", {"back": [("wings", {"c": "#3e3c6a", "kind": "bat"}), ("ears_cat", {"c": "#5c5a8a", "inner": "#ff9fc1"})],
                                   "deco": [("mark", {"c": "#ffe066", "kind": "moon"})], "face": {"mouth": "fang"}}),
    ("dewdrop", "#8fd8ff", "#ffe0ec", {"back": [("rays", {"c": "#5ec8ff", "n": 3, "r": 22, "a0": math.pi * 0.85, "a1": math.pi * 1.35, "petal": True}),
                                               ("rays", {"c": "#5ec8ff", "n": 3, "r": 22, "a0": math.pi * 1.65, "a1": math.pi * 2.15, "petal": True})],
                                      "deco": [("spots", {"c": "#c9ecff", "n": 4, "seed": 19, "r": (1, 1.6), "top": True})]}),
    ("spore", "#f2e6ff", "#d6f2c4", {"deco": [("cap", {"c": "#5ec8ff", "dots": "#e9fdff"})], "shape": (32, 52, 16, 14),
                                    "face": {"cy": 52, "gap": 6, "eyes": "happy"}, "gloss": (21, 47)}),
    ("chanterelle", "#fff0dd", "#ffe0c8", {"deco": [("cap", {"c": "#ffb33b", "dots": "#ffd56b", "n": 3})], "shape": (32, 52, 16, 14),
                                          "face": {"cy": 52, "gap": 6, "mouth": "open"}, "gloss": (21, 47)}),
    # --- dress-up ---
    ("merlin", "#c4b5ff", "#e3e9ff", {"deco": [("wizard_hat", "#5a4fb8")], "face": {"eyes": "wink"}}),
    ("hex", "#a6f5a8", "#e6dcff", {"deco": [("witch_hat", "#4a4462")], "face": {"mouth": "fang"}}),
    ("confetti", "#ffd9b0", "#d9f4ff", {"deco": [("party_hat", {"c": "#ff6b9a", "c2": "#ffe066"})], "face": {"eyes": "happy", "mouth": "open"}}),
    ("dapper", "#d9e2ee", "#ffe6c2", {"deco": [("top_hat", {"c": "#3a3552"})], "over": ["glasses"]}),
    ("captain", "#ffcf9a", "#c9ecff", {"deco": [("bow", {"c": "#ff5a6e", "x": 32, "y": 30})], "over": ["pirate_patch"],
                                      "face": {"mouth": "open"}}),
    ("regal", "#e6dcff", "#fff3c4", {"deco": ["crown"], "face": {"eyes": "sleepy", "mouth": "smile"}}),
    ("scholar", "#ffe0b8", "#d6f2c4", {"back": [("ears_round", {"c": "#ffe0b8", "inner": "#ffc7d3"})], "over": ["glasses"],
                                      "face": {"mouth": "tiny"}}),
    ("cozy", "#ffd0b8", "#e3e9ff", {"deco": [("beanie", {"c": "#7be08b", "c2": "#fffaf0"}), ("scarf", "#ff6b6b")],
                                   "face": {"eyes": "happy"}}),
    ("cupid", "#ffc4d3", "#fff0f5", {"back": [("wings", {"c": "#ffffff", "kind": "angel"})], "deco": [("mark", {"c": "#ff3d6e", "kind": "heart"})],
                                    "face": {"eyes": "wink"}}),
]


def to_svg(p):
    rows = []
    for y in range(H):
        x = 0
        while x < W:
            c = p.g.get((x, y))
            if c is None:
                x += 1
                continue
            x2 = x
            while x2 < W and p.g.get((x2, y)) == c:
                x2 += 1
            rows.append(f'<rect x="{x}" y="{y}" width="{x2 - x}" height="1" fill="{c}"/>')
            x = x2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'shape-rendering="crispEdges">' + "".join(rows) + "</svg>\n")


def contact_sheet(pets, path, scale=4, cols=5):
    rows_n = math.ceil(len(pets) / cols)
    cw, ch = W * scale, (H - 8) * scale
    sw, sh = cw * cols, ch * rows_n
    px = bytearray(b"\xf4\xf1\xe8" * sw * sh)
    for i, (_, p) in enumerate(pets):
        ox, oy = (i % cols) * cw, (i // cols) * ch
        for (x, y), c in p.g.items():
            if y < 8:
                continue
            r, g, b = (round(v * 255) for v in hx(c))
            for dy in range(scale):
                for dx in range(scale):
                    o = ((oy + (y - 8) * scale + dy) * sw + ox + x * scale + dx) * 3
                    px[o:o + 3] = bytes((r, g, b))
    raw = b"".join(b"\x00" + bytes(px[y * sw * 3:(y + 1) * sw * 3]) for y in range(sh))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", sw, sh, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    pets = [make() for make in PETS] + [build(spec) for spec in ROSTER]
    for name, p in pets:
        with open(os.path.join(OUT, f"pet-{name}.svg"), "w") as f:
            f.write(to_svg(p))
    if len(sys.argv) > 1:  # preview sheets, 25 pets per sheet
        for i in range(0, len(pets), 25):
            contact_sheet(pets[i:i + 25], sys.argv[1].replace(".png", f"-{i // 25 + 1}.png"), scale=3)
    print(f"wrote {len(pets)} pets")
