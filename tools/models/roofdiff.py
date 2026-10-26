#!/usr/bin/env python3
"""What a rooftop course's graft LEFT BEHIND, tile by tile and loc by loc.

The courses were grafted off an Old School map dump by graftosrsmap.py, and then rooftopfix.py
applied three rules that deliberately depart from it - a marker is not a floor, a roof and a deck
cannot both be drawn, a pass-through lands one floor short. Both of those are forward passes: they
write, and nothing reads back. So nobody has ever asked the obvious question, which is what Old
School has in that box that we do not.

This asks it. For each course it derives the box from the course's own landing constants, reads the
Old School square and ours, and reports, per level:

  TILES    Old School draws a floor (an overlay or an underlay) and we draw nothing, or the other
           way round. Missing floor is a hole in a roof; extra floor is a slab over a street.
  HEIGHTS  where both draw something, whether the two agree once the fixed offset between the two
           height conventions is taken out. A tile off on its own is a step or a seam in a roof.
  LOCS     Old School places a loc and we have no placement of the same id anywhere near. THIS IS
           THE ONE TO READ FIRST: a rooftop course's look is almost all roof models - the slopes,
           the ridges, the edge pieces - and graftosrsmap only ever brought over the ids its loc
           importer resolved. rooftopfix's own note says it: "Old School's own roof models fill
           those gaps and ours do not".

Nothing is written. A fix is a graft argument or a model conversion, both of which belong to the
tools that own them; this says what to point them at.

  python3 tools/models/roofdiff.py --content ../content --maps "<rev236 cache>" [--course seers]
                                   [--level 3] [--verbose]
"""
import argparse, io, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importosrsmap import MapSource
from osrsloc import load_osrs_locs
from flatcache import Store

COURSES = ('draynor', 'alkharid', 'varrock', 'canifis', 'falador', 'seers', 'pollnivneach',
           'rellekka', 'ardougne', 'apeatoll')


def course_box(path, margin=6):
    """The rectangle a course's own constants cover, with a margin - same rule rooftopfix uses."""
    text = io.open(path, encoding='utf-8').read()
    xs, zs = [], []
    for m in re.finditer(r'=\s*(\d)_(\d+)_(\d+)_(\d+)_(\d+)', text):
        _, mx, mz, lx, lz = (int(g) for g in m.groups())
        xs.append(mx * 64 + lx)
        zs.append(mz * 64 + lz)
    if not xs:
        return None
    return (min(xs) - margin, min(zs) - margin, max(xs) + margin, max(zs) + margin)


def read_pack(path):
    out = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.strip()
        if '=' in line:
            i, n = line.split('=', 1)
            out[int(i)] = n
    return out


def read_jm2(path):
    """-> (tiles, locs). tiles[(lv,lx,lz)] = dict(h, o, u, f); locs = set((lv,lx,lz,id))."""
    tiles, locs = {}, set()
    section = ''
    if not os.path.exists(path):
        return tiles, locs
    for line in io.open(path, encoding='utf-8'):
        t = line.strip()
        if t.startswith('===='):
            section = t.replace('=', '').strip()
            continue
        if ':' not in t:
            continue
        head, rest = t.split(':', 1)
        try:
            lv, lx, lz = (int(v) for v in head.split())
        except ValueError:
            continue
        if section == 'MAP':
            d = {}
            for tok in rest.split():
                m = re.match(r'^([hofu])(\d+)', tok)
                if m:
                    d[m.group(1)] = int(m.group(2))
            tiles[(lv, lx, lz)] = d
        elif section == 'LOC':
            parts = rest.split()
            if parts:
                locs.add((lv, lx, lz, int(parts[0])))
    return tiles, locs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', default='../content')
    ap.add_argument('--maps', required=True, help='the Old School cache the graft read')
    ap.add_argument('--cache', help="the Old School cache its loc CONFIGS are in, for names - without it "
                                    'a missing loc is only an id')
    ap.add_argument('--course')
    ap.add_argument('--level', type=int, help='only this level (default: every level above 0)')
    ap.add_argument('--verbose', action='store_true', help='list every differing tile, not a count')
    ap.add_argument('--margin', type=int, default=6)
    a = ap.parse_args()

    cfg = os.path.join(a.content, 'scripts', 'skill_agility', 'configs')
    ms = MapSource(a.maps)
    # NAMES, BECAUSE AN ID SAYS NOTHING. A rooftop course's look is its roof models, and the box
    # also covers upper floors of a 2006 town that we do NOT want Old School's version of. The two
    # are told apart by what the loc is called.
    names = {}
    if a.cache:
        try:
            names, _bad = load_osrs_locs(Store(a.cache))
        except Exception as e:
            print('(could not read loc names from %s: %s)' % (a.cache, e))
    # our packed loc ids, so an Old School id can be looked for by the name the graft gave it
    packed = read_pack(os.path.join(a.content, 'pack', 'loc.pack'))
    osrs_of = {}
    for pid, name in packed.items():
        m = re.match(r'^osrsloc_(\d+)$', name)
        if m:
            osrs_of[int(m.group(1))] = pid

    for key in COURSES:
        if a.course and a.course != key:
            continue
        box = course_box(os.path.join(cfg, key + '_course.constant'), a.margin)
        if not box:
            continue
        print('')
        print('================ %s   box %d,%d .. %d,%d' % (key.upper(), *box))
        levels = [a.level] if a.level is not None else [1, 2, 3]

        for mx in range(box[0] >> 6, (box[2] >> 6) + 1):
            for mz in range(box[1] >> 6, (box[3] >> 6) + 1):
                reg = '%d_%d' % (mx, mz)
                msq = (mx << 8) | mz
                try:
                    terrain = ms.terrain(reg, msq)
                except SystemExit as e:
                    print('  m%s: %s' % (reg, e))
                    continue
                try:
                    olocs = ms.locs(reg, msq)
                except SystemExit:
                    olocs = None  # no XTEA key for this square: tiles only
                ours, ourlocs = read_jm2(os.path.join(a.content, 'maps', 'm%s.jm2' % reg))

                # ---------------------------------------------------------------- tiles
                for lv in levels:
                    miss, extra, hs = [], [], []
                    for lx in range(64):
                        gx = (mx << 6) + lx
                        if not (box[0] <= gx <= box[2]):
                            continue
                        for lz in range(64):
                            gz = (mz << 6) + lz
                            if not (box[1] <= gz <= box[3]):
                                continue
                            o = terrain[lv][lx][lz]
                            theirs = bool(o.get('ov') or o.get('un'))
                            mine = ours.get((lv, lx, lz))
                            minedrawn = bool(mine and ('o' in mine or 'u' in mine))
                            if theirs and not minedrawn:
                                miss.append((gx, gz, o.get('ov'), o.get('un')))
                            elif minedrawn and not theirs:
                                extra.append((gx, gz, mine.get('o'), mine.get('u')))
                            if theirs and minedrawn and o.get('h') is not None and 'h' in mine:
                                hs.append((gx, gz, o['h'], mine['h']))
                    if not (miss or extra or hs):
                        continue
                    print('  m%s level %d: %d tiles Old School draws and we do not, %d we draw and it does not'
                          % (reg, lv, len(miss), len(extra)))
                    if miss and a.verbose:
                        for gx, gz, ov, un in miss[:40]:
                            print('      missing %d,%d   their overlay %s underlay %s' % (gx, gz, ov, un))
                    # heights: report the spread once the commonest offset is taken out
                    if hs:
                        off = Counter(t - m for _, _, t, m in hs).most_common(1)[0][0]
                        odd = [(gx, gz, t, m) for gx, gz, t, m in hs if t - m != off]
                        print('      heights: offset %+d on %d of %d tiles, %d disagree'
                              % (off, len(hs) - len(odd), len(hs), len(odd)))
                        if odd and a.verbose:
                            for gx, gz, t, m in odd[:20]:
                                print('        %d,%d  theirs h%d  ours h%d' % (gx, gz, t, m))

                # ---------------------------------------------------------------- locs
                if olocs is None:
                    print('  m%s: no XTEA key, so its locs cannot be read' % reg)
                    continue
                # THE SHAPE SAYS WHAT A LOC IS, and a name does not. Old School's roof pieces are
                # UNNAMED - the named ones in these boxes are beds, tables and chests, which are a
                # 2006 town's upper floors and emphatically not wanted - while the map format
                # reserves shapes 12 to 21 for roofs: straight, diagonal, the four corners, flat,
                # and the sloped edges. Those are the pieces a rooftop course is built out of.
                want = defaultdict(set)
                shape_of = {}
                roof_spots = 0
                for lid, lv, lx, lz, shape, rot in olocs:
                    if a.level is not None and lv != a.level:
                        continue
                    if lv < 1:
                        continue
                    gx, gz = (mx << 6) + lx, (mz << 6) + lz
                    if not (box[0] <= gx <= box[2] and box[1] <= gz <= box[3]):
                        continue
                    want[lid].add((lv, lx, lz))
                    shape_of.setdefault(lid, Counter())[shape] += 1
                    if 12 <= shape <= 21:
                        roof_spots += 1
                if not want:
                    continue
                here = defaultdict(set)
                for lv, lx, lz, pid in ourlocs:
                    name = packed.get(pid, '')
                    m = re.match(r'^osrsloc_(\d+)$', name)
                    if m:
                        here[int(m.group(1))].add((lv, lx, lz))
                missing_ids, partial, ok = [], [], 0
                for lid, spots in sorted(want.items()):
                    mine = here.get(lid, set())
                    if not mine:
                        missing_ids.append((lid, len(spots)))
                    elif len(mine) < len(spots):
                        partial.append((lid, len(mine), len(spots)))
                    else:
                        ok += 1
                total_spots = sum(len(v) for v in want.values())
                mine_spots = sum(len(here.get(l, ())) for l in want)
                print('  m%s locs above level 0: Old School places %d of %d ids (%d placements); we have %d placements'
                      % (reg, len(want) - len(missing_ids), len(want), total_spots, mine_spots))

                # AND HOW MANY OF THEM ARE ROOF. This is the number that answers "do the courses
                # look like Old School's": the deck can be perfect and the course still reads as a
                # flat slab if the slopes, ridges and edges above it were never brought over.
                roofs_missing = 0
                roof_ids = []
                for lid, n in missing_ids:
                    sh = shape_of.get(lid, Counter())
                    n_roof = sum(c for s2, c in sh.items() if 12 <= s2 <= 21)
                    if n_roof:
                        roofs_missing += n_roof
                        roof_ids.append((lid, n_roof, sorted(s2 for s2 in sh if 12 <= s2 <= 21)))
                ours_roof = 0
                for lv, lx, lz, pid in ourlocs:
                    nm = packed.get(pid, '')
                    if not re.match(r'^osrsloc_\d+$', nm):
                        continue
                    # our jm2 keeps the shape in the row; counted below from the file instead
                print('      ROOF PIECES (shapes 12-21): Old School places %d here, and %d of them are ids '
                      'we have no placement of' % (roof_spots, roofs_missing))
                if roof_ids:
                    shown = roof_ids if a.verbose else roof_ids[:12]
                    for lid, n_roof, shapes in sorted(roof_ids, key=lambda t: -t[1])[:len(shown)]:
                        known = 'ours' if lid in osrs_of else 'not in loc.pack'
                        print('           loc %-6d x%-4d shapes %-14s %s'
                              % (lid, n_roof, ','.join(str(x) for x in shapes), known))
                    if len(shown) < len(roof_ids):
                        print('           ... and %d more roof ids' % (len(roof_ids) - len(shown)))
                if missing_ids:
                    def nameof(lid):
                        d = names.get(lid) or {}
                        n = d.get('name')
                        return n if n and n != 'null' else ''

                    # ROOFS FIRST. Anything whose name says roof, slope, ridge, tile, thatch,
                    # chimney or gable is the course's own scenery; the rest is mostly a 2006
                    # town's upper storey, where Old School's version is not what we want.
                    ROOFY = ('roof', 'slope', 'ridge', 'thatch', 'chimney', 'gable', 'tiles',
                             'shingle', 'eave', 'rafter', 'awning', 'canopy')
                    roofs = [(l, n) for l, n in missing_ids if any(w in nameof(l).lower() for w in ROOFY)]
                    unnamed = [(l, n) for l, n in missing_ids if not nameof(l)]
                    other = [(l, n) for l, n in missing_ids
                             if nameof(l) and not any(w in nameof(l).lower() for w in ROOFY)]
                    print('      %d ids with NO placement of ours: %d named like roof scenery, %d named '
                          'something else, %d with no name at all'
                          % (len(missing_ids), len(roofs), len(other), len(unnamed)))
                    for label, group in (('roof scenery', roofs), ('unnamed (scenery with no name is '
                                         'usually structure)', unnamed), ('named something else', other)):
                        if not group:
                            continue
                        print('        -- %s' % label)
                        shown = group if a.verbose else group[:10]
                        for lid, n in shown:
                            known = 'ours' if lid in osrs_of else 'not in loc.pack'
                            print('           loc %-6d x%-4d %-28s %s' % (lid, n, nameof(lid)[:28], known))
                        if len(shown) < len(group):
                            print('           ... and %d more' % (len(group) - len(shown)))
                if partial and a.verbose:
                    for lid, got, wanted in partial:
                        print('      loc %-6d we have %d of its %d placements' % (lid, got, wanted))


main()
