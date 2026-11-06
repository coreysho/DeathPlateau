#!/usr/bin/env python3
"""Build the Veteran cape's three models from the Attack cape's, with the DP monogram on the back.

WHAT THIS MAKES. obj_veteran_cape, _manwear and _womanwear: the skillcape shape, recoloured to
bronze, with Jagex's attack emblem cut out and the server's DP monogram built in its place.

WHY A GENERATOR AND NOT THREE HAND-EDITED MODELS. The emblem is not a texture - the 377 client has
none on this model - it is geometry, about two dozen faces sitting a couple of units proud of the
cloth in their own colours. Swapping it means deleting those faces and building new ones, which is
not something to do by hand three times and never be able to redo.

HOW THE OLD EMBLEM IS FOUND. By colour AND position, not either alone. Five colour groups make up
the emblem, but on the inventory mesh two of those colours are also used by the collar at the far
end of the model, so colour alone takes the collar with it; and the emblem's bounding box alone
takes eight cloth faces that happen to pass through it. The intersection is exactly 24 faces on
each of the three meshes.

THE COLOUR IS DERIVED, NOT TABULATED. Every cloth face keeps its own lightness and takes the
bronze hue and saturation, so the model's shading survives intact and no hand-written list of
colour pairs can fall out of step with a mesh. One consequence worth knowing: the gold trim
becomes bright bronze rather than staying gold, because it is all one metal now.

TWO THINGS EVERY NEW VERTEX NEEDS BESIDES A POSITION:

  vlab  the animation label. The worn cape is skinned to the player's movement, and a vertex with
        the wrong label stays put while the cloth under it flaps. Each new vertex takes the label
        of the nearest cloth vertex.
  z     the FRONTMOST local cloth surface, plus a stand-off - not an average of what is nearby.
        This cape is layered, side panels in front of a centre panel, and an average puts a point
        between the two layers where the front panel swallows half the monogram.

    python3 genveterancape.py --content ../../content [--preview out.png]

Re-runnable: it reads the attack cape models and writes new files, touching nothing it reads.
"""
import argparse
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MASK = os.path.join(ROOT, 'Claude outputs', 'dp-icon', 'dp_silhouette.png')

# The brand's red, as the sigil is drawn. The cloth is bronze, so the monogram needs a hue of its
# own or it disappears into the cape.
EMBLEM_RGB = (184, 50, 40)
# Mid bronze - the same ramp the Veteran chat icon is drawn in, so rank and cape match.
BRONZE_RGB = (168, 100, 46)

# source model -> (the emblem's colours, its bounding box, which plane it lies in)
#
# 'xy' is a worn cape standing up, its back facing +z. 'xz' is the inventory model, which lies flat
# with the cape's face pointing up - and up is NEGATIVE y in this format, which is why the
# inventory monogram is pushed to a smaller y rather than a larger one.
SPEC = {
    'obj_attack_cape': dict(
        out='obj_veteran_cape',
        colours={9152, 59, 51, 6563, 7104},
        box=(-12, 8, -12, -6, -12, 22),
        # Mirrored like the worn meshes: the inventory icon's camera (2dxan=504, 2dyan=0) also
        # looks at this face from the far side of it, which the first render showed as "bD".
        plane='xz', height=30.0, stand=3.0, mirror=True,
    ),
    'obj_attack_cape_manwear': dict(
        out='obj_veteran_cape_manwear',
        colours={11224, 7116, 103, 51, 6563},
        box=(-12, 13, -141, -96, 14, 17),
        plane='xy', height=44.0, stand=4.0, mirror=True,
    ),
    'obj_attack_cape_womanwear': dict(
        out='obj_veteran_cape_womanwear',
        colours={11224, 7116, 103, 51, 6563},
        box=(-12, 13, -141, -96, 14, 17),
        plane='xy', height=44.0, stand=4.0, mirror=True,
    ),
}

COLS, ROWS = 21, 20


# ---------------------------------------------------------------- colour
def hsl24to16(h, s, l):
    if l > 243: s >>= 4
    elif l > 217: s >>= 3
    elif l > 192: s >>= 2
    elif l > 179: s >>= 1
    return (((h & 0xff) >> 2) << 10) + ((s >> 5) << 7) + (l >> 1)


def rgb_to_hsl16(r, g, b):
    """ob2palette's conversion. Face colours are stored as hsl16."""
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
    """That face's own lightness, under the bronze's hue and saturation."""
    return (hue_sat & 0xFF80) | (colour & 0x7F)


# ---------------------------------------------------------------- the monogram
def silhouette():
    """dp_silhouette.png as a solid shape, flecks removed.

    The brand sigil itself is no good for this: it is a distressed drawing, and thresholded at
    cape size it gives scattered dots where the grain happens to be dark. A mesh has no texture to
    carry grain, so it needs the shape.
    """
    im = Image.open(MASK).convert('L').point(lambda v: 255 if v < 128 else 0)
    w, h = im.size
    px = im.load()
    seen = [[False] * w for _ in range(h)]
    blobs = []
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] == 0 or seen[y0][x0]:
                continue
            stack, cells = [(x0, y0)], []
            seen[y0][x0] = True
            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and px[nx, ny] > 0:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            blobs.append(cells)
    floor = (w * h) / 1000.0
    clean = Image.new('L', (w, h), 0)
    cp = clean.load()
    for b in blobs:
        if len(b) >= floor:
            for x, y in b:
                cp[x, y] = 255
    # Cropped to the LETTERS. Measuring the raw image instead includes the stray flecks out near
    # the corners, which made the monogram read as taller than wide when the letters are the other
    # way round, and the emblem came out narrow.
    return clean.crop(clean.getbbox())


def grid(mirror):
    sil = silhouette()
    small = sil.resize((COLS, ROWS), Image.BOX).point(lambda v: 255 if v >= 100 else 0)
    g = small.load()
    out = [[g[x, y] > 0 for x in range(COLS)] for y in range(ROWS)]
    # The worn cape's emblem face is seen from the far side of it, so a grid laid out left to
    # right in model space reads right to left on screen. Jagex's sword reads correctly from that
    # side, which is what says the side is right and the order wrong.
    return [list(reversed(r)) for r in out] if mirror else out


def runs(g):
    """Horizontal runs, so one quad covers a stretch of cells rather than one quad per cell."""
    out = []
    for r, row in enumerate(g):
        c = 0
        while c < len(row):
            if not row[c]:
                c += 1
                continue
            s = c
            while c < len(row) and row[c]:
                c += 1
            out.append((r, s, c))
    return out


# ---------------------------------------------------------------- the model
def build(src_dir, src_name, spec, verbose=True):
    m = parse_ob2(open(os.path.join(src_dir, src_name + '.ob2'), 'rb').read())
    x0b, x1b, y0b, y1b, z0b, z1b = spec['box']

    def inside(v):
        return x0b <= m['vx'][v] <= x1b and y0b <= m['vy'][v] <= y1b and z0b <= m['vz'][v] <= z1b

    emblem = [i for i in range(m['fcount'])
              if m['colour'][i] in spec['colours'] and all(inside(v) for v in (m['fa'][i], m['fb'][i], m['fc'][i]))]
    if len(emblem) != 24:
        raise SystemExit(f'{src_name}: expected the emblem to be 24 faces, found {len(emblem)} - '
                         f'the source model is not the one this was written against')
    ev = set()
    for f in emblem:
        ev.update((m['fa'][f], m['fb'][f], m['fc'][f]))
    pri = max(set(m['pri'][f] for f in emblem), key=[m['pri'][f] for f in emblem].count)

    plane = spec['plane']
    # (across, up, depth) as indices into a vertex's (x, y, z), and which way "proud" goes.
    if plane == 'xy':
        A, U, D, sign = 'vx', 'vy', 'vz', +1
    else:
        A, U, D, sign = 'vx', 'vz', 'vy', -1

    ea = [m[A][v] for v in ev]
    eu = [m[U][v] for v in ev]
    ed = [m[D][v] for v in ev]
    if verbose:
        print(f'{src_name}: emblem {len(emblem)} faces / {len(ev)} verts, priority {pri}, '
              f'{A[1]} {min(ea)}..{max(ea)} {U[1]} {min(eu)}..{max(eu)} {D[1]} {min(ed)}..{max(ed)}')

    keep = set(range(m['fcount'])) - set(emblem)
    cloth = set()
    for f in keep:
        for v in (m['fa'][f], m['fb'][f], m['fc'][f]):
            # Only the cloth on the emblem's own side of the cape.
            if (m[D][v] > 6) if sign > 0 else (m[D][v] < -2):
                cloth.add(v)
    cloth = sorted(cloth)
    if len(cloth) < 20:
        raise SystemExit(f'{src_name}: only {len(cloth)} cloth vertices on the emblem side')

    def surface(a, u):
        """The frontmost local cloth depth, and the animation label to go with it."""
        near = sorted(cloth, key=lambda v: (m[A][v] - a) ** 2 + (m[U][v] - u) ** 2)[:6]
        front = max(near, key=lambda v: sign * m[D][v])
        return m[D][front], (m['vlab'][front] if m['vlab'] else 0)

    # Drop the old emblem, and tint every cloth face that remains.
    order = sorted(keep)
    for key in ('fa', 'fb', 'fc', 'colour', 'pri', 'flab', 'alpha', 'finfo'):
        if m.get(key) is not None:
            m[key] = [m[key][i] for i in order]
    m['fcount'] = len(order)
    bronze = rgb_to_hsl16(*BRONZE_RGB)
    m['colour'] = [tint(c, bronze) for c in m['colour']]

    # Where the monogram goes: centred on the old emblem, at the monogram's own proportions. The
    # attack emblem is a sword, far taller than wide, so its box would stretch a DP out of shape.
    sil = silhouette()
    aspect = sil.width / sil.height
    ca, cu = (min(ea) + max(ea)) / 2.0, (min(eu) + max(eu)) / 2.0
    h = spec['height']
    w = h * aspect
    a0, u0 = ca - w / 2, cu - h / 2
    cw, ch = w / COLS, h / ROWS
    base, _ = surface(ca, cu)
    stand = max(spec['stand'], abs(max(ed, key=abs) - base))
    if verbose:
        print(f'  monogram {w:.0f}x{h:.0f}, cell {cw:.1f}x{ch:.1f}, standing {stand:.1f} off the cloth')

    colour = rgb_to_hsl16(*EMBLEM_RGB)
    cache = {}

    def vert(ca_, cu_):
        if (ca_, cu_) in cache:
            return cache[(ca_, cu_)]
        a = round(a0 + ca_ * cw)
        u = round(u0 + cu_ * ch)
        d, lab = surface(a, u)
        pos = {A: a, U: u, D: round(d + sign * stand)}
        m['vx'].append(pos['vx']); m['vy'].append(pos['vy']); m['vz'].append(pos['vz'])
        if m['vlab'] is not None:
            m['vlab'].append(lab)
        m['vcount'] += 1
        cache[(ca_, cu_)] = m['vcount'] - 1
        return m['vcount'] - 1

    added = 0
    for r, c0, c1 in runs(grid(spec['mirror'])):
        a, b, c, d = vert(c0, r), vert(c1, r), vert(c1, r + 1), vert(c0, r + 1)
        for tri in ((a, b, c), (a, c, d)):
            m['fa'].append(tri[0]); m['fb'].append(tri[1]); m['fc'].append(tri[2])
            m['colour'].append(colour)
            m['pri'].append(pri)
            if m['flab'] is not None: m['flab'].append(0)
            if m['alpha'] is not None: m['alpha'].append(0)
            if m['finfo'] is not None: m['finfo'].append(0)
            m['fcount'] += 1
            added += 1

    data = encode(m)
    # It has to read back, or the client never gets as far as drawing it.
    parse_ob2(data)
    if verbose:
        print(f'  {added} new faces -> {m["fcount"]} faces / {m["vcount"]} verts, {len(data)} bytes')
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', default=os.path.join(ROOT, 'content'))
    ap.add_argument('--preview')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    obj = os.path.join(a.content, 'models', 'obj')
    written = []
    for src, spec in SPEC.items():
        data = build(obj, src, spec)
        dst = os.path.join(obj, spec['out'] + '.ob2')
        if a.dry_run:
            print(f'  would write {dst}')
        else:
            open(dst, 'wb').write(data)
            print(f'  wrote {dst}')
        written.append(dst)

    if a.preview and not a.dry_run:
        import ob2render
        # Lit from the front: ob2render uses the client's inventory light, which comes from behind
        # this face and renders it near-black - Jagex's emblem as much as ours.
        orig = ob2render.face_lightness
        ob2render.face_lightness = lambda mm, **kw: orig(mm, lx=50, ly=-10, lz=50)
        ob2render.sheet(written, a.preview, size=340, cols=3, recol=None,
                        xan=0, yan=1024, zan=0, zoom=None, xof=0, yof=0)
        print(f'  preview {a.preview}')


if __name__ == '__main__':
    main()
