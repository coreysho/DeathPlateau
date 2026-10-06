#!/usr/bin/env python3
"""Apply to every rooftop course the three things Al Kharid taught, and nothing else.

Each rule was worked out against one course, in game, with the owner saying what it looked like.
None of them is "copy what Old School has". Old School's data assumes Old School's renderer and its
own models, and three times over, copying a value exactly produced something wrong here. What
survives is what holds up in a 2006 client.

  1. A MARKER IS NOT A FLOOR. An overlay whose primary colour is 0xff00ff is "not drawn", and where
     the tile has no underlay to fall back on, Old School draws nothing at all. Overlay 64 is one,
     and we were painting it - a flat cream slab first, then stone tiles, which put a walkway under
     Al Kharid's second tightrope and a roof in the sky. But blanking every one of them punched
     holes in the roofs, because Old School's own roof models fill those gaps and ours do not. So it
     splits on what is UNDERNEATH: a wall or a building below means the tile is that building's roof
     and keeps a floor; nothing below means open air, and nothing is drawn.

  2. A ROOF AND A DECK CANNOT BOTH BE DRAWN. Where a roof model covers the tile one level down, the
     floor above it is a second surface, and the roof's lips and its edge pieces come up through it
     as seams and wedges. The floor goes - EXCEPT on an obstacle's own tile and the ring around it,
     because a tile with no floor token stops the client offering the obstacle on it. That cost Al
     Kharid its first tightrope for a day.

  3. A PASS-THROUGH LANDS ONE FLOOR SHORT. A jm2 tile stores the flo id PLUS ONE, and graftosrsmap
     wrote Old School's id straight through, so overlay N landed on flo N-1. The +1 is applied only
     where flo[N]'s own colour is nearer Old School's than flo[N-1]'s: the rule does NOT hold
     everywhere, and assuming it once turned wooden floors into water.

  Old School's overlays 161 and 155 are skipped throughout. They are the one-tile strips under the
  obstacles, they are green, and painting them was reverted once already - walking on invisible air
  was preferred to the green.

  python3 tools/models/rooftopfix.py --content ../content --maps "<rev236 cache>" [--course seers]
                                     [--apply]
"""
import argparse, glob, io, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importosrsmap import MapSource
from dat2ext import decompress
from reftable import RefTable, split_group

MAP_HEAD = '==== MAP ===='
LOC_HEAD = '==== LOC ===='


def pack(path):
    out = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.strip()
        if '=' in line:
            i, n = line.split('=', 1)
            out[int(i)] = n
    return out


def osrs_overlays(cache):
    """{id: dict(rgb, rgb2, hideunderlay)} - enough to say whether an overlay is drawn at all."""
    rt = RefTable(decompress(open(os.path.join(cache, 'cache', '255', '2.dat'), 'rb').read()), strict=False)
    ids = rt.file_ids[4]
    blob = decompress(open(os.path.join(cache, 'cache', '2', '4.dat'), 'rb').read())
    out = {}
    for i, f in zip(ids, split_group(blob, len(ids))):
        if not f:
            continue
        d, p = {'hideunderlay': True}, 0
        while p < len(f):
            op = f[p]
            p += 1
            if op == 0:
                break
            if op == 1:
                d['rgb'] = int.from_bytes(f[p:p + 3], 'big'); p += 3
            elif op == 2:
                p += 1
            elif op == 3:
                p += 2
            elif op == 5:
                d['hideunderlay'] = False
            elif op == 7:
                d['rgb2'] = int.from_bytes(f[p:p + 3], 'big'); p += 3
            elif op == 9:
                p += 2
        out[i] = d
    return out


def our_colours(content):
    """{flo name: rgb} out of every .flo the build has."""
    out = {}
    for p in glob.glob(os.path.join(content, '**', '*.flo'), recursive=True):
        cur = None
        for ln in io.open(p, encoding='utf-8', errors='ignore'):
            ln = ln.strip()
            m = re.match(r'^\[(\w+)\]$', ln)
            if m:
                cur = m.group(1)
            elif cur and ln.startswith('colour='):
                try:
                    out[cur] = int(ln.split('=', 1)[1], 16)
                except ValueError:
                    pass
    return out


def course_box(path, margin=6):
    text = io.open(path, encoding='utf-8').read()
    xs, zs = [], []
    for m in re.finditer(r'=\s*(\d)_(\d+)_(\d+)_(\d+)_(\d+)', text):
        _, mx, mz, lx, lz = (int(g) for g in m.groups())
        xs.append(mx * 64 + lx)
        zs.append(mz * 64 + lz)
    return (min(xs) - margin, min(zs) - margin, max(xs) + margin, max(zs) + margin) if xs else None


def obstacle_locs(content, key):
    """The loc names a course's own configs give a right-click option to - its obstacles."""
    out = set()
    for f in (key + '_rooftop.loc', key + '_rooftop_entry.loc'):
        p = os.path.join(content, 'scripts', 'skill_agility', 'configs', f)
        if not os.path.exists(p):
            continue
        cur = None
        for ln in io.open(p, encoding='utf-8'):
            ln = ln.strip()
            m = re.match(r'^\[(\w+)\]$', ln)
            if m:
                cur = m.group(1)
            elif cur and re.match(r'^op\d=', ln):
                out.add(cur)
    return out


def dist(a, b):
    return sum((((a >> s) & 255) - ((b >> s) & 255)) ** 2 for s in (0, 8, 16))


def section(lines, head):
    i = lines.index(head)
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith('====')), len(lines))
    return i, j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--maps', required=True, help='the cache the placements came from (rev236)')
    ap.add_argument('--course', action='append')
    ap.add_argument('--apply', action='store_true', help='write the maps; otherwise only report')
    a = ap.parse_args()

    flo = pack(os.path.join(a.content, 'pack', 'flo.pack'))
    rev = {n: i for i, n in flo.items()}
    locnames = pack(os.path.join(a.content, 'pack', 'loc.pack'))
    ov = osrs_overlays(a.maps)
    col = our_colours(a.content)
    ms = MapSource(a.maps)
    invisible = rev['flo_160'] + 1
    skip = {161, 155}                   # the green obstacle strips - left alone on purpose

    cfg = os.path.join(a.content, 'scripts', 'skill_agility', 'configs')
    courses = sorted(f[:-len('_course.constant')] for f in os.listdir(cfg) if f.endswith('_course.constant'))
    if a.course:
        courses = [c for c in courses if c in a.course]

    for key in courses:
        box = course_box(os.path.join(cfg, key + '_course.constant'))
        if not box:
            continue
        obstacles = obstacle_locs(a.content, key)
        tally = Counter()
        for mx in range(box[0] >> 6, (box[2] >> 6) + 1):
            for mz in range(box[1] >> 6, (box[3] >> 6) + 1):
                p = os.path.join(a.content, 'maps', 'm%d_%d.jm2' % (mx, mz))
                if not os.path.exists(p):
                    continue
                try:
                    theirs = ms.terrain('%d_%d' % (mx, mz), (mx << 8) | mz)
                except SystemExit:
                    continue
                raw = io.open(p, encoding='utf-8', newline='').read()
                eol = '\r\n' if '\r\n' in raw else '\n'
                lines = raw.split(eol)
                li, lj = section(lines, LOC_HEAD)
                roof_at, any_at, near_ob = set(), set(), set()
                for ln in lines[li + 1:lj]:
                    if not ln.strip() or ':' not in ln:
                        continue
                    h, b = ln.split(':', 1)
                    lv, lx, lz = (int(v) for v in h.split())
                    gx, gz = mx * 64 + lx, mz * 64 + lz
                    nm = locnames.get(int(b.split()[0]), '')
                    any_at.add((lv, gx, gz))
                    if nm.startswith('roof') or nm.startswith('oldroof'):
                        roof_at.add((lv, gx, gz))
                    if nm in obstacles:
                        for dx in (-1, 0, 1):
                            for dz in (-1, 0, 1):
                                near_ob.add((lv, gx + dx, gz + dz))
                                near_ob.add((lv + 1, gx + dx, gz + dz))

                mi, mj = section(lines, MAP_HEAD)
                cur = {}
                for k in range(mi + 1, mj):
                    ln = lines[k]
                    if not ln.strip() or ':' not in ln:
                        continue
                    h, b = ln.split(':', 1)
                    lv, lx, lz = (int(v) for v in h.split())
                    v = next((int(t[1:].split(';')[0]) for t in b.split() if t.startswith('o')), None)
                    if v is not None:
                        cur[(lv, mx * 64 + lx, mz * 64 + lz)] = v

                touched = False
                for k in range(mi + 1, mj):
                    ln = lines[k]
                    if not ln.strip() or ':' not in ln:
                        continue
                    head, body = ln.split(':', 1)
                    lv, lx, lz = (int(v) for v in head.split())
                    gx, gz = mx * 64 + lx, mz * 64 + lz
                    if lv < 1 or not (box[0] <= gx <= box[2] and box[1] <= gz <= box[3]):
                        continue
                    t = theirs[lv][lx][lz]
                    their_ov = t['ov']
                    toks = body.split()
                    mine = next((int(x[1:].split(';')[0]) for x in toks if x.startswith('o')), None)

                    # 2. a roof model already covers this tile - the floor on top is a second surface
                    if mine is not None and (lv - 1, gx, gz) in roof_at and (lv, gx, gz) not in near_ob:
                        keep = [x for x in toks if not x.startswith('o')]
                        lines[k] = (head + ': ' + ' '.join(keep)) if keep else head + ':'
                        tally['deck taken off a roof model'] += 1
                        touched = True
                        continue

                    if mine is None or their_ov is None or their_ov in skip:
                        continue
                    d = ov.get(their_ov, {})
                    marker = (d.get('rgb') == 0xFF00FF and d.get('hideunderlay', True)
                              and not (t.get('un') or 0))
                    new = None

                    if marker:
                        # 1. Old School draws nothing here. Is it somebody's roof, or open air?
                        if any((l, gx, gz) in any_at for l in range(lv)):
                            near = Counter(cur[(lv, gx + dx, gz + dz)]
                                           for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                                           if (lv, gx + dx, gz + dz) in cur
                                           and cur[(lv, gx + dx, gz + dz)] not in (invisible, mine))
                            if near:
                                new = near.most_common(1)[0][0]
                                tally["marker tile that is a roof, given its neighbours' floor"] += 1
                        elif mine != invisible:
                            new = invisible
                            tally['marker tile over open air, drawn as nothing'] += 1
                    elif mine == their_ov:
                        # 3. a raw pass-through - but only where the colour agrees
                        # NEARER IS NOT GOOD ENOUGH. The +1 only goes on where flo[N] is Old
                        # School's colour, near enough that it is plainly the same floor - every
                        # case that has ever been right came out exact. Merely closer than flo[N-1]
                        # would move Old School's 55 onto `darkrock`, 843 away from #606058, on the
                        # strength of beating a floor that was worse.
                        want = d.get('rgb2') if d.get('rgb') == 0xFF00FF else d.get('rgb')
                        a_name, b_name = flo.get(mine - 1), flo.get(mine)
                        ca, cb = col.get(a_name), col.get(b_name)
                        if (want is not None and cb is not None and dist(cb, want) <= 400
                                and (ca is None or dist(cb, want) < dist(ca, want))):
                            new = mine + 1
                            tally['%s -> %s (Old School %d)' % (a_name, b_name, their_ov)] += 1

                    if new is not None and new != mine:
                        for i, tok in enumerate(toks):
                            if tok.startswith('o'):
                                parts = tok[1:].split(';')
                                parts[0] = str(new)
                                toks[i] = 'o' + ';'.join(parts)
                        lines[k] = head + ': ' + ' '.join(toks)
                        touched = True

                if a.apply and touched:
                    io.open(p, 'w', encoding='utf-8', newline='').write(eol.join(lines))

        print('\n' + key + ('' if a.apply else '   (report only - pass --apply to write)'))
        if not tally:
            print('   nothing to change')
        for n, c in tally.most_common():
            print('   %6d  %s' % (c, n))


if __name__ == '__main__':
    main()
