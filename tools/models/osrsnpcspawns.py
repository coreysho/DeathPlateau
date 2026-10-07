#!/usr/bin/env python3
"""Old School's own npc spawn coordinates, out of the wiki.

Asked for directly: "is there a spawn list with coords available?" There is, and this is where.
The spawns are NOT in the game cache - they live on the server - but the wiki records them per npc
page in {{LocLine}} rows: a location, a plane, the levels of that variant, and an unnamed parameter
of x:NNNN,y:NNNN pairs. That is a real spawn list with real coordinates, and for anything grafted
from Old School at Old School's own coordinates the numbers go straight in.

  python3 tools/models/osrsnpcspawns.py --match "god ?wars|armadyl|bandos|saradomin|zamorak" \
      --exclude "ancient prison|wilderness" --out gwd.json \
      Spiritual_mage Spiritual_ranger Aviansie Ork Bloodveld ...

WHAT IT WILL NOT TELL YOU, and both of these cost a round of bad spawns before being noticed:

  THE PLANE IS NOT RELIABLE. Every God Wars row says plane 0 whether the npc stands on our level 2
  or our level 0, because the dungeon is its own mapID with its own plane convention. Work the level
  out from your own collision instead - the one where the tile is actually walkable.

  SOME ROWS ARE JUST WRONG. Starlight and Growler, Commander Zilyana's bodyguards, come out at
  z5229 - forty-five tiles south of her and outside the encampment altogether. Where the wiki and a
  placement you have already checked disagree about a named character, keep the checked one.

  AND TWO NPCS CAN SHARE A TILE. Old School alternates what spawns on some squares, and the wiki
  lists the square under both of them. Place both and one ends up inside the other, so de-overlap
  against your own footprints afterwards.
"""
import argparse, json, os, re, sys, time, urllib.parse, urllib.request

UA = 'DeathPlateau-content-tool/1.0 (private server content import)'


def fetch(page, cache_dir):
    """The raw wikitext, cached on disk so a re-run does not hammer the wiki."""
    safe = re.sub(r"[^A-Za-z0-9_]", '', page)
    path = os.path.join(cache_dir, safe + '.wiki')
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, encoding='utf-8', errors='ignore').read()
    url = 'https://oldschool.runescape.wiki/w/' + urllib.parse.quote(page) + '?action=raw'
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode('utf-8', 'ignore')
    os.makedirs(cache_dir, exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)
    time.sleep(0.5)
    return text


def spawns(text, match, exclude):
    out = []
    for m in re.finditer(r'\{\{LocLine(.*?)\}\}', text, re.S):
        body = m.group(1)
        lm = re.search(r'\|location\s*=\s*([^\n|]*)', body)
        loc = lm.group(1).strip() if lm else ''
        if not match.search(loc) or (exclude and exclude.search(loc)):
            continue
        coords = [(int(x), int(y)) for x, y in re.findall(r'x:(\d+),y:(\d+)', body)]
        if not coords:
            continue
        lv = re.search(r'\|levels?\s*=\s*([^\n|]*)', body)
        out.append({'location': loc, 'levels': lv.group(1).strip() if lv else '', 'coords': coords})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pages', nargs='+', help='wiki page titles, e.g. Spiritual_mage')
    ap.add_argument('--match', required=True, help='regex a LocLine location must match')
    ap.add_argument('--exclude', default='', help='regex a LocLine location must NOT match')
    ap.add_argument('--cache', default='.wikicache')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    match = re.compile(a.match, re.I)
    exclude = re.compile(a.exclude, re.I) if a.exclude else None
    result, total = {}, 0
    for page in a.pages:
        try:
            rows = spawns(fetch(page, a.cache), match, exclude)
        except Exception as e:
            print(f'{page:28} could not be read: {e}', file=sys.stderr)
            continue
        if not rows:
            print(f'{page:28} no matching spawns')
            continue
        result[page] = rows
        n = sum(len(r['coords']) for r in rows)
        total += n
        print(f'{page:28} {n:4}')
    json.dump(result, open(a.out, 'w'), indent=1)
    print(f'\n{total} spawns from {len(result)} pages -> {a.out}')


if __name__ == '__main__':
    main()
