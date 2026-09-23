#!/usr/bin/env python3
"""Write content's prayer tab (skill_prayer/interfaces/prayer.if) as 474's (474 interface 271).

    python tools/models/genprayer474.py "caches/474 cache"

474's prayer tab is a new-format interface: twenty-six prayers in five columns, each a 34x34 glow
behind a 30x30 icon, with the prayer's name as its op ("Activate Thick Skin") and a client script
that lit the icon when your level allowed it and drew a tooltip. This writes the same prayers in the
old format, every sprite from the cache, laid out as the owner asked (COLS / PITCH below: four to a
row, Thick Skin to Smite, Chivalry and Piety left out):

  prayer_<key>   the button: buttontype toggle on %prayerN, showing the glow (474 sprite 155) while
                 it is on - the names the content's [if_button,prayer:prayer_<key>] scripts use
  icon_<key>     the icon: 474's dark sprite, and its bright one (the dark id - 20, or its own pair
                 for the later prayers) once stat_base_level,prayer reaches the prayer's level. Chivalry
                 and Piety also need Defence 65/70, a second comparator.
  tip_<key>      a hover tooltip over the icon - "Level 1 / Thick Skin / Increases your Defence by 5%"
                 - the old format's own tooltip component (type 8) standing in for 474's script
  points         the prayer points, as 474 shows them under the grid

The eight prayers 474 has and 377 did not - Sharp Eye, Mystic Will, Hawk Eye, Mystic Lore, Eagle Eye,
Mystic Might, Chivalry and Piety - are here with the rest, on %prayer18-25.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')

# 474's order, which is the grid's: key, varp, name, level, description, extra requirement
PRAYERS = [
    ('thickskin', 'prayer0', 'Thick Skin', 1, 'Increases your Defence by 5%'),
    ('strengthburst', 'prayer1', 'Burst of Strength', 4, 'Increases your Strength by 5%'),
    ('clarity', 'prayer2', 'Clarity of Thought', 7, 'Increases your Attack by 5%'),
    ('sharpeye', 'prayer18', 'Sharp Eye', 8, 'Increases your Ranged by 5%'),
    ('mysticwill', 'prayer19', 'Mystic Will', 9, 'Increases your Magic by 5%'),
    ('rockskin', 'prayer3', 'Rock Skin', 10, 'Increases your Defence by 10%'),
    ('superhumanstrength', 'prayer4', 'Superhuman Strength', 13, 'Increases your Strength by 10%'),
    ('improvedreflexes', 'prayer5', 'Improved Reflexes', 16, 'Increases your Attack by 10%'),
    ('rapidrestore', 'prayer6', 'Rapid Restore', 19, '2x restore rate for all stats\\nexcept Hitpoints and Prayer'),
    ('rapidheal', 'prayer7', 'Rapid Heal', 22, '2x restore rate for Hitpoints'),
    ('protectitems', 'prayer8', 'Protect Item', 25, 'Keep 1 extra item if you die'),
    ('hawkeye', 'prayer20', 'Hawk Eye', 26, 'Increases your Ranged by 10%'),
    ('mysticlore', 'prayer21', 'Mystic Lore', 27, 'Increases your Magic by 10%'),
    ('steelskin', 'prayer9', 'Steel Skin', 28, 'Increases your Defence by 15%'),
    ('ultimatestrength', 'prayer10', 'Ultimate Strength', 31, 'Increases your Strength by 15%'),
    ('incrediblereflexes', 'prayer11', 'Incredible Reflexes', 34, 'Increases your Attack by 15%'),
    ('protectfrommagic', 'prayer12', 'Protect from Magic', 37, 'Protection from magical attacks'),
    ('protectfrommissiles', 'prayer13', 'Protect from Missiles', 40, 'Protection from ranged attacks'),
    ('protectfrommelee', 'prayer14', 'Protect from Melee', 43, 'Protection from close attacks'),
    ('eagleeye', 'prayer22', 'Eagle Eye', 44, 'Increases your Ranged by 15%'),
    ('mysticmight', 'prayer23', 'Mystic Might', 45, 'Increases your Magic by 15%'),
    ('retribution', 'prayer15', 'Retribution', 46, 'Inflicts damage to nearby\\ntargets if you die'),
    ('redemption', 'prayer16', 'Redemption', 49, 'Heals you when damage would\\nleave you under 10% Hitpoints'),
    ('smite', 'prayer17', 'Smite', 52, '1/4 of damage dealt is also\\nremoved from opponent\'s Prayer'),
    ('chivalry', 'prayer24', 'Chivalry', 60, 'Increases your Defence by 20%,\\nStrength by 18% and Attack by 15%\\n(needs Defence 65)'),
    ('piety', 'prayer25', 'Piety', 70, 'Increases your Defence by 25%,\\nStrength by 23% and Attack by 20%\\n(needs Defence 70)'),
]
DEFENCE = {'chivalry': 65, 'piety': 70}
# THE LAYOUT, the owner's own (2026-09-23, from a screenshot): 474's icons in 474's order, four to a
# row, six rows - Thick Skin to Smite - with the prayer points centred under them. Chivalry and Piety
# are not in it; their components are kept in a hidden layer, because their [if_button] scripts name them.
COLS, PITCH_X, PITCH_Y, X0, Y0 = 4, 42, 39, 15, 1
HIDDEN = {'chivalry', 'piety'}
# a dark (locked) icon -> its bright one, where it is not simply 20 lower
BRIGHT = {506: 502, 507: 503, 508: 504, 509: 505, 949: 945, 950: 946}


def main():
    from if3_474 import Cache
    from port474if import Converter
    cache = Cache(sys.argv[1])
    comps = cache.load(271)
    grid = comps[3]  # the layer the prayers sit in
    gx, gy = grid['x'], grid['y']
    pairs = [(fid, fid + 1) for fid in range(4, 56, 2)]
    assert len(pairs) == len(PRAYERS)
    conv = Converter(cache, 271, 'prayer', {}, {}, 'overlay')

    out = ['// 474\'s prayer tab (474 interface 271), GENERATED by LostCityServer tools/models/genprayer474.py -',
           '// regenerate it rather than editing by hand. Scripts: skill_prayer/scripts/prayers/*.rs2.',
           'type=overlay']

    def com(name, kv):
        out.append('')
        out.append('[%s]' % name)
        out.extend('%s=%s' % (k, v) for k, v in kv)

    # the prayers the layout leaves out, inside a hidden layer: the packer only hides layers
    com('unused', [('type', 'layer'), ('x', 0), ('y', 0), ('width', 190), ('height', 261), ('hide', 'yes')])
    glow = conv.sprite(comps[4]['sprite'])
    # which slot each shown prayer takes: 474's order, left to right, COLS to a row
    slot = {key: k for k, key in enumerate(p[0] for p in PRAYERS if p[0] not in HIDDEN)}

    def at(key, dx=0, dy=0):
        k = slot.get(key, 0)
        return X0 + PITCH_X * (k % COLS) + dx, Y0 + PITCH_Y * (k // COLS) + dy

    for (bg, icon), (key, varp, name, level, desc) in zip(pairs, PRAYERS):
        b, i = comps[bg], comps[icon]
        dark = i['sprite']
        bright = BRIGHT.get(dark, dark - 20)
        hide = [('layer', 'unused')] if key in HIDDEN else []
        x, y = at(key)
        com('prayer_%s' % key, [('type', 'graphic'), ('x', x), ('y', y)] + hide +
                               [('buttontype', 'toggle'), ('width', b['width']), ('height', b['height']),
                                ('script1op1', 'pushvar,%s' % varp), ('script1', 'eq,1'),
                                ('activegraphic', glow), ('option', 'Activate @lre@%s' % name)])
        # the icon sits in its glow as 474 had it
        x, y = at(key, i['x'] - b['x'], i['y'] - b['y'])
        kv = [('type', 'graphic'), ('x', x), ('y', y)] + hide + [('width', i['width']),
              ('height', i['height']), ('script1op1', 'stat_base_level,prayer'), ('script1', 'gt,%d' % (level - 1))]
        if key in DEFENCE:
            kv += [('script2op1', 'stat_base_level,defence'), ('script2', 'gt,%d' % (DEFENCE[key] - 1))]
        kv += [('graphic', conv.sprite(dark)), ('activegraphic', conv.sprite(bright))]
        com('icon_%s' % key, kv)
    for (bg, icon), (key, varp, name, level, desc) in zip(pairs, PRAYERS):
        b = comps[bg]
        x, y = at(key)
        hide = [('layer', 'unused')] if key in HIDDEN else []
        com('tip_%s' % key, [('type', '8'), ('x', x), ('y', y)] + hide + [('width', b['width']),
                             ('height', b['height']), ('text', 'Level %d\\n%s\\n%s' % (level, name, desc))])

    # prayer points, where 474 has them: its icon, then current/base
    pic, ptext = comps[0], comps[1]
    com('points_icon', [('type', 'graphic'), ('x', pic['x']), ('y', pic['y']), ('width', pic['width']),
                        ('height', pic['height']), ('graphic', conv.sprite(pic['sprite']))])
    com('points', [('type', 'text'), ('x', ptext['x']), ('y', ptext['y']), ('width', ptext['width']),
                   ('height', ptext['height']), ('script1op1', 'stat_level,prayer'),
                   ('script2op1', 'stat_base_level,prayer'), ('font', 'p12_full'), ('shadowed', 'yes'),
                   ('text', '%1/%2'), ('colour', '0xFF981F')])

    path = os.path.join(CONTENT, 'scripts', 'skill_prayer', 'interfaces', 'prayer.if')
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(out) + '\n')
    new = conv.write_sprites(os.path.join(CONTENT, 'sprites'))
    print('wrote %s; sprites new: %s' % (path, ' '.join(new) or '-'))
    import subprocess
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), 'prayer'])


if __name__ == '__main__':
    main()
