"""產生自然重點整理用的手繪風格植物構造圖（根莖葉總覽、葉脈、三種莖、兩種根）。
執行：python3 tools/make_plant_svg.py  → 把圖嵌進 science/notes.html 的 <!-- fig:... --> 標記之間
"""
import math, pathlib, random
import make_family_svg as base  # 共用手繪線條、圓形、文字函式

base.R = random.Random(11)
R = base.R
j, rough_line, rough_circle, text = base.j, base.rough_line, base.rough_circle, base.text

INK = "#3b3530"
GREEN, GREEN_D = "#cfe8bd", "#6f9a55"
BROWN, SOIL = "#d9b48a", "#f1e4d0"
HEAD = 'xmlns="http://www.w3.org/2000/svg"'


def svg(w, h, label, body):
    frame = f'<rect x="3" y="3" width="{w-6}" height="{h-6}" rx="10" fill="#fffdf8" stroke="#8a8378" stroke-width="1.6"/>'
    return f'<svg viewBox="0 0 {w} {h}" {HEAD} role="img" aria-label="{label}">{frame}{body}</svg>'


def leaf(x, y, L, W, ang, serrate=False, veins="net", fill=GREEN):
    """葉片：基部在 (x,y)，朝 ang 度（順時針，0=向右）延伸 L。"""
    top, bot = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        w = W * (math.sin(math.pi * t) ** 0.85)
        if serrate and 0 < i < n:
            w += (3.5 if i % 2 else -1)
        top.append((t * L + j(0.6), -w + j(0.6)))
        bot.append((t * L + j(0.6), w + j(0.6)))
    pts = top + bot[::-1]
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    g = f'<polygon points="{poly}" fill="{fill}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
    v = []
    if veins == "net":
        v.append(f'<line x1="0" y1="0" x2="{L*0.95:.1f}" y2="0"/>')
        for t in (0.2, 0.35, 0.5, 0.65, 0.8):
            for s in (-1, 1):
                x1 = t * L
                x2 = min(t + 0.14, 0.95) * L
                yy = s * W * (math.sin(math.pi * (t + 0.12)) ** 0.85) * 0.82
                v.append(f'<path d="M{x1:.1f},0 Q{x1+8:.1f},{s*W*0.3:.1f} {x2:.1f},{yy:.1f}"/>')
    elif veins == "parallel":
        for k in (-0.6, -0.3, 0, 0.3, 0.6):
            v.append(f'<path d="M0,{k*W*0.4:.1f} Q{L*0.5:.1f},{k*W*0.95:.1f} {L*0.95:.1f},0"/>')
    if v:
        g += f'<g fill="none" stroke="{GREEN_D}" stroke-width="1.5" stroke-linecap="round">{"".join(v)}</g>'
    return f'<g transform="translate({x} {y}) rotate({ang})">{g}</g>'


def note(x1, y1, x2, y2, tx, ty, main, sub="", anchor="middle"):
    """標註：從 (x1,y1) 拉線到 (x2,y2)，文字放在 (tx,ty)。"""
    g = rough_line(x1, y1, x2, y2, "#c2572e", 1.8, 1)
    g += f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="#c2572e"/>'
    g += text(tx, ty, main, 21, "#2b2a27", "bold", anchor)
    if sub:
        g += text(tx, ty + 22, sub, 15, "#6d685f", "normal", anchor)
    return g


def ground(x1, x2, y, bottom):
    s = f'<polygon points="{x1},{y} {x2},{y} {x2},{bottom} {x1},{bottom}" fill="{SOIL}"/>'
    return s + rough_line(x1, y, x2, y, "#8a6a43", 2.4, 2)


def stem(x, y_base, y_top, w=12, fill=BROWN):
    pts = f"{x-w/2},{y_base} {x+w/2},{y_base} {x+w/2*0.7},{y_top} {x-w/2*0.7},{y_top}"
    return f'<polygon points="{pts}" fill="{fill}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'


# ---------- 圖一：根莖葉總覽 ----------
def overview():
    W, H, gy = 720, 400, 240
    b = f'<rect x="3" y="{gy}" width="{W-6}" height="{H-gy-3}" rx="10" fill="{SOIL}"/>' + rough_line(6, gy, W - 6, gy, "#8a6a43", 2.4, 2)
    # 太陽
    b += rough_circle(80, 62, 22, "#d99a00", "#ffe27a", 2.2)
    for k in range(10):
        a = k * math.pi / 5
        b += rough_line(80 + 30 * math.cos(a), 62 + 30 * math.sin(a), 80 + 42 * math.cos(a), 62 + 42 * math.sin(a), "#d99a00", 2, 1)
    b += text(80, 124, "陽光", 18, "#a06f00", "bold")
    b += rough_line(120, 76, 290, 118, "#d99a00", 2, 1, "6 6")
    # 莖
    sx = 360
    b += stem(sx, gy, 60, 14)
    # 葉
    for y, side in ((200, 1), (160, -1), (118, 1), (86, -1)):
        ang = -32 if side == 1 else -148
        b += leaf(sx, y, 105, 24, ang)
    b += leaf(sx, 62, 60, 17, -90)
    # 根：軸根
    root = f'<polygon points="{sx-8},{gy} {sx+8},{gy} {sx+2},{gy+120} {sx-2},{gy+120}" fill="#e8cfa6" stroke="{INK}" stroke-width="1.8"/>'
    for k, (dy, dx, dy2) in enumerate(((28, 70, 52), (52, -78, 76), (78, 62, 100), (100, -55, 118))):
        sgn = 1 if dx > 0 else -1
        root += rough_line(sx + sgn * 3, gy + dy, sx + dx, gy + dy2, "#a07840", 2.2, 1)
    b += root
    # 水往根移動
    for (x, y, tx, ty) in ((520, 300, 440, 290), (200, 330, 280, 310)):
        b += rough_line(x, y, tx, ty, "#2f78b5", 2, 1, "5 5")
    b += text(540, 304, "水", 19, "#2f78b5", "bold") + text(180, 340, "水", 19, "#2f78b5", "bold")
    # 標註
    b += note(442, 104, 575, 70, 600, 56, "葉", "接收陽光")
    b += note(sx - 7, 215, 190, 232 - 40, 150, 168, "莖", "支撐植物、往陽光長")
    b += note(sx + 3, gy + 100, 520, 372, 590, 366, "根", "固定植物、吸收水分")
    return svg(W, H, "植物構造總覽：葉接收陽光，莖支撐植物並往陽光生長，根固定植物並吸收水分", b)


# ---------- 圖二：葉脈與葉緣 ----------
def leaf_detail():
    W, H = 720, 330
    b = ""
    # 左：網狀脈 桂花（葉緣平滑）
    b += rough_line(70, 190, 100, 190, BROWN, 5, 1)
    b += leaf(100, 190, 230, 62, 0, False, "net")
    b += note(205, 190, 205, 100, 205, 62, "葉脈", "網狀脈：像一張網")
    b += note(190, 131, 118, 104, 80, 90, "葉緣", "平滑")
    b += note(85, 190, 70, 246, 70, 268, "葉柄")
    b += text(215, 300, "桂花（網狀脈）", 19, "#2b2a27", "bold")
    # 右：平行脈 百合（細長）
    b += rough_line(400, 190, 430, 190, BROWN, 5, 1)
    b += leaf(430, 190, 260, 36, 0, False, "parallel")
    b += note(560, 190, 560, 118, 560, 62, "葉脈", "平行脈：一條條平行")
    b += note(600, 221, 640, 246, 640, 266, "葉緣", "平滑")
    b += text(560, 300, "百合（平行脈）", 19, "#2b2a27", "bold")
    return svg(W, H, "兩種葉脈：桂花是網狀脈，百合是平行脈，並標示葉柄與葉緣", b)


# ---------- 圖三：三種莖 ----------
def stems():
    W, H, gy = 720, 350, 270
    b = f'<rect x="3" y="{gy}" width="{W-6}" height="{H-gy-3}" rx="10" fill="{SOIL}"/>' + rough_line(6, gy, W - 6, gy, "#8a6a43", 2.4, 2)
    # 木本：粗壯樹幹
    cx = 120
    b += stem(cx, gy, 140, 30, "#c9a173")
    b += rough_line(cx, 190, cx - 40, 150, INK, 5, 1) + rough_line(cx, 175, cx + 42, 140, INK, 5, 1)
    b += rough_circle(cx - 8, 105, 52, GREEN_D, GREEN, 2.2) + rough_circle(cx + 46, 130, 30, GREEN_D, GREEN, 2.0) + rough_circle(cx - 50, 140, 28, GREEN_D, GREEN, 2.0)
    b += text(cx, gy + 38, "木本莖", 21, "#2b2a27", "bold") + text(cx, gy + 62, "粗壯、長得高", 15, "#6d685f")
    # 草本：細莖、多枝條
    cx = 360
    for dx, top in ((-30, 130), (-10, 90), (12, 110), (32, 150)):
        b += rough_line(cx, gy, cx + dx * 1.3, top, "#5f8f48", 3, 1)
        b += leaf(cx + dx * 1.3, top, 32, 9, -90 + dx, False, None)
        b += leaf(cx + dx * 1.3, top + 28, 28, 8, -20 if dx > 0 else -160, False, None)
    b += text(cx, gy + 38, "草本莖", 21, "#2b2a27", "bold") + text(cx, gy + 62, "較細、枝條多", 15, "#6d685f")
    # 藤本：纏繞支柱
    cx = 600
    b += stem(cx, gy, 60, 8, "#c8c3b8")
    pts = []
    for i in range(0, 41):
        y = gy - i * 5
        pts.append((cx + 20 * math.sin(i * 0.55) + j(0.4), y))
    d = "M" + " L".join(f"{a:.1f},{b_:.1f}" for a, b_ in pts)
    b += f'<path d="{d}" fill="none" stroke="#5f8f48" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
    for i in (6, 14, 22, 30):
        px, py = pts[i]
        side = 1 if i % 2 == 0 else -1
        b += leaf(px, py, 28, 10, -20 if side == 1 else -160, False, None)
    b += text(cx, gy + 38, "藤本莖", 21, "#2b2a27", "bold") + text(cx, gy + 62, "柔軟、要攀爬", 15, "#6d685f")
    b += text(cx + 62, 120, "支柱", 16, "#8a8378")
    return svg(W, H, "三種莖：木本莖粗壯，草本莖較細，藤本莖柔軟要纏繞支柱攀爬", b)


# ---------- 圖四：軸根與鬚根 ----------
def roots():
    W, H, gy = 720, 350, 90
    b = f'<rect x="3" y="{gy}" width="{W-6}" height="{H-gy-3-60}" fill="{SOIL}"/>' + rough_line(6, gy, W - 6, gy, "#8a6a43", 2.4, 2)
    b += f'<rect x="3" y="{H-63}" width="{W-6}" height="60" rx="10" fill="#fffdf8"/>'
    # 地面上小植物
    for cx in (180, 540):
        b += rough_line(cx, gy, cx, 38, "#5f8f48", 4, 1)
        b += leaf(cx, 60, 36, 11, -30, False, None) + leaf(cx, 48, 36, 11, -150, False, None)
    # 軸根
    cx = 180
    b += f'<polygon points="{cx-9},{gy} {cx+9},{gy} {cx+3},{gy+160} {cx-3},{gy+160}" fill="#e8cfa6" stroke="{INK}" stroke-width="1.8"/>'
    for k, (dy, dx, dy2) in enumerate(((22, -62, 44), (40, 70, 66), (66, -58, 94), (88, 60, 118), (112, -42, 140), (132, 40, 156))):
        sgn = 1 if dx > 0 else -1
        b += rough_line(cx + sgn * 5, gy + dy, cx + dx, gy + dy2, "#a07840", 2.2, 1)
    b += text(cx, H - 38, "軸根", 21, "#2b2a27", "bold") + text(cx, H - 14, "一條粗根＋旁邊細根（小白菜）", 15, "#6d685f")
    b += rough_line(cx + 110, gy + 20, cx + 110, gy + 160, "#c2572e", 1.8, 1) + text(cx + 112, gy + 100, "深入土壤", 15, "#c2572e", "bold", "start")
    # 鬚根
    cx = 540
    for k in range(13):
        dx = -92 + k * 15.5
        dy = 55 + 22 * math.cos(k * 0.9) + j(4)
        b += f'<path d="M{cx},{gy} Q{cx+dx*0.45:.1f},{gy+dy*0.55:.1f} {cx+dx:.1f},{gy+dy:.1f}" fill="none" stroke="#a07840" stroke-width="2.2" stroke-linecap="round"/>'
    b += text(cx, H - 38, "鬚根", 21, "#2b2a27", "bold") + text(cx, H - 14, "全部細細的像鬍鬚（蔥、蒜）", 15, "#6d685f")
    b += rough_line(cx + 100, gy + 10, cx + 100, gy + 72, "#c2572e", 1.8, 1) + text(cx + 140, gy + 46, "土壤淺層", 15, "#c2572e", "bold")
    return svg(W, H, "兩種根：軸根有一條粗根深入土壤，鬚根細小分布在土壤淺層", b)


# ---------- 圖五：花的構造 ----------
def flower():
    W, H = 720, 360
    cx, cy = 300, 150
    b = rough_line(cx, cy + 40, cx, 335, "#5f8f48", 5, 1)
    b += leaf(cx, 285, 70, 18, -25, False, None) + leaf(cx, 270, 70, 18, -155, False, None)
    # 花萼（花下方的綠色小片）
    for a in (-60, 0, 60):
        b += leaf(cx, cy + 46, 46, 12, 90 + a, False, None, "#9cc98a")
    # 花瓣
    for k in range(6):
        a = k * 60 - 90
        b += leaf(cx, cy, 82, 24, a, False, None, "#ffc9d6")
    # 雌蕊（中間一根）+ 雄蕊
    b += f'<rect x="{cx-5}" y="{cy-30}" width="10" height="46" rx="5" fill="#9bd07a" stroke="{INK}" stroke-width="1.8"/>'
    b += rough_circle(cx, cy - 34, 8, INK, "#7fbf5a", 1.8)
    for dx in (-26, -16, 16, 26):
        b += rough_line(cx + dx * 0.4, cy + 12, cx + dx, cy - 22, INK, 1.8, 1)
        b += rough_circle(cx + dx, cy - 26, 5.5, "#c28a00", "#ffd34d", 1.6)
    # 標註
    b += note(358, 118, 490, 44, 500, 38, "花瓣", "顏色鮮豔，吸引動物", "start")
    b += note(326, 124, 490, 104, 500, 98, "雄蕊", "頂端有花粉（小蕊）", "start")
    b += note(300, 135, 490, 164, 500, 158, "雌蕊", "通常一根，在中間（大蕊）", "start")
    b += note(312, 200, 490, 224, 500, 218, "花萼", "在花瓣下面，保護花苞", "start")
    b += text(120, 330, "花粉傳到雌蕊，才能結果實", 17, "#6d685f")
    return svg(W, H, "花的構造：花萼、花瓣、雄蕊、雌蕊", b)


# ---------- 圖六：花 → 果實 → 種子 ----------
def fruit_seed():
    W, H = 720, 280
    b = ""
    xs = (90, 260, 430, 620)
    # 1 花
    cx, cy = xs[0], 110
    b += rough_line(cx, cy + 20, cx, 190, "#5f8f48", 4, 1)
    for k in range(5):
        b += leaf(cx, cy, 36, 12, k * 72 - 90, False, None, "#ffc9d6")
    b += rough_circle(cx, cy, 7, "#c28a00", "#ffd34d", 1.8)
    # 2 未成熟果實（綠）
    cx = xs[1]
    b += rough_line(cx, 60, cx, 100, "#5f8f48", 4, 1)
    b += rough_circle(cx, 140, 38, INK, "#b9d98a", 2.2)
    # 3 成熟果實（紅）
    cx = xs[2]
    b += rough_line(cx, 60, cx, 100, "#5f8f48", 4, 1)
    b += rough_circle(cx, 140, 42, INK, "#f08a6a", 2.2)
    b += leaf(cx, 100, 30, 9, -30, False, None)
    # 4 剖開：種子
    cx = xs[3]
    b += rough_circle(cx, 140, 48, INK, "#f4a98c", 2.2)
    b += rough_circle(cx, 140, 34, "#c9744f", "#ffe9c9", 1.6)
    for dx, dy in ((-14, -8), (12, -12), (0, 8), (-10, 16), (16, 10)):
        b += f'<ellipse cx="{cx+dx}" cy="{140+dy}" rx="5" ry="7" fill="#7a4b2a" stroke="{INK}" stroke-width="1.2"/>'
    for a in range(0, 3):
        pass
    for x1, x2 in ((xs[0] + 55, xs[1] - 55), (xs[1] + 55, xs[2] - 58), (xs[2] + 58, xs[3] - 62)):
        b += rough_line(x1, 140, x2, 140, "#c2572e", 2.2, 1) + f'<path d="M{x2-8},132 L{x2},140 L{x2-8},148" fill="none" stroke="#c2572e" stroke-width="2.2" stroke-linecap="round"/>'
    for x, t, sub in ((xs[0], "花", "開花後"), (xs[1], "未成熟果實", "綠色、還硬"), (xs[2], "成熟果實", "顏色鮮豔"), (xs[3], "種子", "果實裡面")):
        b += text(x, 228, t, 20, "#2b2a27", "bold") + text(x, 252, sub, 15, "#6d685f")
    return svg(W, H, "花開後結出未成熟果實，長大成熟，剖開果實裡面有種子", b)


# ---------- 圖七：種子傳播 ----------
def dispersal():
    W, H, gy = 720, 300, 220
    b = f'<rect x="3" y="{gy}" width="{W-6}" height="{H-gy-3}" rx="10" fill="{SOIL}"/>' + rough_line(6, gy, W - 6, gy, "#8a6a43", 2.4, 2)
    # 左：動物吃果實（龍眼、木瓜）
    cx = 170
    b += rough_circle(cx - 60, 110, 24, INK, "#d9a960", 2.0) + rough_circle(cx - 20, 100, 24, INK, "#d9a960", 2.0)
    b += rough_line(cx - 60, 86, cx - 40, 60, "#5f8f48", 3, 1) + rough_line(cx - 20, 76, cx - 40, 60, "#5f8f48", 3, 1)
    # 小鳥
    bx, by = cx + 50, 110
    b += f'<ellipse cx="{bx}" cy="{by}" rx="22" ry="14" fill="#8fb8e0" stroke="{INK}" stroke-width="1.8"/>'
    b += rough_circle(bx + 20, by - 10, 9, INK, "#8fb8e0", 1.8)
    b += f'<polygon points="{bx+28},{by-12} {bx+40},{by-9} {bx+28},{by-6}" fill="#f0a030" stroke="{INK}" stroke-width="1.2"/>'
    b += f'<polygon points="{bx-22},{by} {bx-42},{by-8} {bx-38},{by+6}" fill="#6f9fd0" stroke="{INK}" stroke-width="1.6"/>'
    b += rough_line(cx + 60, by + 30, cx + 110, gy - 6, "#c2572e", 2, 1, "6 6")
    b += f'<ellipse cx="{cx+112}" cy="{gy-8}" rx="5" ry="7" fill="#7a4b2a" stroke="{INK}" stroke-width="1.2"/>'
    b += text(cx, 262, "龍眼、木瓜", 20, "#2b2a27", "bold") + text(cx, 286, "果實芳香甜美，動物吃了把種子帶走", 14, "#6d685f")
    # 右：風（臺灣欒樹，像氣球）
    cx = 520
    for dx, dy in ((-50, 90), (0, 70), (50, 100)):
        b += f'<ellipse cx="{cx+dx}" cy="{dy}" rx="20" ry="26" fill="#f7c68a" stroke="{INK}" stroke-width="2"/>'
        b += rough_line(cx + dx, dy - 26, cx + dx * 0.4, 36, "#5f8f48", 2.6, 1)
        b += f'<ellipse cx="{cx+dx}" cy="{dy}" rx="5" ry="6" fill="#4a3320"/>'
    for y in (120, 150, 180):
        b += f'<path d="M{cx+80},{y} q20,-12 40,0 t40,0" fill="none" stroke="#7fa8c8" stroke-width="2.4" stroke-linecap="round"/>'
    b += text(cx + 30, 210, "風", 17, "#4f7fa6", "bold")
    b += text(cx, 262, "臺灣欒樹", 20, "#2b2a27", "bold") + text(cx, 286, "果實像氣球，種子隨風飄", 14, "#6d685f")
    return svg(W, H, "種子的傳播：動物吃果實帶走種子，臺灣欒樹的果實像氣球隨風飄", b)


FIGS = {"plant-overview": overview, "leaf-detail": leaf_detail, "stem-types": stems, "root-types": roots, "flower": flower, "fruit-seed": fruit_seed, "dispersal": dispersal}


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
