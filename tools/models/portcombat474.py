#!/usr/bin/env python3
"""Port the combat-options tabs to 474's (474 interfaces 75-93), keeping every name the scripts use.

    python tools/models/portcombat474.py "caches/474 cache"            # all of them
    python tools/models/portcombat474.py "caches/474 cache" combat_axe

One combat tab per weapon category, fourteen of them the same shape, so this is one pass rather than
fourteen hand merges. For each, port474if.py converts the 474 interface and then the parts the
scripts know by name are given those names, found by WHAT THEY ARE rather than where they sit:

  style buttons   a graphic whose client script is pushvar,com_mode eq N takes the content's name
                  for the button with the same N - axe0 is still axe0, so player_attackstyles.rs2's
                  [if_button,combat_axe:axe0] ~set_attackstyle(0) still means Chop
  name            the text at the top, which 474 fills with the weapon's name - the content's
                  if_settext(<tab>:name, oc_name) already does exactly that
  specbar_layer   the layer holding the "Use Special Attack" rect, and that rect is specbar, so
                  specwep.rs2's handlers and ~weapon_category_tab_attack's if_sethide still work
  auto_retaliate  the new "Auto Retaliate" button 474 put on every combat tab; its handler calls
                  ~toggle_auto_retaliate (skill_combat/scripts/player/auto_retaliate_button.rs2)

and one part is kept from the content rather than taken from 474: the special attack ENERGY BAR.
474 draws it with models 18554-18564, which this build does not have; the content draws the same
bar with its own com_i3 / com_i4 segments. Those are kept, with their names, scripts and model
settings, moved into 474's bar frame.

474 has no weapon preview (the 377 tab showed the weapon's model); the tab's title is the weapon's
name instead. ~weapon_category_tab_attack no longer takes a preview component.

Tabs with no 474 twin - combat_powered_staff - and the staff tab, whose 474 form (90) carries the
autocast list, are not done here.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')

TABS = {
    'combat_axe': 75, 'combat_blunt': 76, 'combat_bow': 77, 'combat_claw': 78, 'combat_crossbow': 79,
    'combat_hacksword': 81, 'combat_heavysword': 82, 'combat_pickaxe': 83, 'combat_scythe': 86,
    'combat_spear': 87, 'combat_spiked': 88, 'combat_stabsword': 89, 'combat_thrown': 91,
    'combat_unarmed': 92, 'combat_whip': 93,
    # the trident's tab (custom, 2026-09-21) was built from the bow's in 377, and is again from 474's
    'combat_powered_staff': 77,
    # Hunter's two weapons (2026-09-25), started as copies of combat_thrown.if - 474 draws both exactly as
    # the thrown tab: the salamander's Scorch/Flare/Blaze and the chinchompa's Short/Medium/Long fuse
    'combat_salamander': 474, 'combat_chinchompa': 475,
}

# combat_powered_staff: the bow's three buttons with OSRS's powered-staff styles - Accurate,
# Accurate, Longrange, all magic - and the staff tab's icons (Bash, Pound, Focus in 474 interface 90)
POWERED_TEXT = {'Rapid': 'Accurate', r'(Accurate)\n(Ranged XP)': r'(Accurate)\n(Magic XP)',
                r'(Rapid)\n(Ranged XP)': r'(Accurate)\n(Magic XP)',
                r'(Longrange)\n(Ranged XP)\n(Defence XP)': r'(Longrange)\n(Magic XP)\n(Defence XP)'}
POWERED_ICONS = {'i474_268,0': 'i474_266,0', 'i474_269,0': 'i474_267,0', 'i474_270,0': 'i474_252,0'}


def find_if(name):
    for base, dirs, files in os.walk(os.path.join(CONTENT, 'scripts')):
        if name + '.if' in files:
            return os.path.join(base, name + '.if')
    raise SystemExit('%s.if not found' % name)


def parse_if(text):
    """[(name, [(k, v)])] in file order."""
    blocks = []
    for part in re.split(r'\n(?=\[)', text.replace('\r\n', '\n')):
        lines = [l for l in part.split('\n') if l.strip()]
        if not lines or not lines[0].startswith('['):
            continue
        kv = [tuple(l.split('=', 1)) for l in lines[1:] if '=' in l and not l.startswith('//')]
        blocks.append((lines[0][1:-1], kv))
    return blocks


def get(kv, key):
    for k, v in kv:
        if k == key:
            return v
    return None


def port(cache, ifname):
    from port474if import Converter
    gid = TABS[ifname]
    path = find_if(ifname)
    old = parse_if(open(path, encoding='utf-8').read())

    # the content's style buttons, by the com_mode value each one lights on
    style_names = {}
    for name, kv in old:
        if get(kv, 'script1op1') == 'pushvar,com_mode' and get(kv, 'type') == 'graphic':
            style_names[int(get(kv, 'script1').split(',')[1])] = name
    energy = [(name, kv) for name, kv in old if get(kv, 'type') == 'model' and get(kv, 'layer') == 'specbar_layer']

    comps = cache.load(gid)
    names = {}
    spec_layer = None
    for fid, c in comps.items():
        scripts = c.get('scripts') or []
        comps_ = c.get('comparators') or []
        if c['type'] == 5 and scripts and scripts[0][:2] == [5, 43] and comps_:
            mode = comps_[0][1]
            if mode in style_names:
                names[fid] = style_names[mode]
        if c['type'] == 3 and 'Special Attack' in (c.get('option') or ''):
            names[fid] = 'specbar'
            spec_layer = c['parent']
        if c['type'] == 5 and c.get('option') == 'Auto Retaliate':
            names[fid] = 'auto_retaliate'
        if c['type'] == 4 and c.get('text') == '%1' and c['y'] < 10:
            names[fid] = 'name'
        if c['type'] == 4 and 'Combat Lvl' in (c.get('text') or ''):
            names[fid] = 'combat_level'
    if spec_layer is not None:
        names[spec_layer] = 'specbar_layer'
    missing = sorted(set(style_names.values()) - set(names.values()))
    if missing:
        raise SystemExit('%s: no 474 button for %s' % (ifname, ', '.join(missing)))

    conv = Converter(cache, gid, ifname, names, {}, 'overlay')
    out = parse_if(conv.convert())

    # the energy bar: 474's model segments out, the content's in (474 puts its bar 1 right, 1 down)
    if spec_layer is not None and energy:
        out = [(n, kv) for n, kv in out if not (get(kv, 'type') == 'model' and get(kv, 'layer') == 'specbar_layer')]
        at = next(i for i, (n, kv) in enumerate(out) if n == 'specbar') + 1
        # after the bar's frame graphic, so the segments draw on top of it
        while at < len(out) and get(out[at][1], 'layer') == 'specbar_layer' and get(out[at][1], 'type') == 'graphic':
            at += 1
        moved = []
        for i, (name, kv) in enumerate(energy):
            kv2 = [(k, str(int(v) - 1) if k == 'x' else str(int(v) + 1) if k == 'y' else v) for k, v in kv]
            # renamed: nothing refers to them, and their old com_N names can collide with 474's
            moved.append(('energy%d' % i, kv2))
        out = out[:at] + moved + out[at:]
    if ifname == 'combat_powered_staff':
        out = [(n, [(k, POWERED_TEXT.get(v, v) if k == 'text' else POWERED_ICONS.get(v, v) if k == 'graphic' else v)
                    for k, v in kv]) for n, kv in out]
        conv.sprites -= {268, 269, 270}
        conv.sprites |= {266, 267, 252}
    conv.write_sprites(os.path.join(CONTENT, 'sprites'))

    lines = ['// 474\'s %s tab (474 interface %d), ported by LostCityServer tools/models/portcombat474.py -' % (ifname, gid),
             '// regenerate it rather than editing by hand. Style buttons keep the content\'s names; the',
             '// special attack energy bar is the content\'s own; auto_retaliate is 474\'s new button.',
             'type=overlay']
    for name, kv in out:
        lines.append('')
        lines.append('[%s]' % name)
        lines += ['%s=%s' % (k, v) for k, v in kv]
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines) + '\n')
    return path, conv.notes


def port_staff(cache):
    """combat_staff_2 from 474 interface 90. Its 253 components are mostly 72 hidden layers - one per
    autocastable spell, showing that spell's icon in the Spell box - that a 474 client script swaps
    between. This server names the chosen spell in text instead (auto_spell, set by auto_cast.rs2)
    and picks it on a screen of its own (staff_spells), so those layers are left out, and 474's two
    Spell buttons become the content's autocast toggle and chooser."""
    from port474if import Converter
    ifname, gid = 'combat_staff_2', 90
    path = find_if(ifname)
    old = dict(parse_if(open(path, encoding='utf-8').read()))
    comps = cache.load(gid)

    # everything under a hidden layer, and the special attack layer (no staff here has a special)
    def under(fid):
        seen = set()
        while fid is not None and fid not in seen:
            seen.add(fid)
            c = comps[fid]
            if c['type'] == 0 and (c.get('hide') or fid == 87):
                return True
            fid = c['parent']
        return False
    for fid in [f for f in comps if under(f)]:
        del comps[fid]

    names = {0: 'name', 100: 'combat_level', 9: 'auto_retaliate', 5: 'auto_toggle', 4: 'auto_choose',
             11: 'auto_spell', 12: 'styles'}
    for fid, c in comps.items():
        if c['type'] == 5 and (c.get('scripts') or [[0]])[0][:2] == [5, 43] and c['comparators'][0][1] < 3:
            names[fid] = 'staff2' + 'abc'[c['comparators'][0][1]]
    conv = Converter(cache, gid, ifname, names, {}, 'overlay')
    conv.comps = comps
    out = parse_if(conv.convert())

    def replace_scripts(kv, src):
        kv = [(k, v) for k, v in kv if not k.startswith('script')]
        at = next(i for i, (k, v) in enumerate(kv) if k == 'height') + 1
        return kv[:at] + [(k, v) for k, v in src if k.startswith('script')] + kv[at:]

    fixed = []
    for name, kv in out:
        if name == 'auto_toggle':
            # 474 lit it on com_mode 3; this server's autocast is bit 0 of %lastcastspell
            kv = replace_scripts(kv, old['auto_toggle'])
            kv = [(k, 'select' if k == 'buttontype' else v) for k, v in kv]
        elif name == 'auto_choose':
            kv = [(k, v) for k, v in kv if not k.startswith('script')]
            kv = [(k, 'Choose Spell' if k == 'option' else v) for k, v in kv]
        elif name == 'auto_spell':
            # where 474 writes "Spell" under the button, the chosen spell's name, as the content has it
            kv = replace_scripts(kv, old['auto_spell'])
            kv = [(k, v) for k, v in kv if k not in ('text', 'activetext', 'colour', 'activecolour')]
            kv += [(k, v) for k, v in old['auto_spell'] if k in ('text', 'activetext', 'colour', 'activecolour')]
        fixed.append((name, kv))
    conv.write_sprites(os.path.join(CONTENT, 'sprites'))

    lines = ['// 474\'s staff tab (474 interface 90), ported by LostCityServer tools/models/portcombat474.py -',
             '// regenerate it rather than editing by hand. 474\'s per-spell icon layers are left out: the',
             '// chosen spell is named in auto_spell and picked on staff_spells, as before.',
             'type=overlay']
    for name, kv in fixed:
        lines.append('')
        lines.append('[%s]' % name)
        lines += ['%s=%s' % (k, v) for k, v in kv]
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines) + '\n')
    return path, conv.notes


def main():
    from if3_474 import Cache
    cache = Cache(sys.argv[1])
    todo = sys.argv[2:] or sorted(TABS) + ['combat_staff_2']
    for ifname in todo:
        path, notes = port_staff(cache) if ifname == 'combat_staff_2' else port(cache, ifname)
        notes = [n for n in notes if 'model' not in n and 'clientcode' not in n]
        print('%-18s %s%s' % (ifname, os.path.relpath(path, CONTENT), ('  (%d notes)' % len(notes)) if notes else ''))
        for n in notes:
            print('    ' + n)
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py')] + todo)


if __name__ == '__main__':
    main()
