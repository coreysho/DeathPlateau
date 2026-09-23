#!/usr/bin/env python3
"""Lay content's two spellbooks out as 474's (474 interfaces 192 and 193), keeping every spell's script.

    python tools/models/portmagic474.py "caches/474 cache"

474's spellbooks are new-format interfaces: a grid of 24x24 icons with no names at all - a spell is
known by its sprite - which a client script lit when you could cast it and captioned when you
hovered it. The content's books are the 377 ones: a scrolling grid of the same spells in a different
order, each button carrying client scripts that check your level and runes, and a panel of rune
counts that shows while you hover. Those scripts are the valuable part (tools/genstaffruneops.py and
genpouchruneops.py write them), so this keeps every component and only moves and repaints:

  the grid      no longer scrolls - 474's fills the tab - and each spell goes to its 474 slot. The
                slots are listed below in 474's row-major order, which is OSRS's 2007 spell order;
                the cache has no names, so that list is the one thing here written by hand.
  the icons     474's: the grid's own sprite is the dark one, and the lit one is always 50 lower
                (65 -> 15 Wind Strike, 399 -> 349 Teleother Lumbridge; checked by silhouette over every
                pair). graphic is the dark one and activegraphic the lit one, so the spell's existing
                level and rune scripts decide which shows, as they always did.
  the panels    each spell's hover panel moves next to its own row - under it for the top half of the
                book, over it for the bottom - which is where 474's tooltip appeared.

Spells 474 has and the content did not get buttons of their own here, named in NEW; their scripts are
in skill_magic/scripts/spells/home_teleport.rs2 and teleport_house.rs2 (and enchant_bolt, which needs
items the game does not have yet and says so).
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')

MODERN = ['home_teleport', 'wind_strike', 'confuse', 'enchant_bolt', 'water_strike', 'enchant_lvl1', 'earth_strike',
          'weaken', 'fire_strike', 'bones_to_bananas', 'wind_bolt', 'curse', 'bind', 'lowlvl_alchemy',
          'water_bolt', 'varrock_teleport', 'enchant_lvl2', 'earth_bolt', 'lumbridge_teleport', 'telekinetic_grab', 'fire_bolt',
          'falador_teleport', 'crumble_undead', 'teleport_house', 'wind_blast', 'superheat_item', 'camelot_teleport', 'water_blast',
          'enchant_lvl3', 'iban_blast', 'snare', 'magic_dart', 'ardougne_teleport', 'earth_blast', 'highlvl_alchemy',
          'water_orb', 'enchant_lvl4', 'watchtower_teleport', 'fire_blast', 'earth_orb', 'bones_to_peaches', 'saradomin_strike',
          'claws_of_guthix', 'flames_of_zamorak', 'trollheim_teleport', 'wind_wave', 'fire_orb', 'ape_atoll_teleport', 'water_wave',
          'air_orb', 'vulnerability', 'enchant_lvl5', 'earth_wave', 'enfeeble', 'teleother_lumbridge', 'fire_wave',
          'entangle', 'stun', 'charge', 'teleother_falador', 'com_531', 'enchant_lvl6', 'teleother_camelot']
ANCIENT = ['home_teleport', 'smoke_rush', 'shadow_rush', 'paddewwa_teleport', 'blood_rush', 'ice_rush', 'senntisten_teleport',
           'smoke_burst', 'shadow_burst', 'kharyrll_teleport', 'blood_burst', 'ice_burst', 'lassar_teleport', 'smoke_blitz',
           'shadow_blitz', 'dareeyak_teleport', 'blood_blitz', 'ice_blitz', 'carrallanger_teleport', 'smoke_barrage',
           'shadow_barrage', 'annakarl_teleport', 'blood_barrage', 'ice_barrage', 'ghorrock_teleport']

# spell -> (option, level, description, runes [(rune obj, count)])
NEW = {
    'home_teleport': ('Cast @gre@Home Teleport', 0, 'Teleports you to Edgeville without\\nrunes, once every 30 minutes', []),
    'teleport_house': ('Cast @gre@Teleport to House', 40, 'Teleports you to your house', [('lawrune', 1), ('earthrune', 1), ('airrune', 1)]),
    'enchant_bolt': ('Cast @gre@Enchant Crossbow Bolt', 4, 'Enchants gem-tipped\\ncrossbow bolts', []),
}
NEW_ANCIENT = {
    'home_teleport': ('Cast @gre@Edgeville Home Teleport', 0, 'Teleports you to Edgeville without\\nrunes, once every 30 minutes', []),
}


def parse_if(text):
    blocks = []
    for part in re.split(r'\n(?=\[)', text.replace('\r\n', '\n')):
        lines = [l for l in part.split('\n') if l.strip()]
        if not lines or not lines[0].startswith('['):
            if lines:
                blocks.append((None, lines))
            continue
        blocks.append((lines[0][1:-1], [list(l.split('=', 1)) for l in lines[1:] if '=' in l]))
    return blocks


def get(kv, key):
    for k, v in kv:
        if k == key:
            return v
    return None


def put(kv, key, value, after=None):
    for pair in kv:
        if pair[0] == key:
            if value is None:
                kv.remove(pair)
            else:
                pair[1] = str(value)
            return
    if value is None:
        return
    at = len(kv)
    if after:
        for i, (k, v) in enumerate(kv):
            if k == after:
                at = i + 1
    kv.insert(at, [key, str(value)])


# the foot-of-the-book box the content's panels sat on, as rects inside a panel layer (x, y, w, h,
# colour, fill): two border lines, the dark edge, and the black inside
HEADER = ('// LAID OUT AS 474\'s by LostCityServer tools/models/portmagic474.py, which moves and repaints '
          'these components in place and adds 474\'s new spells - rerun it after any generator below.')
FRAME = [(1, 3, 178, 72, '0x726451', False), (2, 4, 176, 70, '0x726451', False),
         (2, 4, 177, 71, '0x2E2B23', False), (3, 5, 174, 68, None, True)]


def port(cache, ifname, gid, slots, new, grid_layer, footer):
    from port474if import Converter
    conv = Converter(cache, gid, ifname, {}, {}, 'overlay')
    comps = cache.load(gid)
    cells = sorted([(c['y'], c['x'], c['sprite']) for f, c in comps.items() if c['type'] == 5], key=lambda t: (t[0], t[1]))
    if len(cells) != len(slots):
        raise SystemExit('%s: %d cells, %d names' % (ifname, len(cells), len(slots)))
    path = os.path.join(CONTENT, 'scripts', 'skill_magic', 'interfaces', ifname + '.if')
    blocks = parse_if(open(path, encoding='utf-8').read())
    # an earlier run's own additions go first - the new spells, their panels and every panel's
    # frame - so running this again on its own output rewrites the book rather than doubling it
    added = set(new) | {'tip_%s' % n for n in new}
    blocks = [(n, kv) for n, kv in blocks
              if not (n in added or re.sub(r'_(title|desc|frame\d|rune\d)$', '', n or '') in added
                      or re.search(r'_frame\d$', n or ''))]
    blocks = [(n, kv if n else [l for l in kv if not l.startswith(HEADER[:40])]) for n, kv in blocks]
    by = {n: kv for n, kv in blocks if n}

    # the grid's layer, if the spells sit in one, fills the tab and stops scrolling
    gx = gy = 0
    if grid_layer:
        put(by[grid_layer], 'x', 0)
        put(by[grid_layer], 'y', 0)
        put(by[grid_layer], 'width', 190)
        put(by[grid_layer], 'height', 261)
        put(by[grid_layer], 'scroll', None)

    panel_of = {}
    template = None
    for (y, x, dark), name in zip(cells, slots):
        bright = dark - 50
        if dark == 356:
            # Home Teleport is always castable, so 474's grid holds its LIT icon; the dark one is 406
            dark, bright = 406, 356
        if name in by:
            kv = by[name]
            put(kv, 'x', x - gx)
            put(kv, 'y', y - gy)
            put(kv, 'width', 24)
            put(kv, 'height', 24)
            put(kv, 'graphic', conv.sprite(dark))
            put(kv, 'activegraphic', conv.sprite(bright))
            if get(kv, 'overlayer'):
                panel_of[get(kv, 'overlayer')] = y
            template = template or kv
        else:
            option, level, desc, runes = new[name]
            kv = [['layer', grid_layer]] if grid_layer else []
            kv += [['type', 'graphic'], ['x', x - gx], ['y', y - gy], ['buttontype', 'normal'], ['width', 24], ['height', 24]]
            if name == 'teleport_house':
                # the same three runes as Lumbridge Teleport - earth, air, law, with every staff and
                # pouch alternative its scripts already know - one of each, and Magic 40
                src = by['lumbridge_teleport']
                kv += [[k, v] for k, v in src if k.startswith('script')]
                put(kv, 'script2', 'gt,0')
                put(kv, 'script4', 'gt,%d' % (level - 1))
                kv += [['graphic', conv.sprite(dark)], ['activegraphic', conv.sprite(bright)]]
            elif level > 0:
                kv += [['script1op1', 'stat_level,magic'], ['script1', 'gt,%d' % (level - 1)]]
                kv += [['graphic', conv.sprite(dark)], ['activegraphic', conv.sprite(bright)]]
            else:
                kv += [['graphic', conv.sprite(bright)]]
            kv += [['option', option]]
            # its panel, like the others: level and name, then what it does
            tip = 'tip_%s' % name
            kv.insert(len(kv) - 1, ['overlayer', tip])
            title = option.split('@gre@')[1]
            blocks.append((tip, [['type', 'layer'], ['x', 5], ['y', 0], ['width', 182], ['height', 76], ['hide', 'yes']]))
            blocks.append(('%s_title' % tip, [['layer', tip], ['type', 'text'], ['x', 3], ['y', 4], ['width', 174], ['height', 14],
                                              ['center', 'yes'], ['font', 'p12_full'], ['shadowed', 'yes'],
                                              ['text', 'Level %d : %s' % (level, title)], ['colour', '0xFFF000']]))
            blocks.append(('%s_desc' % tip, [['layer', tip], ['type', 'text'], ['x', 3], ['y', 17], ['width', 174], ['height', 30],
                                             ['center', 'yes'], ['font', 'p11_full'], ['shadowed', 'yes'],
                                             ['text', desc], ['colour', '0x6B6F33']]))
            if runes:
                # the rune row every other panel has: Lumbridge Teleport's, whose runes are these
                # three, with this spell's counts in its texts
                need = dict(runes)
                src_panel = get(by['lumbridge_teleport'], 'overlayer')
                kids = [kv2 for n2, kv2 in blocks if n2 and get(kv2, 'layer') == src_panel
                        and not re.search(r'_frame\d$', n2) and (get(kv2, 'type') == 'model' or get(kv2, 'script1op1'))]
                for i, kv2 in enumerate(kids):
                    kv2 = [[k, v] for k, v in kv2]
                    put(kv2, 'layer', tip)
                    rune = re.search(r'(\w+rune)$', get(kv2, 'model') or get(kv2, 'script1op1')).group(1).replace('obj_', '')
                    if rune not in need:
                        raise SystemExit('%s: Lumbridge Teleport has %s, which %s does not use' % (ifname, rune, name))
                    if get(kv2, 'type') == 'text':
                        put(kv2, 'script1', 'gt,%d' % (need[rune] - 1))
                        put(kv2, 'text', '%%1/%d' % need[rune])
                    blocks.append(('%s_rune%d' % (tip, i), kv2))
            by[tip] = next(kv for n, kv in blocks if n == tip)
            panel_of[tip] = y
            blocks.append((name, kv))
            by[name] = kv

    # 474 has no box at the foot of the book; the content's panels were drawn over one. It is hidden,
    # and every panel carries the same frame itself, so it reads wherever it appears
    put(by[footer], 'hide', 'yes')
    # the frame goes in front of the panel's first child, whichever order the file is in by now, so the
    # filled rect is under the text and not over it
    def frame(p):
        return [('%s_frame%d' % (p, i), [['layer', p], ['type', 'rect'], ['x', fx], ['y', fy], ['width', fw],
                                         ['height', fh]] + ([['fill', 'yes']] if fill else []) +
                 ([['colour', col]] if col else []))
                for i, (fx, fy, fw, fh, col, fill) in enumerate(FRAME)]
    framed, done = [], set()
    for n, kv in blocks:
        p = get(kv, 'layer') if n else None
        if p in panel_of and p not in done:
            framed += frame(p)
            done.add(p)
        framed.append((n, kv))
    for p in panel_of:
        if p not in done:
            framed += frame(p)
    blocks = framed

    # titles too long for the panel in p12 drop to p11 (iffit.py)
    from iffit import fit_titles
    fit_titles(blocks, get, put)

    # each panel next to its spell's row, as 474's tooltip was
    for panel, y in panel_of.items():
        kv = by[panel]
        h = int(get(kv, 'height') or 76)
        put(kv, 'x', 4)
        put(kv, 'y', y + 26 if y < 130 else max(0, y - h - 2))

    # the grid draws first and the panels over it: every top-level panel after the grid
    names = [n for n, kv in blocks if n]
    top_panels = [n for n in panel_of if get(by[n], 'layer') is None]
    head = [(n, kv) for n, kv in blocks if n is None]
    body = [(n, kv) for n, kv in blocks if n and n not in top_panels]
    panels = [(n, kv) for n, kv in blocks if n in top_panels]
    out = []
    for n, kv in head:
        out += kv
    out.insert(0, HEADER)
    for n, kv in body + panels:
        out.append('')
        out.append('[%s]' % n)
        out += ['%s=%s' % (k, v) for k, v in kv]
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(out) + '\n')
    new_sprites = conv.write_sprites(os.path.join(CONTENT, 'sprites'))
    return path, new_sprites


def port_picker(cache):
    """The staff's autocast picker (staff_spells.if) is 474 interface 319 component for component, in
    the same places; 474 only repainted its sixteen spells with the new icons. So does this, joining
    button to button by position and refusing if any has moved."""
    from port474if import Converter
    conv = Converter(cache, 319, 'staff_spells', {}, {}, 'overlay')
    theirs = [(c['x'], c['y'], c['graphic'], c['activegraphic']) for f, c in sorted(conv.comps.items())
              if c.get('buttontype') and c.get('graphic') is not None]
    path = os.path.join(CONTENT, 'scripts', 'skill_combat', 'interfaces', 'magic', 'staff_spells.if')
    blocks = parse_if(open(path, encoding='utf-8').read())
    ours = [kv for n, kv in blocks if n and get(kv, 'buttontype') and re.match(r'(magicoff|i474_)', get(kv, 'graphic') or '')]
    if len(ours) != len(theirs):
        raise SystemExit('staff_spells: %d spell buttons, 474 has %d' % (len(ours), len(theirs)))
    for kv, (x, y, dark, lit) in zip(ours, theirs):
        if (int(get(kv, 'x')), int(get(kv, 'y'))) != (x, y):
            raise SystemExit('staff_spells: a button at %s,%s where 474 has one at %d,%d' % (get(kv, 'x'), get(kv, 'y'), x, y))
        put(kv, 'graphic', conv.sprite(dark))
        put(kv, 'activegraphic', conv.sprite(lit))
    out = []
    for n, kv in blocks:
        if n is None:
            out += kv
            continue
        out.append('')
        out.append('[%s]' % n)
        out += ['%s=%s' % (k, v) for k, v in kv]
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(out).lstrip('\n') + '\n')
    return path, conv.write_sprites(os.path.join(CONTENT, 'sprites'))


def main():
    global CONTENT
    args = [a for a in sys.argv[1:] if not a.startswith('--content=')]
    for a in sys.argv[1:]:
        if a.startswith('--content='):
            CONTENT = os.path.abspath(a.split('=', 1)[1])
    sys.path.insert(0, os.path.join(CONTENT, 'tools'))
    from if3_474 import Cache
    cache = Cache(args[0])
    path, sprites = port_picker(cache)
    print('staff_spells: %s (%d new sprites)' % (os.path.relpath(path, CONTENT), len(sprites)))
    for ifname, gid, slots, new, layer, footer in (('magic', 192, MODERN, NEW, 'com_510', 'com_42'),
                                                   ('ancient_magic', 193, ANCIENT, NEW_ANCIENT, None, 'com_0')):
        path, sprites = port(cache, ifname, gid, slots, new, layer, footer)
        print('%s: %s (%d new sprites)' % (ifname, os.path.relpath(path, CONTENT), len(sprites)))
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), 'magic', 'ancient_magic'])


if __name__ == '__main__':
    main()
