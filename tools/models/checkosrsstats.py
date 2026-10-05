#!/usr/bin/env python3
"""Audit what fillosrsstats.py decided, for every item it has ever touched.

fillosrsstats picks a base item BY DISPLAY NAME, and a display name is not unique in this build.
It builds its lookup with setdefault, so when several objs share a name the first one wins and the
rest are invisible - and when the name it wants belongs to no obj at all, it falls through to the
modern cache's numbers, which have been rebalanced since 2006. Both are silent.

That is not hypothetical. "Monk's robe top (t)" took prayerbonus 6 and no Saradomin flag from the
cache because this build calls BOTH halves of a monk's robe "Monk's robe", so "Monk's robe top"
matched nothing. The base here is 5 and carries the flag. The same shape of name collision is what
hid "Black kiteshield(h)" behind Old School's "Black shield (h1)" when these items were imported.

So this re-runs the decision and reports the three ways it can be wrong:

  AMBIGUOUS  the base it copied from shares its display name with other objs, so "the first one"
             was a coin toss. Says which others it could have been.
  MISSED     it fell through to the cache, but this build does have an item by that name - the
             lookup just could not see it. These are the ones carrying post-2006 numbers.
  DRIFTED    it says it copied from a base, and the base's params are not what it holds now.

Nothing is written; this only reports.

  python3 tools/models/checkosrsstats.py --content ../../content \\
      --file ../../content/scripts/minigames/game_trail/configs/clue_rewards.obj
"""
import argparse, difflib, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fillosrsstats import read_objs, base_names, VARIANT


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

REPAINT = re.compile(r'^// A repaint of (\w+), so the same armour')
FROM_CACHE = '// Nothing in this build to copy from'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--file', action='append', required=True,
                    help='.obj file to audit; repeatable')
    a = ap.parse_args()

    objs = read_objs(a.content)

    # EVERY obj under a display name, not just the first - which is the whole point.
    byname = collections.defaultdict(list)
    for dbg, f in objs.items():
        nm = (f.get('name') or [None])[0]
        if nm and nm != 'null' and not f.get('certlink'):
            byname[nm.lower()].append(dbg)
    # what fillosrsstats itself would have picked: first seen wins
    first = {nm: dbgs[0] for nm, dbgs in byname.items()}

    # debugname -> obj, normalised, because that is where "top" and "bottom" are written down
    bydebug = {norm(d): d for d in objs}
    ambiguous, missed, drifted, suspect, ok = [], [], [], [], 0
    for path in a.file:
        raw = open(path, newline='', encoding='latin-1').read().replace('\r\n', '\n')
        for block in raw.split('\n\n'):
            m = re.match(r'\[(\w+)\]', block.strip())
            if not m:
                continue
            dbg = m.group(1)
            name = next((l[5:].strip() for l in block.split('\n') if l.startswith('name=')), '')
            params = [l.split('=', 1)[1].strip() for l in block.split('\n') if l.startswith('param=')]

            rep = next((REPAINT.match(l) for l in block.split('\n') if REPAINT.match(l)), None)
            if rep:
                base = rep.group(1)
                basename = (objs.get(base, {}).get('name') or [''])[0].lower()
                # Only an alternative that HAS stats could ever have been chosen - the lift skips
                # paramless objs - so magictraining_adamant_kiteshield, which has none, is not a
                # real ambiguity and listing it just trains people to ignore this report.
                others = [d for d in byname.get(basename, [])
                          if d != base and objs[d].get('param')]
                if others:
                    ambiguous.append((dbg, name, base, others))
                # The ornament params are the ONE thing a repaint is meant not to share: the base
                # carries ornament_kit/ornament_into and the result carries ornament_from. Comparing
                # them makes every ornamented item look drifted when the pairing is exactly right.
                strip = lambda ps: sorted(q for q in ps if not q.startswith('ornament_'))
                want = [p.strip() for p in objs.get(base, {}).get('param', [])]
                if strip(want) != strip(params):
                    drifted.append((dbg, base, sorted(set(want) - set(params)), sorted(set(params) - set(want))))
                if not others and strip(want) == strip(params):
                    ok += 1
                continue

            if FROM_CACHE in block:
                # could this build have supplied a base, under a name the lookup could not reach?
                for cand in base_names(name):
                    here = [d for d in byname.get(cand.lower(), []) if d != dbg]
                    # base_names returns the name unchanged when there is no variant suffix to strip,
                    # so without this every plain item "finds" itself and reads as a missed base.
                    if here and any(objs[d].get('param') for d in here):
                        missed.append((dbg, name, cand, here, first.get(cand.lower())))
                        break
                else:
                    # AND THE CASE NO NAME LOOKUP CAN REACH. "Monk's robe top" is no obj's display
                    # name here - both halves are called "Monk's robe" - so nothing above can tell
                    # that monkrobetop is sitting right there. Fall back to the DEBUGNAMES, which
                    # are the only place the build writes "top" and "bottom" down, and propose a
                    # close one for a person to confirm. It proposes; it does not decide.
                    key = norm(VARIANT.sub('', name))
                    near = difflib.get_close_matches(key, list(bydebug), n=1, cutoff=0.86)
                    cand_dbg = bydebug[near[0]] if near else None
                    cand_params = sorted(p.strip() for p in objs.get(cand_dbg, {}).get('param', [])
                                         if not p.strip().startswith('ornament_'))
                    mine = sorted(p for p in params if not p.startswith('ornament_'))
                    # If it already holds exactly what the proposed base holds, the cache and this
                    # build agree and there is nothing to decide.
                    if cand_dbg and cand_dbg != dbg and cand_params and cand_params != mine:
                        suspect.append((dbg, name, cand_dbg, cand_params, mine))
                    else:
                        ok += 1

    def show(title, rows, fmt):
        print(f'\n{title}: {len(rows)}')
        for r in rows:
            print('  ' + fmt(r))

    show('AMBIGUOUS - copied from one of several objs sharing that display name', ambiguous,
         lambda r: f'{r[0]:<34} "{r[1]}" <- {r[2]}, but {", ".join(r[3])} answer to the same name')
    show('MISSED - took the cache\'s numbers though this build has the base', missed,
         lambda r: f'{r[0]:<34} "{r[1]}" -> looked for "{r[2]}", which is {", ".join(r[3])}')
    show('DRIFTED - says it copied a base, and no longer matches it', drifted,
         lambda r: f'{r[0]:<34} <- {r[1]}  missing {r[2] or "-"}  extra {r[3] or "-"}')
    show('SUSPECT - took the cache\'s numbers, and a debugname here looks like its base', suspect,
         lambda r: f'{r[0]:<34} "{r[1]}" ~ {r[2]}: it has {r[4]}, {r[2]} has {r[3]}')
    print(f'\n{ok} items agree with their base or had nothing to copy from.')
    return 1 if (ambiguous or missed or drifted or suspect) else 0


if __name__ == '__main__':
    sys.exit(main())
