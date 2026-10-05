#!/usr/bin/env python3
"""Every imported item that goes in a hand, and whether it can actually swing.

An obj's attack animation is a param on the obj: combat.rs2's ~combat_get_attack_anim reads
stabattack_anim / slashattack_anim / crushattack_anim / rangeattack_anim off the weapon and plays
what it finds. oc_param returns NULL when the param is not there, and a null animation is no
animation - the player stands still and the hit lands out of nowhere. Nothing errors.

importosrs.py brings the look across and stops at the numbers, and fillosrsstats.py fills the
numbers two ways. A REPAINT copies every param from its base item, so it gets the base's category,
anims, sounds and attackrate for free. An item with nothing here to copy from takes the cache's
params 0-11, which are the TWELVE EQUIPMENT BONUSES AND NOTHING ELSE - no category, no anims, no
attackrate. So a 3rd Age longsword has 72 slash attack and no way to swing, and the Ale of the gods
is held in a hand that cannot move.

The category matters as much as the anims: ~combat_get_weapon_style_data switches on oc_category,
and a weapon with no weapon_* category falls through to weapon_unarmed_table - the wrong combat tab,
the wrong styles, and the wrong attack speed.

  python3 tools/models/checkosrsanims.py --content ../../content [--file one.obj ...]

With no --file it audits every .obj in the build that carries an importer header.
Nothing is written; this only reports.
"""
import argparse, collections, glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fillosrsstats import read_objs
from objconfig474 import load_all

IMPORTED = re.compile(r'import(osrs|474)\.py|Imported from')
ATTACK_ANIMS = ('stabattack_anim', 'slashattack_anim', 'crushattack_anim', 'rangeattack_anim',
                'style1_attack_anim', 'style2_attack_anim', 'style3_attack_anim', 'style4_attack_anim')
# A weapon slot item that is none of these is not meant to be swung - a lit candle, a pet rock, a
# teleport tablet. They are held, not wielded, and no category is the right answer for them.
BONUSES = ('stabattack', 'slashattack', 'crushattack', 'magicattack', 'rangeattack', 'strengthbonus')


def params_of(fields):
    out = collections.defaultdict(list)
    for p in fields.get('param', []):
        k, _, v = p.partition(',')
        out[k.strip()].append(v.strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--file', action='append', default=[])
    ap.add_argument('--all', action='store_true', help='list the held-but-not-weapon items too')
    ap.add_argument('--cache', help='an OSRS cache, to check the attack speed against param 14')
    a = ap.parse_args()

    files = a.file
    if not files:
        for f in glob.glob(os.path.join(a.content, 'scripts', '**', '*.obj'), recursive=True):
            head = open(f, encoding='latin-1').read(2000)
            if IMPORTED.search(head):
                files.append(f)

    objs = read_objs(a.content)          # the whole build, so a base item can be looked up

    # PARAM 14 IS THE ATTACK SPEED and the only authority on it - the import carries no speed at all,
    # so a weapon with no attackrate silently takes the param default of 4. That is right for a
    # scimitar and wrong for a staff, and the difference is not visible without the cache.
    speeds = {}
    if a.cache:
        for i, o in load_all(a.cache).items():
            nm, p = o.get('name'), (o.get('params') or {})
            if nm and 14 in p:
                speeds.setdefault(nm.lower(), p[14])

    no_anim, no_category, no_rate, held, checked = [], [], [], [], 0
    for path in files:
        raw = open(path, newline='', encoding='latin-1').read().replace('\r\n', '\n')
        for block in raw.split('\n\n'):
            m = re.match(r'\[(\w+)\]', block.strip())
            if not m:
                continue
            dbg = m.group(1)
            f = objs.get(dbg)
            if not f:
                continue
            wearpos = (f.get('wearpos') or [None])[0]
            if wearpos != 'righthand':
                continue
            checked += 1
            P = params_of(f)
            cat = (f.get('category') or [''])[0]
            armed = any(k in P for k in BONUSES)
            where = os.path.basename(path)

            if not armed:
                held.append((dbg, where, cat))
                continue
            if not cat.startswith('weapon_'):
                no_category.append((dbg, where, cat or '-'))
            if not any(k in P for k in ATTACK_ANIMS):
                no_anim.append((dbg, where, sorted(k for k in P if k in BONUSES)))
            if 'attackrate' not in P:
                want = speeds.get((f.get('name') or [''])[0].lower())
                # 4 is the default, so a weapon Old School also swings at 4 is already right.
                if want is not None and want != 4:
                    no_rate.append((dbg, where, want))
                elif not a.cache:
                    no_rate.append((dbg, where, None))

    def show(title, rows, fmt):
        print(f'\n{title}: {len(rows)}')
        for r in rows:
            print('  ' + fmt(r))

    show('NO ATTACK ANIMATION - has weapon bonuses, plays nothing when it swings', no_anim,
         lambda r: f'{r[0]:<36} {r[1]:<26} bonuses {", ".join(r[2])}')
    show('NO WEAPON CATEGORY - falls through to weapon_unarmed_table', no_category,
         lambda r: f'{r[0]:<36} {r[1]:<26} category {r[2]}')
    show('WRONG ATTACK SPEED - no attackrate, so it takes the default of 4', no_rate,
         lambda r: f'{r[0]:<36} {r[1]:<26} Old School swings it at {r[2] if r[2] else "?"}')
    if a.all:
        show('HELD, NOT WIELDED - no bonuses, so no category or anim is wanted', held,
             lambda r: f'{r[0]:<36} {r[1]:<26} category {r[2] or "-"}')
    else:
        print(f'\nHELD, NOT WIELDED (no bonuses, nothing wanted): {len(held)}  - pass --all to list')
    print(f'\n{checked} imported items go in a hand.')
    return 1 if (no_anim or no_category or no_rate) else 0


if __name__ == '__main__':
    sys.exit(main())
