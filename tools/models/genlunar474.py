#!/usr/bin/env python3
"""Build the Lunar spellbook, content's lunar_magic interface, from 474's (interface 430).

    python tools/models/genlunar474.py "caches/474 cache"

The normal and Ancient books had 377 panels to keep, and portmagic474.py only moved and repainted
them. There is no 377 Lunar panel - Lunar Diplomacy is 2006 - so this one is written whole, in the
shape those two ended up in, so the three books behave the same:

  the grid      474's own: forty 24x24 icons where 430 puts them, the tab's full 190x261.
  the spells    NOT written by hand. 474 hangs every icon on client script 6 with the spell's
                whole description as its arguments - both sprites, the level, the name, the text
                and up to four (rune, count) pairs - and that call is read here. So the spell list
                is the cache's, which is what decides what the book has, and nothing about a spell
                is typed twice. The one thing added by hand is each spell's content name (SPELLS),
                which the server's triggers use and the cache has no word for.
  the icons     the lit one and the dark one, as the arguments give them (dark = lit + 50, as on
                the other books). graphic is the dark one and activegraphic the lit one, and the
                button's client scripts decide which shows, exactly as they do on magic.if.
  the scripts   one per rune - its count must clear the cost less one - and the Magic level last.
                A rune's ops are COPIED from the spell on magic.if that counts the same rune, so an
                earth count here reads every combination rune and staff that one does, and the
                pouch mirror with it. Astral is the rune nothing else counts: its ops are the
                inventory and the pouch mirror, and no staff supplies it. After a run,
                genstaffruneops.py --check and genpouchruneops.py --check have nothing to add.
  the panels    what the other books show on hover: the level and name, what it does (wrapped to
                the panel with PixFont's own widths, content/tools/ifrender.py), and the runes
                with a count that goes green when you have them. Placed under the spell's row in
                the top half of the book and over it in the bottom half, as portmagic474 does.

Spells that pick a target: 474 says which kind with the click mask (bit 12 npcs, 13 locs, 14
players, 15 held objs). Five spells are offered both npcs and players there; content's only takes
players for the four that only work on players, and only npcs for Monster Examine - an
offer that can only ever say "you can't" is a dead click.

    python tools/models/genlunar474.py "caches/474 cache"      # writes lunar_magic.if and its sprites
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')
IFNAME = 'lunar_magic'
GID = 430

# 474's name for a spell -> content's. Every spell in 430 must be here and nothing else may be.
SPELLS = {
    'Lunar Home Teleport': 'lunar_home_teleport', 'Bake Pie': 'bake_pie', 'Cure Plant': 'cure_plant',
    'Monster Examine': 'monster_examine', 'NPC Contact': 'npc_contact', 'Cure Other': 'cure_other',
    'Humidify': 'humidify', 'Moonclan Teleport': 'moonclan_teleport', 'Tele Group Moonclan': 'tele_group_moonclan',
    'Cure Me': 'cure_me', 'Ourania Teleport': 'ourania_teleport', 'Hunter Kit': 'hunter_kit',
    'Waterbirth Teleport': 'waterbirth_teleport', 'Tele Group Waterbirth': 'tele_group_waterbirth',
    'Cure Group': 'cure_group', 'Stat Spy': 'stat_spy', 'Barbarian Teleport': 'barbarian_teleport',
    'Tele Group Barbarian': 'tele_group_barbarian', 'Superglass Make': 'superglass_make',
    'Khazard Teleport': 'khazard_teleport', 'Tele Group Khazard': 'tele_group_khazard', 'Dream': 'dream',
    'String Jewellery': 'string_jewellery', 'Stat Restore Pot Share': 'stat_restore_pot_share',
    'Magic Imbue': 'magic_imbue', 'Fertile Soil': 'fertile_soil', 'Boost Potion Share': 'boost_potion_share',
    'Fishing Guild Teleport': 'fishing_guild_teleport', 'Tele Group Fishing Guild': 'tele_group_fishing_guild',
    'Plank Make': 'plank_make', 'Catherby Teleport': 'catherby_teleport', 'Tele Group Catherby': 'tele_group_catherby',
    'Ice Plateau Teleport': 'ice_plateau_teleport', 'Tele Group Ice Plateau': 'tele_group_ice_plateau',
    'Energy Transfer': 'energy_transfer', 'Heal Other': 'heal_other', 'Vengeance Other': 'vengeance_other',
    'Vengeance': 'vengeance', 'Heal Group': 'heal_group', 'Spellbook Swap': 'spellbook_swap',
}
# the kinds of target content's button offers, where 474's click mask offers more than will work
TARGET_OVERRIDE = {'monster_examine': 'npc', 'cure_other': 'player', 'stat_spy': 'player',
                   'energy_transfer': 'player', 'heal_other': 'player', 'vengeance_other': 'player'}
# 474's rune obj ids
RUNES = {554: 'firerune', 555: 'waterrune', 556: 'airrune', 557: 'earthrune', 558: 'mindrune',
         559: 'bodyrune', 560: 'deathrune', 561: 'naturerune', 562: 'chaosrune', 563: 'lawrune',
         564: 'cosmicrune', 565: 'bloodrune', 566: 'soulrune', 9075: 'astralrune'}
# the text the normal book's Home Teleport panel carries (portmagic474.NEW): home is Edgeville here
HOME_DESC = 'Teleports you to Edgeville without\\nrunes, once every 30 minutes'
HEADER = ("// GENERATED by LostCityServer tools/models/genlunar474.py from 474's Lunar spellbook (interface 430).\n"
          "// Edit the generator and rerun it; then genstaffruneops.py and genpouchruneops.py, whose --check it passes.")
# panel runes, by how many a spell takes: (model x, text x) - magic.if's own positions
RUNE_X = {1: [78], 2: [38, 114], 3: [26, 78, 130]}
MASK_TARGETS = [(1 << 11, 'obj'), (1 << 12, 'npc'), (1 << 13, 'loc'), (1 << 14, 'player'), (1 << 15, 'heldobj')]


def spells(cache):
    """Every spell 430 draws, in the cache's own words: [(fid, comp, args)] top to bottom."""
    out = []
    for fid, c in sorted(cache.load(GID).items()):
        if c.get('type') != 5:
            continue
        a = c.get('onLoad')
        if not a or a[0] != 6:
            raise SystemExit('430:%d is an icon without script 6 on it' % fid)
        lit, dark, level, name, desc = a[3], a[4], a[5], a[6], a[7]
        runes = [(a[i], a[i + 1]) for i in range(8, len(a) - 1, 2) if a[i] != -1]
        out.append(dict(fid=fid, x=c['x'], y=c['y'], mask=c.get('clickmask', 0), lit=lit, dark=dark,
                        level=level, title=name, desc=desc, runes=runes))
    names = {s['title'] for s in out}
    if names != set(SPELLS):
        raise SystemExit('430 and SPELLS disagree: only in 430 %s, only in SPELLS %s'
                         % (sorted(names - set(SPELLS)), sorted(set(SPELLS) - names)))
    return sorted(out, key=lambda s: (s['y'], s['x']))


def rune_ops():
    """rune -> the ops magic.if counts it with (inventory, pouch mirror, combination runes, staves):
    the longest list any script there opens with that rune's inventory count."""
    txt = open(os.path.join(CONTENT, 'scripts', 'skill_magic', 'interfaces', 'magic.if'), encoding='utf-8').read()
    ops = {}
    for block in re.split(r'\r?\n(?=\[)', txt):
        scripts = {}
        for m in re.finditer(r'^script(\d+)op(\d+)=(.*?)\s*$', block, re.M):
            scripts.setdefault(int(m.group(1)), []).append((int(m.group(2)), m.group(3)))
        for s in scripts.values():
            s = [v for _, v in sorted(s)]
            m = re.match(r'inv_count,inventory:inv,(\w+)$', s[0])
            if m and len(s) > len(ops.get(m.group(1), [])):
                ops[m.group(1)] = s
    ops['astralrune'] = ['inv_count,inventory:inv,astralrune', 'inv_count,rune_pouch_mirror:runes,astralrune']
    return ops


def wrap(text, width=170):
    from ifrender import font
    f = font('p11_full')
    lines, cur = [], ''
    for word in text.split(' '):
        trial = (cur + ' ' + word).strip()
        if cur and f.width(trial) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    if len(lines) > 2:
        raise SystemExit('%r needs %d lines and the panel has room for two' % (text, len(lines)))
    return '\\n'.join(lines)


def target_of(s, name):
    if name in TARGET_OVERRIDE:
        return TARGET_OVERRIDE[name]
    kinds = [k for bit, k in MASK_TARGETS if s['mask'] & bit]
    return ','.join(kinds)


def main():
    global CONTENT
    args = [a for a in sys.argv[1:] if not a.startswith('--content=')]
    for a in sys.argv[1:]:
        if a.startswith('--content='):
            CONTENT = os.path.abspath(a.split('=', 1)[1])
    sys.path.insert(0, os.path.join(CONTENT, 'tools'))
    from if3_474 import Cache
    from port474if import Converter
    cache = Cache(args[0])
    conv = Converter(cache, GID, IFNAME, {}, {}, 'overlay')
    ops = rune_ops()
    out = [HEADER]

    def block(name, kv):
        out.append('')
        out.append('[%s]' % name)
        out.extend('%s=%s' % (k, v) for k, v in kv)

    panels = []
    for s in spells(cache):
        name = SPELLS[s['title']]
        tip = 'tip_' + name
        target = target_of(s, name)
        kv = [('type', 'graphic'), ('x', s['x']), ('y', s['y']), ('buttontype', 'target' if target else 'normal'),
              ('width', 24), ('height', 24), ('overlayer', tip)]
        n = 0
        for rune, count in s['runes']:
            n += 1
            for i, op in enumerate(ops[RUNES[rune]], start=1):
                kv.append(('script%dop%d' % (n, i), op))
        if s['level'] > 0:
            n += 1
            kv.append(('script%dop1' % n, 'stat_level,magic'))
        for i, (rune, count) in enumerate(s['runes'], start=1):
            kv.append(('script%d' % i, 'gt,%d' % (count - 1)))
        if s['level'] > 0:
            kv.append(('script%d' % n, 'gt,%d' % (s['level'] - 1)))
            kv += [('graphic', conv.sprite(s['dark'])), ('activegraphic', conv.sprite(s['lit']))]
        else:
            # Home Teleport needs nothing, so it is always lit - which is how 474 draws it
            kv.append(('graphic', conv.sprite(s['lit'])))
        if target:
            kv += [('actionverb', 'Cast on'), ('actiontarget', target), ('action', s['title'])]
        else:
            kv.append(('option', 'Cast @gre@' + s['title']))
        block(name, kv)

        # the hover panel
        y = s['y'] + 26 if s['y'] < 130 else max(0, s['y'] - 76 - 2)
        p = [(tip, [('type', 'layer'), ('x', 4), ('y', y), ('width', 182), ('height', 76), ('hide', 'yes')])]
        for i, (fx, fy, fw, fh, col, fill) in enumerate([(1, 3, 178, 72, '0x726451', False), (2, 4, 176, 70, '0x726451', False),
                                                         (2, 4, 177, 71, '0x2E2B23', False), (3, 5, 174, 68, None, True)]):
            f = [('layer', tip), ('type', 'rect'), ('x', fx), ('y', fy), ('width', fw), ('height', fh)]
            f += [('fill', 'yes')] if fill else []
            f += [('colour', col)] if col else []
            p.append(('%s_frame%d' % (tip, i), f))
        p.append(('%s_title' % tip, [('layer', tip), ('type', 'text'), ('x', 3), ('y', 4), ('width', 174), ('height', 14),
                                     ('center', 'yes'), ('font', 'p12_full'), ('shadowed', 'yes'),
                                     ('text', 'Level %d : %s' % (s['level'], s['title'])), ('colour', '0xFFF000')]))
        desc = HOME_DESC if name == 'lunar_home_teleport' else wrap(s['desc'])
        p.append(('%s_desc' % tip, [('layer', tip), ('type', 'text'), ('x', 3), ('y', 17), ('width', 174), ('height', 30),
                                    ('center', 'yes'), ('font', 'p11_full'), ('shadowed', 'yes'),
                                    ('text', desc), ('colour', '0x6B6F33')]))
        for i, ((rune, count), x) in enumerate(zip(s['runes'], RUNE_X.get(len(s['runes']), []))):
            r = RUNES[rune]
            p.append(('%s_rune%d' % (tip, i), [('layer', tip), ('type', 'model'), ('x', x), ('y', 35), ('width', 28),
                                               ('height', 28), ('model', 'obj_' + r), ('zoom', 900), ('xan', 512), ('yan', 1024)]))
            t = [('layer', tip), ('type', 'text'), ('x', x + 1), ('y', 62), ('width', 26), ('height', 11)]
            t += [('script1op%d' % j, op) for j, op in enumerate(ops[r], start=1)]
            t += [('script1', 'gt,%d' % (count - 1)), ('center', 'yes'), ('font', 'p11_full'), ('shadowed', 'yes'),
                  ('text', '%%1/%d' % count), ('colour', '0xC00000'), ('activecolour', '0x00C000')]
            p.append(('%s_count%d' % (tip, i), t))
        if len(s['runes']) > 3:
            raise SystemExit('%s takes %d runes; the panel has room for three' % (s['title'], len(s['runes'])))
        panels += p

    # the grid draws first and every panel over it
    for name, kv in panels:
        block(name, kv)
    path = os.path.join(CONTENT, 'scripts', 'skill_magic', 'interfaces', IFNAME + '.if')
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(out) + '\n')
    new = conv.write_sprites(os.path.join(CONTENT, 'sprites'))
    print('%s: %d spells, %d new sprites' % (os.path.relpath(path, CONTENT), len(SPELLS), len(new)))
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), IFNAME])


if __name__ == '__main__':
    main()
