#!/usr/bin/env python3
"""Write the two windows the Lunar spellbook's spells open, from 474's: Monster Examine (474 interface
522, content's monster_examine.if) and NPC Contact (474 interface 429, npc_contact.if).

    python tools/models/genlunarif474.py "caches/474 cache" [--content=<content checkout>]

Both are new-format interfaces, filled in by client scripts this client does not have, so each is
written here component by component from the cache's own positions, fonts and colours, and what
474's scripts did at run time is done by the server (skill_magic/scripts/lunar/lunar_insight.rs2
and lunar_contact.rs2).

MONSTER EXAMINE is 522: a 190-wide panel for the side tab - the Monster Examine icon (sprite 838)
beside the monster's name in orange, four lines of black quill text under it, and a close X (831,
lit 832). It has no background of its own: 474 laid it over the tab's stone, and so does this client
(Client.drawSidebar plots invback under a side modal), so it is opened with if_openside and nothing
has to put the spellbook back afterwards. The lit X is a hidden layer shown while the mouse is over
the X, as on house_options.if. The script wraps the name to the name box's width and moves the box
so the name, one line or three, sits beside the icon's middle; the last line moves up five pixels
when it needs four quill lines, so the fourth clears the bottom of the tab.

NPC CONTACT is 429, "Choose a character": 474's stone frame (sprites 297, 172, 173, 310-315, which
are this build's tradebacking, steelborder and miscgraphics), its close X (535, lit 536) and twelve
heads, each a model over a name in orange that brightens under the mouse. Every name and head is a
button in 474; here each cell has one click box over the head and the name (474's hidden layers
98-109 are exactly those boxes), and the box's hover layer is the brightened name - so one trigger
per contact, [if_button,npc_contact:<key>].

  the contacts  Honest Jimmy, Bert the Sandman, Lanthus and Cyrisus belong to minigames and quests
                this build does not have, so they are not written; the eight left (the keys in
                CELLS) keep 474's order and 474's cells, four to a row in the middle four columns of
                474's six, so neither row has a hole in it - each row moved the few pixels that put
                it under the title's middle. The cache's menu op for Vannaka reads "Vannake";
                the label under him says Vannaka, and so does the op here.
  the heads     474 models 16800-24991, copied from the cache byte for byte - they are the old
                model format, which this client reads - to models/com/com_npc_contact_<key>.ob2 and
                registered in pack/model.pack. 474 drew a new-format model component two ways this
                client's cannot: rolled by its zan, and lifted by half its height (OSRS's
                calculateBoundsCylinder + draw, y offset += height / 2). The lift is made good by
                moving the component down by what it projects to; the roll has nowhere to go in a
                .if (Component has xan and yan only), so a head 474 rolls is written ALREADY rolled,
                re-encoded with osrs2ob2's writer and checked by its round trip. The others are the
                cache's bytes untouched.
"""
import math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')

EXAMINE_GID = 522
CONTACT_GID = 429
# 474 interface 429's label colour under the mouse (its onMouseOver script 45's argument)
ORANGE_LIT = '0xF1B770'

# 474's twelve, in its order: (head fid, label fid, cell fid, content key or None for left out)
CELLS = [(74, 86, 98, None), (75, 87, 99, None), (76, 88, 100, 'ghrim'), (77, 89, 101, 'turael'),
         (78, 90, 102, None), (79, 91, 103, 'mazchna'), (80, 92, 104, 'duradel'), (81, 93, 105, 'vannaka'),
         (82, 94, 106, 'murphy'), (83, 95, 107, 'chaeldar'), (84, 96, 108, None), (85, 97, 109, 'random')]
# the menu op, where the cache's is wrong
OPS = {'vannaka': 'Vannaka'}
PER_ROW = 4
FIRST_COL = 1   # of 474's six columns (0-based): the middle four


class If:
    def __init__(self, head):
        self.lines = list(head)

    def com(self, name, kv):
        self.lines.append('')
        self.lines.append('[%s]' % name)
        for k, v in kv:
            self.lines.append('%s=%s' % (k, v))

    def write(self, path):
        with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write('\n'.join(self.lines) + '\n')


def colour(c):
    return '0x%06X' % (c & 0xFFFFFF)


def converter(cache, gid, ifname, root):
    """port474if's Converter, looking sprites up in the content being written to."""
    from port474if import Converter, content_sprite_index
    conv = Converter(cache, gid, ifname, {}, {}, root)
    conv.index = content_sprite_index(os.path.join(CONTENT, 'sprites'))
    return conv


def close_button(f, conv, x_fid, layer_fid, lit_fid=None, lit_sprite=None):
    """474's X and its lit copy: the X is the close button and shows a hidden layer holding the lit
    one while the mouse is over it; the lit one is a close button too, since this client never lets
    you click through to a component under a hidden layer (house_options.if, smithing.if)."""
    c = conv.comps
    x, lay = c[x_fid], c[layer_fid]
    if lit_fid is not None:
        lit = c[lit_fid]
        lx, ly, sprite = lit['x'], lit['y'], lit['sprite']
    else:
        lx, ly, sprite = x['x'] - lay['x'], x['y'] - lay['y'], lit_sprite
    f.com('close_frame', [('type', 'graphic'), ('x', x['x']), ('y', x['y']), ('overlayer', 'close_layer'),
                          ('buttontype', 'close'), ('width', x['width']), ('height', x['height']),
                          ('graphic', conv.sprite(x['sprite']))])
    f.com('close_layer', [('type', 'layer'), ('x', lay['x']), ('y', lay['y']), ('width', lay['width']),
                          ('height', lay['height']), ('hide', 'yes')])
    f.com('close', [('type', 'graphic'), ('layer', 'close_layer'), ('x', lx), ('y', ly), ('buttontype', 'close'),
                    ('width', x['width']), ('height', x['height']), ('graphic', conv.sprite(sprite))])


# ---------------------------------------------------------------- Monster Examine (522)

def monster_examine(cache):
    conv = converter(cache, EXAMINE_GID, 'monster_examine', 'overlay')
    c = conv.comps
    f = If(['// 474\'s Monster Examine (474 interface 522), GENERATED by LostCityServer tools/models/genlunarif474.py -',
            '// regenerate it rather than editing by hand. Opened as a side modal over the tab\'s stone and',
            '// filled in by skill_magic/scripts/lunar/lunar_insight.rs2.',
            'type=overlay'])
    icon = c[5]
    f.com('icon', [('type', 'graphic'), ('x', icon['x']), ('y', icon['y']), ('width', icon['width']),
                   ('height', icon['height']), ('graphic', conv.sprite(icon['sprite']))])
    t = c[0]
    f.com('name', [('type', 'text'), ('x', t['x']), ('y', t['y']), ('width', t['width']), ('height', t['height']),
                   ('center', 'yes'), ('font', 'q8_full'), ('text', t['text']), ('colour', colour(t['colour']))])
    for i in range(1, 5):
        t = c[i]
        f.com('line%d' % i, [('type', 'text'), ('x', t['x']), ('y', t['y']), ('width', t['width']),
                             ('height', t['height']), ('center', 'yes'), ('font', 'q8_full'), ('text', t['text']),
                             ('colour', colour(t.get('colour', 0)))])
    # 474's hover script swaps 831 for 832; its hidden layer 7 is where the lit one goes
    close_button(f, conv, 6, 7, lit_sprite=c[6]['onMouseOver'][2])
    path = os.path.join(CONTENT, 'scripts', 'skill_magic', 'interfaces', 'monster_examine.if')
    f.write(path)
    return conv, path


# ---------------------------------------------------------------- NPC Contact (429)

def model_name(key):
    return 'com_npc_contact_%s' % key


def head_model(cache, model, zan):
    """The cache's bytes, rolled by zan when 474 rolled it (see the docstring)."""
    data = cache.store.read(7, model)
    if data[-2:] == b'\xff\xff' or (len(data) > 1 and data[-1] in (0xFD, 0xFE) and data[-2] == 0xFF):
        raise SystemExit('474 model %d is new-format; this client cannot read it' % model)
    if not zan:
        return data
    from osrs2ob2 import parse_ob2, encode, roundtrip
    m = parse_ob2(data)
    # Model.method380's roll, with Pix3D's own sine table, applied once to the vertices instead of
    # at every draw
    from ob2render import SIN, COS
    s, co = int(SIN[zan & 2047]), int(COS[zan & 2047])
    vx, vy = [], []
    for x, y in zip(m['vx'], m['vy']):
        vx.append((s * y + co * x) >> 16)
        vy.append((co * y - s * x) >> 16)
    m['vx'], m['vy'] = vx, vy
    out = encode(m)
    ok, why = roundtrip(out, m)
    if not ok:
        raise SystemExit('474 model %d rolled by %d does not round-trip: %s' % (model, zan, why))
    return out


def model_height(data):
    """Model.field1709 / OSRS Model.height: how far the model reaches above its origin (max -y)."""
    from osrs2ob2 import parse_ob2
    return max(0, max(-y for y in parse_ob2(data)['vy']))


def lift(height, zoom, xan):
    """Screen pixels that 474's height / 2 lift moves a model down: added to the camera-space y before
    the pitch, at a depth of about zoom (Client.drawInterface's type 6 arithmetic)."""
    a = xan * math.pi / 1024
    dy = height // 2
    return int(round(dy * math.cos(a) * 512 / (zoom + dy * math.sin(a))))


def register_models(names):
    """Append to pack/model.pack, reading it fresh (other generators may have written it since)."""
    from animconv474 import pack_append
    assigned, _ = pack_append(os.path.join(CONTENT, 'pack', 'model.pack'), names)
    return assigned


def npc_contact(cache):
    conv = converter(cache, CONTACT_GID, 'npc_contact', 'layer')
    c = conv.comps
    f = If(['// 474\'s NPC Contact window (474 interface 429), GENERATED by LostCityServer tools/models/genlunarif474.py -',
            '// regenerate it rather than editing by hand. Opened by the spell; each contact\'s click box is an',
            '// [if_button,npc_contact:<key>] in skill_magic/scripts/lunar/lunar_contact.rs2.',
            'type=layer'])
    for fid in range(0, 74):
        conv.names[fid] = 'frame%d' % fid
        for n, kv in conv.blocks(fid, c[fid]):
            f.com(n, [(k, v) for k, v in kv if not k.startswith('_')])
    t = c[113]
    f.com('title', [('type', 'text'), ('x', t['x']), ('y', t['y']), ('width', t['width']), ('height', t['height']),
                    ('center', 'yes'), ('font', 'b12_full'), ('shadowed', 'yes'), ('text', t['text']),
                    ('colour', colour(t['colour']))])

    kept = [cell for cell in CELLS if cell[3]]
    rows = [CELLS[:6], CELLS[6:]]
    mdir = os.path.join(CONTENT, 'models', 'com')
    os.makedirs(mdir, exist_ok=True)
    names = []
    heads = []
    # 474's middle four columns sit a few pixels left of the window's middle (its title's); each row
    # of four moves right by that much
    middle = c[113]['x'] + c[113]['width'] // 2
    shift = []
    for row in rows:
        centres = [c[s_label]['x'] + c[s_label]['width'] / 2 for _, s_label, _, _ in row[FIRST_COL:FIRST_COL + PER_ROW]]
        shift.append(int(round(middle - sum(centres) / len(centres))))
    for i, (head_fid, label_fid, cell_fid, key) in enumerate(kept):
        row, col = divmod(i, PER_ROW)
        # the slot is one of 474's twelve cells: the contact's head goes where that cell's head is and
        # its name where that cell's name is, centred on it as 474 centres every name
        s_head, s_label, s_cell, _ = rows[row][FIRST_COL + col]
        sh, sl, sc = dict(c[s_head]), dict(c[s_label]), c[s_cell]
        sh['x'] += shift[row]
        sl['x'] += shift[row]
        h, lab = c[head_fid], c[label_fid]
        data = head_model(cache, h['model'], h.get('zan', 0))
        open(os.path.join(mdir, model_name(key) + '.ob2'), 'wb').write(data)
        names.append(model_name(key))
        down = lift(model_height(cache.store.read(7, h['model'])), h['zoom'], h.get('xan', 0))
        f.com('%s_head' % key, [('type', 'model'), ('x', sh['x']), ('y', sh['y'] + down),
                                ('width', h['width']), ('height', h['height']), ('model', model_name(key)),
                                ('zoom', h['zoom']), ('xan', h.get('xan', 0)), ('yan', h.get('yan', 0))])
        text = lab['text'].replace('<br>', '\\n')
        lx = sl['x'] + sl['width'] // 2 - lab['width'] // 2
        label = [('x', lx), ('y', sl['y']), ('width', lab['width']), ('height', lab['height']),
                 ('center', 'yes'), ('font', 'p12_full'), ('shadowed', 'yes'), ('text', text)]
        f.com('%s_label' % key, [('type', 'text')] + label + [('colour', colour(lab['colour']))])
        # the click box - 474's hidden cell layer, from the top of the slot's cell to its bottom and
        # across the head and the name - last, so the mouse finds it over both; its hover layer is
        # the name again, lit
        bx = min(sh['x'], lx)
        bw = max(sh['x'] + h['width'], lx + lab['width']) - bx
        op = OPS.get(key, lab['ops'][0])
        f.com(key, [('type', 'text'), ('x', bx), ('y', sc['y']), ('overlayer', '%s_hover' % key),
                    ('buttontype', 'normal'), ('width', bw), ('height', sc['height']),
                    ('font', 'p12_full'), ('text', ''), ('option', op)])
        f.com('%s_hover' % key, [('type', 'layer'), ('x', 0), ('y', 0), ('width', 512), ('height', 334),
                                 ('hide', 'yes')])
        f.com('%s_hover_label' % key, [('type', 'text'), ('layer', '%s_hover' % key)] + label + [('colour', ORANGE_LIT)])
        heads.append((key, h['model'], h.get('zan', 0), down))
    close_button(f, conv, 110, 111, lit_fid=112)
    path = os.path.join(CONTENT, 'scripts', 'skill_magic', 'interfaces', 'npc_contact.if')
    f.write(path)
    assigned = register_models(names)
    return conv, path, heads, assigned


def main():
    global CONTENT
    args = [a for a in sys.argv[1:] if not a.startswith('--content=')]
    for a in sys.argv[1:]:
        if a.startswith('--content='):
            CONTENT = os.path.abspath(a.split('=', 1)[1])
    from if3_474 import Cache
    cache = Cache(args[0])
    new = []
    conv, path = monster_examine(cache)
    new += conv.write_sprites(os.path.join(CONTENT, 'sprites'))
    print('wrote %s' % os.path.relpath(path, CONTENT))
    conv, path, heads, assigned = npc_contact(cache)
    new += conv.write_sprites(os.path.join(CONTENT, 'sprites'))
    print('wrote %s' % os.path.relpath(path, CONTENT))
    for key, model, zan, down in heads:
        print('  %-9s 474 model %d -> %s (model.pack %d)%s, lowered %dpx for 474\'s lift'
              % (key, model, model_name(key), assigned[model_name(key)],
                 ', rolled %d' % zan if zan else ', byte for byte', down))
    print('sprites new: %s' % (' '.join(new) or '-'))
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), 'monster_examine', 'npc_contact'])


if __name__ == '__main__':
    main()
