#!/usr/bin/env python3
"""List the locs of one OSRS map square, by name and level - so a course can be grafted surgically.

Importing a whole square would replace the 2006 town under it. The rooftop course is a handful of
obstacles and the roof platforms they stand on, so the first job is finding exactly which locs those
are rather than taking all 2904 of them.
"""
import sys, os, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importosrsmap as IM
from osrsloc import load_osrs_locs
from flatcache import Store

ap = argparse.ArgumentParser()
ap.add_argument('--maps', required=True)
ap.add_argument('--cache', required=True)
ap.add_argument('--region', required=True)
ap.add_argument('--level', type=int, default=None, help='only this level')
ap.add_argument('--grep', default=None, help='only names containing this (case-insensitive)')
a = ap.parse_args()

mx, mz = (int(v) for v in a.region.split('_'))
ms = (mx << 8) | mz

src = IM.Source(a.maps) if hasattr(IM, 'Source') else None
if src is None:
    # the class is defined inside importosrsmap with another name; find it
    for n in dir(IM):
        o = getattr(IM, n)
        if isinstance(o, type) and hasattr(o, 'locs') and hasattr(o, 'terrain'):
            src = o(a.maps); break
if src is None:
    raise SystemExit('could not find the map source class in importosrsmap')

locs = src.locs(a.region, ms)
names, _ = load_osrs_locs(Store(a.cache))

rows = []
# decode_locs returns (id, level, x, z, shape, rot)
for (lid, level, x, z, shape, angle) in locs:
    d = names.get(lid) or {}
    nm = d.get('name') or '(unnamed)'
    if a.level is not None and level != a.level:
        continue
    if a.grep and a.grep.lower() not in nm.lower():
        continue
    rows.append((level, nm, lid, mx * 64 + x, mz * 64 + z, shape, angle, d.get('ops')))

rows.sort()
for level, nm, lid, ax, az, shape, angle, ops in rows:
    print(f'level {level}  {nm:<28} id {lid:<6} at {ax},{az}  shape {shape} angle {angle}  ops {ops}')
print(f'\n{len(rows)} locs')
by = collections.Counter(r[0] for r in rows)
print('per level:', dict(sorted(by.items())))
