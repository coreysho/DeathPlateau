#!/usr/bin/env python3
"""Fill in the stats importosrs.py leaves as "TODO by hand" on a freshly imported .obj file.

importosrs.py brings the look across and stops at the numbers, which is right for one item and
impossible for four hundred. Every clue reward is one of two things and each has its own answer:

  A TRIM IS PAINT. "Rune platebody (t)", "Zamorak kiteshield", "Black shield (h3)" and "Green
  d'hide chaps (g)" are a base item with a different colour on it, so they take THAT BASE ITEM'S
  STATS AS THIS BUILD HAS THEM - not Old School's, which has rebalanced several of them since
  (its blue d'hide body defends 23 where this build's defends 45). Copying from the base is what
  keeps a trimmed set identical to the plain one, which is the whole contract of a trim and what
  Studded body (t) was shipped without.

  EVERYTHING ELSE TAKES OLD SCHOOL'S OWN NUMBERS. 3rd age, gilded, blessed d'hide, ranger gloves -
  nothing here to copy from, and the item is post-2006 content, so the cache it came from is the
  authority. Equipment bonuses live in params 0-11 (0-4 attack, 5-9 defence, 10 strength,
  11 prayer) and negatives are stored as unsigned 32-bit, which is why -15 reads 4294967281.

  python3 tools/models/fillosrsstats.py <cache> --content ../../content \\
      --file ../../content/scripts/minigames/game_trail/configs/clue_rewards.obj [--dry-run]
"""
import argparse, difflib, os, re, sys, glob, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TODO = '// TODO by hand: category, param= combat bonuses, equip requirement'

# OSRS equipment params -> this build's param names. Proven against rune platebody, rune
# kiteshield, amulet of glory and dragon scimitar, whose numbers both sides already agree on.
BONUS = {0: 'stabattack', 1: 'slashattack', 2: 'crushattack', 3: 'magicattack', 4: 'rangeattack',
         5: 'stabdefence', 6: 'slashdefence', 7: 'crushdefence', 8: 'magicdefence', 9: 'rangedefence',
         10: 'strengthbonus', 11: 'prayerbonus'}

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


VARIANT = re.compile(r'\s*\((t|g|h[1-5]|or|i|r|t4|g4)\)\s*$', re.I)
GODS = ('zamorak', 'guthix', 'saradomin', 'ancient', 'armadyl', 'bandos')


def signed(v):
    return v - 0x100000000 if isinstance(v, int) and v > 0x7FFFFFFF else v


def read_objs(content):
    """debugname -> {key: [values]}, across every .obj in the build."""
    out = {}
    for path in glob.glob(os.path.join(content, 'scripts', '**', '*.obj'), recursive=True):
        cur = None
        for line in open(path, newline='', encoding='latin-1').read().replace('\r\n', '\n').split('\n'):
            line = line.split('//')[0].strip()
            if line.startswith('[') and line.endswith(']'):
                cur = line[1:-1]; out.setdefault(cur, collections.defaultdict(list))
            elif cur and '=' in line:
                k, v = line.split('=', 1); out[cur][k.strip()].append(v.strip())
    return out


def base_names(name):
    """The items this one is a repaint of, best guess first. Empty when it is its own thing."""
    n = VARIANT.sub('', name).strip()
    low = n.lower()
    out = [n]
    first = low.split()[0] if low.split() else ''
    if first in GODS:
        # god armour is rune armour in a god's colours; the god robes and d'hide are NOT - they
        # are their own items and fall through to Old School's numbers.
        rest = n.split(' ', 1)[1] if ' ' in n else ''
        if rest.lower() in ('full helm', 'platebody', 'platelegs', 'plateskirt', 'kiteshield'):
            out.append('Rune ' + rest)
    # Old School's infinity colour kits put the colour in FRONT of the name rather than a (g)
    # on the end, so the plain robes have to be named rather than derived.
    if low.startswith('light infinity ') or low.startswith('dark infinity '):
        out.append('Infinity ' + n.split(' ', 2)[2])
    if low.startswith('gilded '):
        out.append('Rune ' + n.split(' ', 1)[1])
    # Old School writes the heraldic tier into the name ("Black shield (h1)"); the shield itself is
    # a kiteshield, which is what this build calls it.
    if ' shield' in low and 'kiteshield' not in low:
        out.append(n.replace(' shield', ' kiteshield').replace(' Shield', ' Kiteshield'))
    if ' helm' in low and 'full helm' not in low:
        out.append(n.replace(' helm', ' full helm'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('--content', required=True)
    ap.add_argument('--file', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    import importosrs as IO
    res = IO.load_all(a.cache)
    items = res[0] if isinstance(res, (tuple, list)) else res
    osrs = {}
    for i, d in items.items():
        nm = d.get('name')
        if nm and nm != 'null':
            osrs.setdefault(nm.lower(), d)

    objs = read_objs(a.content)
    # A DISPLAY NAME IS NOT UNIQUE AND THE FIRST ONE IS NOT ALWAYS RIGHT. This used to be a
    # setdefault, so when several objs answered to a name the rest were invisible - and worse, a
    # name no obj displays at all ("Monk's robe top", because this build calls both halves "Monk's
    # robe") fell straight through to the modern cache's rebalanced numbers. Both silently.
    #
    # So: keep EVERY obj under a name, prefer one that actually has stats to copy, and break a tie
    # on how close its debugname is to the name being looked up - the debugnames are the only place
    # this build writes "top" and "bottom" down. tools/models/checkosrsstats.py audits the result.
    byname = collections.defaultdict(list)
    for dbg, f in objs.items():
        nm = (f.get('name') or [None])[0]
        if nm and nm != 'null' and not f.get('certlink'):
            byname[nm.lower()].append(dbg)
    bydebug = {norm(d): d for d in objs}

    def lift_for(cand, wearpos):
        """The obj to copy stats from for a wanted display name, or None.

        WEARPOS IS THE TIE-BREAK, not how alike the two names look. Both halves of a monk's robe
        are called "Monk's robe" and the only thing that tells the top from the legs is the slot
        they go in - which the item being filled states. Name similarity gets this wrong: the top
        reads as closer to "Monk's robe" than the legs do, so it wins both.
        """
        here = [d for d in byname.get(cand.lower(), []) if objs[d].get('param')]
        if len(here) > 1 and wearpos:
            same = [d for d in here if (objs[d].get('wearpos') or [None])[0] == wearpos]
            if same:
                here = same
        return here[0] if here else None

    def lift_by_debugname(name, wearpos):
        """LAST RESORT, once no candidate name matched anything this build displays.

        "Monk's robe top" is no obj's display name here, so nothing above can find monkrobetop
        sitting right there and the stats fall through to the modern cache. The debugnames are the
        only place this build writes "top" and "bottom" down. It must run AFTER every candidate has
        been tried, never instead of one: "Adamant shield" fuzzily resembles adamant_sq_shield, and
        trying it first stops base_names ever reaching "Adamant kiteshield", which is the answer.
        """
        near = difflib.get_close_matches(norm(VARIANT.sub('', name)), list(bydebug), n=3, cutoff=0.86)
        for n in near:
            d = bydebug[n]
            if not objs[d].get('param'):
                continue
            if wearpos and (objs[d].get('wearpos') or [None])[0] != wearpos:
                continue
            return d
        return None

    raw = open(a.file, newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    blocks = raw.split(nl + nl)
    from_base = from_osrs = bare = 0
    out = []
    for b in blocks:
        if TODO not in b:
            out.append(b); continue
        lines = [l for l in b.split(nl) if l.strip() != TODO]
        name = next((l[5:] for l in lines if l.startswith('name=')), '')

        me = next((l[1:-1] for l in lines if l.startswith('[') and l.endswith(']')), None)
        wearpos = next((l[8:].strip() for l in lines if l.startswith('wearpos=')), None)
        lift = None
        for cand in base_names(name):
            dbg = lift_for(cand, wearpos)
            if dbg and dbg != me:
                lift = (dbg, objs[dbg]); break
        if not lift:
            dbg = lift_by_debugname(name, wearpos)
            if dbg and dbg != me:
                lift = (dbg, objs[dbg])

        add = []
        if lift:
            dbg, f = lift
            add.append(f'// A repaint of {dbg}, so the same armour: stats copied from it, not from')
            add.append('// the modern cache, which has rebalanced some of these since 2006.')
            if f.get('category'):
                add.append(f'category={f["category"][0]}')
            add += [f'param={p}' for p in f['param']]
            from_base += 1
        else:
            p = (osrs.get(name.lower()) or {}).get('params', {})
            vals = [(BONUS[k], signed(v)) for k, v in sorted(p.items()) if k in BONUS and signed(v)]
            if vals:
                add.append("// Nothing in this build to copy from, so these are Old School's own.")
                add += [f'param={k},{v}' for k, v in vals]
                from_osrs += 1
            else:
                add.append('// No combat bonuses - this one is worn for the look.')
                bare += 1
        out.append(nl.join(lines + add))

    if not a.dry_run:
        open(a.file, 'w', newline='').write((nl + nl).join(out))
    print(f'{from_base} copied from a base item in this build, {from_osrs} from the cache, '
          f'{bare} with no bonuses at all' + (' (dry run)' if a.dry_run else ''))


if __name__ == '__main__':
    main()
