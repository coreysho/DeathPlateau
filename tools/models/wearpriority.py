#!/usr/bin/env python3
"""Put a worn model's faces in the client's DEPTH-SORTED priority group.

WHY A CAPE BELONGS IN GROUP 10. Model.method382 paints the merged player a priority group at a
time, 0 through 9 in order, and a face's group is fixed in the model. Legs are group 1, a body is
3, a cape is 4 to 7 - so every cape face is painted AFTER the legs and the body, however far
behind them it is. Groups 10 and 11 are the exception: those faces are interleaved by their real
depth instead, which is the whole reason they exist.

Measured on 29 October with tools/models/wearpoke.py, against Saradomin armour, walking: the
infernal max cape puts 133 pixels of itself on the armour, the plain and imbued ancient 111, the
fire 67. Every one of the faces behind it was checked and every one is genuinely BEHIND the armour
- 29 to 70 units behind - so none of it is the mesh poking through. It is all draw order. Moving
the lot to 10 takes all four to zero and leaves the back view alone, because from behind those
faces are in front and depth sorting says so.

Jagex splits a cape between 10 and 4-7 in nearly every cape in the cache - 149 of the 164 here -
so this is the convention rather than a fault in one model, and the same artefact is latent in all
of them.

  python3 tools/models/wearpriority.py --priority 10 content/models/obj/obj_max_cape_manwear.ob2
  python3 tools/models/wearpriority.py --dry-run --priority 10 content/models/obj/*max_cape_*wear.ob2
"""
import argparse, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--priority', type=int, required=True, choices=range(0, 12), metavar='0-11')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    for path in a.files:
        raw = open(path, 'rb').read()
        m = parse_ob2(raw)
        was = dict(sorted(collections.Counter(m['pri']).items()))
        if set(m['pri']) == {a.priority}:
            print(f'{os.path.basename(path):44s} already all {a.priority}')
            continue
        m['pri'] = [a.priority] * m['fcount']
        print(f'{os.path.basename(path):44s} {m["fcount"]:4d}f  {was}  ->  all {a.priority}')
        if a.dry_run:
            continue
        out = encode(m)
        open(path, 'wb').write(out)
        if len(out) != len(raw):
            print(f'     {len(raw)} -> {len(out)} bytes')


if __name__ == '__main__':
    main()
