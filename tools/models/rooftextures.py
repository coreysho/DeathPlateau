#!/usr/bin/env python3
"""Which Old School TEXTURES a rooftop course's models want, and which of them we flatten.

THE COURSES LOOK LIKE SLABS AND THIS IS WHY. osrs2ob2.py keeps a textured face textured only when
377 has the same texture at the same id (SHARED_TEXTURES) or when this fork has imported it
(LOCAL_TEXTURES). Every other textured face is painted with the texture's average colour instead -
which is the right fallback, and on a roof it turns a tiled slate surface into one flat plane of
one colour. The geometry is faithful; the surface is not.

So this counts, per course, the textures the course's own locs actually name: how many faces each
one covers, whether it survives, and - for the ones that do not - what it would take. The answer is
a list of textures to import, and osrs2ob2's own note says what importing one costs:

    the image into content/textures/<name>.png and a line in content/pack/texture.pack; the id in
    LOCAL_TEXTURES; and Pix3D.TEXTURE_COUNT in the Java client high enough to hold it

Nothing is written here.

  python3 tools/models/rooftextures.py --content ../content --maps "<rev236 cache>"
                                       --cache "<newest cache>" [--course falador]
"""
import argparse, io, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importosrsmap import MapSource
from osrsloc import load_osrs_locs
from flatcache import Store
from osrs2ob2 import SHARED_TEXTURES, LOCAL_TEXTURES, decode

COURSES = ('draynor', 'alkharid', 'varrock', 'canifis', 'falador', 'seers', 'pollnivneach',
           'rellekka', 'ardougne', 'apeatoll')


def course_box(path, margin=6):
    text = io.open(path, encoding='utf-8').read()
    xs, zs = [], []
    for m in re.finditer(r'=\s*(\d)_(\d+)_(\d+)_(\d+)_(\d+)', text):
        _, mx, mz, lx, lz = (int(g) for g in m.groups())
        xs.append(mx * 64 + lx)
        zs.append(mz * 64 + lz)
    if not xs:
        return None
    return (min(xs) - margin, min(zs) - margin, max(xs) + margin, max(zs) + margin)


def model_ids(locdef):
    """Every model id a loc config names, across its shapes."""
    out = []
    for key in ('models', 'model'):
        v = locdef.get(key)
        if not v:
            continue
        if isinstance(v, dict):
            out.extend(v.values())
        elif isinstance(v, (list, tuple)):
            for item in v:
                out.append(item[0] if isinstance(item, (list, tuple)) else item)
        else:
            out.append(v)
    flat = []
    for m in out:
        if isinstance(m, (list, tuple)):
            flat.extend(m)
        else:
            flat.append(m)
    return [m for m in flat if isinstance(m, int)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', default='../content')
    ap.add_argument('--maps', required=True)
    ap.add_argument('--cache', required=True)
    ap.add_argument('--course')
    ap.add_argument('--margin', type=int, default=6)
    a = ap.parse_args()

    cfg = os.path.join(a.content, 'scripts', 'skill_agility', 'configs')
    ms = MapSource(a.maps)
    st = Store(a.cache)
    locs, _bad = load_osrs_locs(st)

    from reftable import split_group
    rt = st.reftable(7)

    def model_bytes(mid):
        try:
            return st.read(7, mid)
        except Exception:
            return None

    grand = Counter()
    for key in COURSES:
        if a.course and a.course != key:
            continue
        box = course_box(os.path.join(cfg, key + '_course.constant'), a.margin)
        if not box:
            continue
        # every loc Old School places above ground in the box, with a roof shape
        want = Counter()
        for mx in range(box[0] >> 6, (box[2] >> 6) + 1):
            for mz in range(box[1] >> 6, (box[3] >> 6) + 1):
                reg = '%d_%d' % (mx, mz)
                try:
                    placed = ms.locs(reg, (mx << 8) | mz)
                except SystemExit:
                    continue
                for lid, lv, lx, lz, shape, rot in placed:
                    if lv < 1 or not (12 <= shape <= 21):
                        continue
                    gx, gz = (mx << 6) + lx, (mz << 6) + lz
                    if box[0] <= gx <= box[2] and box[1] <= gz <= box[3]:
                        want[lid] += 1
        if not want:
            continue

        tex_faces = Counter()
        flat_faces = 0
        kept_faces = 0
        plain_faces = 0
        seen_models = set()
        for lid, n in want.items():
            d = locs.get(lid) or {}
            for mid in model_ids(d):
                if mid in seen_models:
                    continue
                seen_models.add(mid)
                b = model_bytes(mid)
                if not b:
                    continue
                try:
                    m = decode(b, SHARED_TEXTURES)
                except Exception:
                    continue
                ids = m.get('texids') or []
                for f in range(m.get('fcount', 0)):
                    t = ids[f] if f < len(ids) else -1
                    if t is None or t < 0:
                        plain_faces += 1
                        continue
                    tex_faces[t] += 1
                    if t in SHARED_TEXTURES or t in LOCAL_TEXTURES:
                        kept_faces += 1
                    else:
                        flat_faces += 1
        print('')
        print('================ %s' % key.upper())
        print('  %d roof placements, %d distinct locs, %d distinct models'
              % (sum(want.values()), len(want), len(seen_models)))
        print('  faces: %d untextured, %d textured and kept, %d textured and FLATTENED to one colour'
              % (plain_faces, kept_faces, flat_faces))
        if not tex_faces:
            continue
        print('  the textures those models name:')
        for t, c in tex_faces.most_common():
            state = 'shared with 377' if t in SHARED_TEXTURES else (
                'imported as %d' % LOCAL_TEXTURES[t] if t in LOCAL_TEXTURES else 'FLATTENED')
            print('      OSRS texture %-4d on %-5d faces   %s' % (t, c, state))
            if state == 'FLATTENED':
                grand[t] += c

    if grand:
        print('')
        print('================ WHAT TO IMPORT')
        print('  textures the rooftop courses name and we paint flat, worst first:')
        for t, c in grand.most_common():
            print('      OSRS texture %-4d on %d faces across the courses' % (t, c))


main()
