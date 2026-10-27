#!/usr/bin/env python3
"""Put an OSRS minimap icon into a free slot of content/sprites/mapfunction.png.

    python genmapicon.py --sprite 1513 --slot 71 [--dry-run]

WHY A TOOL AND NOT A ONE-OFF PASTE. The sheet is the only record of what each slot holds, and a
slot is referenced by number from a loc's mapfunction= line, so a slot written by hand is a number
nobody can check afterwards. Run this and the provenance is the command.

THE SHEET. 150x120 at 15x15 (sprites/meta/mapfunction.opt), so 10 columns by 8 rows: slot = row*10
+ column, counting from 0. MAGENTA (255,0,255) IS THE TRANSPARENT KEY, not alpha - the packer reads
the sheet as indexed colour, and a slot left alpha-zero comes out black on the minimap.

HOW TO FIND THE OSRS SPRITE ID. A shop's icon is not on the shop; it is an invisible ground
decoration beside it, whose maparea= names a record in config group 35, whose opcode 1 is the
sprite id. Aleck's Hunter Emporium is OSRS loc 19751 -> maparea 67 -> sprite 1513, a kebbit.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flatcache, osrssprite
from PIL import Image

CACHE = '../../caches/newest cache'
SHEET = '../../content/sprites/mapfunction.png'
KEY = (255, 0, 255, 255)
CELL = 15


def osrs_icon(cache, gid):
    """Decode one OSRS sprite group into a CELLxCELL RGBA tile, transparent where the palette is 0."""
    s = osrssprite.decode(flatcache.Store(cache).read(8, gid))
    if not s:
        raise SystemExit(f'sprite {gid} does not decode')
    if len(s['sprites']) != 1:
        raise SystemExit(f'sprite {gid} is a group of {len(s["sprites"])}, not a single icon')
    if (s['width'], s['height']) != (CELL, CELL):
        raise SystemExit(f'sprite {gid} is {s["width"]}x{s["height"]}, not {CELL}x{CELL}')
    sp, pal = s['sprites'][0], s['palette']
    tile = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    for y in range(sp['h']):
        for x in range(sp['w']):
            v = sp['px'][y * sp['w'] + x]
            if v == 0:
                continue
            c = pal[v]
            tile.putpixel((x + sp['ox'], y + sp['oy']), ((c >> 16) & 255, (c >> 8) & 255, c & 255, 255))
    return tile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sprite', type=int, required=True, help='OSRS sprite group id')
    ap.add_argument('--slot', type=int, required=True, help='mapfunction index to write')
    ap.add_argument('--cache', default=CACHE)
    ap.add_argument('--sheet', default=SHEET)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    sheet = Image.open(a.sheet).convert('RGBA')
    cols = sheet.width // CELL
    if not 0 <= a.slot < cols * (sheet.height // CELL):
        raise SystemExit(f'slot {a.slot} is off a {cols}x{sheet.height // CELL} sheet')
    tile = osrs_icon(a.cache, a.sprite)

    # Magenta behind, icon on top: the packer keys on the colour, so every pixel must be opaque.
    cell = Image.new('RGBA', (CELL, CELL), KEY)
    cell.alpha_composite(tile)
    x, y = (a.slot % cols) * CELL, (a.slot // cols) * CELL
    drawn = sum(1 for v in tile.getchannel('A').tobytes() if v)
    print(f'sprite {a.sprite} -> slot {a.slot} at ({x},{y}): {drawn}/{CELL * CELL} pixels drawn')
    if a.dry_run:
        return
    sheet.paste(cell, (x, y))
    sheet.save(a.sheet)
    print('wrote', a.sheet)


if __name__ == '__main__':
    main()
