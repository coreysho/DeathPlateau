#!/usr/bin/env python3
"""Render a range of OSRS spotanims as 377 models, so a cloud can be CHOSEN rather than guessed.

The Zulrah venom cloud has been wrong twice: it was 1045 (the barrage's two orbs, so what lay on
the platform was a pair of projectiles) and is now 1043, which the owner still reports as wrong.
This converts each candidate exactly as importosrsspot would - decode the model, bake the spot's
own recolours in, re-encode to ob2 - and draws it, so the choice is made from pictures.
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flatcache import Store
from osrsspot import decode_osrs_spot, load_osrs_spots
from osrs2ob2 import convert_checked, decode as decode_osrs_model, encode as encode_ob2, SHARED_TEXTURES
from osrslocimport import bake
import ob2render

ap = argparse.ArgumentParser()
ap.add_argument('cache')
ap.add_argument('--from', dest='lo', type=int, required=True)
ap.add_argument('--to', dest='hi', type=int, required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--size', type=int, default=170)
ap.add_argument('--cols', type=int, default=6)
a = ap.parse_args()

st = Store(a.cache)
spots = load_osrs_spots(st)
tmp = os.path.join(os.path.dirname(os.path.abspath(a.out)), '_spotrender')
os.makedirs(tmp, exist_ok=True)

paths, labels = [], []
for sid in range(a.lo, a.hi + 1):
    if sid not in spots:
        continue
    try:
        d = decode_osrs_spot(spots[sid])
        if 'model' not in d:
            continue
        m = decode_osrs_model(st.read(7, d['model']))
        if m is None:
            print(f'{sid}: model {d["model"]} does not reconcile'); continue
        bake(m, d.get('recol'), d.get('retex'), SHARED_TEXTURES)
        ob2 = encode_ob2(m)
        p = os.path.join(tmp, f'spot_{sid}.ob2')
        open(p, 'wb').write(ob2)
        paths.append(p)
        labels.append(sid)
        print(f'{sid}: model {d["model"]}  {m["vcount"]} verts  anim {d.get("anim")}  recol {d.get("recol")}')
    except Exception as e:
        print(f'{sid}: {str(e)[:60]}')

if not paths:
    raise SystemExit('nothing rendered')
ob2render.sheet(paths, a.out, size=a.size, cols=a.cols)
print(f'\nwrote {a.out} - {len(paths)} spotanims, ids {labels}')
