#!/usr/bin/env python3
"""Find the spotanims that are SHAPED like a gas cloud lying on the ground.

The Zulrah venom cloud has now been wrong twice by identification - 1045 was the barrage's two
orbs, and 1043, which replaced it, renders as a bright green spiky crystal. Guessing an id from a
description has failed twice, so this picks by geometry instead, over every spotanim in the cache.

A puff of gas on a tile is: wider than it is tall, about a tile across or more, and TRANSLUCENT -
it must carry face alpha, which is the one property a solid projectile or crystal does not have.
Colour is checked last and loosely, because a spot's recolours are baked in before this sees it.
"""
import sys, os, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flatcache import Store
from osrsspot import decode_osrs_spot, load_osrs_spots
from osrs2ob2 import decode as decode_osrs_model, encode as encode_ob2, SHARED_TEXTURES
from osrslocimport import bake

ap = argparse.ArgumentParser()
ap.add_argument('cache')
ap.add_argument('--min-width', type=int, default=110)   # a tile is 128
ap.add_argument('--max-ratio', type=float, default=0.85)  # height / width
ap.add_argument('--limit', type=int, default=40)
ap.add_argument('--lo', type=int, default=0)
ap.add_argument('--hi', type=int, default=99999)
ap.add_argument('--max-verts', type=int, default=4096)
ap.add_argument('--render')
a = ap.parse_args()

st = Store(a.cache)
spots = load_osrs_spots(st)
print(f'{len(spots)} spotanims in the cache\n')

hits = []
for sid in sorted(spots):
    if sid < a.lo or sid > a.hi:
        continue
    try:
        d = decode_osrs_spot(spots[sid])
        if 'model' not in d:
            continue
        raw = st.read(7, d['model'])
        if raw is None:
            continue
        m = decode_osrs_model(raw)
        if m is None:
            continue
        bake(m, d.get('recol'), d.get('retex'), SHARED_TEXTURES)
        ob2 = encode_ob2(m)
    except Exception:
        continue

    # bounds straight off the ob2 we would actually ship
    import ob2render
    try:
        tmp = ob2render.P(ob2, len(ob2) - 18)
        vcount = tmp.g2(); fcount = tmp.g2(); tcount = tmp.g1()
        f_tex, f_pri, f_alpha, f_flabel, f_vlabel = tmp.g1(), tmp.g1(), tmp.g1(), tmp.g1(), tmp.g1()
    except Exception:
        continue
    if f_alpha != 1:
        continue
    if vcount > a.max_verts:
        continue                                  # not translucent: not gas
    xs = m.get('vx') or []; ys = m.get('vy') or []; zs = m.get('vz') or []
    if not xs:
        continue
    w = max(max(xs) - min(xs), max(zs) - min(zs))
    h = max(ys) - min(ys)
    if w < a.min_width or h > w * a.max_ratio:
        continue
    # A PUFF HAS SOME DEPTH. A model with no height at all is a decal painted on the floor, not gas.
    if h < w * 0.12:
        continue
    # AND IT IS GREEN. Hue is the top six bits of HSL16 and RS greens sit around 16-34. The spot's
    # own recolours are baked in above, so this is the colour it would really be in game. Alpha is
    # already required, so between them this is "translucent, flat, wide and green" - which is what a
    # cloud IS, rather than what some id was once said to be.
    cols = [c for c in (m.get('colour') or []) if c]
    greens = sum(1 for c in cols if 16 <= ((c >> 10) & 0x3f) <= 34)
    if not cols or greens < len(cols) * 0.5:
        continue
    hits.append((sid, d['model'], vcount, fcount, w, h, round(h / max(w, 1), 2), d.get('anim'),
                 f'{greens}/{len(cols)}'))

hits.sort(key=lambda r: r[6])                     # flattest first
print(f'{"spot":>6} {"model":>7} {"verts":>6} {"faces":>6} {"width":>6} {"height":>7} {"h/w":>5} {"anim":>6} {"green":>9}')
for r in hits[:a.limit]:
    print(f'{r[0]:>6} {r[1]:>7} {r[2]:>6} {r[3]:>6} {r[4]:>6} {r[5]:>7} {r[6]:>5} {r[7]:>6} {r[8]:>9}')
print(f'\n{len(hits)} translucent, wide, flat spotanims in all')
