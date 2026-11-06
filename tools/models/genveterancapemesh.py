#!/usr/bin/env python3
"""Build the Veteran cape's mesh from scratch - a skillcape silhouette with no hole in it.

WHY NOT KEEP USING THE ATTACK CAPE'S MESH. It has a real hole in the middle of its back. Render it
with its emblem stripped and nothing behind it and you see the background straight through. Jagex's
solid emblem covers that hole rather than mending it, so anything we put there had to cover it too
- which is the only reason there was ever a disc behind our icon, and why every attempt to shrink,
reshape or hide that disc failed. A mesh with no hole needs no disc.

HOW IT IS BUILT. A cape is a sheet: a grid of vertices, x spreading wider as it falls, z bulging
out at the centre and wrapping back at the edges. Two layers - an outer face and an inner one a
little behind it, each with its own vertices so the client computes their normals separately - so
the cape is opaque from either side and has a lining.

THE ANIMATION LABELS ARE COPIED FROM THE ATTACK CAPE, by height. A worn cape is skinned to the
player's movement through those labels and there is no way to invent them: the attack cape's run
in bands down its length (8 at the collar, 11 across the middle, 12 at the hem), so each new
vertex takes the label of the nearest original vertex at its own height. That is the one thing
here that has to be borrowed rather than designed.

    python3 genveterancapemesh.py --content ../../content [--preview out.png]
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode  # noqa: E402
import dpglyph  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# Bronze, the same ramp the Veteran chat icon is drawn in.
OUTER = (198, 126, 64)
# The same bronze, deepened, for the hem.
OUTER_HEM = (142, 84, 40)
TRIM = (242, 186, 126)
# A darker lip right at the rim, so the cape has an edge rather than just stopping.
EDGE = (118, 68, 30)
LINING = (64, 38, 18)
# A DARK DEVICE ON BRONZE CLOTH. With no disc behind it the mark is read against the cape itself,
# and the cape is bronze - so a bronze mark has nothing to contrast with. Dark is also this
# shape's own idiom: the skillcape it is modelled on wears a dark grey sword on its gold shield.
EMBLEM = (58, 32, 14)
# A lighter rim just behind the device, so it reads as inlaid rather than painted on. The chat
# icon is a bronze mark with a DARK outline; on bronze cloth the device is the dark one, so the
# outline is the light one - the same idea the other way up.
EMBLEM_RIM = (236, 170, 110)

COLS, ROWS = 11, 13          # vertices across and down
SKIN = 'obj_attack_cape_manwear'   # whose animation labels we borrow


def hsl24to16(h, s, l):
    if l > 243: s >>= 4
    elif l > 217: s >>= 3
    elif l > 192: s >>= 2
    elif l > 179: s >>= 1
    return (((h & 0xff) >> 2) << 10) + ((s >> 5) << 7) + (l >> 1)


def rgb_to_hsl16(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mn, mx = min(r, g, b), max(r, g, b)
    h = s = 0.0
    l = (mn + mx) / 2.0
    if mn != mx:
        s = (mx - mn) / (mx + mn) if l < 0.5 else (mx - mn) / (2.0 - mx - mn)
        if r == mx: h = (g - b) / (mx - mn)
        elif g == mx: h = (b - r) / (mx - mn) + 2.0
        else: h = (r - g) / (mx - mn) + 4.0
    h /= 6.0
    return hsl24to16(int(h * 256.0), max(0, min(255, int(s * 256.0))), max(0, min(255, int(l * 256.0))))


def shape(s, t):
    """One point of the cape's outer surface.

    s is -1 at the left edge to +1 at the right; t is 0 at the collar to 1 at the hem.
    """
    # Wider as it falls, the way a cape hangs. The first attempt was 21 to 34 and read as a
    # tapered board rather than a cape; a skillcape flares.
    half = 23.0 + 17.0 * t
    x = half * s

    # The top edge rises at the corners into the yoke that sits over the shoulders, which is what
    # makes a skillcape read as one rather than as a sheet; the hem dips to a soft point.
    # A plain parabola. abs(s) ** 1.5 gave the shoulders a kink either side of the centre that
    # read as a wavy top edge rather than as a yoke.
    top = -150.0 - 24.0 * s * s
    bottom = -20.0 - 9.0 * (1.0 - abs(s) ** 2)
    y = top + (bottom - top) * t

    # Bulging away from the back at the centre and wrapping round the body at the edges, plus a
    # few soft vertical folds. THE FOLDS ARE GEOMETRY, NOT PAINT: the client shades a face from
    # its own normal, so undulating the surface is what gives a cape its light and dark bands.
    # Without them the whole sheet faces one way and reads as flat card.
    folds = 3.6 * math.cos(5.0 * math.pi * s) * (0.30 + 0.70 * t)
    z = 24.0 - 3.0 * t - 36.0 * s * s + folds
    return x, y, z


def build(mirror_emblem, lab_src):
    m = dict(vcount=0, fcount=0, vx=[], vy=[], vz=[], tris=[], fa=[], fb=[], fc=[],
             colour=[], pri=[], flab=None, finfo=None, vlab=[], alpha=None)

    def label_for(y):
        """The nearest borrowed vertex at this height, so the cape flaps like the one it copies."""
        return lab_src[min(range(len(lab_src)), key=lambda i: abs(lab_src[i][0] - y))][1]

    def add(x, y, z):
        m['vx'].append(round(x)); m['vy'].append(round(y)); m['vz'].append(round(z))
        m['vlab'].append(label_for(y))
        m['vcount'] += 1
        return m['vcount'] - 1

    def face(a, b, c, colour, pri):
        m['fa'].append(a); m['fb'].append(b); m['fc'].append(c)
        m['colour'].append(colour); m['pri'].append(pri)
        m['fcount'] += 1

    trim = rgb_to_hsl16(*TRIM)
    edge = rgb_to_hsl16(*EDGE)
    lining = rgb_to_hsl16(*LINING)
    # One tone per row, bright at the collar and deepening toward the hem.
    body = []
    for r in range(ROWS):
        k = r / (ROWS - 1)
        body.append(rgb_to_hsl16(*(round(a + (b - a) * k) for a, b in zip(OUTER, OUTER_HEM))))

    # Two sheets of vertices: the outer surface, and a lining a little behind it. Separate
    # vertices, so the client works out each sheet's normals from its own faces only - sharing
    # them makes the lighting of the two fight.
    front = [[None] * COLS for _ in range(ROWS)]
    back = [[None] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        t = r / (ROWS - 1)
        for c in range(COLS):
            s = -1.0 + 2.0 * c / (COLS - 1)
            x, y, z = shape(s, t)
            front[r][c] = add(x, y, z)
            back[r][c] = add(x * 0.985, y, z - 3.0)

    PRI = 6
    for r in range(ROWS - 1):
        for c in range(COLS - 1):
            # A TRIM ALL THE WAY ROUND, not just down the sides. A border on every edge - collar,
            # hem and both flanks - is what a cape in this game has and what stops a sheet of one
            # colour reading as cardboard; the first version banded only the sides and the collar
            # and still looked like card.
            # THE STRIPES ARE INSET, not on the rim. A border on the outermost column was
            # invisible: those faces are where the cape curls away from the viewer and the light
            # has already fallen off them, so whatever colour they are they render dark. One
            # column in, on the flat of the cape, is where the attack cape wears its stripes too.
            if c == 0 or c == COLS - 2:
                col = edge
            elif c == 1 or c == COLS - 3 or r == 0:
                col = trim
            else:
                # The body darkens as it falls, so the cloth has depth down its length rather
                # than being one flat tone from collar to hem.
                col = body[r]
            a, b = front[r][c], front[r][c + 1]
            d, e = front[r + 1][c + 1], front[r + 1][c]
            face(a, b, d, col, PRI)
            face(a, d, e, col, PRI)
            # The lining, wound the other way so it is drawn only from behind.
            a2, b2 = back[r][c], back[r][c + 1]
            d2, e2 = back[r + 1][c + 1], back[r + 1][c]
            face(d2, b2, a2, lining, PRI)
            face(e2, d2, a2, lining, PRI)

    # Close the rim so the two sheets do not show an open edge from the side.
    rim = []
    rim += [(front[0][c], front[0][c + 1], back[0][c], back[0][c + 1]) for c in range(COLS - 1)]
    rim += [(front[ROWS - 1][c + 1], front[ROWS - 1][c], back[ROWS - 1][c + 1], back[ROWS - 1][c])
            for c in range(COLS - 1)]
    rim += [(front[r + 1][0], front[r][0], back[r + 1][0], back[r][0]) for r in range(ROWS - 1)]
    rim += [(front[r][COLS - 1], front[r + 1][COLS - 1], back[r][COLS - 1], back[r + 1][COLS - 1])
            for r in range(ROWS - 1)]
    for fa_, fb_, ba_, bb_ in rim:
        face(fa_, fb_, bb_, lining, PRI)
        face(fa_, bb_, ba_, lining, PRI)

    # ---- the device, flat, on the outer surface
    #
    # FLAT AND AT ONE DEPTH. The client shades a face from its own normal, so an emblem that
    # follows the cape's curve gives every triangle its own tone and reads as crumpled foil.
    ink, _ = dpglyph.veteran()
    if mirror_emblem:
        ink = [list(reversed([(1.0 - x, y) for x, y in t])) for t in ink]

    size = 34.0
    cx, cy = 0.0, -108.0
    depth = max(m['vz'][v] for v in range(m['vcount'])) + 3.0
    lab = label_for(cy)
    cache = {}

    def evert(nx, ny, lift=0.0):
        key = (round(nx, 4), round(ny, 4), lift)
        if key not in cache:
            m['vx'].append(round(cx + (nx - 0.5) * size))
            m['vy'].append(round(cy + (ny - 0.5) * size))
            m['vz'].append(round(depth + lift))
            m['vlab'].append(lab)
            m['vcount'] += 1
            cache[key] = m['vcount'] - 1
        return cache[key]

    rim_ink, _ = dpglyph.veteran(dilate=1)
    if mirror_emblem:
        rim_ink = [list(reversed([(1.0 - x, y) for x, y in t])) for t in rim_ink]
    rc = rgb_to_hsl16(*EMBLEM_RIM)
    for t in rim_ink:
        a, b, c = (evert(x, y) for x, y in t)
        face(a, b, c, rc, PRI + 1)

    ec = rgb_to_hsl16(*EMBLEM)
    for t in ink:
        a, b, c = (evert(x, y, 1.6) for x, y in t)
        face(a, b, c, ec, PRI + 2)

    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', default=os.path.join(ROOT, 'content'))
    ap.add_argument('--preview')
    a = ap.parse_args()

    objdir = os.path.join(a.content, 'models', 'obj')
    src = parse_ob2(open(os.path.join(objdir, SKIN + '.ob2'), 'rb').read())
    if src['vlab'] is None:
        raise SystemExit(SKIN + ' carries no vertex labels to borrow')
    lab_src = [(src['vy'][v], src['vlab'][v]) for v in range(src['vcount'])]
    print(f'borrowing animation labels from {SKIN}: {len(set(l for _, l in lab_src))} distinct')

    written = []
    for name, mirror in (('obj_veteran_cape_manwear', True),
                         ('obj_veteran_cape_womanwear', True),
                         ('obj_veteran_cape', True)):
        m = build(mirror, lab_src)
        data = encode(m)
        parse_ob2(data)          # it has to read back, or the client never gets as far as drawing it
        path = os.path.join(objdir, name + '.ob2')
        open(path, 'wb').write(data)
        written.append(path)
        print(f'  {name}: {m["vcount"]} verts, {m["fcount"]} faces, {len(data)} bytes')

    if a.preview:
        import ob2render
        orig = ob2render.face_lightness
        ob2render.face_lightness = lambda mm, **kw: orig(mm, lx=50, ly=-10, lz=50)
        ob2render.sheet(written[:1], a.preview, size=420, cols=1, recol=None,
                        xan=0, yan=1024, zan=0, zoom=None, xof=0, yof=0)
        print('  preview', a.preview)


if __name__ == '__main__':
    main()
