#!/usr/bin/env python3
"""Give content's skill tab (scripts/interfaces/stats.if) pre-Sailing OSRS's art.

    python tools/models/genstatsosrs.py "caches/newest cache"

OSRS's skill tab until Sailing (2013-2025) was 474's: the same 3x8 grid of stone cells on a 63x31
pitch, the icon at the left of each, level over level with a slash between, and the total in the
last cell. What OSRS changed was the art, and a current cache still carries it: sprite 174 is a
cell's left half, 175 its right half with the slash, 176 the right half without one - the total's
cell - and the skill icons are enum 255's. (The cells today's tab draws, 187/188, and its total bar,
189-191, came with Sailing and are not used here.)

So this re-skins the 474 file rather than moving anything, and every name and place the scripts and
genxplock.py rely on stays as it is:

  - 474's left and right halves (miscgraphics,4 and i474_175) become OSRS's 174 and 175
  - an icon becomes OSRS's where OSRS's differs (Runecraft, Slayer, Farming, Hunter, Construction)
  - the total's cell, which 474 drew as nested rects, becomes 174 + 176 like the others, and says
    "Total level:" over the number in the small yellow font, as OSRS's did

It runs on the 474 layout; a second run finds no 474 art to replace and stops.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')
PATH = os.path.join(CONTENT, 'scripts', 'interfaces', 'stats.if')
SPRITES = os.path.join(CONTENT, 'sprites')
MARK = "// PRE-SAILING OSRS's art"


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
    if MARK in raw or 'miscgraphics,4' not in raw:
        raise SystemExit('stats.if has no 474 cell art to replace - is it already done?')
    head, blocks = parse(raw)

    left = write_sprite('osrsstat_cell_l', cache.sprite(174))
    right = write_sprite('osrsstat_cell_r', cache.sprite(175))
    plain = write_sprite('osrsstat_cell_rplain', cache.sprite(176))
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
        if g == 'miscgraphics,4':
            put(kv, 'graphic', left)
        elif g == 'i474_175,0':
            put(kv, 'graphic', right)
        elif get(kv, 'type') == 'graphic' and get(kv, 'width') == '25':
            put(kv, 'graphic', icon(g))
        if get(kv, 'layer') == 'com_42' and get(kv, 'type') == 'rect':
            continue  # 474's box for the total; OSRS's cell replaces it below
        if n == 'total_label':
            put(kv, 'y', 3); put(kv, 'font', 'p11_full'); put(kv, 'text', 'Total level:')
        if get(kv, 'script1op1') == 'op9':
            put(kv, 'y', 16); put(kv, 'font', 'p11_full')
        out.append((n, kv, comments))
        if n == 'com_42':
            # the total's cell, drawn first inside its layer: the left half and the plain right half,
            # where the row layers put theirs
            out.append(('total_cell_l', [['layer', 'com_42'], ['type', 'graphic'], ['x', 0], ['y', 0], ['width', 36],
                                         ['height', 36], ['graphic', left]], []))
            out.append(('total_cell_r', [['layer', 'com_42'], ['type', 'graphic'], ['x', 30], ['y', 0], ['width', 36],
                                         ['height', 36], ['graphic', plain]], []))

    lines = [MARK + ' (174 / 175 / 176 and enum 255\'s icons), by LostCityServer tools/models/genstatsosrs.py;',
             '// the layout is 474\'s, which OSRS\'s was. Rerun genxplock.py after editing.']
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
