#!/usr/bin/env python3
"""Give content's skill tab (scripts/interfaces/stats.if) pre-Sailing OSRS's art.

    python tools/models/genstatsosrs.py "caches/newest cache"

OSRS's skill tab until Sailing (2013-2025) was 474's: the same 3x8 grid of stone cells, with the
knobbed frame between them, the icon at the left of each, level over level with a slash between. It
differed in the details below, measured off a pre-Sailing screenshot at 2x by matching each thing's
own pixels (the result differs from that screenshot in 16 pixels of 49,536). This makes those
changes to the 474 file and nothing else, so every name the scripts and genxplock.py use is kept:

  - the rows are 32 pixels apart, not 31, and each row's cell art sits a pixel above its row
  - the levels sit by one rule, 33,5 and 45,17 in each 63x32 cell, which 474 kept only roughly; the
    icons sit where OSRS put them one by one (a table, ICON_AT)
  - the icons are OSRS's (enum 255) where they differ: Runecraft, Slayer, Farming, Hunter, Construction
  - the total's box is OSRS's black cell with the stone rim (sprites 183 / 184, halves like every
    other cell's) where 474 drew nested rects, and says "Total level:" over the number in small yellow
  - hovering it shows your total experience, "Total XP: 4,600,000,000", where 474's panel showed
    combat level and quest points. That is client code 329 (Client-Java), which sums every skill as
    a long: 23 skills at 200M do not fit the int a component script adds in.

(A current cache's other cell art - 174/175/176, and Sailing's 187-191 - is not 474's knobbed frame
and is not used.)

It runs on the 474 layout; a second run finds no 474 art to replace and stops.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')
PATH = os.path.join(CONTENT, 'scripts', 'interfaces', 'stats.if')
SPRITES = os.path.join(CONTENT, 'sprites')
MARK = "// PRE-SAILING OSRS's changes to 474's tab"


def parse(text):
    head, blocks = [], []
    for part in re.split(r'\n(?=\[)', text.replace('\r\n', '\n')):
        lines = [l for l in part.split('\n') if l.strip()]
        if lines and lines[0].startswith('['):
            blocks.append([lines[0][1:-1], [l.split('=', 1) for l in lines[1:] if '=' in l],
                           [l for l in lines[1:] if l.startswith('//')]])
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
            p[1] = str(v)
            return
    kv.append([k, str(v)])


def write_sprite(name, im):
    im.save(os.path.join(SPRITES, name + '.png'))
    return '%s,0' % name


def main():
    from osrsif import Cache
    from PIL import Image
    cache = Cache(sys.argv[1])
    raw = open(PATH, encoding='utf-8').read()
    if MARK in raw:
        raise SystemExit("stats.if has already been given OSRS's changes")
    head, blocks = parse(raw)

    wanted = set(cache.enum(255).values())
    icons = {}

    def icon(g):
        m = re.match(r'i474_(\d+),0$', g)
        if not m or int(m.group(1)) not in wanted:
            return g
        if g not in icons:
            sid = int(m.group(1))
            im = cache.sprite(sid)
            mine = Image.open(os.path.join(SPRITES, 'i474_%d.png' % sid)).convert('RGB')
            icons[g] = g if mine.tobytes() == im.tobytes() else write_sprite('osrsstat_icon%d' % sid, im)
        return icons[g]

    out = []
    for n, kv, comments in blocks:
        g = get(kv, 'graphic') or ''
        # OSRS's rows are 32 apart where 474's are 31 (measured off a pre-Sailing screenshot: the same
        # digits, 64 pixels apart at 2x). Every visible top-level component - the row layers, the
        # total's cell, the click boxes - moves down by its row number; the hover panels stay put.
        if get(kv, 'layer') is None and get(kv, 'hide') is None and get(kv, 'y') is not None:
            y, h = int(get(kv, 'y')), int(get(kv, 'height') or 0)
            row = max(0, min(7, int((y + min(h, 31) / 2) // 31)))
            put(kv, 'y', y + row)
            if get(kv, 'buttontype') or n == 'total_hover_target':
                put(kv, 'height', 32)
        # and a row's cell art sits a pixel above the row: both halves of every cell
        if g in ('i474_175,0', 'miscgraphics,4'):
            put(kv, 'y', int(get(kv, 'y')) - 1)
        if get(kv, 'type') == 'graphic' and get(kv, 'width') == '25':
            put(kv, 'graphic', icon(g))
        if get(kv, 'layer') == 'com_42' and get(kv, 'type') == 'rect':
            continue  # 474's square box; OSRS's chamfered black cell replaces it below
        if n == 'total_label':
            put(kv, 'x', 6); put(kv, 'y', 7); put(kv, 'font', 'p11_full'); put(kv, 'text', 'Total level:')
        if get(kv, 'script1op1') == 'op9':
            put(kv, 'x', 6); put(kv, 'y', 17); put(kv, 'font', 'p11_full')
        # the hover: one line, the total experience, at the foot of the panel where the others' boxes end
        if n in ('com_65', 'total_hover_qp_label', 'com_67'):
            continue
        if n == 'total_hover_box':
            put(kv, 'y', 21); put(kv, 'height', 18)
        if n == 'total_hover_label':
            put(kv, 'y', 23); put(kv, 'width', 170); put(kv, 'text', 'Total XP:')
            kv.insert(4, ['clientcode', '329'])
        out.append((n, kv, comments))
        if n == 'com_42':
            # the total's cell: OSRS's black cell with the stone rim, in two halves like every cell
            # (183 left, 184 right), where 474 had nested rects
            for part, x, sid in (('l', 0, 183), ('r', 30, 184)):
                out.append(('total_cell_%s' % part, [['layer', 'com_42'], ['type', 'graphic'], ['x', x], ['y', -1],
                                                    ['width', 36], ['height', 36],
                                                    ['graphic', write_sprite('osrsstat_total_%s' % part, cache.sprite(sid))]],
                            []))

    # EXACT PLACES, measured off a pre-Sailing screenshot at 2x (every figure below is where the thing
    # is there, found by matching its own pixels). The levels follow one rule, which 474 kept only
    # roughly: the level at 33,5 in each 63x32 cell and the base level at 45,17. The icons OSRS placed
    # one by one (its script took an offset per skill), so they are a table: where 474's differs.
    ICON_AT = {'com_49': (132, 5), 'com_52': (132, 37), 'com_55': (131, 69), 'com_58': (133, 101),
               'com_61': (132, 133), 'com_64': (132, 165), 'com_54': (68, 69),
               'construction_icon': (4, 229), 'hunter_icon': (67, 229)}
    blocks_by = {n: kv for n, kv, _ in out}

    def origin(n):
        kv = blocks_by[n]
        x, y = int(get(kv, 'x') or 0), int(get(kv, 'y') or 0)
        if get(kv, 'layer'):
            px, py = origin(get(kv, 'layer'))
            x, y = x + px, y + py
        return x, y

    for n, kv, _ in out:
        parent = get(kv, 'layer')
        if parent and get(blocks_by[parent], 'hide') == 'yes':
            continue
        ax, ay = origin(n)
        px, py = (ax - int(get(kv, 'x') or 0), ay - int(get(kv, 'y') or 0))
        op = get(kv, 'script1op1') or ''
        target = None
        if n in ICON_AT:
            target = ICON_AT[n]
        elif op.startswith('stat_level,') or op.startswith('stat_base_level,'):
            col, row = max(0, min(2, round((ax - 33) / 63))), max(0, min(7, round((ay - 5) / 32)))
            base = op.startswith('stat_base_level,')
            target = (33 + 63 * col + (12 if base else 0), 5 + 32 * row + (12 if base else 0))
        if target:
            put(kv, 'x', target[0] - px); put(kv, 'y', target[1] - py)

    lines = [MARK + ' (its icons, the total\'s text and hover), by LostCityServer',
             '// tools/models/genstatsosrs.py; the rest is 474\'s, which OSRS\'s was. Rerun genxplock.py after editing.']
    lines += [l for l in head if not l.startswith('//')]
    for n, kv, comments in out:
        lines.append('')
        lines.append('[%s]' % n)
        lines += ['%s=%s' % (k, v) for k, v in kv]
        lines += comments  # a comment above the next block is read as the tail of this one
    with open(PATH, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('stats.if re-skinned; icons replaced: %s' % (' '.join(sorted(v for k, v in icons.items() if k != v)) or '-'))
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'genxplock.py')], cwd=CONTENT)
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), 'stats'])


if __name__ == '__main__':
    main()
