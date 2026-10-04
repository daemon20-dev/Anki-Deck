"""Generate the hill / landscape SVG used in src/scene.html.

    python3 tools/gen_hills.py   # rewrites the <!-- hills --> block in src/scene.html
    python3 tools/build.py

Ridgelines are deterministic sums of sines, so re-running gives the same art.
Depth comes from atmospheric perspective: far layers are hazier (lighter at
their base, where mist settles), near layers are darker and sharper.
"""
import math
import pathlib
import re

W, H = 1440, 480
STEP = 20
SCENE = pathlib.Path(__file__).resolve().parent.parent / "src" / "scene.html"


def ridge(base, waves):
    return lambda x: base - sum(a * math.sin(x / p + ph) for a, p, ph in waves)


def peaks(base, height, spots):
    """Mountain range: soft-shouldered peaks at the given (x, scale) spots."""
    def f(x):
        y = base
        for cx, s in spots:
            d = (x - cx) / (160 * s)
            y -= height * s * math.exp(-d * d)
        y -= 4 * math.sin(x / 47) + 2.5 * math.sin(x / 19 + 1.3)   # gentle crags
        return y
    return f


def outline(f):
    pts = [(x, f(x)) for x in range(0, W + STEP, STEP)]
    d = f"M{pts[0][0]} {pts[0][1]:.0f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d += f" Q{x0} {y0:.0f} {(x0 + x1) / 2:.0f} {(y0 + y1) / 2:.0f}"
    return d + f" L{W} {pts[-1][1]:.0f}"


def hill(f, fill, rim=None, rim_op=0.0):
    line = outline(f)
    out = f'<path d="{line} L{W} {H} L0 {H}Z" fill="{fill}"/>'
    if rim:
        out += f'<path d="{line}" fill="none" stroke="{rim}" stroke-opacity="{rim_op}" stroke-width="1.2"/>'
    return out


def pine(x, base, h):
    """Three-tier pine with a short trunk."""
    w = h * 0.36
    tiers = []
    for i, (top, bot, wid) in enumerate([(0.0, 0.42, 0.55), (0.22, 0.70, 0.78), (0.45, 0.94, 1.0)]):
        yt, yb, hw = base - h + top * h, base - h + bot * h, w * wid
        tiers.append(f"M{x:.0f} {yt:.0f} L{x + hw:.0f} {yb:.0f} L{x - hw:.0f} {yb:.0f}Z")
    tiers.append(f"M{x - 1.2:.0f} {base - h * 0.08:.0f} h2.4 V{base + 4:.0f} h-2.4Z")
    return " ".join(tiers)


def treeline(f, clusters, seed):
    """Clusters of pines planted on ridge f: (x_start, x_end, count, max_h)."""
    rnd = seed
    paths = []
    for x0, x1, n, hmax in clusters:
        for i in range(n):
            rnd = (rnd * 1103515245 + 12345) % 2**31
            jitter = (rnd % 1000) / 1000
            x = x0 + (x1 - x0) * (i + jitter * 0.8) / n
            rnd = (rnd * 1103515245 + 12345) % 2**31
            h = hmax * (0.55 + 0.45 * ((rnd % 1000) / 1000))
            paths.append(pine(x, f(x) + 3, h))
    return " ".join(paths)


# ── Back group: mountains, far hills, mid hills, lake ─────────────────────
mountains = peaks(318, 105, [(140, 0.7), (380, 1.0), (560, 0.6), (930, 1.15), (1180, 0.75), (1380, 0.9)])
far = ridge(318, [(14, 210, 0.4), (9, 97, 2.1), (4, 41, 0.7)])
mid = ridge(368, [(18, 260, 2.5), (8, 113, 0.3), (3, 37, 1.9)])
lake_y = 412

back = (
    '<defs>'
    '<linearGradient id="gm-g-mtn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1636"/><stop offset=".6" stop-color="#141d44"/><stop offset="1" stop-color="#19244f"/></linearGradient>'
    '<linearGradient id="gm-g-far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1634"/><stop offset=".6" stop-color="#131c42"/><stop offset="1" stop-color="#18234d"/></linearGradient>'
    '<linearGradient id="gm-g-mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1029"/><stop offset="1" stop-color="#0e1636"/></linearGradient>'
    '<linearGradient id="gm-g-lake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2552"/><stop offset=".5" stop-color="#111a3e"/><stop offset="1" stop-color="#0a1030"/></linearGradient>'
    '<linearGradient id="gm-g-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3570" stop-opacity="0"/><stop offset="1" stop-color="#2a3570" stop-opacity=".3"/></linearGradient>'
    '</defs>'
    + hill(mountains, "url(#gm-g-mtn)", "#dfe6ff", 0.10)
    + f'<rect x="0" y="240" width="{W}" height="190" fill="url(#gm-g-haze)"/>'
    + hill(far, "url(#gm-g-far)", "#dfe6ff", 0.08)
    + hill(mid, "url(#gm-g-mid)", "#dfe6ff", 0.07)
    + f'<path fill="#0a1029" d="{treeline(mid, [(40, 260, 7, 22), (980, 1120, 5, 20)], 7)}"/>'
    # a still lake tucked into the valley, catching the moon
    + f'<path d="M560 {lake_y + 16} C680 {lake_y - 6} 860 {lake_y - 13} 1060 {lake_y - 13} '
      f'C1260 {lake_y - 13} 1380 {lake_y - 10} {W} {lake_y - 8} V{H} H560Z" fill="url(#gm-g-lake)"/>'
    + f'<path d="M640 {lake_y + 3} C800 {lake_y - 11} 1100 {lake_y - 13} {W} {lake_y - 8}" fill="none" stroke="#c9d4ff" stroke-opacity=".10" stroke-width="1"/>'
    + ''.join(
        f'<rect x="{x}" y="{lake_y - 10 + i * 5}" width="{w}" height="1.2" rx=".6" fill="#ffe9cf" fill-opacity="{op}"/>'
        for i, (x, w, op) in enumerate([(1000, 46, .30), (990, 70, .22), (1008, 34, .26), (982, 88, .14), (1012, 26, .18)])
    )
)

# ── Near group: foreground hill, dense pines, cabin ──────────────────────
near = ridge(430, [(16, 300, 1.2), (10, 140, 4.0), (3, 45, 0.5)])
cab_x = 820
cab_y = near(cab_x)
cabin = (
    f'<path fill="#04071a" d="M{cab_x - 20} {cab_y + 6} V{cab_y - 16} L{cab_x - 24} {cab_y - 14} L{cab_x} {cab_y - 34} '
    f'L{cab_x + 24} {cab_y - 14} L{cab_x + 20} {cab_y - 16} V{cab_y + 6}Z M{cab_x + 9} {cab_y - 24} V{cab_y - 36} h6 V{cab_y - 19}Z"/>'
    f'<circle cx="{cab_x - 5}" cy="{cab_y - 8}" r="30" fill="url(#gm-g-win)"/>'
    f'<rect x="{cab_x - 11}" y="{cab_y - 13}" width="12" height="9" rx="1" fill="#ffc27a"/>'
    f'<path d="M{cab_x - 5} {cab_y - 13} V{cab_y - 4} M{cab_x - 11} {cab_y - 8.5} H{cab_x + 1}" stroke="#04071a" stroke-width="1.2"/>'
)
front = (
    '<defs><radialGradient id="gm-g-win"><stop offset="0" stop-color="#ffb35c" stop-opacity=".45"/>'
    '<stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/></radialGradient></defs>'
    + hill(near, "#04071a", "#c9d4ff", 0.07)
    + f'<path fill="#04071a" d="{treeline(near, [(0, 230, 9, 64), (470, 640, 5, 46), (1180, 1440, 10, 70)], 3)}"/>'
    + cabin
)

VB = f'viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice"'
block = (
    "<!-- hills -->\n"
    f'  <div class="gm-layer gm-hills gm-hills--back"><svg {VB}>{back}</svg></div>\n'
    '  <div class="gm-layer gm-mist"></div>\n'
    f'  <div class="gm-layer gm-hills gm-hills--near"><svg {VB}>{front}</svg></div>\n'
    "  <!-- /hills -->\n"
)

text = SCENE.read_text(encoding="utf-8")
text, n = re.subn(r"<!-- hills -->\n.*?<!-- /hills -->\n", block, text, flags=re.S)
assert n == 1, "hills markers not found in src/scene.html"
SCENE.write_text(text, encoding="utf-8")
print("updated", SCENE.name, f"({len(block)} bytes of hills)")
