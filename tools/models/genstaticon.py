#!/usr/bin/env python3
"""Put a skill icon into content/sprites/staticons2.png.

WHY THIS EXISTS. staticons2 is the 377 client's second skill-icon sheet: six drawn 25x25 cells in
a 6x3 grid, of which 377 only ever referenced four (0 Slayer, 1 Farming, 2 Runecrafting, 5
Construction). Cell 4 is a rat and cell 3 a spade - neither is Hunter, and Jagex's own Hunter icon
is in a cache this repo does not ship. So the sheet has to be edited, and editing a spritesheet by
hand is how you end up one pixel off with no way to tell.

The paste step needs NO CACHE. Hand it any PNG - an icon pulled off the wiki, an export from a
cache, anything - and it lands in the cell, scaled and keyed, with the rest of the sheet untouched:

    python3 tools/models/genstaticon.py --sprite hunter.png --cell 4 --content ../Content

The two listing steps DO need a cache, and are for pulling the icon out of one yourself:

    python3 tools/models/genstaticon.py --cache "C:/LostCityServer/caches/osrs" --list
    python3 tools/models/genstaticon.py --cache "C:/LostCityServer/caches/osrs" --dump out/

--list prints every sprite group in index 8 whose sprites are small enough to be an icon; --dump
writes them all out as PNGs so the right one can be picked by eye. Neither writes to the repo.

TRANSPARENCY IS MAGENTA, not alpha. tools/pack/PixPack.ts keys 0xFF00FF when it splits the sheet,
so that is what a transparent pixel has to be written as - an alpha channel is thrown away by the
packer and a black background would render as a black square in the stats tab.

SCALING IS NEAREST-NEIGHBOUR AND ASPECT-PRESERVING. A 25x25 cell next to five hand-drawn ones is
not the place for smooth resampling; the icon is centred in the cell with the remainder keyed out.
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CELL = 25
KEY = (255, 0, 255)


def load_png(path):
    from PIL import Image
    return Image.open(path).convert('RGBA')


def fit_to_cell(img):
    """Scale to fit CELLxCELL without distortion, centre, and key the rest to magenta."""
    from PIL import Image
    w, h = img.size
    if w == 0 or h == 0:
        raise SystemExit('%s is empty' % img)
    scale = min(CELL / w, CELL / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    small = img.resize((nw, nh), Image.NEAREST)
    cell = Image.new('RGBA', (CELL, CELL), KEY + (255,))
    cell.alpha_composite(small, ((CELL - nw) // 2, (CELL - nh) // 2))
    # Anything still transparent, or already magenta, ends up as the key colour.
    px = cell.load()
    for y in range(CELL):
        for x in range(CELL):
            r, g, b, a = px[x, y]
            if a < 128:
                px[x, y] = KEY + (255,)
            else:
                px[x, y] = (r, g, b, 255)
    return cell


def paste(content, sprite_path, cell_index, sheet='staticons2'):
    from PIL import Image
    sheet_path = os.path.join(content, 'sprites', '%s.png' % sheet)
    if not os.path.exists(sheet_path):
        raise SystemExit('no such sheet: %s' % sheet_path)
    im = Image.open(sheet_path).convert('RGBA')
    cols = im.size[0] // CELL
    rows = im.size[1] // CELL
    if im.size[0] % CELL or im.size[1] % CELL:
        raise SystemExit('%s is %dx%d, which is not a whole number of %dpx cells'
                         % (sheet_path, im.size[0], im.size[1], CELL))
    if not 0 <= cell_index < cols * rows:
        raise SystemExit('cell %d is outside the %dx%d grid (0..%d)'
                         % (cell_index, cols, rows, cols * rows - 1))
    cell = fit_to_cell(load_png(sprite_path))
    cx, cy = (cell_index % cols) * CELL, (cell_index // cols) * CELL
    before = im.crop((cx, cy, cx + CELL, cy + CELL)).tobytes()
    im.paste(cell, (cx, cy))
    im.convert('RGB').save(sheet_path)
    after = cell.tobytes()
    print('%s cell %d written (%dx%d grid)%s'
          % (sheet, cell_index, cols, rows, '' if before != after else ' - unchanged, same pixels'))


def cache_groups(cache):
    """Every index-8 sprite group that decodes, with its sprite sizes."""
    from dat2 import Store
    import osrssprite
    st = Store(cache)
    if 8 not in st.idx:
        raise SystemExit('%s has no main_file_cache.idx8 - index 8 is the sprite index' % cache)
    for gid in range(st.count(8)):
        try:
            raw = st.read(8, gid)
        except Exception:
            continue
        if not raw:
            continue
        got = osrssprite.decode(raw)
        if not got:
            continue
        yield gid, got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', help='an OSRS cache folder (the one holding main_file_cache.dat2)')
    ap.add_argument('--list', action='store_true', help='print index-8 groups that could hold icons')
    ap.add_argument('--dump', help='write every candidate sprite to this folder as PNG')
    ap.add_argument('--max-size', type=int, default=64,
                    help='only consider sprites no larger than this (default 64)')
    ap.add_argument('--sprite', help='a PNG to paste into the sheet')
    ap.add_argument('--cell', type=int, help='which cell of the sheet to paste into, row-major from 0')
    ap.add_argument('--sheet', default='staticons2', help='sheet name (default staticons2)')
    ap.add_argument('--content', default='../Content', help='path to the Content repo')
    a = ap.parse_args()

    if a.sprite is not None:
        if a.cell is None:
            raise SystemExit('--sprite needs --cell')
        paste(a.content, a.sprite, a.cell, a.sheet)
        return

    if not a.cache:
        ap.print_help()
        return

    if a.dump:
        os.makedirs(a.dump, exist_ok=True)
    n = 0
    for gid, sprites in cache_groups(a.cache):
        small = [(i, s) for i, s in enumerate(sprites)
                 if s.size[0] <= a.max_size and s.size[1] <= a.max_size]
        if not small:
            continue
        n += 1
        sizes = ', '.join('%d:%dx%d' % (i, s.size[0], s.size[1]) for i, s in small[:8])
        print('group %-6d %d sprite(s)  %s%s' % (gid, len(sprites), sizes,
                                                 ' ...' if len(small) > 8 else ''))
        if a.dump:
            for i, s in small:
                s.save(os.path.join(a.dump, 'g%d_s%d.png' % (gid, i)))
    print('%d group(s) with sprites <= %dpx' % (n, a.max_size))
    if a.dump:
        print('written to %s - find the Hunter icon, then re-run with --sprite <that file> --cell 4'
              % a.dump)


main()
