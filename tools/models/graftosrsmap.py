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

# AN OVERLAY ID MEANS SOMETHING DIFFERENT IN EACH CACHE, and a graft that passes them through
# writes whatever 377 happens to keep at that id. Old School's 55 is the deck of a rooftop course;
# 377's 55 is `lightrock`, a pale quarry rock, so Draynor's course arrived as a blank slab over the
# town's slate. The remap for that was written into this file as a constant - and then Al Kharid
# showed why that was wrong too: 55 there wants a DESERT roof, not Draynor's grey slate, and its
# 64 (sand, 0xb8b098) was landing on 377's `mud2` and terracing the roofs brown.
#
# So the mapping belongs to the GRAFT, not to the tool: --overlay 55=roofdeck_greyslate. What the
# tool owes the caller is a loud warning for every overlay it passes through whose Old School
# colour is nothing like the 377 floor of the same id, which is what both of those bugs looked like
# and what nobody noticed until it was in front of the owner.
MISMATCH = 60           # sum of |dR|+|dG|+|dB| past which a passed-through overlay is called out

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importosrsmap as IM
import osrslocimport as LI
import jm2
from flatcache import Store
from osrsloc import load_osrs_locs
from animconv474 import pack_append
from animconvosrs import convert_seqs


def read_flo_colours(content):
    """Every 377 floor's own colour, by flo id, read out of the .flo configs beside flo.pack."""
    import glob, re
    name_colour = {}
    for path in glob.glob(os.path.join(content, 'scripts', '**', '*.flo'), recursive=True):
        cur = None
        for line in open(path, newline='', encoding='latin-1').read().splitlines():
            line = line.split('//')[0].strip()
            if line.startswith('[') and line.endswith(']'):
                cur = line[1:-1]
            elif cur and line.startswith('colour='):
                name_colour[cur] = int(line.split('=', 1)[1], 0)
    out = {}
    for l in open(os.path.join(content, 'pack', 'flo.pack')):
        if '=' in l:
            i, nm = l.strip().split('=', 1)
            if nm in name_colour:
                out[int(i)] = name_colour[nm]
    return out


def read_osrs_overlay_colours(st):
    """Every Old School overlay's own colour. Where the primary is the 0xFF00FF 'not drawn' marker
    the secondary is what it actually shows, which is true of every course deck overlay there is."""
    from reftable import split_group
    ids = st.reftable(2).file_ids[4]
    files = split_group(st.read(2, 4), len(ids))
    out = {}
    for fid, b in zip(ids, files):
        p = 0; rgb = None; rgb2 = None
        while p < len(b):
            op = b[p]; p += 1
            if op == 0: break
            if op == 1: rgb = int.from_bytes(b[p:p + 3], 'big'); p += 3
            elif op == 2: p += 1
            elif op == 3: p += 2
            elif op == 5: pass
            elif op == 7: rgb2 = int.from_bytes(b[p:p + 3], 'big'); p += 3
            elif op == 9: p += 2
            else: break
        if rgb == 0xFF00FF and rgb2 is not None:
            rgb = rgb2
        if rgb is not None:
            out[fid] = rgb
    return out


def warn_overlay(value, osrs_colour, flo_colour, flo_name, warned, level=0, roof_hits=None):
    """An overlay passed through unmapped.

    TWO FAULTS LIVED HERE. The colour test read osrs_colour[value - 1], which is the colour of a
    DIFFERENT Old School overlay - `value` is already the Old School id for anything unmapped, and
    only the 377 side needs the minus one. And a colour test cannot catch the case that matters
    anyway: Old School's course deck is #606058 and 377 keeps greyroof (#5b5b5b) at that id, so
    grey passed for grey and Al Kharid shipped 452 tiles of slate roof on a sandstone town, while
    Rellekka shipped 176 tiles of `invisible` - a roof you can see straight through.

    So anything unmapped ABOVE GROUND is counted and reported at the end whatever its colour. A
    floor a player stands on at level 1 or higher is a deck, and a deck is always a decision.
    """
    if level >= 1 and roof_hits is not None:
        roof_hits[value] += 1
    if value in warned:
        return
    a = osrs_colour.get(value)
    b = flo_colour.get(value - 1)
    if a is None or b is None:
        return
    d = sum(abs(((a >> s) & 255) - ((b >> s) & 255)) for s in (16, 8, 0))
    if d <= MISMATCH:
        return
    warned.add(value)
    print(f'# WARNING overlay {value}: Old School paints it #{a:06x}, and this build keeps '
          f'{flo_name.get(value - 1, "?")} (#{b:06x}) at that id'
          f' - pass --overlay {value}=<floor> if that is wrong')


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
    ap.add_argument('--overlay', action='append', default=[], metavar='OSRS=FLONAME',
                    help='map an Old School overlay id onto a 377 floor BY NAME, for the tiles '
                         'this graft writes. Repeatable. Every course needs its own: the deck of '
                         'a slate town and the deck of a desert town are not the same floor.')
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

    flo = {}
    for l in open(os.path.join(a.content, 'pack', 'flo.pack')):
        if '=' in l:
            i, nm = l.strip().split('=', 1); flo[nm] = int(i)
    flo_max = max(flo.values())

    # --overlay, resolved BY NAME so a content tree without the floor stops here rather than
    # writing an overlay the client would index off the end of its table.
    # A tile stores the overlay as the flo id PLUS ONE; the client reads FloType[value - 1].
    overlay_remap = {}
    for r in a.overlay:
        osrs_ov, _, dst = r.partition('=')
        if dst not in flo:
            raise SystemExit(f'--overlay {r}: {dst} is not in pack/flo.pack')
        overlay_remap[int(osrs_ov)] = flo[dst] + 1
    flo_colour = read_flo_colours(a.content)
    osrs_colour = read_osrs_overlay_colours(st)
    flo_name = {v: k for k, v in flo.items()}
    warned = set()
    from collections import Counter
    roof_hits = Counter()      # unmapped overlays written above ground - see warn_overlay

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
                    if t['ov'] in overlay_remap:
                        t['ov'] = overlay_remap[t['ov']]
                    elif t['ov']:
                        warn_overlay(t['ov'], osrs_colour, flo_colour, flo_name, warned, lv, roof_hits)
                    if land.get((lv, x, z)) != t:
                        land[(lv, x, z)] = t
                        tchanged += 1
        if roof_hits:
            worst = ", ".join(f"{v} ({n} tiles, now {flo_name.get(v - 1, chr(63))})"
                              for v, n in roof_hits.most_common(6))
            print(f"# WARNING {sum(roof_hits.values())} tile(s) ABOVE GROUND took an overlay this "
                  f"graft was not told about: {worst}. A floor a player stands on at level 1 or "
                  f"higher is a deck - pass --overlay <id>=<floor> for each, or it wears whatever "
                  f"377 keeps at that number.")
            roof_hits.clear()

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

        # AND THE SEQS THOSE LOCS PLAY. importosrsmap.py writes these and this did not, so a graft
        # that pulled in an animated loc wrote `anim=osrsloc_anim_<id>` naming a seq that existed
        # nowhere, and the build stopped on it. The Trollheim graft was the first to hit it, with
        # the Old fire pit. Appended for the same reason as the .loc above.
        if anim_names:
            seq_text = convert_seqs(st, anim_names, a.content)
            sp = a.out + '.seq'
            if os.path.exists(sp):
                have = open(sp, newline='').read().rstrip()
                body = [l for l in seq_text.split(CRLF) if not l.startswith('//')]
                open(sp, 'w', newline='').write(have + CRLF + CRLF + CRLF.join(body))
                print(f'#   appended {len(anim_names)} seq(s) to {sp}')
            else:
                open(sp, 'w', newline='').write(seq_text)
                print(f'#   wrote {sp}')


if __name__ == '__main__':
    main()
