#!/usr/bin/env python3
"""Compare a grafted rooftop course against the OSRS map it came from, level by level.

Reported from play: "all courses need relooked at for graphics and correct animations and correct
spots that it takes you to", with three graphics faults named - the decks read as flat untextured
slabs, you can see inside the buildings from above, and some roof models are wrong.

All three are the same question asked three ways: WHAT DOES OLD SCHOOL HAVE HERE THAT WE DO NOT?
So rather than nine hand audits, this walks each course's area in both maps and prints the
differences:

  * locs Old School has in the box that we have nothing at - missing roofs, which is what you are
    looking through when you can see the furniture;
  * tiles whose overlay differs - a deck wearing the wrong floor, which is the flat-slab look;
  * and the per-level tile counts, because a course on level 3 with nothing on level 2 beneath it
    is a hole by construction.

The box comes from the course's own .constant: every coord in it, plus a margin, which is the area
a player on that course can actually see. Nothing is written - this only reports.

  python3 tools/models/rooftopaudit.py --content ../../content --maps "<rev236 cache>" [--course varrock]
"""
import argparse, io, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importosrsmap import MapSource
from dat2ext import decompress
from reftable import RefTable, split_group
from osrsloc import decode_osrs_loc


def load_osrs_locnames(cache):
    """{id: name} straight out of the OpenRS2 flat cache - the SAME cache the placements come from,
    because loc ids drift between revisions and reading names from a different one mislabels
    everything."""
    rt = RefTable(decompress(open(os.path.join(cache, 'cache', '255', '2.dat'), 'rb').read()), strict=False)
    ids = rt.file_ids[6]
    blob = decompress(open(os.path.join(cache, 'cache', '2', '6.dat'), 'rb').read())
    out = {}
    for i, f in zip(ids, split_group(blob, len(ids))):
        if not f:
            continue
        try:
            out[i] = decode_osrs_loc(f)
        except Exception:
            pass
    return out


def pack(path):
    out = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.strip()
        if '=' in line:
            i, n = line.split('=', 1)
            out[int(i)] = n
    return out


def jm2_sections(path):
    s = io.open(path, encoding='utf-8').read().splitlines()
    heads = [i for i, l in enumerate(s) if l.startswith('==== ')]
    out = {}
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(s)
        out[s[i].strip('= ').strip()] = [l for l in s[i + 1:end] if l.strip() and ':' in l]
    return out


def course_box(constant_path, margin):
    """Every coord the course names, as an absolute-tile bounding box."""
    text = io.open(constant_path, encoding='utf-8').read()
    xs, zs, levels = [], [], set()
    for m in re.finditer(r'=\s*(\d)_(\d+)_(\d+)_(\d+)_(\d+)', text):
        lv, mx, mz, lx, lz = (int(g) for g in m.groups())
        xs.append(mx * 64 + lx)
        zs.append(mz * 64 + lz)
        levels.add(lv)
    if not xs:
        return None
    return (min(xs) - margin, min(zs) - margin, max(xs) + margin, max(zs) + margin), sorted(levels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--maps', required=True, help='the OSRS cache the courses were grafted from')
    ap.add_argument('--course', action='append', help='audit only these (default: all)')
    ap.add_argument('--margin', type=int, default=6)
    ap.add_argument('--verbose', action='store_true', help='list every missing loc, not a summary')
    a = ap.parse_args()

    C = a.content
    ms = MapSource(a.maps)
    L = load_osrs_locnames(a.maps)
    locnames = pack(os.path.join(C, 'pack', 'loc.pack'))
    flonames = pack(os.path.join(C, 'pack', 'flo.pack'))

    cfgdir = os.path.join(C, 'scripts', 'skill_agility', 'configs')
    courses = sorted(f[:-len('_course.constant')] for f in os.listdir(cfgdir)
                     if f.endswith('_course.constant'))
    if a.course:
        courses = [c for c in courses if c in a.course]

    for name in courses:
        got = course_box(os.path.join(cfgdir, f'{name}_course.constant'), a.margin)
        if not got:
            print(f'{name}: no coords in its .constant'); continue
        (x0, z0, x1, z1), levels = got
        print(f'\n=== {name}: x {x0}..{x1}  z {z0}..{z1}   course runs on levels {levels}')

        regions = sorted({(x >> 6, z >> 6) for x in (x0, x1) for z in (z0, z1)})

        ours_loc = defaultdict(set)      # level -> {(x,z)}
        ours_name = {}                   # (level,x,z) -> our loc name
        ours_ov = {}                     # (level,x,z) -> our overlay name
        ours_tiles = Counter()
        for mx, mz in regions:
            p = os.path.join(C, 'maps', f'm{mx}_{mz}.jm2')
            if not os.path.exists(p):
                print(f'   (we have no m{mx}_{mz})'); continue
            sec = jm2_sections(p)
            for ln in sec.get('LOC', []):
                lv, lx, lz = (int(v) for v in ln.split(':')[0].split())
                gx, gz = mx * 64 + lx, mz * 64 + lz
                if x0 <= gx <= x1 and z0 <= gz <= z1:
                    ours_loc[lv].add((gx, gz))
                    ours_name[(lv, gx, gz)] = locnames.get(int(ln.split(':')[1].split()[0]), '?')
            for ln in sec.get('MAP', []):
                lv, lx, lz = (int(v) for v in ln.split(':')[0].split())
                gx, gz = mx * 64 + lx, mz * 64 + lz
                if not (x0 <= gx <= x1 and z0 <= gz <= z1):
                    continue
                ours_tiles[lv] += 1
                for tok in ln.split(':')[1].split():
                    if tok.startswith('o'):
                        # A TILE STORES THE FLO ID PLUS ONE; the client reads FloType[value - 1],
                        # which is why no tile anywhere uses 0. Read it as-is and every floor in
                        # the game comes out one place wrong - road reads as darkstone, water as
                        # gungywater - and a correct deck looks like a bug.
                        ours_ov[(lv, gx, gz)] = flonames.get(int(tok[1:].split(';')[0]) - 1, tok)

        theirs_loc = defaultdict(set)
        theirs_name = {}
        theirs_ov = {}
        for mx, mz in regions:
            reg = f'{mx}_{mz}'
            try:
                for t in ms.locs(reg, (mx << 8) | mz):
                    lid, lv, lx, lz = t[0], t[1], t[2], t[3]
                    gx, gz = mx * 64 + lx, mz * 64 + lz
                    if x0 <= gx <= x1 and z0 <= gz <= z1:
                        theirs_loc[lv].add((gx, gz))
                        theirs_name[(lv, gx, gz)] = (L.get(lid) or {}).get('name') or f'loc {lid}'
            except SystemExit:
                print(f'   (no XTEA key for l{reg} - locs there cannot be compared)')
            try:
                tiles = ms.terrain(reg, (mx << 8) | mz)
            except SystemExit:
                continue
            for lv in range(4):
                for lx in range(64):
                    for lz in range(64):
                        gx, gz = mx * 64 + lx, mz * 64 + lz
                        if x0 <= gx <= x1 and z0 <= gz <= z1 and tiles[lv][lx][lz]['ov'] is not None:
                            theirs_ov[(lv, gx, gz)] = tiles[lv][lx][lz]['ov']

        for lv in range(4):
            missing = theirs_loc[lv] - ours_loc[lv]
            extra = ours_loc[lv] - theirs_loc[lv]
            if not (theirs_loc[lv] or ours_loc[lv] or ours_tiles[lv]):
                continue
            print(f'   level {lv}: ours {len(ours_loc[lv]):4} locs / {ours_tiles[lv]:4} tiles   '
                  f'Old School {len(theirs_loc[lv]):4} locs   '
                  f'| missing {len(missing):4}  only-ours {len(extra):4}')
            if missing:
                c = Counter(theirs_name[(lv, x, z)] for x, z in missing)
                top = ', '.join(f'{k}x{n}' for n, k in c.most_common(6))
                print(f'      not here: {top}')
                if a.verbose:
                    for x, z in sorted(missing)[:40]:
                        print(f'         {x},{z}  {theirs_name[(lv, x, z)]}')

        decks = Counter(v for (lv, x, z), v in ours_ov.items() if lv >= 1)
        if decks:
            print('   our overlays above ground: ' + ', '.join(f'{k}x{n}' for k, n in decks.most_common(6)))


if __name__ == '__main__':
    main()
