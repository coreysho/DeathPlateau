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
import argparse, difflib, glob, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fillosrsstats import read_objs, base_names, VARIANT
from objconfig474 import load_all


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

REPAINT = re.compile(r'^// A repaint of (\w+), so the same armour')
FROM_CACHE = '// Nothing in this build to copy from'
REPAINT_ANY = '// A repaint of'
NO_BONUS = '// No combat bonuses'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--cache', help="an OSRS cache: lets UNMARKED ask whether Old School separates "
                                    "two items too, instead of assuming every variant is pure paint")
    ap.add_argument('--file', action='append', default=[],
                    help='.obj file to audit; repeatable. Default: every imported .obj in the build.')
    a = ap.parse_args()

    # DEFAULT TO EVERY IMPORTED FILE, the way checkosrsanims.py does. Pointing this at two files
    # and calling the import audited is how the God Wars gear, the defenders and the Warriors' Guild
    # batches went a round without ever being looked at: they came through the same tool and have
    # the same failure mode.
    if not a.file:
        for f in glob.glob(os.path.join(a.content, 'scripts', '**', '*.obj'), recursive=True):
            if re.search(r'import(osrs|474)\.py|Imported from', open(f, encoding='latin-1').read(2000)):
                a.file.append(f)
        print(f'{len(a.file)} imported .obj files')

    # The cache's own verdict on whether two items should have the same bonuses. Params 0-11 are the
    # twelve equipment bonuses; anything else on the record is not a stat.
    cbyname = {}
    if a.cache:
        for i, o in load_all(a.cache).items():
            nm = o.get('name')
            if nm and nm != 'null':
                cbyname.setdefault(nm.lower(), {k: v for k, v in (o.get('params') or {}).items() if k <= 11})

    BONUS = {0: 'stabattack', 1: 'slashattack', 2: 'crushattack', 3: 'magicattack', 4: 'rangeattack',
             5: 'stabdefence', 6: 'slashdefence', 7: 'crushdefence', 8: 'magicdefence',
             9: 'rangedefence', 10: 'strengthbonus', 11: 'prayerbonus'}

    def signed(v):
        return v - 0x100000000 if isinstance(v, int) and v > 0x7FFFFFFF else v

    def stats_of(nm):
        p = cbyname.get(nm.lower())
        return None if p is None else {BONUS[k]: signed(v) for k, v in p.items() if k in BONUS}

    def shared_stats(a_name, b_name):
        """The bonuses Old School gives BOTH of these the same, by name.

        PER STAT, not per item. The first version of this asked "does the cache separate these two
        at all" and skipped the item when it did - which made the whole check vacuous: a skillcape(t)
        legitimately differs from its base by prayerbonus, so every other stat on it became
        unexaminable, and a deliberately broken stabdefence of 99 went unreported. The legitimate
        difference has to narrow the comparison, not cancel it.

        Without a cache, every stat is compared, which is the old behaviour and errs towards
        reporting rather than towards a quiet all-clear.
        """
        x, y = stats_of(a_name), stats_of(b_name)
        if x is None or y is None:
            return None                      # nothing to narrow with: compare everything
        return {k for k in set(x) | set(y) if x.get(k, 0) == y.get(k, 0)}

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
    ambiguous, missed, drifted, suspect, unmarked, ok = [], [], [], [], [], 0
    seen = {'repaint': 0, 'cache': 0, 'nobonus': 0, 'unmarked_stats': 0, 'unmarked_bare': 0}
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
                seen['repaint'] += 1
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

            # AN ITEM WITH NO MARKER WAS NEVER TOUCHED BY fillosrsstats - imported before it existed,
            # or filled in by hand - and the three reports above skip it in silence. 223 of them in
            # this build carry equipment stats, so reporting the rest clean without a word about
            # them is the kind of all-clear that is worse than no report. Hold them to the same
            # rule: if the name says it is a repaint of something here, the stats have to match.
            marked = (REPAINT_ANY in block) or (FROM_CACHE in block) or (NO_BONUS in block)
            if not marked:
                # AN IMBUE IS MEANT TO CHANGE THE STATS - a berserker ring (i) is +8 where the plain
                # one is +4, and a slayer helmet (i) gains magic and ranged attack it never had.
                # Holding those to "must match the base" is holding them to the opposite of what
                # they are for, the same way comparing ornament params read every decorated item as
                # drifted. imbue_from is the item saying so.
                if any(p.startswith('imbue_from') for p in params):
                    continue
                mine = sorted(p for p in params
                              if not p.startswith('ornament_') and not p.startswith('imbue_'))
                if not any(re.match(r'(stab|slash|crush|magic|range)attack|strengthbonus|\w+defence', q) for q in mine):
                    seen['unmarked_bare'] += 1
                    continue
                seen['unmarked_stats'] += 1
                for cand in base_names(name):
                    if cand.lower() == name.lower():
                        continue              # itself, not a base
                    here = [d for d in byname.get(cand.lower(), [])
                            if d != dbg and objs[d].get('param')]
                    if not here:
                        continue
                    base = here[0]
                    want = sorted(q.strip() for q in objs[base].get('param', [])
                                  if not q.strip().startswith('ornament_')
                                  and not q.strip().startswith('imbue_'))
                    # A TRIM IS NOT ALWAYS PURE PAINT: a skillcape(t) is +4 prayer where the plain
                    # cape is 0, and that IS the reward for trimming it. So the comparison runs over
                    # the stats Old School gives both of them the SAME, and a stat it separates is
                    # left alone - narrowed, not cancelled.
                    shared = shared_stats(name, cand)
                    key = lambda q: q.split(',')[0]
                    w = {q for q in want if shared is None or key(q) in shared}
                    m = {q for q in mine if shared is None or key(q) in shared}
                    if w != m:
                        unmarked.append((dbg, name, base, sorted(w - m), sorted(m - w)))
                    break
                continue

            if FROM_CACHE in block:
                seen['cache'] += 1
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
    show('UNMARKED - never went through fillosrsstats, and does not match the base its name claims', unmarked,
         lambda r: f'{r[0]:<34} "{r[1]}" vs {r[2]}  missing {r[3] or "-"}  extra {r[4] or "-"}')
    show('SUSPECT - took the cache\'s numbers, and a debugname here looks like its base', suspect,
         lambda r: f'{r[0]:<34} "{r[1]}" ~ {r[2]}: it has {r[4]}, {r[2]} has {r[3]}')
    # WHAT WAS ACTUALLY LOOKED AT. A report of zero means nothing without this: the first run of the
    # widened sweep said "clean" across 69 files while silently skipping 223 items that carry
    # equipment stats and no fillosrsstats marker, because the three original reports only ever
    # examined items the tool itself had written a comment into.
    print(f'\n{ok} items agree with their base or had nothing to copy from.')
    print(f'examined: {seen["repaint"]} repaints, {seen["cache"]} filled from the cache, '
          f'{seen["unmarked_stats"]} unmarked but carrying stats; '
          f'skipped {seen["unmarked_bare"]} unmarked with no stats to check.')
    return 1 if (ambiguous or missed or drifted or suspect or unmarked) else 0


if __name__ == '__main__':
    sys.exit(main())
