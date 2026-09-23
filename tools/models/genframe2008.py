#!/usr/bin/env python3
"""Pull the 2008-style game frame (the one with the chat-filter bar and the door logout icon) out
of an OSRS cache into content/sprites.

WHY NOT THE 474 CACHE. genframe474.py established that the rev-474 frame is the 377 frame: the
chat bar with "Public chat / Private chat / Trade/compete / Report abuse" and the stone surround
around a 479x96 chatbox. The frame people remember as "474" - a parchment chatbox the full width
of the screen, a row of All / Game / Public / Private / Clan / Trade buttons under it, a door on
the logout tab and a clan-chat tab - arrived with clan chat in 2008. Old School RuneScape was
later given exactly that frame back as its "fixed" layout, so a current OSRS cache still ships
every piece of it, unchanged, in index 8.

HOW THE PIECES WERE FOUND. Not by guessing dimensions this time: the cache says where they go.
Interface 548 is OSRS's fixed-mode frame and interface 162 its chatbox. Decoding their IF3
components gives each piece's sprite id and its x/y on the 765x503 canvas, which is where the
table below comes from:

    group  size     at         what                          content/sprites name
    4      4x334    0,4        left edge of the viewport     backleft1
    1039   717x4    0,0        top edge                      backtop1 (with 1441)
    1441   48x4     717,0      top edge, right end           backtop1
    1037   29x156   516,4      left of the minimap           backvmid1
    1182   172x156  545,4      minimap surround              mapback
    1038   48x156   717,4      right of the minimap          backright1
    1611   249x8    516,160    under the minimap             backhmid1 (with 1036)
    1036   249x38   516,167    top tab row                   backhmid1
    1033   31x133   516,205    left of the side panel        backvmid2
    1031   190x261  547,205    side panel                    invback
    1035   28x261   737,205    right of the side panel       backright2
    1034   28x128   519,338    right of the chatbox          backvmid3
    1017   519x142  0,338      parchment chatbox             chatback
    1018   519x23   0,480      stone strip under it          backbase1
    1032   246x37   519,466    bottom tab row                backbase2

Those tile the canvas exactly - nothing overlaps but the one row where 1036 sits on 1611, and
1036 is drawn last there as it is in 548. The 377 pieces backleft2 and backhmid2 have no
counterpart: the parchment covers where they went. They are left on disk, unused.

Plus the sheets the client draws per-state:

    tabstones     38x36 x5   1026 1027 1028 1029 1030   selected-tab stones: top-left, top-right,
                                                         bottom-left, bottom-right, middle (33 wide)
    sideicons     33x36 x15  168 898-903 | 904 905-910   top row 0-6, clan 7, bottom row 8-13,
                                                         and 14 = the clan icon dimmed, for while
                                                         the server has no clan chat to open
    chatbuttons   56x22 x4   3051-3054                   normal, hover, selected, selected+hover
    reportbutton  113x22 x2  3057 3058                   normal, hover - WIDENED, see below

THE REPORT BUTTON IS WIDENED. Current OSRS has an eighth filter button (Channel) and a 79px
Report button to make room for it. The 2008 row has six filter buttons on a 66px pitch and a
Report button that fills the rest, 113px. Its ends are kept pixel-for-pixel and the middle is
stretched nearest-neighbour; the texture is noise, so the stretch does not show.

Every icon is written on its full cache canvas (33x36 for a tab icon), not trimmed: the packer
crops to the opaque pixels and records the offset, so the canvas is what positions the icon in
its tab exactly as the cache does.

    python tools/models/genframe2008.py "caches/newest cache"
"""
import os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KEY = (255, 0, 255)

# name -> [(group, x, y)] composited in order onto a canvas the size of their union
FRAME = {
    'backleft1':  [(4, 0, 0)],
    'backtop1':   [(1039, 0, 0), (1441, 717, 0)],
    'backvmid1':  [(1037, 0, 0)],
    'mapback':    [(1182, 0, 0)],
    'backright1': [(1038, 0, 0)],
    'backhmid1':  [(1611, 0, 0), (1036, 0, 7)],
    'backvmid2':  [(1033, 0, 0)],
    'invback':    [(1031, 0, 0)],
    'backright2': [(1035, 0, 0)],
    'backvmid3':  [(1034, 0, 0)],
    'chatback':   [(1017, 0, 0)],
    'backbase1':  [(1018, 0, 0)],
    'backbase2':  [(1032, 0, 0)],
}

# name -> (tile w, tile h, [group per tile])
SHEETS = {
    'tabstones':   (38, 36, [1026, 1027, 1028, 1029, 1030]),
    # 15 and 16 are the magic tab's icon for Ancient Magicks and the Lunar spellbook: OSRS sprites 1580
    # (the purple book) and 1581 (the pale book with the moon); 1579, the round sigil, is Arceuus's.
    # 474 had one icon for every book. The client picks them by the %spellbook varp,
    # clientcode 11 - see Client.java's spellbookIcon.
    'sideicons':   (33, 36, [168, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 904, 1580, 1581]),
    'chatbuttons': (56, 22, [3051, 3052, 3053, 3054]),
    'reportbutton': (113, 22, [3057, 3058]),
}
DIMMED = {('sideicons', 14)}
REPORT_CAP = 10  # columns kept as-is at each end of the Report button when it is widened


def open_store(folder):
    sys.path.insert(0, HERE)
    if any(f.endswith('.flatcache') for f in os.listdir(folder)):
        from flatcache import Store
    else:
        from dat2 import Store
    return Store(folder)


def group_image(st, gid):
    """The group's first sprite on its full canvas, transparent pixels as the magenta key."""
    import osrssprite
    from PIL import Image
    d = osrssprite.decode(st.read(8, gid))
    if not d:
        raise SystemExit('group %d does not decode as a sprite group - wrong cache?' % gid)
    s, pal = d['sprites'][0], d['palette']
    im = Image.new('RGB', (d['width'], d['height']), KEY)
    px = im.load()
    for y in range(s['h']):
        for x in range(s['w']):
            v = s['px'][y * s['w'] + x]
            if v:
                c = pal[v]
                px[s['ox'] + x, s['oy'] + y] = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    return im


def widen(im, w):
    from PIL import Image
    if im.size[0] == w:
        return im
    cap = REPORT_CAP
    mid = im.crop((cap, 0, im.size[0] - cap, im.size[1])).resize((w - cap * 2, im.size[1]), Image.NEAREST)
    out = Image.new('RGB', (w, im.size[1]), KEY)
    out.paste(im.crop((0, 0, cap, im.size[1])), (0, 0))
    out.paste(mid, (cap, 0))
    out.paste(im.crop((im.size[0] - cap, 0, im.size[0], im.size[1])), (w - cap, 0))
    return out


def dim(im):
    """Greyed and darkened, magenta left alone - the look of a tab with nothing behind it."""
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            p = px[x, y]
            if p == KEY:
                continue
            g = (p[0] * 3 + p[1] * 6 + p[2]) // 10
            g = g * 55 // 100
            px[x, y] = (g, g, g)
    return im


def colours(im):
    return len({p for p in im.getdata() if p != KEY})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache', help='an OSRS cache: a folder of .flatcache files or main_file_cache.dat2')
    ap.add_argument('--out', default=os.path.join(ROOT, 'content', 'sprites'))
    a = ap.parse_args()
    from PIL import Image

    st = open_store(a.cache)
    for name, parts in FRAME.items():
        ims = [(group_image(st, g), x, y) for g, x, y in parts]
        w = max(x + im.size[0] for im, x, y in ims)
        h = max(y + im.size[1] for im, x, y in ims)
        out = Image.new('RGB', (w, h), KEY)
        for im, x, y in ims:
            out.paste(im, (x, y))
        out.save(os.path.join(a.out, name + '.png'))
        print('  %-12s %3dx%-3d  %3d colours  from %s' % (name, w, h, colours(out),
                                                       ' + '.join(str(g) for g, _, _ in parts)))

    for name, (tw, th, groups) in SHEETS.items():
        sheet = Image.new('RGB', (tw * len(groups), th), KEY)
        for i, g in enumerate(groups):
            im = group_image(st, g)
            if name == 'reportbutton':
                im = widen(im, tw)
            if (name, i) in DIMMED:
                im = dim(im)
            if im.size[0] > tw or im.size[1] > th:
                raise SystemExit('%s tile %d: group %d is %dx%d, bigger than %dx%d'
                                 % (name, i, g, im.size[0], im.size[1], tw, th))
            sheet.paste(im, (i * tw, 0))
        sheet.save(os.path.join(a.out, name + '.png'))
        with open(os.path.join(a.out, 'meta', name + '.opt'), 'w', newline='\n') as f:
            f.write('%dx%d\n' % (tw, th))
        n = colours(sheet)
        print('  %-12s %dx%d x%-2d %3d colours%s' % (name, tw, th, len(groups), n,
              '  - OVER 255, the packer will quantise it' if n > 255 else ''))


main()
