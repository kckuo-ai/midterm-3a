"""產生自然重點整理用的植物構造科學繪圖（國中課本風格：細墨線＋漸層上色＋標註線）。
圖：根莖葉總覽、葉（葉脈／葉緣／葉形）、三種莖、兩種根、花的縱剖面、花→果實→種子、種子傳播。
執行：python3 tools/make_plant_svg.py  → 把圖嵌進 science/notes.html 的 <!-- fig:... --> 標記之間
"""
import math, pathlib, random

FONT = "'Noto Sans TC','PingFang TC','Microsoft JhengHei',sans-serif"
INK = "#2f2a26"
_P = "x"


def setp(name):
    global _P
    _P = name


def U(n):
    return f"url(#{_P}-{n})"


GRADS = {
    "lf": (0, 0, 0, 1, [(0, "#e4f3cf"), (1, "#7db168")]),
    "lf2": (0, 0, 0, 1, [(0, "#bcdc9a"), (1, "#4f8a45")]),
    "stg": (0, 0, 1, 0, [(0, "#bddea1"), (.55, "#8ebb73"), (1, "#5d8d49")]),
    "bark": (0, 0, 1, 0, [(0, "#bd9e7a"), (.6, "#8d6d4c"), (1, "#5d432c")]),
    "root": (0, 0, 1, 0, [(0, "#fbf0da"), (1, "#dcc297")]),
    "soil": (0, 0, 0, 1, [(0, "#eadcc2"), (1, "#b79a72")]),
    "pk": (0, 0, 0, 1, [(0, "#fff3f5"), (1, "#f0a0b6")]),
    "pk2": (0, 0, 0, 1, [(0, "#ffe6ec"), (1, "#e690a9")]),
    "sun": (0, 0, 1, 1, [(0, "#fff6b8"), (1, "#f5b82a")]),
    "gua": (0, 0, 1, 1, [(0, "#d9eb8c"), (1, "#8fbd4f")]),
    "gua2": (0, 0, 1, 1, [(0, "#f3f0a0"), (1, "#c9d36a")]),
    "lan": (0, 0, 0, 1, [(0, "#ffd9b8"), (1, "#e48a63")]),
    "lon": (0, 0, 1, 1, [(0, "#d6b47e"), (1, "#a67c4b")]),
    "ov": (0, 0, 0, 1, [(0, "#d7eeb8"), (1, "#a7d07e")]),
    "sky": (0, 0, 0, 1, [(0, "#f2f9ff"), (1, "#fffdf8")]),
}


def defs():
    out = []
    for n, (x1, y1, x2, y2, st) in GRADS.items():
        stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in st)
        out.append(f'<linearGradient id="{_P}-{n}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{stops}</linearGradient>')
    return "<defs>" + "".join(out) + "</defs>"


def svg(w, h, label, body):
    frame = f'<rect x="2" y="2" width="{w-4}" height="{h-4}" rx="8" fill="{U("sky")}" stroke="#b9b2a4" stroke-width="1.2"/>'
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">{defs()}{frame}{body}</svg>'


# ---------- 基本繪圖工具 ----------
def seg(pts):
    s, n = "", len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return s


def sm(pts):
    return f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" + seg(pts)


def smc(pts):
    n = len(pts)
    s = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return s + " Z"


def pa(d, fill="none", stroke=INK, sw=1.1, op=None, extra=""):
    o = f' opacity="{op}"' if op is not None else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{o} {extra}/>'


def ln(x1, y1, x2, y2, stroke=INK, sw=1.0, dash=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{op}"' if op is not None else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}{o}/>'


def ell(cx, cy, rx, ry, fill, stroke=INK, sw=1.0, rot=0):
    t = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot else ""
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{t}/>'


def circ(cx, cy, r, fill, stroke=INK, sw=1.0):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def txt(x, y, t, size=16, color="#222", weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" '
            f'font-family="{FONT}" stroke="#fffdf8" stroke-width="3" paint-order="stroke" stroke-linejoin="round">{t}</text>')


def qb(p0, c, p1, n=14):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]))
    return out


def tube(pts, w0, w1, fill, stroke=INK, sw=1.0):
    n = len(pts)
    Lf, Rt = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        Lf.append((x + nx * w, y + ny * w))
        Rt.append((x - nx * w, y - ny * w))
    d = sm(Lf) + f" L{Rt[-1][0]:.1f},{Rt[-1][1]:.1f}" + seg(Rt[::-1]) + " Z"
    return pa(d, fill, stroke, sw)


def label(px, py, lx, ly, main, sub="", anchor="start", ex=None, ey=None):
    """標註：紅點在 (px,py)，文字在 (lx,ly)，細線相連。"""
    if ex is None:
        if anchor == "start":
            ex, ey = lx - 6, ly - 6
        elif anchor == "end":
            ex, ey = lx + 6, ly - 6
        else:
            ex = lx
            ey = (ly + (26 if sub else 8)) if ly < py else (ly - 20)
    g = ln(px, py, ex, ey, "#444", 0.9) + f'<circle cx="{px}" cy="{py}" r="2.4" fill="#c2402a"/>'
    g += txt(lx, ly, main, 17, "#1f1f1f", "bold", anchor)
    if sub:
        g += txt(lx, ly + 18, sub, 13, "#666", "normal", anchor)
    return g


def arrow(x1, y1, x2, y2, color, sw=1.8, dash=None):
    a = math.atan2(y2 - y1, x2 - x1)
    h = 8
    p1 = (x2 - h * math.cos(a - .45), y2 - h * math.sin(a - .45))
    p2 = (x2 - h * math.cos(a + .45), y2 - h * math.sin(a + .45))
    return ln(x1, y1, x2, y2, color, sw, dash) + f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'


def inset(idn, cx, cy, r, inner):
    return (f'<clipPath id="{_P}-{idn}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<g clip-path="url(#{_P}-{idn})">{inner}</g><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#555" stroke-width="2"/>')


# ---------- 葉 ----------
def prof(t, kind):
    if kind == "ovate":
        return math.sin(math.pi * t ** 0.75) ** 0.9
    if kind == "lanceolate":
        return (math.sin(math.pi * t) ** 0.75) * (1 - 0.3 * t)
    return math.sin(math.pi * t) ** 0.8


def leaf(x, y, L, W, ang, kind="elliptic", margin="entire", ven="net", bend=0.0, fill="lf", detail=True):
    rng = random.Random(int(x * 7 + y * 3))
    n = 26

    def mid(t):
        return (t * L, bend * L * t * t)

    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        w = W * prof(t, kind)
        if margin == "serrate" and 0 < i < n and w > 2:
            w += (W * 0.07 + 1.2) if i % 2 else 0
        mx, my = mid(t)
        top.append((mx, my - w))
        bot.append((mx, my + w))
    if margin == "serrate":
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in top + bot[::-1][1:]) + " Z"
    else:
        d = sm(top) + seg(bot[::-1]) + " Z"
    g = pa(d, U(fill), INK, 1.1)
    half = sm([mid(i / n) for i in range(n + 1)]) + seg(bot[::-1]) + " Z"
    g += pa(half, "#2f5d2a", "none", 0, 0.10)
    v = []
    if ven == "net":
        v.append(pa(sm([mid(i / 12 * 0.97) for i in range(13)]), "none", "#4c7f3f", 1.5))
        for t in (0.1, 0.19, 0.28, 0.37, 0.46, 0.55, 0.64, 0.73, 0.82):
            for s in (-1, 1):
                t2 = min(t + 0.2, 0.97)
                sx, sy = mid(t)
                ex, ey = mid(t2)
                ey += s * W * prof(t2, kind) * 0.86
                cx, cy = mid(t + 0.07)
                cy += s * W * prof(t + 0.07, kind) * 0.38
                v.append(pa(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", "none", "#4c7f3f", 0.85))
                if detail:
                    for u in (0.3, 0.55, 0.78):
                        px = (1 - u) ** 2 * sx + 2 * (1 - u) * u * cx + u * u * ex
                        py = (1 - u) ** 2 * sy + 2 * (1 - u) * u * cy + u * u * ey
                        a = math.radians(rng.uniform(-30, 30))
                        l = 0.045 * L
                        v.append(ln(px, py, px + l * math.cos(a), py + s * l * (0.8 + math.sin(abs(a))), "#4c7f3f", 0.45, op=0.75))
    elif ven == "parallel":
        for k in range(-4, 5):
            pts = [(t * L, mid(t)[1] + k / 4 * 0.8 * W * prof(t, kind)) for t in [i / 14 * 0.97 + 0.015 for i in range(15)]]
            v.append(pa(sm(pts), "none", "#4c7f3f", 1.3 if k == 0 else 0.75))
    g += "".join(v)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang})">{g}</g>'


def heart_leaf(x, y, L, ang):
    d = (f"M0,0 C{-.06*L:.1f},{-.28*L:.1f} {.22*L:.1f},{-.58*L:.1f} {.46*L:.1f},{-.3*L:.1f} "
         f"C{.7*L:.1f},{-.16*L:.1f} {.9*L:.1f},{-.05*L:.1f} {L:.1f},0 "
         f"C{.9*L:.1f},{.05*L:.1f} {.7*L:.1f},{.16*L:.1f} {.46*L:.1f},{.3*L:.1f} "
         f"C{.22*L:.1f},{.58*L:.1f} {-.06*L:.1f},{.28*L:.1f} 0,0 Z")
    g = pa(d, U("lf"), INK, 1.1) + pa(f"M0,0 L{L*.92:.1f},0", "none", "#4c7f3f", 1.2)
    for t in (.2, .4, .6):
        for s in (-1, 1):
            g += pa(f"M{t*L:.1f},0 Q{(t+.1)*L:.1f},{s*.12*L:.1f} {(t+.18)*L:.1f},{s*.2*L*(1-t*.6):.1f}", "none", "#4c7f3f", 0.7)
    return f'<g transform="translate({x} {y}) rotate({ang})">{g}</g>'


def maple_leaf(x, y, R, ang):
    tips = [(-135, .85), (-68, 1.0), (0, 1.1), (68, 1.0), (135, .85)]
    pts = []
    for a, k in tips:
        pts += [(a - 12, .45), (a - 5, .82 * k), (a, k), (a + 5, .82 * k)]
    pts.append((tips[-1][0] + 12, .45))
    poly = []
    for a, r in pts:
        aa = math.radians(a - 90)
        poly.append((R * r * math.cos(aa), R * r * math.sin(aa)))
    g = pa("M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in poly) + " Z", U("lf2"), INK, 1.1)
    for a, k in tips:
        aa = math.radians(a - 90)
        g += ln(0, 0, R * k * .85 * math.cos(aa), R * k * .85 * math.sin(aa), "#2f5d2a", 0.8)
    return f'<g transform="translate({x} {y}) rotate({ang})">{g}</g>'


# ---------- 土壤、根、太陽 ----------
def soil(x1, x2, y1, y2, seed=3, dots=140):
    rng = random.Random(seed)
    g = f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="{U("soil")}"/>'
    for _ in range(dots):
        x, y = rng.uniform(x1 + 4, x2 - 4), rng.uniform(y1 + 6, y2 - 4)
        g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.6, 1.8):.1f}" fill="#8f7550" opacity="{rng.uniform(.25, .55):.2f}"/>'
    for _ in range(max(4, dots // 25)):
        x, y = rng.uniform(x1 + 20, x2 - 20), rng.uniform(y1 + 20, y2 - 12)
        g += ell(x, y, rng.uniform(4, 8), rng.uniform(3, 5), "#cdbb9c", "#8f7550", 0.7, rng.uniform(-30, 30))
    g += pa(f"M{x1},{y1} Q{(x1+x2)/2},{y1-3} {x2},{y1}", "none", "#7a5c36", 1.8)
    return g


def rootbranch(rng, x, y, ang, length, w, depth, out):
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a)
    bend = rng.uniform(-.22, .22) * length
    cx, cy = (x + ex) / 2 + bend * math.sin(a), (y + ey) / 2 - bend * math.cos(a)
    pts = qb((x, y), (cx, cy), (ex, ey), 12)
    out.append(tube(pts, w, max(w * .35, .7), U("root"), "#8b6b43", 0.7))
    if depth > 0:
        for tt in (.3, .55, .78):
            px, py = pts[int(tt * 12)]
            side = rng.choice((-1, 1))
            rootbranch(rng, px, py, ang + side * rng.uniform(35, 65), length * rng.uniform(.35, .5), w * .55, depth - 1, out)
    else:
        for _ in range(4):
            px, py = pts[rng.randint(6, 12)]
            b = a + rng.uniform(-1.4, 1.4)
            out.append(ln(px, py, px + 6 * math.cos(b), py + 6 * math.sin(b), "#a4854f", 0.5))


def sun(cx, cy, r=24):
    g = ""
    for k in range(14):
        a = k * 2 * math.pi / 14
        g += ln(cx + (r + 5) * math.cos(a), cy + (r + 5) * math.sin(a), cx + (r + 15) * math.cos(a), cy + (r + 15) * math.sin(a), "#e2a010", 1.6)
    return g + circ(cx, cy, r, U("sun"), "#d99a10", 1.2)


def twig(x1, y1, x2, y2, w0=8, w1=5):
    return tube(qb((x1, y1), ((x1 + x2) / 2, (y1 + y2) / 2 - 10), (x2, y2), 8), w0, w1, U("bark"), INK, .9)


# ---------- 圖一：根莖葉總覽 ----------
def overview():
    setp("ov")
    W, H, gy = 780, 520, 262
    rng = random.Random(5)
    sx = 392

    def cxat(y):
        return sx + 5 * math.sin((gy - y) / 48)

    b = soil(4, W - 4, gy, H - 4, 3, 200)
    b += sun(80, 66) + txt(80, 118, "陽光", 16, "#9a6b00", "bold", "middle")
    b += arrow(118, 90, 262, 150, "#e2a010", 1.6, "6 5") + arrow(112, 104, 232, 215, "#e2a010", 1.6, "6 5")
    cl = [(cxat(y), y) for y in range(gy, 54, -12)] + [(cxat(54), 54)]
    b += tube(cl, 17, 7, U("stg"), INK, 1.0)
    for ny, side in ((216, 1), (172, -1), (128, 1), (92, -1)):
        nx = cxat(ny)
        ex, ey = nx + side * 40, ny - 17
        pet = f"M{nx:.1f},{ny:.1f} Q{nx+side*20:.1f},{ny-6:.1f} {ex:.1f},{ey:.1f}"
        b += pa(pet, "none", "#5d8d49", 3) + pa(pet, "none", INK, 0.6)
        b += leaf(ex, ey, 112, 38, -36 if side == 1 else -144, "ovate", "serrate", "net", -0.06 * side)
        b += ell(nx, ny, 9, 3.6, "#9cc47f", INK, 0.8)
        b += ell(nx + side * 4, ny - 9, 3.2, 6.5, "#8a7a45", INK, 0.7, side * 25)
    tx = cxat(54)
    b += leaf(tx, 56, 36, 10, -100, "lanceolate", "entire", "net", detail=False) + leaf(tx, 56, 32, 9, -76, "lanceolate", "entire", "net", detail=False)
    b += ell(tx, 54, 4, 6.5, "#7a9c4f", INK, 0.8)
    rr = []
    tap = qb((sx, gy), (sx + 10, gy + 100), (sx - 6, gy + 230), 18)
    rr.append(tube(tap, 11, 2.2, U("root"), "#8b6b43", 0.8))
    for i, t in enumerate((.1, .2, .3, .42, .55, .68, .8)):
        px, py = tap[int(t * 18)]
        side = 1 if i % 2 == 0 else -1
        rootbranch(rng, px, py, 90 - side * rng.uniform(38, 62), rng.uniform(80, 120) * (1 - t * .5), 4.5 - 2 * t, 1, rr)
    b += "".join(rr)
    b += arrow(660, 430, 560, 400, "#2f78b5", 1.6, "5 4") + arrow(150, 440, 240, 400, "#2f78b5", 1.6, "5 4") + arrow(190, 330, 270, 340, "#2f78b5", 1.6, "5 4")
    b += txt(668, 440, "水", 17, "#2f78b5", "bold") + txt(130, 452, "水", 17, "#2f78b5", "bold") + txt(160, 336, "水", 17, "#2f78b5", "bold")
    b += label(tx + 4, 48, tx + 64, 28, "頂芽", "", "start", tx + 58, 22)
    b += label(500, 96, 600, 70, "葉片", "進行光合作用", "start")
    b += label(cxat(128) + 28, 118, 600, 150, "葉柄", "連接葉片與莖", "start")
    b += label(cxat(128) + 4, 119, 600, 214, "側芽", "（腋芽）葉腋的小芽", "start")
    b += label(cxat(216) - 8, 218, 210, 246, "節", "葉子長出的位置", "end")
    b += label(cxat(150) - 6, 150, 214, 150, "莖", "支撐、輸送水分養分", "end")
    b += label(sx, gy + 100, 600, 336, "主根（軸根）", "固定植物、吸水", "start")
    b += label(445, gy + 70, 600, 410, "側根", "", "start", 594, 404)
    return svg(W, H, "植物構造總覽：頂芽、葉片、葉柄、節、側芽、莖、主根、側根", b)


# ---------- 圖二：葉 ----------
def leaf_detail():
    setp("lf")
    W, H = 780, 600
    b = tube(qb((30, 330), (60, 300), (92, 262), 8), 11, 8, U("stg"), INK, 1)
    b += ell(92, 262, 9, 4, "#9cc47f", INK, .8, -40)
    b += pa("M92,262 Q112,252 138,246", "none", "#5d8d49", 3.4) + pa("M92,262 Q112,252 138,246", "none", INK, 0.6)
    b += leaf(138, 246, 270, 80, -8, "elliptic", "entire", "net", 0.04)
    b += txt(270, 372, "桂花", 19, "#1f1f1f", "bold", "middle") + txt(270, 394, "網狀脈・葉緣平滑", 14, "#666", "normal", "middle")
    b += label(250, 247, 200, 60, "葉脈", "主脈與側脈連成網狀", "middle")
    b += label(215, 188, 130, 130, "葉緣", "平滑", "end")
    b += label(115, 254, 60, 214, "葉柄", "", "end")
    b += label(335, 275, 405, 345, "葉片", "", "start")
    b += tube(qb((470, 150), (466, 260), (472, 380), 10), 13, 11, U("stg"), INK, 1)
    b += leaf(472, 330, 280, 40, -16, "lanceolate", "entire", "parallel", -0.05)
    b += txt(610, 372, "百合", 19, "#1f1f1f", "bold", "middle") + txt(610, 394, "平行脈・葉緣平滑", 14, "#666", "normal", "middle")
    b += label(600, 255, 640, 140, "葉脈", "一條條互相平行", "middle")
    b += ln(30, 418, 750, 418, "#cfc8b8", 1, "4 4")
    b += txt(40, 446, "葉緣（放大）", 16, "#1f1f1f", "bold")
    for cx, kind in ((100, "smooth"), (240, "saw")):
        inner = f'<rect x="{cx-60}" y="465" width="120" height="100" fill="#f5fbec"/>'
        if kind == "smooth":
            inner += pa(f"M{cx-60},538 Q{cx-20},500 {cx},498 T{cx+60},538 L{cx+60},575 L{cx-60},575 Z", U("lf"), INK, 1.8)
        else:
            pts = [(cx - 60, 550), (cx - 40, 522), (cx - 30, 546), (cx - 10, 514), (cx, 544), (cx + 20, 512), (cx + 30, 544), (cx + 50, 516), (cx + 60, 540)]
            inner += pa("M" + " L".join(f"{a},{c}" for a, c in pts) + f" L{cx+60},575 L{cx-60},575 Z", U("lf"), INK, 1.8)
        b += inset(f"c{cx}", cx, 515, 50, inner)
        b += txt(cx, 586, "平滑" if kind == "smooth" else "鋸齒", 15, "#222", "bold", "middle")
    b += txt(440, 446, "葉形（葉子的形狀）", 16, "#1f1f1f", "bold")
    b += leaf(446, 520, 90, 30, 0, "elliptic", "entire", "net", detail=False) + txt(491, 574, "橢圓形", 14, "#444", "normal", "middle")
    b += heart_leaf(590, 548, 82, -90) + txt(590, 574, "心形", 14, "#444", "normal", "middle") + txt(590, 592, "像愛心", 12, "#888", "normal", "middle")
    b += maple_leaf(700, 520, 44, 0) + txt(700, 574, "掌形", 14, "#444", "normal", "middle") + txt(700, 592, "像手掌", 12, "#888", "normal", "middle")
    return svg(W, H, "葉的構造與分類：網狀脈與平行脈、葉緣、葉形", b)


# ---------- 圖三：三種莖 ----------
def tree(cx, gy, rng):
    g = ell(cx, 120, 105, 70, "#cfe5b7", "none", 0).replace('fill="#cfe5b7"', 'fill="#cfe5b7" opacity="0.55"')
    trunk = qb((cx, gy), (cx + 5, gy - 90), (cx - 3, 200), 16)
    g += tube(trunk, 36, 22, U("bark"), INK, 1.1)
    for k in range(-2, 3):
        pts = qb((cx + k * 6, gy - 4), (cx + k * 6 + rng.uniform(-3, 3), gy - 80), (cx + k * 5 - 2, 204), 12)
        g += pa(sm(pts), "none", "#3f2d1c", 0.7, 0.7)
    g += pa(f"M{cx-18},{gy} Q{cx-34},{gy+4} {cx-48},{gy+8}", "none", INK, 1) + pa(f"M{cx+18},{gy} Q{cx+34},{gy+4} {cx+48},{gy+8}", "none", INK, 1)
    limbs = [((cx - 3, 205), (cx - 52, 150), 16, 6), ((cx - 3, 205), (cx + 50, 148), 16, 6), ((cx - 3, 208), (cx - 2, 100), 14, 5),
             ((cx - 20, 168), (cx - 78, 118), 9, 3), ((cx + 22, 165), (cx + 78, 120), 9, 3)]
    ends = []
    for p0, p1, w0, w1 in limbs:
        c = ((p0[0] + p1[0]) / 2 + rng.uniform(-6, 6), (p0[1] + p1[1]) / 2 - 8)
        g += tube(qb(p0, c, p1, 10), w0, w1, U("bark"), INK, .9)
        ends.append(p1)
    for ex, ey in ends:
        for _ in range(16):
            a = rng.uniform(-170, -10)
            r = rng.uniform(0, 36)
            lx, ly = ex + r * math.cos(math.radians(a)) * 1.1, ey + r * math.sin(math.radians(a)) * 0.8 - 6
            g += leaf(lx, ly, rng.uniform(26, 34), rng.uniform(9, 12), rng.uniform(-175, -5), "elliptic", "entire", "net", detail=False, fill=rng.choice(("lf", "lf2")))
    return g


def herb(cx, gy):
    g = ""
    for (dx, dy), lean in [((-28, -150), -14), ((-8, -205), -4), ((14, -180), 6), ((34, -125), 16), ((-42, -100), -22)]:
        tip = (cx + dx, gy + dy)
        pts = qb((cx + dx * .15, gy), (cx + dx * .55 + lean, gy + dy * .55), tip, 14)
        g += tube(pts, 5, 2.4, U("stg"), "#4c7f3f", .7)
        for k, t in enumerate((.35, .55, .75)):
            px, py = pts[int(t * 14)]
            for s in (-1, 1):
                g += leaf(px, py, 36, 11, (-25 if s == 1 else -155) - (k * 6 * s), "elliptic", "serrate", "net", detail=False, fill="lf2")
        for p in range(5):
            a = p * 72 - 90
            g += ell(tip[0] + 8 * math.cos(math.radians(a)), tip[1] + 8 * math.sin(math.radians(a)), 6.5, 4.6, U("pk"), "#b3566f", .7, a)
        g += circ(tip[0], tip[1], 2.6, "#f2c94c", "#a37a00", .6)
    return g


def vines(cx, gy):
    g = ""
    px = cx - 70
    g += tube([(px, gy), (px, 70)], 7, 6, "#cdb98b", "#7a6a45", .9)
    pts = [(px + 14 * math.sin(i * .62), gy - i * 3.0) for i in range(61)]
    g += pa(sm(pts), "none", "#4c7f3f", 3.4) + pa(sm(pts), "none", "#9fcd84", 1.4)
    for i in (8, 17, 26, 35, 44, 53):
        x, y = pts[i]
        g += heart_leaf(x, y, 30, -35 if i % 2 else -145)
    fx, fy = px + 6, 78
    g += pa(f"M{fx-4},{fy} L{fx-26},{fy-24} Q{fx-2},{fy-36} {fx+22},{fy-24} Z", U("pk2"), "#a8456a", 1.1)
    g += ell(fx - 2, fy - 28, 5, 2, "#fff7c0", "#b49400", .6)
    qx = cx + 60
    stem = qb((qx, gy), (qx + 30, gy - 100), (qx - 10, 100), 16)
    g += pa(f"M{qx-62},70 L{qx+80},70", "none", "#9b8a62", 2.4) + pa(f"M{qx+62},70 L{qx+62},{gy}", "none", "#9b8a62", 2.4)
    g += pa(sm(stem), "none", "#4c7f3f", 3.2) + pa(sm(stem), "none", "#9fcd84", 1.2)
    for i, t in enumerate((.25, .45, .62, .8)):
        x, y = stem[int(t * 16)]
        s = 1 if i % 2 == 0 else -1
        g += maple_leaf(x + s * 26, y - 6, 22, s * 20)
        pts2 = []
        for k in range(40):
            r = 7 * (1 - k / 55)
            pts2.append((x + s * 6 + s * k * .9 + r * math.cos(k * .7), y + 6 - k * .5 + r * math.sin(k * .7)))
        g += pa(sm(pts2), "none", "#2f6d3a", 1.2)
    return g


def stems():
    setp("st")
    W, H, gy = 800, 560, 410
    rng = random.Random(8)
    b = soil(4, W - 4, gy, H - 4, 4, 70)
    b += f'<rect x="4" y="{gy+44}" width="{W-8}" height="{H-gy-48}" fill="#fffdf8"/>'
    b += tree(150, gy, rng) + herb(405, gy) + vines(650, gy)
    inner = f'<rect x="30" y="280" width="80" height="80" fill="{U("bark")}"/>'
    for k in range(9):
        x = 34 + k * 9
        inner += pa(f"M{x},282 Q{x+rng.uniform(-6,6)},320 {x+rng.uniform(-4,4)},360", "none", "#2f2113", 1.4, .8)
    b += inset("bk", 70, 320, 38, inner)
    b += ln(100, 300, 140, 340, "#888", .9, "3 3") + txt(22, 378, "樹皮放大：縱向裂紋", 13, "#555")
    for x, t, s, e in ((150, "木本莖", "粗壯，可以持續長高", "例：樟樹、木棉、青楓"), (405, "草本莖", "較細，向四面八方長出枝條", "例：長春花、大花咸豐草"),
                       (650, "藤本莖", "柔軟，無法直立，要攀爬", "例：牽牛花、絲瓜")):
        b += txt(x, gy + 70, t, 21, "#1f1f1f", "bold", "middle") + txt(x, gy + 94, s, 14, "#666", "normal", "middle") + txt(x, gy + 112, e, 13, "#888", "normal", "middle")
    b += label(578, 250, 535, 232, "莖纏繞", "牽牛花", "end", 539, 226)
    b += label(706, 262, 740, 150, "卷鬚", "絲瓜", "middle")
    return svg(W, H, "三種莖：木本莖粗壯、草本莖較細、藤本莖柔軟需攀爬（牽牛花纏繞、絲瓜用卷鬚）", b)


# ---------- 圖四：根 ----------
def roots():
    setp("rt")
    W, H, gy = 780, 500, 120
    rng = random.Random(12)
    b = soil(4, W - 4, gy, H - 70, 9, 220)
    b += f'<rect x="4" y="{H-70}" width="{W-8}" height="66" fill="#fffdf8"/>'
    cx = 195
    for k, (ang, L) in enumerate(((-100, 70), (-80, 78), (-122, 58), (-58, 56), (-140, 44), (-40, 42))):
        b += leaf(cx + (k % 3 - 1) * 4, gy - 4, L, 24, ang, "ovate", "entire", "net", detail=False, fill="lf" if k % 2 else "lf2")
    rr = []
    tap = qb((cx, gy), (cx + 6, gy + 120), (cx - 4, gy + 290), 18)
    rr.append(tube(tap, 18, 2.4, U("root"), "#8b6b43", .9))
    for i, t in enumerate((.08, .16, .26, .36, .47, .58, .7, .82)):
        px, py = tap[int(t * 18)]
        side = 1 if i % 2 == 0 else -1
        rootbranch(rng, px, py, 90 - side * rng.uniform(40, 60), rng.uniform(70, 105) * (1 - t * .55), 4.2 - 2.2 * t, 1, rr)
    b += "".join(rr)
    b += label(cx + 4, gy + 140, 330, gy + 150, "主根", "一條粗根往下長", "start")
    b += label(cx + 52, gy + 112, 330, gy + 214, "側根", "旁邊長出較細的根", "start")
    b += arrow(110, gy + 20, 110, gy + 270, "#c2402a", 1.6) + txt(104, gy + 150, "深入土壤", 14, "#c2402a", "bold", "end")
    cx = 585
    for k, ang in enumerate((-92, -80, -104, -70, -112)):
        L = (100, 90, 90, 70, 66)[k]
        b += tube(qb((cx + (k - 2) * 3, gy + 2), (cx + (k - 2) * 8, gy - L * .5), (cx + math.cos(math.radians(ang)) * L * .6, gy - L), 8), 8, 4.5, U("lf2"), INK, .8)
    b += pa(f"M{cx-14},{gy-4} Q{cx},{gy-9} {cx+14},{gy-4} L{cx+12},{gy+14} L{cx-12},{gy+14} Z", "#f4f0e2", INK, .9)
    rr = []
    for k in range(30):
        a = 90 + (k - 15) * 5.2 + rng.uniform(-3, 3)
        L = rng.uniform(70, 125) * (1 - abs(k - 15) / 40)
        rootbranch(rng, cx + (k - 15) * 1.2, gy + 12, a, L, 2.3, 1, rr)
    b += "".join(rr)
    b += label(cx + 42, gy + 90, 640, gy + 160, "鬚根", "細小的根", "start")
    b += arrow(740, gy + 14, 740, gy + 108, "#c2402a", 1.6) + txt(734, gy + 66, "淺層", 14, "#c2402a", "bold", "end")
    for x, t, s in ((195, "軸根", "例：小白菜、菠菜"), (585, "鬚根", "例：蔥、蒜")):
        b += txt(x, H - 38, t, 21, "#1f1f1f", "bold", "middle") + txt(x, H - 14, s, 14, "#666", "normal", "middle")
    return svg(W, H, "兩種根：軸根有一條粗主根與側根深入土壤，鬚根由許多細根組成，分布在淺層", b)


# ---------- 花 ----------
def petal(bx, by, tx, ty, w, bend, fill):
    dx, dy = tx - bx, ty - by
    d = math.hypot(dx, dy)
    nx, ny = -dy / d, dx / d

    def Q(t, off):
        return (bx + dx * t + nx * off, by + dy * t + ny * off)

    left = [Q(0, 0), Q(.2, w * .55 + bend * .2), Q(.5, w + bend * .8), Q(.82, w * .72 + bend * .6), Q(1, bend * .1)]
    right = [Q(1, bend * .1), Q(.82, -w * .72 + bend * .6), Q(.5, -w + bend * .8), Q(.2, -w * .55 + bend * .2), Q(0, 0)]
    pink = "pk" in fill
    g = pa(sm(left) + seg(right) + " Z", fill, "#a8456a" if pink else INK, 1.1)
    for k in (-.55, -.28, 0, .28, .55):
        pts = [Q(t, k * w * (math.sin(math.pi * min(t * 1.1, 1)) ** .6) + bend * .8 * math.sin(math.pi * t) * .8) for t in (.05, .25, .5, .75, .92)]
        g += pa(sm(pts), "none", "#b35a78" if pink else "#4c7f3f", .6, .8)
    return g


def pollen(cx, cy, r, rng):
    g = ""
    for _ in range(9):
        x, y = cx + rng.uniform(-r * .6, r * .6), cy + rng.uniform(-r * .6, r * .6)
        rr = rng.uniform(5, 8)
        g += circ(x, y, rr, "#ffd54a", "#a37a00", .9)
        for a in range(0, 360, 45):
            g += ln(x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a)), x + (rr + 2.2) * math.cos(math.radians(a)), y + (rr + 2.2) * math.sin(math.radians(a)), "#a37a00", .7)
    return g


def flower():
    setp("fl")
    W, H = 800, 560
    rng = random.Random(4)
    cx = 330
    b = tube(qb((cx, H - 6), (cx + 6, 500), (cx, 462), 8), 12, 12, U("stg"), INK, 1)
    b += petal(cx - 4, 440, cx - 62, 96, 34, -8, U("pk2")) + petal(cx + 4, 440, cx + 66, 100, 34, 8, U("pk2"))
    b += petal(cx - 12, 440, cx - 150, 124, 40, -26, U("pk")) + petal(cx + 12, 440, cx + 154, 130, 40, 26, U("pk"))
    b += petal(cx - 22, 452, cx - 104, 392, 15, -7, U("lf2")) + petal(cx + 22, 452, cx + 104, 392, 15, 7, U("lf2"))
    for ax, ay, rot in [(cx - 52, 232, -25), (cx - 30, 210, -10), (cx + 36, 212, 10), (cx + 58, 236, 25)]:
        sx = cx + (-14 if ax < cx else 14)
        fil = sm(qb((sx, 440), (sx + (ax - sx) * .2, 340), (ax, ay + 8), 10))
        b += pa(fil, "none", "#8c7a3a", 2.4) + pa(fil, "none", "#e6dca0", 1.0)
        b += ell(ax, ay, 14, 6, "#f4a53b", "#a35a00", 1, rot)
        for _ in range(5):
            b += f'<circle cx="{ax+rng.uniform(-9,9):.1f}" cy="{ay+rng.uniform(-3,3):.1f}" r="1.7" fill="#ffd54a"/>'
    b += pa(smc([(cx, 380), (cx + 28, 396), (cx + 30, 436), (cx, 452), (cx - 30, 436), (cx - 28, 396)]), U("ov"), INK, 1.2)
    b += pa(smc([(cx, 388), (cx + 20, 402), (cx + 21, 432), (cx, 444), (cx - 21, 432), (cx - 20, 402)]), "#f2f9df", "#6c8f4e", .8)
    for ox, oy in ((-10, 408), (10, 408), (-11, 424), (11, 424), (0, 398), (0, 436)):
        b += ell(cx + ox, oy, 5.2, 6.4, "#fff2b8", "#a89000", .8) + circ(cx + ox, oy, 1.6, "#c9a400", "none", 0)
    sty = sm(qb((cx, 384), (cx + 6, 290), (cx, 176), 14))
    b += pa(sty, "none", "#72a05a", 5.5) + pa(sty, "none", INK, .7)
    b += pa(smc([(cx - 12, 178), (cx - 8, 160), (cx, 154), (cx + 8, 160), (cx + 12, 178), (cx, 184)]), "#f6e27a", "#8a7000", 1.1)
    for dx in (-6, 0, 6):
        b += circ(cx + dx, 158 + abs(dx) * .3, 1.6, "#c9a400", "none", 0)
    b += pa(smc([(cx - 30, 446), (cx - 22, 462), (cx + 22, 462), (cx + 30, 446), (cx, 452)]), "#9cc47f", INK, 1)
    b += pa(f"M{cx+58},222 C{cx+110},150 {cx+60},150 {cx+14},160", "none", "#e08a00", 1.6, extra='stroke-dasharray="5 4"')
    b += f'<polygon points="{cx+12},160 {cx+22},154 {cx+21},166" fill="#e08a00"/>'
    L = 600
    b += label(cx + 112, 240, L, 90, "花瓣", "顏色鮮豔，吸引動物", "start")
    b += label(cx + 58, 236, L, 180, "雄蕊", "花絲＋花藥（有花粉）", "start")
    b += label(cx + 8, 165, L, 252, "柱頭", "黏黏的，接住花粉", "start")
    b += label(cx + 3, 290, L, 316, "花柱", "", "start")
    b += label(cx + 18, 426, L, 380, "子房", "裡面有胚珠", "start")
    b += label(cx + 66, 419, L, 446, "花萼", "在花瓣外圍，保護花苞", "start")
    b += label(cx + 22, 458, L, 508, "花托", "", "start")
    b += inset("pl", 110, 440, 64, f'<rect x="40" y="370" width="140" height="140" fill="#fff7dc"/>{pollen(110, 440, 70, rng)}')
    b += ln(166, 408, cx - 40, 238, "#888", .9, "3 3") + txt(110, 530, "花粉（放大）", 14, "#444", "normal", "middle")
    b += txt(60, 70, "花的縱剖面", 18, "#1f1f1f", "bold") + txt(60, 92, "橘色虛線：花粉傳到柱頭", 13, "#c06a00")
    return svg(W, H, "花的縱剖面：花瓣、花萼、雄蕊（花絲、花藥、花粉）、雌蕊（柱頭、花柱、子房、胚珠）、花托", b)


# ---------- 花 → 果實 → 種子 ----------
def fruit_seed():
    setp("fs")
    W, H = 800, 380
    rng = random.Random(6)
    xs = (95, 290, 490, 690)
    b = ""
    cx = xs[0]
    b += twig(cx - 80, 70, cx + 10, 110) + leaf(cx - 60, 76, 80, 24, 20, "elliptic", "entire", "net", detail=False)
    b += pa(f"M{cx+10},110 L{cx+10},124", "none", "#5d8d49", 3)
    for p in range(5):
        a = p * 72 - 90
        b += ell(cx + 10 + 18 * math.cos(math.radians(a)), 150 + 18 * math.sin(math.radians(a)), 14, 11, "#ffffff", "#b9b2a0", 1, a)
    for _ in range(26):
        a, r = rng.uniform(0, 6.28), rng.uniform(2, 15)
        b += ln(cx + 10, 150, cx + 10 + r * math.cos(a), 150 + r * math.sin(a), "#e9d070", .7) + circ(cx + 10 + r * math.cos(a), 150 + r * math.sin(a), 1.3, "#f2c94c", "none", 0)
    cx = xs[1]
    b += twig(cx - 80, 70, cx + 10, 110) + leaf(cx - 60, 76, 80, 24, 20, "elliptic", "entire", "net", detail=False)
    b += pa(f"M{cx+10},110 L{cx+10},132", "none", "#5d8d49", 3) + ell(cx + 10, 156, 24, 26, U("gua"), INK, 1.1)
    b += pa(f"M{cx-6},176 L{cx-12},190 L{cx-2},183 L{cx+10},194 L{cx+22},183 L{cx+32},190 L{cx+26},176 Z", "#8a6a3a", INK, .8)
    b += pa(f"M{cx-4},140 Q{cx-8},128 {cx+2},124", "none", "#fff", 2, .7)
    b += txt(cx + 44, 124, "花瓣凋謝", 12, "#888") + txt(cx + 44, 140, "子房膨大", 12, "#888")
    cx = xs[2]
    b += twig(cx - 80, 60, cx + 14, 100) + leaf(cx - 62, 66, 84, 26, 18, "elliptic", "entire", "net", detail=False) + leaf(cx + 10, 100, 70, 22, -20, "elliptic", "entire", "net", detail=False)
    b += pa(f"M{cx+14},100 L{cx+14},118", "none", "#5d8d49", 3)
    b += pa(smc([(cx + 14, 118), (cx + 50, 134), (cx + 56, 176), (cx + 36, 208), (cx + 14, 214), (cx - 8, 208), (cx - 28, 176), (cx - 22, 134)]), U("gua2"), INK, 1.2)
    b += pa(f"M{cx-12},140 Q{cx-20},160 {cx-16},184", "none", "#ffffff", 3, .6)
    for _ in range(9):
        b += circ(cx + 14 + rng.uniform(-28, 28), rng.uniform(140, 200), .9, "#8e9a3a", "none", 0)
    b += pa(f"M{cx-2},213 L{cx-8},226 L{cx+4},220 L{cx+14},230 L{cx+24},220 L{cx+36},226 L{cx+30},213 Z", "#7a5a30", INK, .8)
    cx = xs[3]
    b += circ(cx, 170, 70, "#a8cf6a", INK, 1.3) + circ(cx, 170, 62, "#f6f2d2", "#9aaa5a", .8) + circ(cx, 170, 40, "#f2b8a2", "#c9796b", .9)
    for _ in range(18):
        a, r = rng.uniform(0, 360), rng.uniform(8, 30)
        b += ell(cx + r * math.cos(math.radians(a)), 170 + r * math.sin(math.radians(a)), 3.6, 2.6, "#e6cf8e", "#8a6d1c", .7, a)
    for x1, x2, y in ((xs[0] + 55, xs[1] - 55, 150), (xs[1] + 50, xs[2] - 55, 160), (xs[2] + 62, xs[3] - 80, 170)):
        b += arrow(x1, y, x2, y, "#c2402a", 2)
    b += label(cx + 52, 132, cx + 60, 60, "果皮", "", "middle")
    b += label(cx + 30, 200, cx + 80, 300, "果肉", "", "middle", cx + 76, 276)
    b += label(cx - 8, 164, cx - 100, 300, "種子", "", "middle", cx - 98, 276)
    for x, t, s in ((xs[0], "花", "開花、傳粉"), (xs[1], "未成熟果實", "子房長大"), (xs[2], "成熟果實", "果實變大、變色"), (xs[3], "果實剖面", "種子在果實裡面")):
        b += txt(x, 336, t, 18, "#1f1f1f", "bold", "middle") + txt(x, 358, s, 13, "#666", "normal", "middle")
    b += txt(W / 2, 24, "子房 → 果實，胚珠 → 種子（以番石榴為例）", 15, "#555", "normal", "middle")
    return svg(W, H, "花到果實到種子：開花傳粉後子房長成果實，胚珠成為種子（以番石榴為例）", b)


# ---------- 種子傳播 ----------
def bird(x, y, s=1.0, flip=False):
    """棲息的小鳥（側面，預設朝右；flip=True 朝左）。腳底約在 y+44。"""
    g = pa("M-28,4 L-74,-6 L-66,6 L-76,18 L-28,16 Z", "#5f86b8", INK, 1.1)  # 叉形尾羽
    g += ln(-34, 8, -66, 4, "#3f628f", .7) + ln(-34, 11, -68, 12, "#3f628f", .7)
    g += ln(-6, 30, -8, 44, "#b8793a", 1.8) + ln(10, 30, 10, 44, "#b8793a", 1.8)  # 腳
    for fx in (-8, 10):
        g += ln(fx, 44, fx + 7, 45, "#b8793a", 1.5) + ln(fx, 44, fx - 6, 46, "#b8793a", 1.5)
    body = [(-30, 8), (-22, -8), (-6, -17), (10, -22), (20, -32), (32, -37), (44, -30), (46, -20), (41, -11), (35, -5),
            (38, 8), (31, 23), (12, 32), (-8, 30), (-22, 21)]
    g += pa(smc(body), "#7ea7d6", INK, 1.3)
    g += pa(smc([(35, -5), (38, 8), (31, 23), (12, 32), (-8, 30), (-14, 18), (6, 9), (24, 1)]), "#f7f1df", "none", 0)  # 淺色腹部
    g += pa("M35,-5 Q38,8 31,23 Q12,32 -8,30", "none", INK, 1.2)
    g += pa(smc([(4, -12), (20, -6), (14, 12), (-12, 22), (-38, 20), (-26, 2), (-8, -8)]), "#5f86b8", INK, 1.2)  # 翅膀
    for k in range(4):
        g += pa(f"M{-30+k*9},{19-k*2} Q{-14+k*8},{10-k*3} {-4+k*7},{-2-k*2}", "none", "#3f628f", .8)
    g += pa("M46,-22 L60,-17 L46,-13 Z", "#f0a030", INK, 1.1)  # 喙
    g += circ(39, -25, 4.6, "#fff", INK, .9) + circ(40, -25, 2.8, INK, "none", 0) + circ(41, -26, 0.9, "#fff", "none", 0)
    t = f"translate({x} {y}) scale({-s if flip else s} {s})"
    return f'<g transform="{t}">{g}</g>'


def sprout(x, y):
    return (pa(f"M{x},{y} Q{x+2},{y-16} {x},{y-28}", "none", "#5d8d49", 2.4)
            + leaf(x, y - 28, 22, 8, -150, "elliptic", "entire", "net", detail=False) + leaf(x, y - 28, 22, 8, -30, "elliptic", "entire", "net", detail=False))


def lantern(x, y, s=1.0, rot=0):
    g = pa(smc([(0, -26), (14, -18), (22, 2), (14, 24), (0, 30), (-14, 24), (-22, 2), (-14, -18)]), U("lan"), "#a8452a", 1.3)
    for k in (-8, 0, 8):
        g += pa(f"M{k*.3},-25 Q{k*2.2},0 {k*.3},29", "none", "#a8452a", .7)
    for yy in (-12, -2, 8, 18):
        g += pa(f"M-14,{yy} Q0,{yy-3} 14,{yy}", "none", "#c06a4a", .5, .6)
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">{g}</g>'


def dispersal():
    setp("dp")
    W, H, gy = 800, 480, 392
    rng = random.Random(2)
    b = soil(4, W - 4, gy, H - 4, 7, 60) + ln(W / 2, 20, W / 2, gy - 10, "#cfc8b8", 1, "4 4")
    # 左：龍眼，動物傳播
    b += '<g transform="translate(0 24)">' + twig(30, 70, 360, 100)
    for lx, ang in ((90, 40), (170, 55), (250, 60)):
        ly = 76 + (lx - 30) * .09
        b += leaf(lx, ly, 70, 17, ang, "elliptic", "entire", "net", detail=False) + leaf(lx, ly, 62, 16, ang - 38, "elliptic", "entire", "net", detail=False)
    for fx, fy in ((196, 138), (222, 148), (214, 170), (240, 134), (180, 162), (240, 164), (205, 191)):
        b += ln(fx, fy, 218, 90, "#7a6a45", 1) + circ(fx, fy, 13, U("lon"), INK, 1) + circ(fx - 4, fy - 4, 3, "#fff", "none", 0).replace('fill="#fff"', 'fill="#fff" opacity=".35"')
    b += tube(qb((240, 176), (300, 172), (372, 164), 10), 6, 4, U("bark"), INK, .9) + bird(306, 124, 1.0, True) + "</g>"
    b += arrow(290, 210, 336, 300, "#c2402a", 1.6, "5 4")
    b += ell(342, gy - 6, 5, 7, "#4a3320", "none", 0) + sprout(372, gy + 2)
    b += txt(40, 40, "動物傳播：龍眼、木瓜", 18, "#1f1f1f", "bold") + txt(40, 62, "果實芳香甜美，吸引動物來吃", 13, "#666")
    b += txt(20, 150, "① 動物吃果實", 13, "#444") + txt(262, 232, "② 動物離開後，", 13, "#444") + txt(262, 250, "種子隨糞便排出", 13, "#444")
    b += txt(20, 300, "③ 種子落在適合", 13, "#444") + txt(20, 318, "的地方，長成新植物", 13, "#444")
    # 右：臺灣欒樹，風力傳播
    b += '<g transform="translate(0 26)">' + twig(430, 80, 760, 62)
    for lx in (480, 570, 660):
        ly = 76 - (lx - 430) * .05
        b += leaf(lx, ly, 78, 14, 35, "lanceolate", "serrate", "net", detail=False) + leaf(lx + 6, ly, 72, 13, 60, "lanceolate", "serrate", "net", detail=False)
    for fx, fy in ((520, 140), (560, 160), (600, 136), (640, 158), (500, 188), (590, 204)):
        b += pa(f"M{fx},{fy-30} Q{fx+4},{fy-60} {fx+(560-fx)*.2:.0f},64", "none", "#7a6a45", 1) + lantern(fx, fy, 0.9, rng.uniform(-8, 8))
    b += "</g>"
    for yy in (130, 170, 210):
        b += pa(f"M668,{yy} q18,-12 36,0 t36,0 t30,0", "none", "#7fa8c8", 2)
    b += txt(735, 118, "風", 16, "#4f7fa6", "bold")
    b += pa("M600,250 C640,285 700,280 735,322", "none", "#c2402a", 1.6, extra='stroke-dasharray="5 4"')
    b += lantern(735, 352, .8, 24) + sprout(770, gy + 2)
    inner = pa(smc([(470, 270), (494, 290), (494, 322), (470, 342), (446, 322), (446, 290)]), U("lan"), "#a8452a", 1.4)
    for sx, sy in ((460, 296), (480, 296), (470, 318)):
        inner += circ(sx, sy, 7, "#2c2420", "none", 0) + circ(sx - 2, sy - 2, 1.6, "#8a7d70", "none", 0)
    b += inset("cap", 470, 306, 50, '<rect x="400" y="250" width="140" height="120" fill="#fff7ee"/>' + inner)
    b += txt(470, 378, "果實剖面：種子在裡面", 12, "#555", "normal", "middle")
    b += txt(430, 40, "風力傳播：臺灣欒樹", 18, "#1f1f1f", "bold") + txt(430, 62, "果實像氣球（燈籠）、很輕，種子隨風飄", 13, "#666")
    return svg(W, H, "種子的傳播：龍眼靠動物吃果實帶走種子，臺灣欒樹的果實像氣球、種子隨風飄", b)


FIGS = {"plant-overview": overview, "leaf-detail": leaf_detail, "stem-types": stems, "root-types": roots,
        "flower": flower, "fruit-seed": fruit_seed, "dispersal": dispersal}


def inject():
    p = pathlib.Path(__file__).resolve().parent.parent / "science" / "notes.html"
    html = p.read_text(encoding="utf-8")
    for key, fn in FIGS.items():
        a, b = f"<!-- fig:{key} -->", f"<!-- /fig:{key} -->"
        i, k = html.index(a) + len(a), html.index(b)
        html = html[:i] + "\n" + fn() + "\n" + html[k:]
    p.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    inject()
    print("ok")
