#!/usr/bin/env python3
"""Build the Veteran cape from the Attack cape: mend its hole, recolour it, and put our device on.

WHY THIS IS BACK. The cape was built from scratch for a while, because the attack cape has a gap
in the middle of its back which its own emblem hides - and our device is an open shape, so it
needed a disc behind it, and the disc was the thing nobody wanted. But a hand-built cape kept
failing in game in ways a render never showed: it painted over the player, stood off his back like
a plank, lay on the floor as a lump. Three rounds of that did not match a professional mesh.

So the hole is MENDED instead, and the reason to replace the mesh goes away. Everything that was
hard to reproduce - the drape, the fold of the edges, the collar, the animation labels, the draw
priorities that decide what covers the player from which side - is Jagex's and already right.

THE HOLE IS FOUND, NOT GUESSED. On a closed surface every edge is shared by two faces; an edge
used by only one is on a boundary. Walk those into loops and one of them is the gap: eight
vertices, flat at z 15, right where the emblem sat. It is filled as a fan from its own centroid in
the cloth's colour, so every point of the patch is interpolated between vertices already on the
cloth and it follows the curve and the light instead of lying across them.

    python3 genveterancape.py --content ../../content [--preview out.png]
"""
import argparse
import collections
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode  # noqa: E402
import dpglyph  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# TWO MATERIALS, NOT ONE. This was a single bronze tint over the whole cape - cloth and trim
# alike, "all one metal" - because one hue cannot be two things. The cape is now dark cloth with
# a gunmetal trim, which needs the two told apart, and the source model already separates them:
# on the worn model two thirds of the surface is the trim ramp and a third is cloth.
#
# Only the HUE AND SATURATION of these constants are used - tint() keeps each face's own
# lightness, which is what preserves Jagex's shading - so their brightness here is chosen to be
# readable in a diff, not to set how dark the cape is.
#
# NOTE: the bronze these replace was deliberately the ramp the Veteran chat icon is drawn in, so
# the rank read as one thing. That link is broken until the icon is recoloured to match.
CLOTH_RGB = (120, 87, 61)
# Gunmetal: a NEUTRAL dark grey. Saturation 0 on purpose - the first saturation step this palette
# can express (32..63 of 255, after the >>5) already reads as teal rather than as a cast, and the
# screenshot this was matched to is itself saturation 0 once quantised. Gunmetal here is a matter
# of lightness, not of hue.
TRIM_RGB = (150, 150, 150)
# Jagex's trim ramp tops out at lightness 103 of 127, which is a bright gold highlight and comes
# out as near-white silver. Gunmetal sits lower, so the trim ramp is pulled down the same way the
# cloth is - and separately from it, because the two are the contrast the cape is made of.
TRIM_LIGHT = 1.0
# HOW DARK THE CLOTH IS, as a scale on each cloth face's own lightness - the one thing hue and
# saturation cannot do. Jagex's ramp runs from 12 to 103 across the cape and its lining, and a
# straight hue swap keeps all of it, which comes out as a mid brown. The cape being asked for is
# nearly black, so the whole ramp is pulled down together: the relative shading survives, the
# cape just stops catching the light. Trim and device are not scaled - they are the thing meant
# to catch it.
CLOTH_LIGHT = 0.32
cloth_light = CLOTH_LIGHT
trim_light = TRIM_LIGHT
# THE TRIM BANDS ARE MAGENTA IN THE MESH. Resolved through the client palette, hues 52-55 are
# rgb(249,15,209) and rgb(157,10,167) - a placeholder ramp, not a colour anybody sees, because the
# Attack cape's own obj config recolours it. The old global tint absorbed it by accident, which is
# why nothing ever looked wrong; painting the two groups separately means this one has to be
# handled on purpose instead.
#
# Its brightest step is hue 53 at saturation 1, rgb(222,207,222), which reads as a pale lining
# rather than as part of the ramp - it was excluded on that basis once, and the render said so by
# keeping brown bands where it wanted grey ones. Saturation is shed as lightness climbs in
# hsl24to16 above (>>1 past 179, >>2 past 192), so at lightness 103 it survives as 1.
#
# Hue alone, then. Everything else on the cape is hue 0, 6 or 8, so one threshold separates them,
# and the areas printed below say so if that ever stops being true.
TRIM_HUE = 40
# The device, LIGHT against the cloth now - the old dark brown device worked on bronze and would
# disappear into a cape this dark.
EMBLEM_RGB = (200, 200, 200)
# A darker rim just behind it, so it reads as struck into the cloth rather than painted on. It was
# lighter than the device when the cloth was bronze; against dark cloth the separation has to come
# from the other side.
EMBLEM_RIM_RGB = (118, 118, 118)

EMBLEM_COLOURS = {11224, 7116, 103, 51, 6563, 9152, 59, 7104}

SPEC = {
    'obj_attack_cape': dict(out='obj_veteran_cape', box=(-12, 8, -12, -6, -12, 22),
                            plane='xz', mirror=False, flip=True, height=24.0),
    'obj_attack_cape_manwear': dict(out='obj_veteran_cape_manwear', box=(-12, 13, -141, -96, 14, 17),
                                    plane='xy', mirror=True, flip=False, height=26.0),
    'obj_attack_cape_womanwear': dict(out='obj_veteran_cape_womanwear', box=(-12, 13, -141, -96, 14, 17),
                                      plane='xy', mirror=True, flip=False, height=26.0),
}


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


def tint(colour, hue_sat):
    """That face's own lightness, under the bronze's hue and saturation.

    Derived rather than tabulated, so the model's shading survives whole and no list of colour
    pairs can fall out of step with a mesh. The gold trim becomes bright bronze: it is all one
    metal now.
    """
    return (hue_sat & 0xFF80) | (colour & 0x7F)


def area2(m, i):
    a, b, c = m['fa'][i], m['fb'][i], m['fc'][i]
    return ((m['vx'][b] - m['vx'][a]) * (m['vy'][c] - m['vy'][a])
            - (m['vy'][b] - m['vy'][a]) * (m['vx'][c] - m['vx'][a]))


def boundary_loops(m, faces):
    """Edges used by exactly one of these faces, walked into closed loops."""
    use = collections.Counter()
    for i in faces:
        a, b, c = m['fa'][i], m['fb'][i], m['fc'][i]
        for e in ((a, b), (b, c), (c, a)):
            use[tuple(sorted(e))] += 1
    nxt = collections.defaultdict(list)
    for (a, b), n in use.items():
        if n == 1:
            nxt[a].append(b)
            nxt[b].append(a)
    loops, seen = [], set()
    for start in list(nxt):
        if start in seen:
            continue
        loop, cur, prev = [start], start, None
        seen.add(start)
        while True:
            opts = [v for v in nxt[cur] if v != prev and v not in seen]
            if not opts:
                break
            prev, cur = cur, opts[0]
            seen.add(cur)
            loop.append(cur)
        if len(loop) >= 3:
            loops.append(loop)
    return loops


def orient(tris, spec):
    """Turn a device to face the way this mesh is seen from.

    EVERY REFLECTION ALSO REVERSES WINDING, so an odd number of them needs the triangles reversed
    or the client culls the whole device.
    """
    refl = 0
    if spec['mirror']:
        tris = [[(1.0 - x, y) for x, y in t] for t in tris]
        refl += 1
    if spec['flip']:
        tris = [[(x, 1.0 - y) for x, y in t] for t in tris]
        refl += 1
    return [list(reversed(t)) for t in tris] if refl % 2 else tris


def build(objdir, src, spec, verbose=True):
    m = parse_ob2(open(os.path.join(objdir, src + '.ob2'), 'rb').read())
    x0, x1, y0, y1, z0, z1 = spec['box']

    def inside(v):
        return x0 <= m['vx'][v] <= x1 and y0 <= m['vy'][v] <= y1 and z0 <= m['vz'][v] <= z1

    emblem = {i for i in range(m['fcount'])
              if m['colour'][i] in EMBLEM_COLOURS
              and all(inside(v) for v in (m['fa'][i], m['fb'][i], m['fc'][i]))}
    if not emblem:
        raise SystemExit(f'{src}: found no emblem to remove')
    ev = {v for i in emblem for v in (m['fa'][i], m['fb'][i], m['fc'][i])}
    ea = [m['vx'][v] for v in ev]
    eu = [m['vy'][v] for v in ev] if spec['plane'] == 'xy' else [m['vz'][v] for v in ev]
    pri = max(set(m['pri'][i] for i in emblem), key=[m['pri'][i] for i in emblem].count)
    if verbose:
        print(f'{src}: emblem {len(emblem)} faces, priority {pri}')

    # The gap the emblem was covering, found from the outer surface once it is taken off.
    outer = [i for i in range(m['fcount']) if i not in emblem and area2(m, i) > 0]
    gap = None
    for lp in boundary_loops(m, outer):
        if all(x0 <= m['vx'][v] <= x1 and y0 <= m['vy'][v] <= y1 for v in lp):
            gap = lp
            break

    keep = sorted(set(range(m['fcount'])) - emblem)
    touching = [i for i in outer if gap and any(v in set(gap) for v in (m['fa'][i], m['fb'][i], m['fc'][i]))]
    fill_col = max(set(m['colour'][i] for i in touching), key=[m['colour'][i] for i in touching].count) if touching else 0
    fill_pri = max(set(m['pri'][i] for i in touching), key=[m['pri'][i] for i in touching].count) if touching else pri

    for k in ('fa', 'fb', 'fc', 'colour', 'pri', 'flab', 'alpha', 'finfo'):
        if m.get(k) is not None:
            m[k] = [m[k][i] for i in keep]
    m['fcount'] = len(keep)

    cloth = rgb_to_hsl16(*CLOTH_RGB)
    trim = rgb_to_hsl16(*TRIM_RGB)

    def is_trim(c):
        return ((c >> 10) & 0x3F) >= TRIM_HUE

    def repaint(c):
        if is_trim(c):
            lit = max(1, min(0x7F, int(round((c & 0x7F) * trim_light))))
            return (trim & 0xFF80) | lit
        lit = max(1, min(0x7F, int(round((c & 0x7F) * cloth_light))))
        return (cloth & 0xFF80) | lit

    if verbose:
        # Said out loud because the split is the whole point: a source model whose trim stopped
        # being gold would silently come out as cloth, and the cape would lose its border.
        share = collections.Counter()
        for i in range(m['fcount']):
            share['trim' if is_trim(m['colour'][i]) else 'cloth'] += abs(area2(m, i))
        total = sum(share.values()) or 1
        print('  %.0f%% cloth, %.0f%% trim' % (100.0 * share['cloth'] / total, 100.0 * share['trim'] / total))

    m['colour'] = [repaint(c) for c in m['colour']]
    fill_col = repaint(fill_col)

    def face(a, b, c, colour, priority):
        m['fa'].append(a); m['fb'].append(b); m['fc'].append(c)
        m['colour'].append(colour); m['pri'].append(priority)
        if m['flab'] is not None: m['flab'].append(0)
        if m['alpha'] is not None: m['alpha'].append(0)
        if m['finfo'] is not None: m['finfo'].append(0)
        m['fcount'] += 1

    if gap:
        cx = sum(m['vx'][v] for v in gap) / len(gap)
        cy = sum(m['vy'][v] for v in gap) / len(gap)
        cz = sum(m['vz'][v] for v in gap) / len(gap)
        m['vx'].append(round(cx)); m['vy'].append(round(cy)); m['vz'].append(round(cz))
        if m['vlab'] is not None:
            labs = [m['vlab'][v] for v in gap]
            m['vlab'].append(max(set(labs), key=labs.count))
        m['vcount'] += 1
        hub = m['vcount'] - 1
        for i in range(len(gap)):
            a, b = gap[i], gap[(i + 1) % len(gap)]
            t = ((m['vx'][b] - m['vx'][a]) * (m['vy'][hub] - m['vy'][a])
                 - (m['vy'][b] - m['vy'][a]) * (m['vx'][hub] - m['vx'][a]))
            face(a, b, hub, fill_col, fill_pri) if t > 0 else face(b, a, hub, fill_col, fill_pri)
        if verbose:
            print(f'  mended a {len(gap)}-vertex gap in the cloth')
    elif verbose:
        print('  no gap in this mesh')

    # ---- the device, flat and on one animation label
    A, U, D, sign = ('vx', 'vy', 'vz', 1) if spec['plane'] == 'xy' else ('vx', 'vz', 'vy', -1)
    lab = 0
    if m['vlab'] is not None:
        labs = [m['vlab'][v] for v in ev]
        lab = max(set(labs), key=labs.count)
    # THE DEPTH OF THE EMBLEM WE TOOK OFF, not the deepest point of the whole cape.
    #
    # In game the device floated clear of the cloth, and this line is why: it measured the
    # frontmost cloth ANYWHERE - which is the hem, at z 24 - while the cloth under the emblem sits
    # at 14..20. The device was placed at 20..26 and stood up to ten units off its own backing.
    # Jagex's emblem is at 15..16 on that same cloth: flush. Taking the depth from the faces being
    # replaced puts ours exactly where theirs was, and keeps it right on the other meshes too.
    depth = max(sign * m[D][v] for v in ev)

    ink = orient(dpglyph.veteran()[0], spec)
    rim = orient(dpglyph.veteran(dilate=1)[0], spec)

    ca = (min(ea) + max(ea)) / 2.0
    cu = (min(eu) + max(eu)) / 2.0
    size = spec['height']
    cache = {}

    def vert(nx, ny, lift):
        key = (round(nx, 4), round(ny, 4), lift)
        if key not in cache:
            pos = {A: round(ca + (nx - 0.5) * size), U: round(cu + (ny - 0.5) * size),
                   D: round(sign * (depth + lift))}
            m['vx'].append(pos['vx']); m['vy'].append(pos['vy']); m['vz'].append(pos['vz'])
            if m['vlab'] is not None:
                m['vlab'].append(lab)
            m['vcount'] += 1
            cache[key] = m['vcount'] - 1
        return cache[key]

    for t_ in rim:
        a, b, c = (vert(x, y, 0.0) for x, y in t_)
        face(a, b, c, rgb_to_hsl16(*EMBLEM_RIM_RGB), pri)
    for t_ in ink:
        a, b, c = (vert(x, y, 1.0) for x, y in t_)
        face(a, b, c, rgb_to_hsl16(*EMBLEM_RGB), pri + 1)

    if verbose:
        print(f'  device {size:.0f} wide at ({ca:.0f}, {cu:.0f}); {m["fcount"]} faces total')
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', default=os.path.join(ROOT, 'content'))
    ap.add_argument('--preview')
    ap.add_argument('--cloth-light', type=float, default=CLOTH_LIGHT,
                    help="scale on the cloth lightness ramp (1.0 = Jagex's own)")
    ap.add_argument('--trim-light', type=float, default=TRIM_LIGHT,
                    help="scale on the trim lightness ramp (1.0 = Jagex's own)")
    a = ap.parse_args()

    global cloth_light, trim_light
    cloth_light = a.cloth_light
    trim_light = a.trim_light
    objdir = os.path.join(a.content, 'models', 'obj')
    written = []
    for src, spec in SPEC.items():
        m = build(objdir, src, spec)
        data = encode(m)
        parse_ob2(data)        # it has to read back, or the client never gets as far as drawing it
        path = os.path.join(objdir, spec['out'] + '.ob2')
        open(path, 'wb').write(data)
        written.append(path)
        print(f'  wrote {spec["out"]} ({len(data)} bytes)')

    if a.preview:
        import ob2render
        orig = ob2render.face_lightness
        ob2render.face_lightness = lambda mm, **kw: orig(mm, lx=50, ly=-10, lz=50)
        ob2render.sheet(written, a.preview, size=340, cols=3, recol=None,
                        xan=0, yan=1024, zan=0, zoom=None, xof=0, yof=0)
        print('  preview', a.preview)


if __name__ == '__main__':
    main()
