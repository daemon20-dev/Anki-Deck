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


def contour(f, x0, x1, dy, op, color="#c9d4ff"):
    """A faint fold line following ridge f, dy below it, fading at both ends."""
    pts = [(x, f(x) + dy + 6 * math.sin((x - x0) / (x1 - x0) * math.pi)) for x in range(x0, x1 + 1, STEP)]
    d = f"M{pts[0][0]} {pts[0][1]:.0f}" + "".join(f" L{x} {y:.0f}" for x, y in pts[1:])
    gid = f"gm-cf-{x0}-{dy}"
    return (f'<linearGradient id="{gid}" x1="{x0}" x2="{x1}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="0"/><stop offset=".5" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>'
            f'<path d="{d}" fill="none" stroke="url(#{gid})" stroke-width="1"/>')


def shrubs(f, xs):
    """Low rounded bushes sitting on ridge f."""
    out = []
    for x, r in xs:
        y = f(x) + 2
        out.append(f"M{x - r * 1.6:.0f} {y + 2:.0f} A{r:.0f} {r * 0.8:.0f} 0 0 1 {x:.0f} {y - r * 0.4:.0f} "
                   f"A{r * 0.9:.0f} {r * 0.7:.0f} 0 0 1 {x + r * 1.5:.0f} {y + 2:.0f}Z")
    return " ".join(out)


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
REFLECT_X = 1150   # under the moon on a typical desktop window

back = (
    '<defs>'
    '<linearGradient id="gm-g-mtn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1636"/><stop offset=".6" stop-color="#141d44"/><stop offset="1" stop-color="#19244f"/></linearGradient>'
    '<linearGradient id="gm-g-far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1634"/><stop offset=".6" stop-color="#131c42"/><stop offset="1" stop-color="#18234d"/></linearGradient>'
    '<linearGradient id="gm-g-mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1029"/><stop offset="1" stop-color="#0e1636"/></linearGradient>'
    '<linearGradient id="gm-g-lake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2552"/><stop offset=".5" stop-color="#111a3e"/><stop offset="1" stop-color="#0a1030"/></linearGradient>'
    '<radialGradient id="gm-g-glow"><stop offset="0" stop-color="#fff1dc" stop-opacity=".22"/><stop offset="1" stop-color="#fff1dc" stop-opacity="0"/></radialGradient>'
    '<linearGradient id="gm-g-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3570" stop-opacity="0"/><stop offset="1" stop-color="#2a3570" stop-opacity=".3"/></linearGradient>'
    '</defs>'
    + hill(mountains, "url(#gm-g-mtn)", "#dfe6ff", 0.10)
    + f'<rect x="0" y="240" width="{W}" height="190" fill="url(#gm-g-haze)"/>'
    + hill(far, "url(#gm-g-far)", "#dfe6ff", 0.08)
    + hill(mid, "url(#gm-g-mid)", "#dfe6ff", 0.07)
    + contour(mountains, 300, 520, 34, 0.05) + contour(mountains, 820, 1060, 40, 0.05)
    + contour(far, 120, 420, 22, 0.05) + contour(far, 700, 1000, 26, 0.04)
    + f'<path fill="#0d1432" d="{treeline(far, [(600, 700, 6, 11), (1240, 1330, 5, 10)], 11)}"/>'
    + contour(mid, 200, 520, 18, 0.05)
    + f'<path fill="#0a1029" d="{treeline(mid, [(40, 300, 10, 22), (420, 520, 4, 16), (900, 1120, 8, 20), (1300, 1420, 5, 18)], 7)}"/>'
    # a still lake tucked into the valley, catching the moon
    + f'<path d="M560 {lake_y + 16} C680 {lake_y - 6} 860 {lake_y - 13} 1060 {lake_y - 13} '
      f'C1260 {lake_y - 13} 1380 {lake_y - 10} {W} {lake_y - 8} V{H} H560Z" fill="url(#gm-g-lake)"/>'
    + f'<path d="M640 {lake_y + 3} C800 {lake_y - 11} 1100 {lake_y - 13} {W} {lake_y - 8}" fill="none" stroke="#c9d4ff" stroke-opacity=".10" stroke-width="1"/>'
    # gentle ripples across the lake (thin, long, very faint)
    + ''.join(
        f'<path d="M{x0} {y} Q{(x0 + x1) / 2:.0f} {y - 1.2} {x1} {y}" stroke="#aebbf0" stroke-opacity="{op}" stroke-width=".8" fill="none" stroke-linecap="round"/>'
        for x0, x1, y, op in [(700, 860, lake_y - 4, .07), (900, 1080, lake_y - 1, .06), (1220, 1420, lake_y - 3, .06),
                               (640, 760, lake_y + 6, .05), (820, 1040, lake_y + 9, .05), (1240, 1400, lake_y + 8, .05),
                               (760, 960, lake_y + 18, .04), (1250, 1430, lake_y + 20, .04)]
    )
)

# ── Moon glints on the water (two interleaved sets that fade in turn) ───
def glints(seed):
    """Stylised moon path: rounded bars stacked under the moon, long near the
    far shore and breaking into shorter, fainter pieces as they come closer."""
    rnd, out = seed, []

    def rand():
        nonlocal rnd
        rnd = (rnd * 1103515245 + 12345) % 2**31
        return (rnd >> 8) % 1000 / 1000

    for i in range(10):
        y = lake_y - 11 + i * 4.2
        half = 10 + i * 5                              # the path widens toward the viewer
        op = 0.85 - i * 0.06
        pieces = 1 if i < 2 else 2 + int(rand() * 2)   # solid at the top, broken lower down
        for k in range(pieces):
            w = (34 - i * 1.5) * (0.5 + rand() * 0.6) if pieces > 1 else 44 - i * 8
            x = REFLECT_X + (rand() * 2 - 1) * half * (0.3 if pieces == 1 else 1) - w / 2
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="2.4" rx="1.2" '
                       f'fill="url(#gm-g-glint)" fill-opacity="{op * (0.7 + rand() * 0.3):.2f}"/>')
    return ('<defs><linearGradient id="gm-g-glint"><stop offset="0" stop-color="#ffe7cc" stop-opacity=".2"/>'
            '<stop offset=".5" stop-color="#fff4e6"/><stop offset="1" stop-color="#ffe7cc" stop-opacity=".2"/></linearGradient></defs>'
            + "".join(out))


def couple(x, base):
    """A man and a shorter woman walking left (toward the cabin), hand in hand."""
    ink = "#04071a"
    limb = f'stroke="{ink}" stroke-linecap="round" fill="none"'
    man = (
        f'<g transform="translate({x} {base}) scale(1.05)">'
        f'<circle cx="-.6" cy="-25" r="2.7" fill="{ink}"/>'
        f'<path d="M-3.4 -21.4 Q0 -22.6 2.8 -21.2 L2.4 -12.6 L-2.6 -12.6Z" fill="{ink}"/>'      # torso
        f'<path d="M-1.4 -13 L-4.6 -6.5 L-5.2 0 M1.2 -13 L2.2 -6.5 L4.4 -.4" {limb} stroke-width="2.3"/>'  # legs, mid-stride
        f'<path d="M-2.6 -20.4 L-5.6 -16 L-8.6 -12.8 M2 -20.4 L3.6 -16.4 L4.6 -13.6" {limb} stroke-width="1.7"/>'  # arms
        '</g>'
    )
    woman = (
        f'<g transform="translate({x - 16} {base}) scale(.94)">'
        f'<circle cx="-.4" cy="-23.6" r="2.5" fill="{ink}"/>'
        f'<path d="M1.4 -25.4 Q4.4 -24 3.6 -19.6 Q2.2 -21 1.6 -22.4Z" fill="{ink}"/>'         # hair falling back
        f'<path d="M-2.4 -19.8 Q0 -20.8 2.4 -19.6 L1.8 -15.4 L5.2 -7 L-5.2 -7 L-1.8 -15.4Z" fill="{ink}"/>'  # A-line dress
        f'<path d="M-1.4 -7.5 L-3.6 -.4 M1.4 -7.5 L3 -.2" {limb} stroke-width="1.8"/>'          # legs
        f'<path d="M-2 -18.6 L-4.4 -12.8 M2 -18.6 L5.2 -15 L7.6 -12.4" {limb} stroke-width="1.5"/>'  # arms (right one reaches back)
        '</g>'
    )
    # joined hands where his forward arm meets her trailing arm
    hands = f'<circle cx="{x - 8.9:.1f}" cy="{base - 12.6:.1f}" r="1.6" fill="{ink}"/>'
    people = man + woman + hands
    # faint moonlit rim (a soft pale copy behind the silhouette) so the pair
    # reads against the dark hill
    rim = (f'<g transform="translate(1.2 -.8)" opacity=".28" filter="url(#gm-f-rim)">'
           + people.replace(ink, "#b9c6f0") + '</g>')
    return rim + people


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
    '<defs><filter id="gm-f-rim" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation=".7"/></filter>'
    '<radialGradient id="gm-g-win"><stop offset="0" stop-color="#ffb35c" stop-opacity=".45"/>'
    '<stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/></radialGradient></defs>'
    + hill(near, "#04071a", "#c9d4ff", 0.07)
    + contour(near, 260, 520, 22, 0.05) + contour(near, 960, 1200, 20, 0.04)
    # a faint footpath winding down from the cabin
    + f'<path d="M{cab_x + 6} {cab_y + 6} C{cab_x + 30} {cab_y + 20} {cab_x - 40} {cab_y + 30} {cab_x - 10} {H}" '
      f'fill="none" stroke="#8d9bd6" stroke-opacity=".03" stroke-width="4" stroke-linecap="round"/>'
    + f'<path fill="#04071a" d="{shrubs(near, [(300, 7), (338, 5), (690, 6), (760, 4), (1010, 5), (1120, 7)])}"/>'
    + f'<path fill="#04071a" d="{treeline(near, [(0, 260, 12, 66), (440, 650, 7, 48), (980, 1060, 3, 38), (1240, 1440, 10, 72)], 3)}"/>'
    + couple(918, near(918) + 1.5)
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
