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
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode  # noqa: E402
import dpglyph  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MASK = os.path.join(ROOT, 'Claude outputs', 'dp-icon', 'dp_silhouette.png')

# The brand's red, as the sigil is drawn.
EMBLEM_RGB = (184, 50, 40)

# THE BACKING PLATE IS NOT DECORATION. THE CLOTH HAS A HOLE WHERE THE EMBLEM GOES.
#
# Render the attack cape with its emblem removed and nothing put back and you see the player's
# torso - the armour they are wearing - straight through the cape. Jagex's emblem is a solid gold
# disc, and plugging that hole is half of what it is for. A monogram is open letters: counters,
# the gap between D and P, the space around the spike. Put one there on its own and the armour
# shows through every one of those gaps, which is exactly what the first wear render showed.
#
# So a disc goes down first, in a light bronze, and the monogram sits on top of it. That plugs the
# hole and gives the red something to read against - the cape's centre panel is dark, and the
# brand red on dark brown is mud. It is also what the shape has always done: a light disc with a
# dark device on it.
# AND IT CANNOT BE MUCH LIGHTER THAN THIS. hsl24to16 throws saturation away as lightness climbs -
# s >>= 1 above 179, >>= 2 above 192, >>= 3 above 217 - so a pale bronze plate comes out GREY, and
# a cream one comes out a flat stone grey with no bronze left in it at all. Both were tried in the
# client and both lost the colour. This sits at lightness 177, just under the first step down.
BACKING_RGB = (238, 178, 116)

# The counters of the D and the P. Normally the plate's own colour - they are meant to read as
# holes in the letters - but kept separate so it can be set to something loud to find out whether
# a bright patch inside a letter is really the counter or a culled triangle showing the plate.
COUNTER_RGB = BACKING_RGB
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
        # Flipped rather than mirrored: this mesh lies flat and its icon camera looks at the
        # emblem from the opposite side again, so a mirror alone came out rotated 180 degrees.
        plane='xz', height=30.0, stand=3.0, mirror=False, flip=True,
    ),
    'obj_attack_cape_manwear': dict(
        out='obj_veteran_cape_manwear',
        colours={11224, 7116, 103, 51, 6563},
        box=(-12, 13, -141, -96, 14, 17),
        # HEIGHT IS BOUNDED BY THE ANIMATION LABEL, not by taste. The emblem is rigid on one
        # label (see emblem_lab below), and on the cape's front face that label's cloth only
        # spans x -20..20, y -139..-98. Run the emblem past that and it overhangs cloth on
        # neighbouring labels, which deform away from it under a walk - the cloth pokes through
        # and the emblem tears into horizontal stripes. 36 keeps it inside at the monogram's own
        # proportions, and is still half again the width of Jagex's.
        plane='xy', height=36.0, stand=4.0, mirror=True,
    ),
    'obj_attack_cape_womanwear': dict(
        out='obj_veteran_cape_womanwear',
        colours={11224, 7116, 103, 51, 6563},
        box=(-12, 13, -141, -96, 14, 17),
        plane='xy', height=36.0, stand=4.0, mirror=True,
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


def disc_fan(cols, rows, points=16):
    """The plate, as a triangle fan from its centre - in grid coordinates.

    A FAN AND NOT A GRID OF QUADS, and this is the difference between a cape that survives being
    walked in and one that does not. Built row by row like the monogram, the plate's quads do not
    share their corners: a row spanning columns 4..17 sits against one spanning 3..18, so a vertex
    of one lands in the middle of the other's edge. Those T-junctions are seamless while the model
    is still and split into hairline cracks the moment it is posed and the vertices move apart by
    fractions of a pixel - and what shows through the cracks is the dark cloth, so the plate
    stripes. A fan has no T-junctions: every triangle shares whole edges with its neighbours.

    Returns (centre, ring) in grid coordinates, for the caller to turn into vertices.
    """
    cx, cy = cols / 2.0, rows / 2.0
    ring = []
    for i in range(points):
        t = 2.0 * math.pi * i / points
        ring.append((cx + cx * math.cos(t), cy + cy * math.sin(t)))
    return (cx, cy), ring


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

    # ONE ANIMATION LABEL FOR THE WHOLE EMBLEM, taken from the faces being removed.
    #
    # Jagex puts all 26 of its emblem's vertices on a single label while the cloth around them
    # spans eight, so the emblem moves as one rigid piece with that part of the cape. Giving each
    # new vertex the label of its OWN nearest cloth vertex - the obvious thing, and what this did
    # first - spreads the monogram across all eight, and the moment the cape is posed they move
    # apart and the emblem tears into horizontal stripes. It looks perfect standing still, which
    # is why it has to be rendered mid-walk before it is believed.
    emblem_lab = 0
    if m['vlab'] is not None:
        labs = [m['vlab'][v] for v in ev]
        emblem_lab = max(set(labs), key=labs.count)

    def surface(a, u):
        """The frontmost local cloth depth at (across, up)."""
        near = sorted(cloth, key=lambda v: (m[A][v] - a) ** 2 + (m[U][v] - u) ** 2)[:6]
        return m[D][max(near, key=lambda v: sign * m[D][v])]

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
    # THE EMBLEM SITS ON A FLAT PLANE, NOT ON THE CLOTH'S CURVE, and this is what stops it looking
    # choppy. The client shades a face from its own normal. Follow the cape's curve and every
    # triangle of the monogram gets a slightly different normal and so a slightly different red,
    # and the letters read as crumpled foil rather than as paint. Jagex's emblem spans ONE unit of
    # depth across its whole width - it is flat - and shades as a single tone. Ours spanned seven.
    #
    # A plane rather than a fixed depth, so it still leans with the cape instead of sticking out
    # of it: least squares over the cloth under the emblem, then pushed out far enough to clear
    # the frontmost of that cloth everywhere.
    # ONE DEPTH FOR EVERY EMBLEM VERTEX, not a tilted plane and certainly not the cloth's curve.
    #
    # A tilted plane was the first attempt and it still shaded in steps, because a vertex's depth
    # is rounded to a whole unit: tilt the plane and the rounding quantises it into a staircase,
    # the triangles stop being exactly coplanar, and each one picks up its own normal and its own
    # shade again. A single constant depth rounds to one number everywhere, so every triangle of
    # the monogram is exactly coplanar and shades as one flat tone - which is what Jagex's does,
    # and why its 26 vertices span a single unit of depth where ours spanned seven.
    #
    # It stands off the FRONTMOST cloth under it, so a flat badge on a curved cape never sinks in.
    region = [v for v in cloth if a0 - cw <= m[A][v] <= a0 + w + cw and u0 - ch <= m[U][v] <= u0 + h + ch]
    if len(region) < 6:
        region = cloth
    front = max(sign * m[D][v] for v in region)
    stand = spec['stand']
    flat = front + stand                      # in sign-space; vert() multiplies it back out
    if verbose:
        print(f'  monogram {w:.0f}x{h:.0f}, flat at depth {sign * flat:.0f}, '
              f'{stand:.0f} clear of {len(region)} cloth verts')

    cache = {}

    def vert(ca_, cu_, off):
        """One grid corner at a given stand-off, shared between the quads that meet there."""
        if (ca_, cu_, off) in cache:
            return cache[(ca_, cu_, off)]
        a = round(a0 + ca_ * cw)
        u = round(u0 + cu_ * ch)
        # off is measured out from the flat plane, so the plate, the letters and the counters
        # sit at three fixed depths rather than three curved sheets.
        pos = {A: a, U: u, D: round(sign * (flat + (off - stand)))}
        m['vx'].append(pos['vx']); m['vy'].append(pos['vy']); m['vz'].append(pos['vz'])
        if m['vlab'] is not None:
            m['vlab'].append(emblem_lab)
        m['vcount'] += 1
        cache[(ca_, cu_, off)] = m['vcount'] - 1
        return m['vcount'] - 1

    added = 0

    def face(tri, colour, priority):
        nonlocal added
        m['fa'].append(tri[0]); m['fb'].append(tri[1]); m['fc'].append(tri[2])
        m['colour'].append(colour)
        m['pri'].append(priority)
        if m['flab'] is not None: m['flab'].append(0)
        if m['alpha'] is not None: m['alpha'].append(0)
        if m['finfo'] is not None: m['finfo'].append(0)
        m['fcount'] += 1
        added += 1

    # The plate, as a fan, at the emblem's own priority.
    centre, ring = disc_fan(COLS, ROWS)
    backing = rgb_to_hsl16(*BACKING_RGB)
    hub = vert(centre[0], centre[1], stand)
    rim = [vert(px, py, stand) for px, py in ring]
    for i in range(len(rim)):
        face((hub, rim[i], rim[(i + 1) % len(rim)]), backing, pri)

    # THE MONOGRAM IS POLYGONS, NOT A GRID OF LITTLE SQUARES. One quad per run of a bitmap is the
    # obvious way to turn a picture into geometry and it looks wrong for a reason that has nothing
    # to do with resolution: every edge becomes a staircase. Jagex's device is a handful of large
    # polygons, so its edges are straight lines at any size, and beside it ours read as a smudge.
    # dpglyph traces the letterforms and triangulates them instead - see that module.
    ink, counters = dpglyph.monogram()
    # Each mesh is seen from its own side, so the monogram is mirrored, flipped, or both to come
    # out reading the right way round. EVERY REFLECTION ALSO REVERSES WINDING: a straight
    # x -> 1-x left every face pointing away from the camera and the client culled the whole
    # monogram, which is how this was found. Two reflections make a rotation and cancel out, so
    # what matters is whether the count is odd. The old bitmap version flipped the PICTURE, where
    # winding does not arise - which is why none of this came up until now.
    reflections = 0
    if spec['mirror']:
        ink = [[(1.0 - x, y) for x, y in t] for t in ink]
        counters = [[(1.0 - x, y) for x, y in t] for t in counters]
        reflections += 1
    if spec.get('flip'):
        ink = [[(x, 1.0 - y) for x, y in t] for t in ink]
        counters = [[(x, 1.0 - y) for x, y in t] for t in counters]
        reflections += 1
    if reflections % 2:
        ink = [list(reversed(t)) for t in ink]
        counters = [list(reversed(t)) for t in counters]

    # SCALED TO FIT INSIDE THE PLATE, exactly. The old emblem put the monogram's bounding box over
    # the plate's, so the corners - the sigil's spike, the D's top serif - landed on bare cloth
    # outside the disc and read as stray red blocks nobody could explain. This finds the furthest
    # ink vertex from the centre and shrinks until that one vertex is on the rim, so every part of
    # the monogram is on the plate and none of it is wasted.
    pts = [p for t in ink + counters for p in t]
    reach = max(math.hypot((x - 0.5) * 2, (y - 0.5) * 2) for x, y in pts)
    fit = 0.94 / reach

    def place(t, off):
        return tuple(vert(COLS * (0.5 + (x - 0.5) * fit), ROWS * (0.5 + (y - 0.5) * fit), off) for x, y in t)

    # A PRIORITY HIGHER THAN THE PLATE so the two can never be sorted into each other: they sit a
    # unit apart, which is inside the margin the client's depth sort works to once a pose has moved
    # everything, and priority makes the order a fact rather than a race.
    emblem_colour = rgb_to_hsl16(*EMBLEM_RGB)
    for t in ink:
        face(place(t, stand + 1.0), emblem_colour, pri + 1)
    # The counters of the D and the P, painted over the letters in the plate's own colour rather
    # than cut out of them - the same picture, without stitching a hole into a polygon.
    for t in counters:
        # LEVEL WITH THE PLATE, not standing in front of the letters. Priority already decides
        # that these paint last, so they do not need to be physically nearer - and two units of
        # float would show as a raised island inside each letter at any grazing angle.
        face(place(t, stand), rgb_to_hsl16(*COUNTER_RGB), pri + 2)

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
