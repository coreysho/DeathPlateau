#!/usr/bin/env python3
"""Write one .ob2 per priority group of an OSRS model, so each layer can be drawn on its own.

    python3 layers.py "<cache dir>" <osrs model id> <out dir> [<base id>]

Writes <out dir>/<base id + k>.ob2, one per distinct face priority, and prints which is which.
The other groups' faces are not removed - their three vertex indices are set to the same vertex,
so the face has zero screen area and the client's own cull test (> 0) never passes it. Nothing
else about the file changes: no face list to renumber, no texture triangle indices to remap, no
second code path to be wrong.

This is what broke the Infernal cape's "back-face culling" diagnosis. Drawn alone, the layer that
carried the crust texture drew nothing in EITHER winding - which no culling story explains, and
which sent the search back into the client, where a negative palette index was throwing inside
the raster. A whole model can hide that; one layer at a time cannot.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models'))
from flatcache import Store                                  # noqa: E402
from osrs2ob2 import decode, encode, roundtrip                # noqa: E402

def main():
    if len(sys.argv) not in (4, 5):
        raise SystemExit(__doc__)
    cache, mid, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    base = int(sys.argv[4]) if len(sys.argv) == 5 else 91000
    st = Store(cache)
    src = decode(st.read(7, mid))
    if src is None:
        raise SystemExit('model %d does not decode' % mid)
    pris = sorted(set(src['pri'] or [0]))
    for k, keep in enumerate(pris):
        m = decode(st.read(7, mid))
        fa, fb, fc = list(m['fa']), list(m['fb']), list(m['fc'])
        live = 0
        for i in range(m['fcount']):
            if (m['pri'] or [0] * m['fcount'])[i] != keep:
                fa[i] = fb[i] = fc[i] = 0
            else:
                live += 1
        m['fa'], m['fb'], m['fc'] = fa, fb, fc
        ob2 = encode(m)
        ok, why = roundtrip(ob2, m)
        if not ok:
            raise SystemExit('priority %d: %s' % (keep, why))
        open(os.path.join(out, '%d.ob2' % (base + k)), 'wb').write(ob2)
        tex = sum(1 for i in range(m['fcount'])
                  if (m['pri'] or [0] * m['fcount'])[i] == keep and (m['finfo'] or [0])[i] & 2)
        print('%d.ob2: priority %d only, %d faces live, %d of them textured'
              % (base + k, keep, live, tex))

main()
