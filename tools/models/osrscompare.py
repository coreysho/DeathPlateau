#!/usr/bin/env python3
"""A shipped worn model against the OSRS model it was imported from.

WHY THIS EXISTS. Three rounds of cape fixes in October each measured the change against a render
of our own build and each came out worse in game, because there was nothing to be right ABOUT. A
worn model's priorities are not a free choice: the artist set them against a body, and the only
thing that says what they should be is the model the import came from. This is that reference.

WHAT IT FOUND, run on 31 October. The import is faithful - the clue hunter garb, a torso, comes
through from OSRS 31630 byte-for-byte identical in its priorities, so 377 and OSRS really do share
the 0-11 scheme the importer assumes. The capes do not, and all of them differ in one way:

    clue hunter cloak   OSRS 31626   {0: 78, 6: 382}                  ours {6: 382, 10: 78}
    infernal max cape   OSRS 33102   {0: 61, 1: 70, 4: 204, 5: 260,   ours {4: 204, 5: 260,
                                      6: 34, 7: 16}                         6: 34, 7: 16, 10: 131}

Every face OSRS puts at priority 0 or 1 - painted FIRST, under the body, which is where the artist
put the collar and the shoulder on purpose - has been moved into group 10, where the client
interleaves by depth and a face can be drawn in FRONT of the body instead. That is content commit
1e84179fe and tools/capecollar.py, 13 October: 140 cape models, and in 135 of them the only change
is exactly 0 -> 10 and 1 -> 10.

So the cape over the armour is not something the import got wrong and not something the renderer
does to OSRS geometry. It is one edit, applied to one slot, that took faces out of the group that
was hiding them.

    python3 tools/models/osrscompare.py obj_infernal_max_cape_manwear=33102
    python3 tools/models/osrscompare.py --variants          # every Max cape variant in the spec
    python3 tools/models/osrscompare.py --cache caches/osrs obj_clue_hunter_cloak_manwear=31626

Exit status is 1 if any pair differs, so it can be a check rather than a report.
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from flatcache import Store
from osrsmodel import layout
from osrs2ob2 import parse_ob2

# what each priority group means for a worn model, as Model.method382 paints it
WHERE = {0: 'under the body', 1: 'under the body', 2: 'under the body',
         3: 'with the body', 4: 'over the body', 5: 'over the body',
         6: 'over the body', 7: 'over the body', 8: 'over the body', 9: 'over the body',
         10: 'depth-sorted', 11: 'depth-sorted'}


def osrs_priorities(store, mid):
    raw = store.read(7, mid)
    L = layout(raw)
    if L is None:
        return None, None
    if L['has_pri']:
        return L['fc'], list(raw[L['fpri']:L['fpri'] + L['fc']])
    return L['fc'], [L['pri']] * L['fc']


def ours_priorities(name):
    for sub in ('obj', 'idk'):
        p = os.path.join(ROOT, 'content', 'models', sub, name + '.ob2')
        if os.path.exists(p):
            m = parse_ob2(open(p, 'rb').read())
            return m['fcount'], m['pri']
    return None, None


def hist(pri):
    return dict(sorted(collections.Counter(pri).items()))


def variants_from_spec():
    """The Max cape variants, whose OSRS worn model ids the spec records as provenance."""
    spec = json.load(open(os.path.join(ROOT, 'content', 'tools', 'maxcapevariantspec.json')))
    out = []
    for v in spec['variants']:
        for part in ('cape', 'hood'):
            blk = v.get(part) or {}
            for slot in ('manwear', 'womanwear'):
                mid = blk.get(slot)
                if not mid:
                    continue
                out.append(('obj_%s_max_%s_%s' % (v['key'], 'cape' if part == 'cape' else 'hood',
                                                  slot), mid))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs', nargs='*', metavar='name=osrs_id')
    ap.add_argument('--cache', default=os.path.join(ROOT, 'caches', 'osrs'))
    ap.add_argument('--variants', action='store_true',
                    help='every Max cape variant whose OSRS id the spec records')
    a = ap.parse_args()

    jobs = [(p.split('=')[0], int(p.split('=')[1])) for p in a.pairs]
    if a.variants:
        jobs += variants_from_spec()
    if not jobs:
        ap.error('give at least one name=osrs_id, or --variants')

    store = Store(a.cache)
    bad = 0
    for name, mid in jobs:
        fo, po = osrs_priorities(store, mid)
        fn, pn = ours_priorities(name)
        if pn is None:
            # the god variants have no mesh of their own: they are the plain Max cape with a
            # config recolour, so there is nothing here to compare and that is not a fault
            print('%-44s no mesh of its own (a config recolour)' % name)
            continue
        if po is None:
            print('%-44s OSRS %-6d unreadable' % (name, mid))
            continue
        print('%s' % name)
        print('   OSRS %-6d %4df  %s' % (mid, fo, hist(po)))
        print('   ours        %4df  %s' % (fn, hist(pn)))
        if fo != fn:
            print('   DIFFERENT MESH: %d faces against %d, so the priorities are not comparable'
                  % (fn, fo))
            bad += 1
            continue
        moves = collections.Counter((x, y) for x, y in zip(po, pn) if x != y)
        if not moves:
            print('   identical, face for face')
            continue
        bad += 1
        for (src, dst), n in sorted(moves.items(), key=lambda kv: -kv[1]):
            print('   %4d faces moved %d -> %d   (%s -> %s)'
                  % (n, src, dst, WHERE.get(src, '?'), WHERE.get(dst, '?')))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
