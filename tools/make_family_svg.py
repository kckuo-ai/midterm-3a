"""產生社會重點整理用的手繪風格家庭圖（家庭的組成、親屬稱謂階層圖）。
執行：python3 tools/make_family_svg.py  → 直接把兩張圖嵌進 social/notes.html 的 <!-- fig:... --> 標記之間
"""
import random, math, pathlib

R = random.Random(7)
FONT = "'LXGW WenKai TC','Kaiti TC','BiauKai','DFKai-SB',serif"

def j(a=1.6):
    return R.uniform(-a, a)

def rough_line(x1, y1, x2, y2, color="#3b3530", w=2.2, passes=2, dash=None):
    out = []
    for p in range(passes):
        mx, my = (x1 + x2) / 2 + j(2.2), (y1 + y2) / 2 + j(2.2)
        d = f"M{x1+j():.1f},{y1+j():.1f} Q{mx:.1f},{my:.1f} {x2+j():.1f},{y2+j():.1f}"
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        op = 1 if p == 0 else 0.55
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w if p==0 else w*0.7:.1f}" stroke-linecap="round" opacity="{op}"{extra}/>')
    return "".join(out)

def rough_rect(x, y, w, h, stroke="#3b3530", fill="#fff", sw=2.2):
    # 不規則的填色底 + 兩次描邊
    pts = [(x + j(2), y + j(2)), (x + w + j(2), y + j(2)), (x + w + j(2), y + h + j(2)), (x + j(2), y + h + j(2))]
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    s = f'<polygon points="{poly}" fill="{fill}" stroke="none"/>'
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        (ax, ay), (bx, by) = corners[i], corners[(i + 1) % 4]
        # 稍微超出角落，像手畫
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        s += rough_line(ax - ux * 3, ay - uy * 3, bx + ux * 3, by + uy * 3, stroke, sw)
    return s

def text(x, y, t, size=20, color="#2b2a27", weight="normal", anchor="middle"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" font-family="{FONT}">{t}</text>'

def rough_circle(cx, cy, r, stroke="#3b3530", fill="none", sw=2.0):
    out = []
    for p in range(2):
        pts = []
        start = R.uniform(0, 6.28)
        n = 22
        for k in range(n + 2):
            a = start + 2 * math.pi * k / n
            rr = r + j(r * 0.08)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        out.append(f'<path d="{d}" fill="{fill if p==0 else "none"}" stroke="{stroke}" stroke-width="{sw if p==0 else sw*0.7:.1f}" stroke-linejoin="round" opacity="{1 if p==0 else 0.5}"/>')
    return "".join(out)

# ---------- 圖一：家庭的組成 ----------
def person(cx, base, s=1.0, label="", color="#c2572e", hair=None):
    """火柴人：base 是腳底的 y。"""
    r = 11 * s
    head_y = base - 62 * s
    g = rough_circle(cx, head_y, r, "#3b3530", "#ffe9d6", 1.8)
    if hair == "gray":
        g += f'<path d="M{cx-r:.1f},{head_y-2:.1f} Q{cx:.1f},{head_y-r-7*s:.1f} {cx+r:.1f},{head_y-2:.1f}" fill="#cfcfcf" stroke="#8a8a8a" stroke-width="1.5"/>'
    neck = head_y + r
    hip = base - 22 * s
    # 身體（三角形衣服）
    body = [(cx, neck), (cx - 13 * s, hip), (cx + 13 * s, hip)]
    g += f'<polygon points="{" ".join(f"{a+j(1):.1f},{b+j(1):.1f}" for a,b in body)}" fill="{color}" opacity="0.85" stroke="#3b3530" stroke-width="1.6"/>'
    g += rough_line(cx - 4 * s, neck + 8 * s, cx - 17 * s, neck + 24 * s, "#3b3530", 1.8, 1)
    g += rough_line(cx + 4 * s, neck + 8 * s, cx + 17 * s, neck + 24 * s, "#3b3530", 1.8, 1)
    g += rough_line(cx - 6 * s, hip, cx - 8 * s, base, "#3b3530", 1.8, 1)
    g += rough_line(cx + 6 * s, hip, cx + 8 * s, base, "#3b3530", 1.8, 1)
    if label:
        g += text(cx, base + 20, label, 16)
    return g

def family_types():
    W, H = 980, 262
    panels = [
        ("爸爸、媽媽和我", "", [("爸爸", 1, "#4a7fbf", None), ("媽媽", 1, "#d9667a", None), ("我", .72, "#f2b33d", None)]),
        ("外婆、爸媽和妹妹", "三代同住", [("外婆", .95, "#8e7cc3", "gray"), ("爸爸", 1, "#4a7fbf", None), ("媽媽", 1, "#d9667a", None), ("妹妹", .65, "#f2b33d", None)]),
        ("爸爸、弟弟和我", "單親", [("爸爸", 1, "#4a7fbf", None), ("弟弟", .62, "#5fb08a", None), ("我", .72, "#f2b33d", None)]),
        ("爺爺、奶奶和我", "和祖父母住", [("爺爺", .95, "#6b8f71", "gray"), ("奶奶", .95, "#c98b5a", "gray"), ("我", .72, "#f2b33d", None)]),
        ("育幼院", "老師和孩子也是家人", [("老師", 1, "#4a7fbf", None), ("哥哥", .8, "#5fb08a", None), ("姊姊", .78, "#d9667a", None), ("我", .62, "#f2b33d", None)]),
    ]
    pw, gap = 186, 7
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="五種不同的家庭組成">']
    for i, (title, tag, people) in enumerate(panels):
        x = 6 + i * (pw + gap)
        out.append(rough_rect(x, 6, pw, 250, "#8a8378", "#fffdf8", 1.8))
        if title == "育幼院":
            # 屋頂
            out.append(rough_line(x + 16, 62, x + pw / 2, 22, "#8a8378", 2))
            out.append(rough_line(x + pw / 2, 22, x + pw - 16, 62, "#8a8378", 2))
        n = len(people)
        span = pw - 36
        for k, (name, s, col, hair) in enumerate(people):
            cx = x + 18 + span * (k + 0.5) / n
            out.append(person(cx, 172, s * 1.3, name, col, hair))
        out.append(text(x + pw / 2, 218, title, 19, weight="bold"))
        if tag:
            hl = tag == "單親"
            if hl:
                out.append(f'<rect x="{x+pw/2-26}" y="227" width="52" height="24" rx="4" fill="#fff1a8"/>')
            out.append(text(x + pw / 2, 245, tag, 16 if not hl else 18, "#6d685f" if not hl else "#c0392b", "bold" if hl else "normal"))
    out.append("</svg>")
    return "".join(out)

# ---------- 圖二：親屬稱謂階層圖 ----------
DAD_FILL, DAD_LINE = "#fde3d3", "#c2572e"
MOM_FILL, MOM_LINE = "#dbeaf8", "#3f78b5"
TANG_FILL, TANG_LINE = "#d9efd6", "#2f7d5b"
BIAO_FILL, BIAO_LINE = "#e8e0fa", "#6a4fb3"

def node(cx, y, w, h, main, sub, fill, line, main_size=24, sub_size=15):
    s = rough_rect(cx - w / 2, y, w, h, line, fill, 2.2)
    if sub:
        s += text(cx, y + h / 2 + 1, main, main_size, weight="bold")
        s += text(cx, y + h / 2 + 22, sub, sub_size, "#5b554c")
    else:
        s += text(cx, y + h / 2 + 8, main, main_size, weight="bold")
    return s

def kid_node(cx, y, kind):
    w, h = 112, 84
    if kind == "堂":
        s = rough_rect(cx - w / 2, y, w, h, TANG_LINE, TANG_FILL, 2.4)
        s += text(cx, y + 34, "堂哥　堂姐", 18, weight="bold") + text(cx, y + 62, "堂弟　堂妹", 18, weight="bold")
    elif kind == "表":
        s = rough_rect(cx - w / 2, y, w, h, BIAO_LINE, BIAO_FILL, 2.4)
        s += text(cx, y + 34, "表哥　表姐", 18, weight="bold") + text(cx, y + 62, "表弟　表妹", 18, weight="bold")
    else:
        s = rough_rect(cx - w / 2 - 14, y, w + 28, h, "#b8860b", "#fff1a8", 2.6)
        s += text(cx, y + 36, "★ 我", 24, "#c0392b", "bold") + text(cx, y + 64, "和兄弟姊妹", 17)
    return s

def family_tree():
    W, H = 980, 700
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="親屬稱謂階層圖：爺爺奶奶、外公外婆在三樓，爸媽和伯伯叔叔姑姑舅舅阿姨在二樓，我和堂表兄弟姊妹在一樓">']
    # 樓層色帶與標籤
    floors = [(52, 132, "3樓", "爺爺奶奶", "那一輩"), (196, 304, "2樓", "爸爸媽媽", "那一輩"), (394, 500, "1樓", "我", "這一輩")]
    for y1, y2, f, a, b in floors:
        o.append(rough_rect(4, y1, 972, y2 - y1, "#e6e0d4", "#f6f1e6", 1.2))
        o.append(text(42, y1 + (y2 - y1) / 2 - 10, f, 26, "#8a5a2b", "bold"))
        o.append(text(42, y1 + (y2 - y1) / 2 + 14, a, 14, "#6d685f"))
        o.append(text(42, y1 + (y2 - y1) / 2 + 31, b, 14, "#6d685f"))
    # 樓梯箭頭：輩分
    o.append(text(42, 34, "↑輩分高", 15, "#8a5a2b", "bold"))
    # 兩邊標題
    o.append(text(340, 32, "爸爸的親人", 22, DAD_LINE, "bold"))
    o.append(text(795, 32, "媽媽的親人", 22, MOM_LINE, "bold"))

    # 第三代（祖父母）
    y1, h1 = 62, 62
    o.append(node(280, y1, 100, h1, "爺爺", "（祖父）", DAD_FILL, DAD_LINE))
    o.append(node(400, y1, 100, h1, "奶奶", "（祖母）", DAD_FILL, DAD_LINE))
    o.append(rough_line(330, y1 + 31, 350, y1 + 31, DAD_LINE, 2.5, 1))
    o.append(node(735, y1, 100, h1, "外公", "（外祖父）", MOM_FILL, MOM_LINE))
    o.append(node(855, y1, 100, h1, "外婆", "（外祖母）", MOM_FILL, MOM_LINE))
    o.append(rough_line(785, y1 + 31, 805, y1 + 31, MOM_LINE, 2.5, 1))

    # 第二代
    y2, h2, w2 = 208, 84, 106
    dad_kids = [(140, "伯伯", "＋伯母"), (260, "叔叔", "＋嬸嬸"), (380, "姑姑", "＋姑丈"), (500, "爸爸", "")]
    mom_kids = [(660, "媽媽", ""), (785, "舅舅", "＋舅媽"), (910, "阿姨", "＋姨丈")]
    bar = 172
    # 樹枝：爺爺奶奶 → 子女
    o.append(rough_line(340, y1 + 31, 340, bar, DAD_LINE, 2.4))
    o.append(rough_line(140, bar, 500, bar, DAD_LINE, 2.4))
    for cx, *_ in dad_kids:
        o.append(rough_line(cx, bar, cx, y2, DAD_LINE, 2.4))
    o.append(rough_line(795, y1 + 31, 795, bar, MOM_LINE, 2.4))
    o.append(rough_line(660, bar, 910, bar, MOM_LINE, 2.4))
    for cx, *_ in mom_kids:
        o.append(rough_line(cx, bar, cx, y2, MOM_LINE, 2.4))
    for cx, m, s in dad_kids:
        o.append(node(cx, y2, w2, h2, m, s, DAD_FILL, DAD_LINE, 26))
    for cx, m, s in mom_kids:
        o.append(node(cx, y2, w2, h2, m, s, MOM_FILL, MOM_LINE, 26))
    # 爸爸 ♥ 媽媽
    o.append(rough_line(555, y2 + 42, 605, y2 + 42, "#c0392b", 2.6))
    o.append(text(580, y2 + 34, "♥", 22, "#c0392b"))
    o.append(text(580, y2 + 64, "結婚", 14, "#c0392b"))
    # 伯伯比爸爸大、叔叔比爸爸小（小註）
    o.append(text(140, y2 + 104, "比爸爸大", 14, "#6d685f"))
    o.append(text(260, y2 + 104, "比爸爸小", 14, "#6d685f"))

    # 第一代（我這一輩）
    y3 = 404
    kids = [(140, "堂"), (260, "堂"), (380, "表"), (580, "我"), (785, "表"), (910, "表")]
    for cx, k in kids:
        top = y2 + h2 if cx != 580 else y2 + 70
        col = {"堂": TANG_LINE, "表": BIAO_LINE, "我": "#b8860b"}[k]
        o.append(rough_line(cx, top + (24 if cx in (140, 260) else 0), cx, y3, col, 2.4))
        o.append(kid_node(cx, y3, k))

    # 圖例與口訣
    ly = 540
    o.append(rough_rect(70, ly, 840, 140, "#d8d0c2", "#fffdf8", 1.6))
    o.append(rough_rect(96, ly + 22, 34, 24, TANG_LINE, TANG_FILL, 2))
    o.append(text(142, ly + 41, "堂：只有「伯伯、叔叔」的孩子（爸爸的兄弟）", 19, anchor="start"))
    o.append(rough_rect(96, ly + 60, 34, 24, BIAO_LINE, BIAO_FILL, 2))
    o.append(text(142, ly + 79, "表：「姑姑、舅舅、阿姨」的孩子都是表", 19, anchor="start"))
    o.append(text(96, ly + 118, "爸爸的兄弟有兩種（伯伯、叔叔），媽媽的兄弟只有一種（舅舅）。", 18, "#5b554c", anchor="start"))
    o.append("</svg>")
    return "".join(o)



def inject():
    """把兩張圖嵌進 social/notes.html 的標記之間。"""
    root = pathlib.Path(__file__).resolve().parent.parent / "social"
    p = root / "notes.html"
    html = p.read_text(encoding="utf-8")
    for key, svg in (("family-types", family_types()), ("family-tree", family_tree())):
        a, b = f"<!-- fig:{key} -->", f"<!-- /fig:{key} -->"
        i, k = html.index(a) + len(a), html.index(b)
        html = html[:i] + "\n" + svg + "\n" + html[k:]
    p.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    inject()
    print("ok")
