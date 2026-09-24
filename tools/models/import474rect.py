#!/usr/bin/env python3
"""
Patch a RECTANGLE of a rev 474 map square into a map square the build already has - for a building
Jagex added between 2004 and 2007 (first user: Otto's house at Otto's Grotto, m39_54, Barbarian
Training, July 2007) without replacing the whole square.

import474map.py refuses an existing .jm2, and rightly: 474's m39_54 differs from 377's in 2,550
terrain tiles and ~1,500 locs (a 2007 re-decoration of the whole lake), and the square also holds
the top of Baxtorian Falls, whose Waterfall Quest locs the scripts name. So only the rectangle is
taken:

  * terrain - every tile of the rect on the given level is replaced by 474's (jm2.patch_map), so the
              house brings its own floor overlay, roof-removal flags and heights;
  * locs    - every 377 loc ANCHORED in the rect on that level is removed (the grass tufts and the
              tree that stood where the house now is), and every 474 loc anchored there is added,
              resolved exactly as import474map.py does (reuse a byte-identical 377 loc, else import
              `loc474_<id>`). --skip-loc drops 474 ids you do not want (ground-cover variants).
NPC and OBJ spawns are untouched; the LOC section is edited line by line, so the rest of the file
diffs clean.

    python3 tools/models/import474rect.py "caches/474 cache" --region 39_54 \\
        --rect 0:3:30:8:35 --rect 1:3:30:9:36 --skip-loc 16382 \\
        --content content --out content/scripts/<area>/configs/<name> [--dry-run]

    python3 tools/models/import474rect.py "caches/474 cache" --region 39_54 --rect 0:2:46:3:57 \\
        --terrain-only --content content --out unused

--rect is level:x0:z0:x1:z1, inclusive, local to the square. --terrain-only takes the tiles alone -
for a shoreline Jagex moved, where 377's own decoration should stay. Otherwise writes <out>.loc with
the imported locs (appended to if it exists), models under models/loc, and loc.pack / model.pack
entries. Resolving locs reads every 377 loc model once, which takes minutes; terrain-only does not.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import474map import Cache474, Resolver, import_loc
from osrslocimport import Content377
from animconv474 import pack_append
import jm2

CRLF = '\r\n'


def in_rect(r, lv, x, z):
    return r[0] == lv and r[1] <= x <= r[3] and r[2] <= z <= r[4]


def read_lines(path):
    raw = open(path, newline='').read()
    nl = CRLF if CRLF in raw else '\n'
    return raw.split(nl), nl


def patch_locs(path, drop, add):
    """Remove LOC lines anchored where drop(lv, x, z) is true and add `add` (id, lv, x, z, shape, rot)
    lines, keeping the section sorted by (level, x, z) and every untouched line as it was."""
    lines, nl = read_lines(path)
    out = []; sec = None; body = []; removed = []
    def key(l):
        m = re.match(r'(\d) (\d+) (\d+):', l)
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    def flush():
        new = []
        for (i, lv, x, z, sh, rot) in add:
            new.append(f'{lv} {x} {z}: {i}' if (sh == 10 and rot == 0) else
                       f'{lv} {x} {z}: {i} {sh}' if rot == 0 else f'{lv} {x} {z}: {i} {sh} {rot}')
        out.extend(sorted(body + new, key=key))    # stable: existing lines keep their order
    for l in lines:
        if l.startswith('===='):
            if sec == 'LOC': flush(); out.append('')
            sec = l.strip('= ').strip(); out.append(l); continue
        if sec == 'LOC':
            if not l: continue
            if drop(*key(l)): removed.append(l); continue
            body.append(l); continue
        out.append(l)
    if sec == 'LOC': flush()
    open(path, 'w', newline='').write(nl.join(out))
    return removed


def tidy(path):
    """jm2.patch_map appends tiles the square never had (a roof's upper level) after the MAP section's
    closing blank line; put that blank line back in front of the next header."""
    lines, nl = read_lines(path)
    out = []
    for i, l in enumerate(lines):
        if l == '' and i + 1 < len(lines) and lines[i + 1] and not lines[i + 1].startswith('===='):
            continue
        if l.startswith('====') and out and out[-1] != '':
            out.append('')
        out.append(l)
    open(path, 'w', newline='').write(nl.join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache'); ap.add_argument('--region', required=True)
    ap.add_argument('--rect', action='append', required=True, help='level:x0:z0:x1:z1 (inclusive, local)')
    ap.add_argument('--skip-loc', action='append', type=int, default=[], help='474 loc id to leave out')
    ap.add_argument('--content', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--header', action='append', default=[])
    ap.add_argument('--terrain-only', action='store_true',
                    help='patch the tiles and leave every loc as it is (e.g. a shoreline Jagex moved)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    rects = [tuple(int(v) for v in r.split(':')) for r in a.rect]
    C = a.content; reg = a.region
    path = os.path.join(C, 'maps', f'm{reg}.jm2')
    if not os.path.exists(path): raise SystemExit(f'{path} does not exist - use import474map.py for a new square')

    c = Cache474(a.cache)
    land4 = c.terrain(reg); locs4 = c.locs_of(reg)
    inr = lambda lv, x, z: any(in_rect(r, lv, x, z) for r in rects)
    tiles = {k: d for k, d in land4.items() if inr(*k)}
    if a.terrain_only:
        print(f'{len(tiles)} tiles (terrain only)')
        if not a.dry_run:
            jm2.patch_map(path, tiles); tidy(path)
            print(f'm{reg}.jm2: {len(tiles)} tiles patched')
        return
    c3 = Content377(C); R = Resolver(c, c3)
    take = [l for l in locs4 if inr(l[1], l[2], l[3]) and l[0] not in a.skip_loc]
    plan = {oid: R.resolve(oid) for oid in sorted({l[0] for l in take})}
    for oid, p in plan.items(): print(f'  474 loc {oid}: {p[0]} {p[1]}')

    lines = [] if os.path.exists(a.out + '.loc') else \
        ['// Imported from the rev 474 cache by tools/models/import474rect.py: part of m' + reg + '.'] + \
        ['// ' + h for h in a.header] + ['']
    model_files = {}; notes = []; newname = {}
    for oid, (k, v) in plan.items():
        if k == 'import' and v not in newname:
            newname[v] = import_loc(c, v, lines, model_files, notes)
    for n in notes: print('  note:', n)
    print(f'{len(tiles)} tiles, {len(take)} locs; import {len(newname)} loc types, {len(model_files)} models')
    if a.dry_run: return

    locids, _ = pack_append(os.path.join(C, 'pack', 'loc.pack'), [newname[k] for k in sorted(newname)])
    if model_files: pack_append(os.path.join(C, 'pack', 'model.pack'), sorted(model_files))
    os.makedirs(os.path.join(C, 'models', 'loc'), exist_ok=True)
    for n, b in model_files.items():
        open(os.path.join(C, 'models', 'loc', n + '.ob2'), 'wb').write(b)
    if newname:
        mode = 'a' if os.path.exists(a.out + '.loc') else 'w'
        open(a.out + '.loc', mode, newline='').write(CRLF.join(lines))
    idmap = {}
    for oid, (k, v) in plan.items():
        if k == 'reuse': idmap[oid] = v
        elif k == 'import': idmap[oid] = locids[newname[v]]
    add = [(idmap[l[0]], l[1], l[2], l[3], l[4], l[5]) for l in take if l[0] in idmap]
    jm2.patch_map(path, tiles)
    removed = patch_locs(path, inr, add)
    tidy(path)
    print(f'm{reg}.jm2: {len(tiles)} tiles patched, {len(removed)} 377 locs removed, {len(add)} added')
    for n, i in sorted(locids.items(), key=lambda t: t[1]): print(f'  loc.pack {i}={n}')


if __name__ == '__main__':
    main()
