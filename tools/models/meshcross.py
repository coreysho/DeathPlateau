#!/usr/bin/env python3
"""Do two worn models actually pass through each other?

THE THIRD KIND OF CLIPPING, after draw order (WearSweep's default) and a model drawn over a body it
is behind (--islands). Here the two meshes genuinely intersect: an edge of one crosses a face of the
other, so there is no order that draws them correctly and no priority that helps. The only fixes are
to the geometry.

It counts edge-through-face crossings both ways, in the BASE POSE. A pair that reads 0 here and
still looks wrong in game is an animation fault instead: the two models are skinned to different
vertex labels and come apart when the limb bends, which is what the wrist of a glove does.

  python3 tools/models/meshcross.py content/models/obj/obj_armadyl_chainskirt_manwear.ob2 \
                                    content/models/obj/obj_macro_digger_boots_manwear.ob2

Measured on 30 October, on the kit from the screenshot: the Armadyl chainskirt and the gravedigger
boots cross on 22 + 51 edges, which is the boots coming through the legs. The chestplate and the
chainskirt cross 0 times, and the arms and the gloves 0 - so neither of those is geometry.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from osrs2ob2 import parse_ob2


def triangles(path):
    m = parse_ob2(open(path, 'rb').read())
    v = np.array([m['vx'], m['vy'], m['vz']], dtype=float).T
    f = np.array([m['fa'], m['fb'], m['fc']]).T
    return v[f]


def through(p0, p1, t):
    """Möller-Trumbore, for a segment rather than a ray: does p0-p1 cross triangle t?"""
    e1, e2 = t[1] - t[0], t[2] - t[0]
    d = p1 - p0
    h = np.cross(d, e2)
    a = e1 @ h
    if abs(a) < 1e-9:
        return False
    f = 1.0 / a
    s = p0 - t[0]
    u = f * (s @ h)
    if u < 0 or u > 1:
        return False
    q = np.cross(s, e1)
    v = f * (d @ q)
    if v < 0 or u + v > 1:
        return False
    return 1e-6 < f * (e2 @ q) < 1 - 1e-6


def crossings(a, b):
    """Edges of a that pass through a face of b. Boxes first, or this is a million pairs."""
    lo, hi = b.min(axis=1), b.max(axis=1)
    n = 0
    for t in a:
        near = np.where(np.all(hi >= t.min(axis=0), axis=1) & np.all(lo <= t.max(axis=0), axis=1))[0]
        if not len(near):
            continue
        for i, j in ((0, 1), (1, 2), (2, 0)):
            if any(through(t[i], t[j], b[k]) for k in near):
                n += 1
                break
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('a')
    ap.add_argument('b')
    a = ap.parse_args()
    A, B = triangles(a.a), triangles(a.b)
    n1, n2 = crossings(A, B), crossings(B, A)
    print(f'{os.path.basename(a.a)} ({len(A)}f) x {os.path.basename(a.b)} ({len(B)}f)')
    print(f'  edges crossing: {n1} + {n2}' + ('   (the meshes intersect)' if n1 + n2 else '   (they do not touch)'))


if __name__ == '__main__':
    main()
