#!/usr/bin/env python3
"""The DP monogram as POLYGONS rather than as a grid of little squares.

WHY THIS EXISTS. The first cape emblem emitted one quad per horizontal run of a 21x20 bitmap. It
is the obvious way to turn a picture into geometry and it looks wrong for a reason that has
nothing to do with resolution: every edge of the shape becomes a staircase of axis-aligned steps.
Jagex's own emblem - a shield and a sword - is a handful of large polygons, so its edges are clean
straight lines at any size. Next to it ours read as a red smudge.

So: trace the silhouette's outline, throw away the steps, and triangulate what is left.

  1. the silhouette, despeckled, at a working resolution
  2. connected components - the D, the P and the spike between them
  3. a boundary walk around each one, and around each enclosed hole
  4. Douglas-Peucker on every contour, which is the step that removes the staircases: a run of
     single-pixel steps along a diagonal collapses to the one straight line it was always meant
     to be
  5. ear clipping into triangles

HOLES ARE NOT CUT OUT, THEY ARE PAINTED OVER. The counters of the D and the P would need the
outline and the hole stitched together into one polygon, which is fiddly and easy to get subtly
wrong. They sit on a solid plate, so instead the letters are drawn filled and the counters are
drawn ON TOP in the plate's own colour, a hair further out. Same picture, no stitching.

Coordinates come out normalised to 0..1, x right and y DOWN, which is the order the caller's grid
already uses.
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SILHOUETTE = os.path.join(ROOT, 'Claude outputs', 'dp-icon', 'dp_silhouette.png')

# Traced at this width. High enough that the letterforms are accurate, low enough that a boundary
# walk over them is instant; the simplification afterwards is what sets the final smoothness.
WORK_W = 200


def _mask(path, work_w=WORK_W):
    """The silhouette as a set of (x, y) ink cells, despeckled and cropped to the letters."""
    im = Image.open(path).convert('L').point(lambda v: 255 if v < 128 else 0)
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
    clean = clean.crop(clean.getbbox())
    work_h = max(1, round(clean.height * work_w / clean.width))
    small = clean.resize((work_w, work_h), Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)
    sp = small.load()
    return {(x, y) for y in range(work_h) for x in range(work_w) if sp[x, y]}, work_w, work_h


def _components(cells):
    """4-connected groups of cells."""
    todo = set(cells)
    out = []
    while todo:
        seed = todo.pop()
        stack, group = [seed], {seed}
        while stack:
            x, y = stack.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in todo:
                    todo.discard(n)
                    group.add(n)
                    stack.append(n)
        out.append(group)
    return out


# Moore neighbourhood, clockwise from "west".
_MOORE = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]


def _trace(group):
    """A closed boundary walk around one solid group.

    Moore-neighbour tracing. It stops on a REPEATED (cell, backtrack) state rather than on
    "reached the start again": the walk's whole state is which cell it is on and which neighbour
    it came from, so repeating one means it is about to retrace the loop it just made. That is
    provably bounded, where the usual "stop at the start" test runs forever on a shape whose
    boundary passes through the start cell more than once - which these letterforms do, and which
    the first attempt at this hit, returning a 45,577-point contour for a 5,695-cell letter.
    """
    start = min(group, key=lambda q: (q[1], q[0]))
    p = start
    b = (start[0] - 1, start[1])          # west of the start, which cannot be ink
    contour = []
    seen = set()
    while True:
        if (p, b) in seen:
            break
        seen.add((p, b))
        contour.append(p)
        d = _MOORE.index((b[0] - p[0], b[1] - p[1]))
        nxt = None
        for k in range(1, 9):
            dd = (d + k) % 8
            c = (p[0] + _MOORE[dd][0], p[1] + _MOORE[dd][1])
            if c in group:
                prev = _MOORE[(dd - 1) % 8]
                nxt, b = c, (p[0] + prev[0], p[1] + prev[1])
                break
        if nxt is None:
            break                                   # a single isolated cell
        p = nxt
    return contour


def _holes(group, w, h):
    """The enclosed background regions of a group - the counters of the D and the P."""
    bbox = (min(x for x, _ in group), min(y for _, y in group),
            max(x for x, _ in group), max(y for _, y in group))
    inside = {(x, y)
              for y in range(bbox[1], bbox[3] + 1)
              for x in range(bbox[0], bbox[2] + 1)
              if (x, y) not in group}
    out = []
    todo = set(inside)
    while todo:
        seed = todo.pop()
        stack, region, touches_edge = [seed], {seed}, False
        while stack:
            x, y = stack.pop()
            if x <= bbox[0] or x >= bbox[2] or y <= bbox[1] or y >= bbox[3]:
                touches_edge = True
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in todo:
                    todo.discard(n)
                    region.add(n)
                    stack.append(n)
        # A counter is background that cannot reach the outside of the letter.
        if not touches_edge and len(region) >= 8:
            out.append(region)
    return out


def _simplify(pts, eps):
    """Douglas-Peucker on a closed ring. This is the step that removes the staircases."""
    if len(pts) < 4:
        return pts

    def dp(chain):
        if len(chain) < 3:
            return chain
        (ax, ay), (bx, by) = chain[0], chain[-1]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy) or 1.0
        worst, at = 0.0, 0
        for i in range(1, len(chain) - 1):
            px, py = chain[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if d > worst:
                worst, at = d, i
        if worst <= eps:
            return [chain[0], chain[-1]]
        return dp(chain[:at + 1])[:-1] + dp(chain[at:])

    # Split the ring at its two furthest-apart points so the walk is two open chains; running
    # Douglas-Peucker on a closed ring directly collapses it to nothing.
    far = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    a, b = pts[:far + 1], pts[far:] + [pts[0]]
    ring = dp(a)[:-1] + dp(b)[:-1]
    return ring if len(ring) >= 3 else pts


def _area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))


def _earclip(poly):
    """Triangulate a simple polygon. Winding is normalised so every triangle comes out the same way."""
    p = list(poly)
    if _area2(p) < 0:
        p.reverse()
    n = len(p)
    if n < 3:
        return []
    idx = list(range(n))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 4 * n:
        guard += 1
        clipped = False
        for i in range(len(idx)):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            ax, ay = p[a]; bx, by = p[b]; cx, cy = p[c]
            cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
            if cross <= 0:
                continue                           # reflex corner, not an ear
            bad = False
            for j in idx:
                if j in (a, b, c):
                    continue
                px, py = p[j]
                d1 = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
                d2 = (cx - bx) * (py - by) - (cy - by) * (px - bx)
                d3 = (ax - cx) * (py - cy) - (ay - cy) * (px - cx)
                if d1 >= 0 and d2 >= 0 and d3 >= 0:
                    bad = True
                    break
            if bad:
                continue
            tris.append((p[a], p[b], p[c]))
            idx.pop(i)
            clipped = True
            break
        if not clipped:
            break
    if len(idx) == 3:
        tris.append((p[idx[0]], p[idx[1]], p[idx[2]]))
    return tris


def monogram(eps_frac=0.012, path=SILHOUETTE):
    """The monogram as triangles, normalised to 0..1 with y DOWN.

    Returns (ink, counters): ink is the letters, counters are their enclosed holes, to be drawn on
    top in the plate's colour.
    """
    cells, w, h = _mask(path)
    scale = max(w, h)
    eps = eps_frac * scale
    ink, counters = [], []
    for group in _components(cells):
        if len(group) < 20:
            continue
        ring = _simplify(_trace(group), eps)
        ink.extend(_earclip(ring))
        for hole in _holes(group, w, h):
            hring = _simplify(_trace(hole), eps)
            counters.extend(_earclip(hring))

    def norm(tris):
        return [tuple((x / w, y / h) for x, y in t) for t in tris]

    return norm(ink), norm(counters)


# The Veteran rank's own chat icon, as it is drawn on content/sprites/mod_icons.png: two horns
# sweeping up and out, a spike up the middle, the three merging into a body over a stem and a
# foot. Thirteen cells, because that is the size a chat icon is drawn at and this shape was
# designed to survive it.
#
# USING THIS ON THE CAPE rather than the DP monogram makes the rank one mark in both places, and
# a shape drawn to read at thirteen pixels reads at any size. It encloses no holes - every gap
# between the horns and the spike is open to the top - so it needs no counters.
VETERAN_ICON = [
    '.............',
    '##.........##',
    '###.......###',
    '###.......###',
    '.###..#..###.',
    '.###.###.###.',
    '..#########..',
    '..#########..',
    '...#######...',
    '....#####....',
    '.....###.....',
    '....#####....',
    '.............',
]


def _grid_mask(rows, upscale=16):
    """A character grid blown up, so the tracer has room to round its corners off."""
    cells = set()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == '#':
                for dy in range(upscale):
                    for dx in range(upscale):
                        cells.add((x * upscale + dx, y * upscale + dy))
    return cells, len(rows[0]) * upscale, len(rows) * upscale


def veteran(eps_cells=0.62, upscale=16):
    """The chat icon as triangles, normalised to 0..1 with y DOWN.

    eps_cells is the Douglas-Peucker tolerance in CELLS of the original 13x13 art: enough to turn
    a staircase of single-cell steps into the one diagonal it stands for, not so much that a horn
    loses its point.
    """
    cells, w, h = _grid_mask(VETERAN_ICON, upscale)
    eps = eps_cells * upscale
    ink = []
    for group in _components(cells):
        if len(group) < upscale * upscale // 2:
            continue
        ink.extend(_earclip(_simplify(_trace(group), eps)))
    return [tuple((x / w, y / h) for x, y in t) for t in ink], []


if __name__ == '__main__':
    import sys
    from PIL import ImageDraw
    ink, counters = monogram()
    print(f'{len(ink)} ink triangles, {len(counters)} counter triangles')
    S = 600
    im = Image.new('RGB', (S, S), (30, 30, 30))
    d = ImageDraw.Draw(im)
    for t in ink:
        d.polygon([(x * S, y * S) for x, y in t], fill=(184, 50, 40))
    for t in counters:
        d.polygon([(x * S, y * S) for x, y in t], fill=(238, 178, 116))
    out = sys.argv[1] if len(sys.argv) > 1 else 'dpglyph.png'
    im.save(out)
    print('wrote', out)
