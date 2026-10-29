#!/usr/bin/env python3
"""Drop the faces that have no area from a .ob2, which is where thin dark lines over armour come from.

A triangle whose three points are the same, or lie on one line, encloses nothing. In the base pose
the client culls it: method382 keeps a face only when the screen-space cross product is > 0, and a
flat triangle's is 0. Give it an animation and a perspective divide, though, and the three points
stop being exactly collinear - the cross product comes out 1 or 2, the face is kept, and it
rasterises as a one-pixel line. On a cape, whose faces are priority 4-7 and so are painted AFTER
the legs' priority 1 and the body's 3, that line lands ON TOP of the armour however far behind it
the cape is.

That is the thin dark mark across a plateskirt in the max cape screenshots of 29 October. The
infernal max cape's manwear model carries five of them, its womanwear fifteen, and they are in
Jagex's own models - OSRS 33102 and 33114 have exactly the same face indices - so this is faithful
import of a fault, not one we introduced.

Removing them cannot change what is drawn: a face with no area draws nothing when the client is
right about it.

  python3 tools/models/stripdegenerate.py content/models/obj/obj_infernal_max_cape_manwear.ob2
  python3 tools/models/stripdegenerate.py --dry-run content/models/obj/*max_cape*.ob2
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode


def degenerate(m):
    """Indices of the faces with no area, and why each one has none."""
    out = []
    for i in range(m['fcount']):
        a, b, c = m['fa'][i], m['fb'][i], m['fc'][i]
        if a == b or b == c or a == c:
            out.append((i, 'a vertex used twice')); continue
        p = [(m['vx'][v], m['vy'][v], m['vz'][v]) for v in (a, b, c)]
        if len(set(p)) < 3:
            out.append((i, 'two vertices in the same place')); continue
        u = [p[1][k] - p[0][k] for k in range(3)]
        v = [p[2][k] - p[0][k] for k in range(3)]
        if (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]) == (0, 0, 0):
            out.append((i, 'three points on one line'))
    return out


def strip(m, drop):
    """A copy of m without those faces. Every per-face array goes with them."""
    keep = [i for i in range(m['fcount']) if i not in drop]
    out = dict(m)
    out['fcount'] = len(keep)
    for key in ('fa', 'fb', 'fc', 'colour', 'pri', 'flab', 'finfo', 'alpha'):
        if m.get(key) is not None:
            out[key] = [m[key][i] for i in keep]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    touched = 0
    for path in a.files:
        raw = open(path, 'rb').read()
        m = parse_ob2(raw)
        d = degenerate(m)
        name = os.path.basename(path)
        if not d:
            print(f'{name:44s} {m["fcount"]:4d}f  clean')
            continue
        why = {}
        for _, w in d:
            why[w] = why.get(w, 0) + 1
        print(f'{name:44s} {m["fcount"]:4d}f  {len(d)} with no area  {why}')
        print(f'     faces {[i for i, _ in d]}')
        if a.dry_run:
            continue
        out = encode(strip(m, {i for i, _ in d}))
        open(path, 'wb').write(out)
        touched += 1
        print(f'     rewritten, {len(raw)} -> {len(out)} bytes')
    if not a.dry_run:
        print(f'\n{touched} file(s) rewritten')


if __name__ == '__main__':
    main()
