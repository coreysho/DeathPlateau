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
- 29 to 70 units behind - so none of it is the mesh poking through. It is all draw order.

IT DOES NOT LEAVE THE BACK VIEW ALONE, whatever this file said for a day. Bucket-granularity depth
is not fine enough to keep a cape clear of the body it is draped over, so from behind the armour
is painted through the middle of the cape - a hole, where the fixed priority had been holding the
cape shut over the body exactly as it holds a helmet shut over a head. Measured over all 164
cape-slot models with WearSweep --selfdiff, against the authored bytes and a gender-matched kit:
63,742 pixels gained from the front and 529,170 lost from the back, and 152 of the 164 worse off.
Only twelve survived, and the rest were put back.

So this script is for ONE MODEL AT A TIME, with the back view rendered before and after, and
content/tools/capepriority_battery.py will fail until its table is updated to say so.

Jagex splits a cape between 10 and 4-7 in nearly every cape in the cache - 149 of the 164 here -
and that split is the convention doing real work, not a fault to be flattened away.

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
