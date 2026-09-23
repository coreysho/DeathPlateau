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

The listing steps DO need a cache, and are for pulling the icon out of one yourself. caches/ is in
this repo's .gitignore ("Tens of MB each - never commit"), so a cache only ever exists on the
machine that downloaded it:

    python3 tools/models/genstaticon.py --cache "C:/LostCityServer/caches/osrs" --skills --dump out/

--skills is the one to use. Index 8 of an OSRS cache holds thousands of sprite groups and looking
through them all is not a job for a person; the skill icons are the group that holds twenty-odd
sprites which are ALL small and ALL exactly the same size, which almost nothing else in the index
is. That shape is what --skills matches, and it ranks what it finds so the likeliest group prints
first. --list is the unranked version for when that misses. Neither writes to the repo.

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

# A skill-icon group is twenty-odd same-sized sprites and almost nothing else in index 8 is.
# The bounds are loose on purpose - caches of different years ship different skill counts.
SKILLSET_MIN, SKILLSET_MAX, SKILLS_EXPECTED = 15, 32, 23


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
    ap.add_argument('--skills', action='store_true',
                    help='only groups shaped like a skill-icon set: many sprites, all small, all '
                         'the same size. Ranked, likeliest first')
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

    found = []
    for gid, sprites in cache_groups(a.cache):
        small = [(i, s) for i, s in enumerate(sprites)
                 if s.size[0] <= a.max_size and s.size[1] <= a.max_size]
        if not small:
            continue
        sizes = {s.size for _, s in small}
        uniform = len(sizes) == 1
        if a.skills and not (uniform and SKILLSET_MIN <= len(small) == len(sprites) <= SKILLSET_MAX):
            continue
        # Likeliest first: a full set of same-sized icons beats a near-miss, and among those the
        # one whose count is closest to the number of skills a cache of that era ships.
        rank = (0 if uniform else 1, abs(len(small) - SKILLS_EXPECTED))
        found.append((rank, gid, sprites, small, uniform))

    found.sort(key=lambda r: r[0])
    for _, gid, sprites, small, uniform in found:
        shape = '%dx%d' % small[0][1].size if uniform else '%d sizes' % len({s.size for _, s in small})
        print('group %-6d %2d sprite(s)  %s' % (gid, len(sprites), shape))
        if a.dump:
            for i, s in small:
                s.save(os.path.join(a.dump, 'g%d_s%d.png' % (gid, i)))
    print('%d group(s)%s' % (len(found), ' shaped like a skill-icon set' if a.skills else
                             ' with sprites <= %dpx' % a.max_size))
    if not found and a.skills:
        print('nothing matched - re-run without --skills to see everything small')
    if a.dump and found:
        print('written to %s - find the Hunter icon, then:' % a.dump)
        print('  python3 tools/models/genstaticon.py --sprite %s/gN_sN.png --cell 4 '
              '--content ../Content' % a.dump)


main()
