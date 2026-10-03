#!/usr/bin/env python3
"""Build the Magic shortbow (i)'s three models with ONE frame of its sparkle.

WHY THIS IS NOT JUST AN importosrs.py RUN. Old School's Magic shortbow (i) (obj 12788) carries a
sparkle that its icon ANIMATES - the wiki's own trivia says so: "The icon of the bow is animated,
but only shows one frame at a time." The animation is baked into the mesh rather than driven by a
seq: each of models 48061, 47997 and 47999 holds the sparkle THREE TIMES, at three places along
the limb, as four flat faces each, and Old School shows one of the three per frame.

The 377 client cannot animate an inventory icon, so it draws all twelve at once. That is what the
owner was shown on 2026-10-03: a bow buried under six pale slabs.

So this keeps ONE position and makes the other eight faces undrawn - which IS one frame, and the
closest thing to the real item a client without icon animation can show. Transparent rather than
deleted, the same choice osrs2ob2.py makes for a face Old School never draws: dropping faces would
shift every index its round-trip check compares.

The three positions are faces 56-67 in all three models, four to a position, and they sort cleanly
into three groups by how far along the limb they sit. Nothing here is hardcoded to an index: the
grouping is computed and checked, so a cache update that renumbers them is a loud failure rather
than a silently wrong bow.

  python3 tools/models/genmsbi.py "<osrs cache>" --content ../../content
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flatcache import Store
from osrs2ob2 import decode, encode, roundtrip

SPARKLE_HSL = 9443          # the pale cream the sparkle is painted
UNDRAWN = 255               # face alpha the client reads as "do not draw this"
KEEP = 1                    # which of the three positions to show: 0 nearest the lower limb,
                            # 1 the grip, 2 the upper limb. The grip reads at every icon angle.

MODELS = {48061: 'obj_magic_shortbow_i',
          47997: 'obj_magic_shortbow_i_manwear',
          47999: 'obj_magic_shortbow_i_womanwear'}


def sparkle_groups(m):
    """The twelve sparkle faces, split into the three positions along the limb."""
    pale = [i for i in range(m['fcount']) if m['colour'][i] == SPARKLE_HSL]
    if len(pale) != 12:
        raise SystemExit(f'expected 12 sparkle faces, found {len(pale)} - the cache model has changed')

    def along(i):
        vs = (m['fa'][i], m['fb'][i], m['fc'][i])
        zs = [m['vz'][v] for v in vs]
        return (min(zs) + max(zs)) / 2

    ordered = sorted(pale, key=along)
    groups = [ordered[0:4], ordered[4:8], ordered[8:12]]
    # The three really are three places and not one smear: the gap between neighbouring groups has
    # to be bigger than the spread inside either of them, or the split means nothing.
    for a, b in zip(groups, groups[1:]):
        spread = max(along(i) for i in a) - min(along(i) for i in a)
        gap = min(along(i) for i in b) - max(along(i) for i in a)
        if gap <= spread / 2:
            raise SystemExit('the sparkle faces do not fall into three positions any more')
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('--content', required=True)
    ap.add_argument('--keep', type=int, default=KEEP, choices=(0, 1, 2))
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    st = Store(a.cache)
    mdir = os.path.join(a.content, 'models', 'obj')
    for mid, name in MODELS.items():
        m = decode(st.read(7, mid))
        groups = sparkle_groups(m)
        hide = [i for g in (groups[:a.keep] + groups[a.keep + 1:]) for i in g]

        if m['alpha'] is None:
            m['alpha'] = [0] * m['fcount']
        for i in hide:
            m['alpha'][i] = UNDRAWN

        ob2 = encode(m)
        ok, why = roundtrip(ob2, m)
        if not ok:
            raise SystemExit(f'{name}: {why}')
        print(f'{name}: kept sparkle {a.keep} ({groups[a.keep]}), hid {sorted(hide)}')
        if not a.dry_run:
            open(os.path.join(mdir, name + '.ob2'), 'wb').write(ob2)

    if a.dry_run:
        print('# dry run - nothing written')


if __name__ == '__main__':
    main()
