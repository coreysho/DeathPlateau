#!/usr/bin/env python3
"""The colour a rooftop course's deck is painted, against the colour Old School paints it.

A .jm2 tile stores the flo id PLUS ONE, so `o118` is flo 117. Get that off by one and every reading
of the map is wrong by a floor - which is worth saying twice, because it is how this check was
written the first time and it made a correct course look broken and a broken one look fine.

graftosrsmap warns about a pass-through whose colour is nothing like Old School's, but only for the
overlays it passes through at the time; a remap chosen by hand (--overlay 55=roofdeck_greyslate) is
never checked against anything afterwards. This checks what is actually on the map today.

  python3 tools/models/roofcolour.py --content ../content --maps "<rev236 cache>" [--course falador]
"""
import argparse, io, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importosrsmap import MapSource
from rooftopfix import osrs_overlays

COURSES = ('draynor', 'alkharid', 'varrock', 'canifis', 'falador', 'seers', 'pollnivneach',
           'rellekka', 'ardougne')


def course_box(path, margin=6):
    xs, zs = [], []
    for m in re.finditer(r'=\s*(\d)_(\d+)_(\d+)_(\d+)_(\d+)',
                         io.open(path, encoding='utf-8').read()):
        _, mx, mz, lx, lz = (int(g) for g in m.groups())
        xs.append(mx * 64 + lx)
        zs.append(mz * 64 + lz)
    return (min(xs) - margin, min(zs) - margin, max(xs) + margin, max(zs) + margin) if xs else None


def load_flo(content):
    """flo id -> (name, colour). The id comes from flo.pack; the colour from the config."""
    cfg, cur = {}, None
    for line in io.open(os.path.join(content, 'scripts', '_unpack', '377', 'all.flo'), encoding='utf-8'):
        t = line.split('//')[0].strip()
        m = re.match(r'^\[(\w+)\]$', t)
        if m:
            cur = m.group(1)
            cfg[cur] = {}
            continue
        if cur and '=' in t:
            k, v = t.split('=', 1)
            cfg[cur][k.strip()] = v.strip()
    out = {}
    for line in io.open(os.path.join(content, 'pack', 'flo.pack'), encoding='utf-8'):
        line = line.strip()
        if '=' not in line:
            continue
        i, n = line.split('=', 1)
        c = cfg.get(n, {}).get('colour')
        out[int(i)] = (n, int(c, 16) if c else None)
    return out


def dist(a, b):
    return sum(abs(((a >> s) & 255) - ((b >> s) & 255)) for s in (0, 8, 16))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', default='../content')
    ap.add_argument('--maps', required=True)
    ap.add_argument('--course')
    ap.add_argument('--margin', type=int, default=6)
    ap.add_argument('--near', type=int, default=90, help='colour distance under which a mapping passes')
    a = ap.parse_args()

    cfg = os.path.join(a.content, 'scripts', 'skill_agility', 'configs')
    ms = MapSource(a.maps)
    ov = osrs_overlays(a.maps)
    flo = load_flo(a.content)
    # the nearest 377 floor to a colour, for suggesting a better one
    def nearest(rgb):
        best, bd = None, 1 << 30
        for i, (n, c) in flo.items():
            if c is None:
                continue
            d = dist(c, rgb)
            if d < bd:
                bd, best = d, (i, n, c)
        return best, bd

    for key in COURSES:
        if a.course and a.course != key:
            continue
        box = course_box(os.path.join(cfg, key + '_course.constant'), a.margin)
        if not box:
            continue
        pairs = Counter()
        for mx in range(box[0] >> 6, (box[2] >> 6) + 1):
            for mz in range(box[1] >> 6, (box[3] >> 6) + 1):
                reg = '%d_%d' % (mx, mz)
                try:
                    terr = ms.terrain(reg, (mx << 8) | mz)
                except SystemExit:
                    continue
                path = os.path.join(a.content, 'maps', 'm%s.jm2' % reg)
                if not os.path.exists(path):
                    continue
                section = ''
                for line in io.open(path, encoding='utf-8'):
                    t = line.strip()
                    if t.startswith('===='):
                        section = t.replace('=', '').strip()
                        continue
                    if section != 'MAP' or ':' not in t:
                        continue
                    head, rest = t.split(':', 1)
                    try:
                        lv, lx, lz = (int(v) for v in head.split())
                    except ValueError:
                        continue
                    if lv < 1:
                        continue
                    gx, gz = (mx << 6) + lx, (mz << 6) + lz
                    if not (box[0] <= gx <= box[2] and box[1] <= gz <= box[3]):
                        continue
                    mine = None
                    for tok in rest.split():
                        m = re.match(r'^o(\d+)', tok)
                        if m:
                            mine = int(m.group(1))
                    theirs = terr[lv][lx][lz].get('ov')
                    if mine and theirs:
                        pairs[(mine - 1, theirs)] += 1   # a jm2 overlay is the flo id PLUS ONE
        if not pairs:
            continue
        print('')
        print('================ %s' % key.upper())
        for (mo, to), c in pairs.most_common():
            name, colour = flo.get(mo, ('?', None))
            theirs = (ov.get(to) or {}).get('rgb')
            if theirs == 0xFF00FF:
                verdict = "Old School's is the not-drawn marker"
            elif colour is None or theirs is None:
                verdict = 'no colour to compare'
            else:
                d = dist(colour, theirs)
                if d <= a.near:
                    verdict = 'ok (%d apart)' % d
                else:
                    (bi, bn, bc), bd = nearest(theirs)
                    verdict = 'WRONG, %d apart - nearest 377 floor is %s (#%06x, %d apart), flo %d' % (
                        d, bn, bc, bd, bi)
            print('   %5d tiles  ours flo %-4d %-20s %-9s  theirs %-4d %-9s  %s'
                  % (c, mo, name[:20], ('#%06x' % colour) if colour is not None else '-',
                     to, ('#%06x' % theirs) if theirs is not None else '-', verdict))


main()
