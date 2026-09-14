#!/usr/bin/env python3
"""Pull the game frame out of the rev 474 (Oct 2007) cache into content/sprites.

THE HEADLINE IS THAT THERE IS ALMOST NOTHING TO PULL. The frame is the same in 377 and 474 -
Jagex did not redesign it between mid-2006 and late 2007; that came with the 2009 rewrite. Run
this and fourteen of the sixteen pieces come out byte-identical to the ones already committed:

    backbase1  backbase2  backhmid1  backhmid2  backleft1  backleft2  backright1  backright2
    backtop1   backvmid1  backvmid2  backvmid3  chatback   invback

Two differ:

  mapback   the minimap surround. The stone-and-vine art is the same; 474's transparent hole is
            184 pixels smaller, so the circle it leaves for the minimap is a hair tighter. The
            minimap is drawn first and this is blitted over it, so that is cosmetic.
  compass   the real one. 377 has the dark red disc with a tan cross and N/S/E/W letters; 474 has
            the pale gold dial with the red-and-blue needle. Both are 51x51 and opaque, and the
            client draws both through the same circular mask (compassMaskLineOffsets), so it is a
            straight swap with no code behind it.

HOW THE PIECES WERE FOUND. 474 sprites are numbered, not named - the name hashes 377 uses
(`new Pix8(jagMedia, "backleft1", 0)`) find nothing in its idx8. They were matched on EXACT
DIMENSIONS instead: 765x4 and 4x334 and 172x156 are distinctive enough that there is one
candidate each, and the matches landed on groups 0-14 contiguously, which is the frame set in
order. The compass is group 169.

Magenta (0xFF00FF) is the packer's transparent colour and content/sprites/mapback.png already
uses it for the minimap hole, so that is what a zero palette index is written as here.

    python tools/models/genframe474.py "caches/474 cache" [--all]

Without --all only the pieces that actually differ are written.
"""
import os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 474 idx8 group -> the name content/sprites uses
PIECES = {0: 'backbase1', 1: 'backbase2', 2: 'backhmid1', 3: 'backhmid2',
          4: 'backleft1', 5: 'backleft2', 6: 'backright1', 7: 'backright2',
          8: 'backtop1', 9: 'backvmid1', 10: 'backvmid2', 11: 'backvmid3',
          12: 'mapback', 13: 'chatback', 14: 'invback', 169: 'compass'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('--all', action='store_true', help='write every piece, not only the ones that differ')
    ap.add_argument('--out', default=os.path.join(ROOT, 'content', 'sprites'))
    a = ap.parse_args()

    sys.path.insert(0, HERE)
    from dat2 import Store
    import osrssprite
    from PIL import Image

    st = Store(a.cache)
    same = []
    for group, name in sorted(PIECES.items()):
        d = osrssprite.decode(st.read(8, group))
        s = d['sprites'][0]
        pal = d['palette']
        im = Image.new('RGB', (s['w'], s['h']), (255, 0, 255))
        px = im.load()
        for y in range(s['h']):
            for x in range(s['w']):
                v = s['px'][y * s['w'] + x]
                if not v:
                    continue                      # index 0 is transparent -> leave it magenta
                c = pal[v]
                px[x, y] = ((c >> 16) & 255, (c >> 8) & 255, c & 255)

        dst = os.path.join(a.out, f'{name}.png')
        old = None
        if os.path.exists(dst):
            o = Image.open(dst)
            if o.mode == 'RGBA':
                bg = Image.new('RGB', o.size, (255, 0, 255))
                bg.paste(o, (0, 0), o)
                o = bg
            old = o.convert('RGB')

        if old is not None and old.size == im.size and list(old.getdata()) == list(im.getdata()):
            same.append(name)
            if not a.all:
                continue
        else:
            n = -1
            if old is not None and old.size == im.size:
                n = sum(1 for p, q in zip(old.getdata(), im.getdata()) if p != q)
            print(f'  {name:11} group {group:4}  {s["w"]}x{s["h"]:<4} differs ({n} px)')
        im.save(dst)
    print(f'identical to what is already committed: {len(same)} of {len(PIECES)} '
          f'({", ".join(same)})')


main()
