#!/usr/bin/env python3
"""
Build the Trading Post's model out of OSRS parts: one .ob2, the parts scaled, placed and merged.

WHAT IT IS. A standing wooden board (the frame of the Shooting Star noticeboard) with trade notices
pinned to it, a gold-trimmed strongbox at its foot - the collection box - and a crate with coins on
it. A 2x1 loc, because the board is two tiles wide. Nothing in the cache looks like it, which was
the brief: players interact with an object, not an npc, and it should not be the Grand Exchange.

WHY ONE MERGED MODEL AND NOT model=/model2=. A loc's extra models are all drawn at its origin, and
there is no per-model offset or scale in a loc config, so a chest at the board's foot has to have
its offset baked into its vertices. Merging is straightforward: vertices are appended, face
indices and texture-triangle indices shift by what came before, and per-face tables that only
some parts carry (alpha, priority, face info) are filled with each part's own default for the
parts that lack them.

  python3 gentradingpostmodel.py "<newest cache>" --content ../../content [--preview out.png]
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flatcache import Store
from osrs2ob2 import decode, encode, roundtrip
from animconv474 import pack_append

NAME = 'trading_post'
FILE = NAME + '_8'           # shape 10 (centrepiece) models carry the _8 suffix in model.pack

def hsl(h, s, l):
    return (h << 10) | (s << 7) | l


# (osrs model, scale, dx, dy, dz, rotate quarter-turns about y, recolours src->dst)
# Recolours here are by colour alone. The board's are not - see crest() - because its frame, panel
# and crest share their colours and only position tells them apart.
# Units: 128 per tile, y negative is up, the loc's origin at the centre of its 2x1 footprint.
PARTS = [
    # the board. Its own z (25..49) already sits it at the back half of the footprint, front face
    # at z=25. Recoloured: the star chart on its face becomes plain board for the notices to sit
    # on, and the moon-and-stars crest becomes gold.
    (41603, 1.00,   0,   0,   0, 0, []),
    # the strongbox at the left foot, turned to face out
    (14984, 0.52, -78,   0, -22, 0, []),
    # a crate at the right foot, and a scatter of coins on its lid
    (15402, 0.62,  74,   0, -18, 0, []),
    (26003, 0.46,  74, -50, -20, 0, []),
    # a sack leaning between them
    (5494,  0.48,  18,   0, -36, 0, []),
]


# THE NOTICES are not from the cache: each is a parchment rectangle a hair in front of the board,
# with a few ink lines across it, drawn from both sides so the client's backface cull cannot drop it
# whichever way the loc is turned. (x centre, y centre, width, height, lines)
NOTICES = [(-72, -168, 44, 40, 4), (-20, -176, 40, 30, 3), (30, -164, 48, 44, 5), (80, -172, 36, 34, 3),
           (-48, -122, 50, 34, 3), (8, -126, 36, 38, 4), (62, -120, 46, 30, 3)]
PARCHMENT = hsl(8, 2, 100)
INK = hsl(8, 2, 40)
PIN = hsl(0, 7, 45)
CORK = hsl(6, 3, 30)
BACKING = (-108, -199, 108, -97, 30)   # x0, y0, x1, y1, z
BACK = (-108, -199, 108, -97, 46)
BOARD = 7690                           # the board's own darkest wood
FRONT_Z = 25


def notices():
    m = dict(ver=2, vcount=0, fcount=0, vx=[], vy=[], vz=[], fa=[], fb=[], fc=[], colour=[], alpha=None,
             textured=0, priority=255, pri=[], tris=[], vlab=None, flab=None, finfo=None)

    def quad(x0, y0, x1, y1, z, colour):
        v = m['vcount']
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            m['vx'].append(x); m['vy'].append(y); m['vz'].append(z)
        m['vcount'] += 4
        for a, b, c in ((0, 1, 2), (0, 2, 3), (2, 1, 0), (3, 2, 0)):
            m['fa'].append(v + a); m['fb'].append(v + b); m['fc'].append(v + c)
            m['colour'].append(colour); m['pri'].append(0)
        m['fcount'] += 4

    # the cork the notices are pinned to, over the star chart the board was built around. Behind
    # the frame's front bars (z=25), in front of the recessed chart (z=31 and deeper).
    # IN TILES, not one quad each: the client sorts faces by their centres, and one board-sized
    # triangle has its centre in front of half the notices from any three-quarter view.
    def tiled(x0, y0, x1, y1, z, colour, n=8, rows=4):
        for i in range(n):
            for j in range(rows):
                quad(x0 + (x1 - x0) * i // n, y0 + (y1 - y0) * j // rows,
                     x0 + (x1 - x0) * (i + 1) // n, y0 + (y1 - y0) * (j + 1) // rows, z, colour)
    tiled(*BACKING, CORK)
    tiled(*BACK, BOARD)
    for cx, cy, w, h, lines in NOTICES:
        quad(cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2, FRONT_Z - 2, PARCHMENT)
        pad, gap = 5, (h - 10) // max(1, lines)
        for i in range(lines):
            y = cy - h // 2 + 7 + i * gap
            right = cx + w // 2 - pad - (10 if i == lines - 1 else 0)
            quad(cx - w // 2 + pad, y, right, y + 2, FRONT_Z - 3, INK)
        quad(cx - 2, cy - h // 2 + 1, cx + 2, cy - h // 2 + 5, FRONT_Z - 4, PIN)
    return m


# THE CREST. The noticeboard's moon and stars (three light greys, all on the plane z=34 above
# y=-200) and the disc behind them (7580 on that same plane) become one gold medallion with a
# darker rim, so nothing of the Shooting Star board is left to recognise.
CREST_GOLD = hsl(8, 6, 62)
CREST_RIM = hsl(8, 6, 40)


def crest(m):
    for i in range(m['fcount']):
        a, b, c = m['fa'][i], m['fb'][i], m['fc'][i]
        x = (m['vx'][a] + m['vx'][b] + m['vx'][c]) / 3
        y = (m['vy'][a] + m['vy'][b] + m['vy'][c]) / 3
        z = (m['vz'][a] + m['vz'][b] + m['vz'][c]) / 3
        if y < -200 and abs(x) < 30 and round(z) == 34:
            m['colour'][i] = CREST_GOLD if m['colour'][i] in (9313, 9412, 9447, 7580) else m['colour'][i]
        elif y < -200 and abs(x) < 30 and m['colour'][i] in (7582, 7585):
            m['colour'][i] = CREST_RIM
    return m


# THE PANEL. Every face centred inside the frame comes out - the star chart, the shooting-star
# streaks that cross it in front of where the notices go, and the board's back, whose few big
# triangles beat the small notices in the client's depth sort and cut across them. The cork and a
# plain wooden back in notices() are the panel now. The frame is what is left: its bars start at |x|=106 and at
# y=-197 above and y=-99 below.
PANEL = (-107, -198, 107, -98)


def hollow(m):
    x0, y0, x1, y1 = PANEL
    def inside(i):
        vs = (m['fa'][i], m['fb'][i], m['fc'][i])
        return x0 <= sum(m['vx'][v] for v in vs) / 3 <= x1 and y0 <= sum(m['vy'][v] for v in vs) / 3 <= y1
    keep = [i for i in range(m['fcount']) if not inside(i)]
    for k in ('fa', 'fb', 'fc', 'colour', 'pri', 'alpha', 'finfo', 'flab'):
        if m.get(k):
            m[k] = [m[k][i] for i in keep]
    m['fcount'] = len(keep)
    return m


def transform(m, scale, dx, dy, dz, quarter):
    for i in range(m['vcount']):
        x, y, z = m['vx'][i], m['vy'][i], m['vz'][i]
        for _ in range(quarter % 4):
            x, z = z, -x
        m['vx'][i] = int(round(x * scale)) + dx
        m['vy'][i] = int(round(y * scale)) + dy
        m['vz'][i] = int(round(z * scale)) + dz
    return m


def recolour(m, pairs):
    fi = m.get('finfo') or [0] * m['fcount']
    for i in range(m['fcount']):
        if fi[i] & 2:
            continue
        for a, b in pairs:
            if m['colour'][i] == a:
                m['colour'][i] = b
                break


def merge(parts):
    out = dict(ver=2, vcount=0, fcount=0, vx=[], vy=[], vz=[], fa=[], fb=[], fc=[], colour=[],
               alpha=None, textured=0, priority=255, pri=[], tris=[], vlab=None, flab=None, finfo=None)
    any_alpha = any(p['alpha'] for p in parts)
    any_finfo = any(p.get('finfo') for p in parts)
    alpha, finfo = [], []
    for p in parts:
        vo, to = out['vcount'], len(out['tris'])
        out['vx'] += p['vx']; out['vy'] += p['vy']; out['vz'] += p['vz']
        out['fa'] += [a + vo for a in p['fa']]
        out['fb'] += [b + vo for b in p['fb']]
        out['fc'] += [c + vo for c in p['fc']]
        out['colour'] += p['colour']
        # ONE PRIORITY FOR EVERY FACE. The client draws a higher-priority face after a lower one
        # whatever their depth, so the parts' own priorities (the board 0-8, the coins 1-5, the
        # chest 0-1) painted the props over the board's back panel when seen from behind - you
        # could see straight through it. With one priority the client falls back to a pure depth
        # sort, which is right from every side.
        out['pri'] += [0] * p['fcount']
        alpha += p['alpha'] if p['alpha'] else [0] * p['fcount']
        fi = p.get('finfo') or [0] * p['fcount']
        # a textured face's info carries its texture triangle's index in the top six bits
        finfo += [((f >> 2) + to) << 2 | (f & 3) if f & 2 else f for f in fi]
        out['tris'] += [tuple(v + vo for v in t) for t in (p.get('tris') or [])]
        out['vcount'] += p['vcount']
        out['fcount'] += p['fcount']
    if any_alpha:
        out['alpha'] = alpha
    if any_finfo:
        out['finfo'] = finfo
    return out


def build(st):
    parts = []
    for mid, scale, dx, dy, dz, q, rec in PARTS:
        m = decode(st.read(7, mid))
        if m is None:
            raise SystemExit(f'model {mid} does not decode')
        recolour(m, rec)
        if mid == 41603:
            hollow(crest(m))
        parts.append(transform(m, scale, dx, dy, dz, q))
    parts.append(notices())
    m = merge(parts)
    ob2 = encode(m)
    ok, why = roundtrip(ob2, m)
    if not ok:
        raise SystemExit(f'merged model does not survive a round trip: {why}')
    return m, ob2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('--content', required=True)
    ap.add_argument('--preview')
    a = ap.parse_args()
    m, ob2 = build(Store(a.cache))
    path = os.path.join(a.content, 'models', 'loc', FILE + '.ob2')
    open(path, 'wb').write(ob2)
    ids, _ = pack_append(os.path.join(a.content, 'pack', 'model.pack'), [FILE])
    print(f'wrote {path}: {m["vcount"]} verts, {m["fcount"]} faces, model id {ids[FILE]}')
    if a.preview:
        import ob2render
        from PIL import Image
        views = [(120, 0), (100, 220), (100, 2048 - 220), (60, 1024)]  # front, both three-quarters, back
        tiles = [ob2render.render(ob2render.Model(path), size=260, xan=x, yan=y) for x, y in views]
        sheet = Image.new('RGB', (260 * len(tiles), 260))
        for i, t in enumerate(tiles):
            sheet.paste(t, (260 * i, 0))
        sheet.save(a.preview)
        print(a.preview)


if __name__ == '__main__':
    main()
