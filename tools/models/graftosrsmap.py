#!/usr/bin/env python3
"""Graft PART of an OSRS map square onto the 377 square already there, instead of replacing it.

importosrsmap.py writes a whole square, every level - which is right for somewhere this build does
not have, and wrong for a rooftop agility course. The courses sit on top of towns that exist here
already: Draynor's square carries 222 tiles and 238 locs of 2006 content at level 1 alone, and
replacing it would take the town with it.

So this takes only the levels and the area asked for and leaves everything else of ours alone.
Measured for Draynor before writing it: the course corridor holds 84 tiles and 54 locs of ours at
level 3, against 528 tiles and 389 locs at level 0 that must not be touched.

  python3 graftosrsmap.py --maps "<rev236 cache>" --cache "<newest cache>" \
      --region 48_51 --levels 3 --box 3084,3250,3107,3285 --content ../../content \
      --out ../../content/scripts/skill_agility/configs/draynor_rooftop

--box is in ABSOLUTE tile coordinates and may span several squares; each --region takes the part of
the box that falls inside it. Levels are a comma list. Everything else - the loc resolution, the
model conversion, loc.pack and model.pack - is importosrsmap's own machinery, called here.
"""
import argparse, os, sys

CRLF = chr(13) + chr(10)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importosrsmap as IM
import osrslocimport as LI
import jm2
from flatcache import Store
from osrsloc import load_osrs_locs
from animconv474 import pack_append


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--maps', required=True)
    ap.add_argument('--cache', required=True)
    ap.add_argument('--region', action='append', required=True)
    ap.add_argument('--levels', required=True, help='comma list, e.g. "3" or "1,2,3"')
    ap.add_argument('--box', required=True, help='x0,z0,x1,z1 in absolute tiles, inclusive')
    ap.add_argument('--content', required=True)
    ap.add_argument('--out')
    ap.add_argument('--rename', action='append', default=[], metavar='ID:NAME')
    ap.add_argument('--locs-only', action='store_true',
                    help='graft the locs but leave the terrain alone - for a ground-level obstacle '
                         'whose tile belongs to the 2006 town under it, like a rough wall')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    levels = {int(v) for v in a.levels.split(',')}
    X0, Z0, X1, Z1 = (int(v) for v in a.box.split(','))
    rename = {}
    for r in a.rename:
        i, _, n = r.partition(':'); rename[int(i)] = n

    st = Store(a.cache)
    locs, _ = load_osrs_locs(st)
    src = None
    for n in dir(IM):
        o = getattr(IM, n)
        if isinstance(o, type) and hasattr(o, 'locs') and hasattr(o, 'terrain'):
            src = o(a.maps); break
    if src is None:
        raise SystemExit('could not find the map source class in importosrsmap')
    c377 = LI.Content377(a.content)

    flo_max = max(int(l.split('=')[0]) for l in open(os.path.join(a.content, 'pack', 'flo.pack')) if '=' in l)
    texnames = {}
    for l in open(os.path.join(a.content, 'pack', 'texture.pack')):
        if '=' in l:
            i, nm = l.strip().split('=', 1); texnames[int(i)] = nm

    already = {}
    for l in open(os.path.join(a.content, 'pack', 'loc.pack')):
        if '=' in l:
            i, n = l.strip().split('=', 1)
            already[n] = int(i)

    results = {}
    staged = {}
    for reg in a.region:
        mx, mz = (int(v) for v in reg.split('_')); ms = (mx << 8) | mz
        inbox = lambda x, z: X0 <= mx * 64 + x <= X1 and Z0 <= mz * 64 + z <= Z1

        old = os.path.join(a.content, 'maps', f'm{reg}.jm2')
        if not os.path.exists(old):
            raise SystemExit(f'{old} does not exist - use importosrsmap.py for a square this build lacks')
        land, ours, npcs, objs = jm2.read(old)

        tchanged = 0
        tiles = None if a.locs_only else src.terrain(reg, ms)
        for lv in (() if a.locs_only else levels):
            for x in range(64):
                for z in range(64):
                    if not inbox(x, z):
                        continue
                    t = dict(tiles[lv][x][z])
                    if t['ov'] in IM.OVERLAY_REMAP: t['ov'] = IM.OVERLAY_REMAP[t['ov']]
                    if land.get((lv, x, z)) != t:
                        land[(lv, x, z)] = t
                        tchanged += 1

        kept = [l for l in ours if not (l[1] in levels and inbox(l[2], l[3]))]
        dropped = len(ours) - len(kept)
        theirs = [l for l in src.locs(reg, ms) if l[1] in levels and inbox(l[2], l[3])]
        for (oid, lv, x, z, sh, rot) in theirs:
            if oid not in results:
                # ALREADY IMPORTED BY AN EARLIER AREA counts as reuse, not as a fresh import.
                # LI.resolve only knows the 377 locs, so without this a loc that some other graft
                # already brought across is defined twice and the build stops on "Duplicate config"
                # - which is what osrsloc_2639 did, having come in with Kraken Cove.
                if f'osrsloc_{oid}' in already:
                    results[oid] = ('reuse', already[f'osrsloc_{oid}'])
                else:
                    results[oid] = LI.resolve(st, locs, c377, oid)
        staged[reg] = (land, kept, theirs, npcs, objs)
        print(f'# m{reg}: {tchanged} tiles grafted, {dropped} of our locs replaced by {len(theirs)} of theirs')

    imp = sorted({r[1] for r in results.values() if r[0] == 'import'})
    reuse = sorted({r[1] for r in results.values() if r[0] == 'reuse'})
    drop = {k: r[1] for k, r in results.items() if r[0] == 'drop'}
    print(f'# loc ids: {len(reuse)} reused as-is, {len(imp)} to import, {len(drop)} dropped {drop}')
    if a.dry_run:
        return

    lines = ['// OSRS locs grafted by tools/models/graftosrsmap.py (osrslocimport.py).',
             '// Models re-encoded by osrs2ob2.py with the loc recolours baked in.', '']
    model_files, anim_names = {}, {}
    for oid in imp:
        LI.import_loc(st, locs, oid, a.content, texnames, anim_names, lines, model_files, rename)
    if imp:
        pack_append(os.path.join(a.content, 'pack', 'loc.pack'),
                    [rename.get(i) or f'osrsloc_{i}' for i in imp])
        pack_append(os.path.join(a.content, 'pack', 'model.pack'), list(model_files))
        os.makedirs(os.path.join(a.content, 'models', 'loc'), exist_ok=True)
        for n, b in model_files.items():
            open(os.path.join(a.content, 'models', 'loc', n + '.ob2'), 'wb').write(b)
        print(f'# wrote {len(model_files)} loc models')

    locpack = {}
    for l in open(os.path.join(a.content, 'pack', 'loc.pack')):
        if '=' in l:
            i, n = l.strip().split('=', 1); locpack[n] = int(i)

    def new_id(oid):
        r = results[oid]
        if r[0] == 'reuse': return r[1]
        if r[0] == 'import': return locpack[rename.get(r[1]) or f'osrsloc_{r[1]}']
        return None

    for reg, (land, kept, theirs, npcs, objs) in staged.items():
        out = list(kept)
        for (oid, lv, x, z, sh, rot) in theirs:
            nid = new_id(oid)
            if nid is not None:
                out.append((nid, lv, x, z, sh, rot))
        jm2.write(os.path.join(a.content, 'maps', f'm{reg}.jm2'), land, out, npcs, objs)
        print(f'#   wrote maps/m{reg}.jm2 ({len(out)} locs in all)')

    if a.out and imp:
        # APPEND, NEVER OVERWRITE. A second graft over the same area imports only what the first
        # one did not, because everything else counts as reuse by then - so writing the file fresh
        # DELETES the definitions the first graft made while the maps still reference them. That is
        # how six Draynor obstacles vanished on 2026-10-02: the build still packed and the course
        # was simply not there.
        path = a.out + '.loc'
        if os.path.exists(path):
            have = open(path, newline='').read().rstrip()
            body = [l for l in lines if not l.startswith('//')]
            open(path, 'w', newline='').write(have + CRLF + CRLF + CRLF.join(body))
            print(f'#   appended {len(imp)} loc(s) to {path}')
        else:
            open(path, 'w', newline='').write(CRLF.join(lines))
            print(f'#   wrote {path}')


if __name__ == '__main__':
    main()
