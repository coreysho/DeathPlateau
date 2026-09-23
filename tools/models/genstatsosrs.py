#!/usr/bin/env python3
"""Lay content's skill tab (scripts/interfaces/stats.if) out as current OSRS's (OSRS interface 320).

    python tools/models/genstatsosrs.py "caches/newest cache"

OSRS's tab is 24 cells of 62x30 on a 63x30 grid, each drawn by client script 393: two halves of a
stone cell (sprites 187, and 188 with the slash across it), the skill's icon (enum 255) at 3,4, the
current level at 32,4 and the base level at 44,16, small yellow font. Under the grid is a bar
(sprites 189 / 191 / 190) that says "Total level: N". This tab had 474's layout: the same icon and
level offsets on a 63x31 grid of 474's full cells, and the total in the last cell.

So this moves rather than rebuilds. Every component the stats tab has keeps its name, because the
names are used - xplock.rs2 retitles the hover panels, genxplock.py reads the guide buttons, the
gamemode battery reads both - and each is put in the OSRS cell of the 474 cell it was in, by what it
is: an icon to 3,4, a level to 32,4 or 44,16, a click box over the whole cell. 474's cell art goes,
and OSRS's is drawn under the grid.

OSRS's last cell is Sailing, which this game does not have. It is an empty cell, so the grid is whole.

Run it on the 474 layout only once; a second run finds no 474 grid to map from and stops. It reruns
content's genxplock.py (whose lock buttons follow the guide buttons) and ifids.py.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')
PATH = os.path.join(CONTENT, 'scripts', 'interfaces', 'stats.if')
SPRITES = os.path.join(CONTENT, 'sprites')
KEY = (255, 0, 255)
MARK = '// LAID OUT AS OSRS\'s'

# 474's grid, which the file is in, and OSRS's, which it goes to
OLD_W, OLD_H = 63, 31
NEW_X, NEW_Y, NEW_W, NEW_H = 1, 1, 63, 30
ROWS = 8
BAR_Y = 241


def parse(text):
    head, blocks = [], []
    for part in re.split(r'\n(?=\[)', text.replace('\r\n', '\n')):
        lines = [l for l in part.split('\n') if l.strip()]
        if lines and lines[0].startswith('['):
            blocks.append([lines[0][1:-1], [l.split('=', 1) for l in lines[1:] if '=' in l]])
        else:
            head += lines
    return head, blocks


def get(kv, k):
    for a, b in kv:
        if a == k:
            return b
    return None


def put(kv, k, v):
    for p in kv:
        if p[0] == k:
            if v is None:
                kv.remove(p)
            else:
                p[1] = str(v)
            return
    if v is not None:
        # after the geometry, where the other files keep it
        at = max([i + 1 for i, p in enumerate(kv) if p[0] in ('type', 'layer', 'x', 'y')] or [0])
        kv.insert(at, [k, str(v)])


def cell_of(x, y, w, h):
    col = max(0, min(2, int((x + w / 2) // OLD_W)))
    row = max(0, min(ROWS - 1, int((y + h / 2) // OLD_H)))
    return col, row


def origin(col, row):
    return NEW_X + col * NEW_W, NEW_Y + row * NEW_H


def write_sprite(name, im):
    im.save(os.path.join(SPRITES, name + '.png'))
    return '%s,0' % name


def main():
    from osrsif import Cache
    from PIL import Image, ImageOps
    cache = Cache(sys.argv[1])
    raw = open(PATH, encoding='utf-8').read()
    if MARK in raw:
        raise SystemExit('stats.if is already laid out as OSRS\'s - nothing to map from')
    head, blocks = parse(raw)
    by = {n: kv for n, kv in blocks}

    # the art: both halves of a cell, an empty right half for the Sailing cell, the total bar, and the
    # icons wherever OSRS's differ from the 474 ones content has
    left = write_sprite('osrsstat_left', cache.sprite(187))
    right = write_sprite('osrsstat_right', cache.sprite(188))
    blank = write_sprite('osrsstat_blank', ImageOps.mirror(cache.sprite(187)))
    bar_l = write_sprite('osrsstat_bar_l', cache.sprite(189))
    bar_m = write_sprite('osrsstat_bar_m', cache.sprite(191))
    bar_r = write_sprite('osrsstat_bar_r', cache.sprite(190))
    icons = {}

    def icon(g):
        """OSRS's version of a skill icon: content's i474_N where it is the same picture, else its own."""
        m = re.match(r'i474_(\d+),0$', g)
        if not m or int(m.group(1)) not in set(cache.enum(255).values()):
            return g
        if g not in icons:
            sid = int(m.group(1))
            im = cache.sprite(sid)
            mine = Image.open(os.path.join(SPRITES, 'i474_%d.png' % sid)).convert('RGB')
            icons[g] = g if mine.tobytes() == im.tobytes() else write_sprite('osrsstat_icon%d' % sid, im)
        return icons[g]

    # every component's absolute place; row layers are opened out so their children stand alone
    layers = {n for n, kv in blocks if get(kv, 'type') == 'layer'}
    offset = {}
    for n, kv in blocks:
        p = get(kv, 'layer')
        ox, oy = offset.get(p, (0, 0))
        offset[n] = (ox + int(get(kv, 'x') or 0), oy + int(get(kv, 'y') or 0))
    rowlayers = {n for n in layers if get(by[n], 'hide') is None}

    out, dropped, total_cell = [], [], None
    for n, kv in blocks:
        t, g = get(kv, 'type'), get(kv, 'graphic') or ''
        ax, ay = offset[n]
        w, h = int(get(kv, 'width') or 0), int(get(kv, 'height') or 0)
        parent = get(kv, 'layer')
        if n in rowlayers:
            dropped.append(n)
            continue
        in_row = parent in rowlayers
        if in_row or (parent is None and t != 'layer'):
            op = get(kv, 'script1op1') or ''
            # 474's cell art, and the total cell's own box
            if t == 'graphic' and (g.startswith('miscgraphics,4') or g.startswith('i474_175')):
                dropped.append(n)
                continue
            if t == 'rect' and parent == 'com_42':
                dropped.append(n)
                continue
            col, row = cell_of(ax, ay, w, h)
            cx, cy = origin(col, row)
            put(kv, 'layer', None)
            if n == 'total_label':
                dropped.append(n)
                continue
            if op == 'op9':
                # the total, on the bar
                total_cell = (col, row)
                put(kv, 'x', 2); put(kv, 'y', BAR_Y + 3); put(kv, 'width', 186); put(kv, 'height', 14)
                put(kv, 'font', 'p11_full'); put(kv, 'center', 'yes'); put(kv, 'text', 'Total level: %1')
            elif n == 'total_hover_target':
                put(kv, 'x', 0); put(kv, 'y', BAR_Y); put(kv, 'width', 190); put(kv, 'height', 19)
            elif t == 'graphic' and w == 25 and h == 25:
                put(kv, 'x', cx + 3); put(kv, 'y', cy + 4)
                put(kv, 'graphic', icon(g))
            elif op.startswith('stat_level,'):
                put(kv, 'x', cx + 32); put(kv, 'y', cy + 4); put(kv, 'width', 15); put(kv, 'height', 12)
                put(kv, 'font', 'p11_full')
            elif op.startswith('stat_base_level,'):
                put(kv, 'x', cx + 44); put(kv, 'y', cy + 16); put(kv, 'width', 15); put(kv, 'height', 12)
                put(kv, 'font', 'p11_full')
            elif get(kv, 'buttontype') or get(kv, 'overlayer'):
                put(kv, 'x', cx); put(kv, 'y', cy); put(kv, 'width', 62)
                put(kv, 'height', 32 if row == ROWS - 1 else 30)
            else:
                raise SystemExit('%s: a %s in cell %d,%d this does not know how to place' % (n, t, col, row))
        elif n == 'com_42':
            dropped.append(n)
            continue
        out.append([n, kv])

    # the cells, under everything: two halves each, the last one empty
    art = []
    for col in range(3):
        for row in range(ROWS):
            cx, cy = origin(col, row)
            empty = (col, row) == (2, ROWS - 1)
            art.append(['cell%d_%d' % (col, row), [['type', 'graphic'], ['x', cx], ['y', cy], ['width', 36],
                                                   ['height', 36], ['graphic', left]]])
            art.append(['cell%d_%d_r' % (col, row), [['type', 'graphic'], ['x', cx + (26 if empty else 31)],
                                                     ['y', cy], ['width', 36], ['height', 36],
                                                     ['graphic', blank if empty else right]]])
    for i, (x, gname) in enumerate([(1, bar_l)] + [(x, bar_m) for x in (36, 72, 108)] + [(153, bar_r)]):
        art.append(['totalbar%d' % i, [['type', 'graphic'], ['x', x], ['y', BAR_Y], ['width', 36], ['height', 19],
                                       ['graphic', gname]]])

    lines = [MARK + ' (OSRS interface 320), by LostCityServer tools/models/genstatsosrs.py, which moved every',
             '// component to its OSRS cell and drew OSRS\'s cells under them. Rerun genxplock.py after editing.']
    lines += [l for l in head if not l.startswith('//')]
    for n, kv in art + out:
        lines.append('')
        lines.append('[%s]' % n)
        lines += ['%s=%s' % (k, v) for k, v in kv]
    with open(PATH, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('stats.if: %d components moved, %d dropped (%s), total from cell %s'
          % (len(out), len(dropped), ' '.join(dropped[:12]) + (' ...' if len(dropped) > 12 else ''), total_cell))
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'genxplock.py')], cwd=CONTENT)
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), 'stats'])


if __name__ == '__main__':
    main()
