#!/usr/bin/env python3
"""Import a whole cast of rev 474 npcs at once, with their chatheads, sharing their models.

importnpc474.py does one npc and does not bring its chathead across. That is fine for a boss. It
is not fine for a quest, and it fails in two ways that only show up at scale:

  NO FACE. A 474 npc config carries a `heads` list - one or two chathead models - and
  importnpc474.py drops it, so every npc it brings in opens a dialogue with an empty frame where a
  face should be. head1=/head2= are emitted here.

  MODEL.PACK RUNS OUT. The model.pack id ranges a parallel round gets are a few hundred wide, and
  npcs are the expensive thing in them: a robed villager is eight models, and a cast of thirty is
  most of a range on its own. But a cast is not thirty different sets of art - the Moon Clan are
  one set of robes recoloured, and the six Ethereal beings of Lunar Diplomacy's Dream World are
  literally one model set with six recolours. Run one npc at a time and each one copies its own
  private duplicate of the same file. Run them together and a 474 model id already copied under
  some local name is referenced again instead: Lunar Diplomacy's 33 npcs came to 115 distinct
  models rather than something near 270, which is the only reason they fitted the round's range.

Everything else is importnpc474.py's: models are copied byte-for-byte (474 model files are already
in the format the 377 client reads), and each cache recolour goes back through the RGB15 preimage
table rather than being announced and dropped.

Animations are NOT handled here. Convert them first with animconv474.py (with --used-only if the
round's anim range is tight) and name the local seqs in the batch.

Batch file is TSV, '#' comments allowed. Columns after `walk` are optional; '-' means none:

    474id  local_name        ready              walk               attack          defend  death
    4511   oneiromancer      seq_474_4424       seq_474_4426
    4527   suqah             seq_474_4386       seq_474_4383       seq_474_4384    -       seq_474_4389
    4509   lunar_me          human_staffready   human_walk_f       human_staff_pound  human_staff_block  human_death

    python3 importnpc474batch.py <cache> <batch.tsv> --content ../../content \\
        --out ../../content/scripts/quests/quest_lunar/configs/lunar_npcs.npc

What the cache cannot tell us - hitpoints, attack/strength/defence, param= bonuses, huntmode,
drops - is not invented here. The written .npc is a skeleton to add those to by hand.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dat2 import Store
from npcconfig474 import load_all as load_npcs
from animconv474 import pack_append
from import474 import hsl16_to_rgb15


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('batch', help='TSV: 474id, local_name, ready, walk, [attack], [defend], [death]')
    ap.add_argument('--content', required=True, help='content/ root')
    ap.add_argument('--out', required=True, help='the .npc config to write')
    ap.add_argument('--header', action='append', default=[],
                    help='a comment line for the top of the .npc (repeatable)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    st = Store(a.cache)
    npcs = load_npcs(a.cache)
    mdir = os.path.join(a.content, 'models', 'npc')

    shared = {}          # 474 model id -> the local model name it was copied under
    newmodels = {}       # local model name -> raw bytes
    out = ['// Imported from the rev 474 cache by tools/models/importnpc474batch.py: models copied',
           '// byte-for-byte, chatheads brought across, and one copy of each model shared between',
           '// every npc that wears it. Combat stats, huntmode and drops are by hand - the cache',
           '// carries none of them.']
    out += ['// ' + h for h in a.header] + ['']
    names = []

    for lineno, raw in enumerate(open(a.batch, encoding='utf-8'), 1):
        raw = raw.strip()
        if not raw or raw.startswith('#'):
            continue
        f = raw.split('\t')
        if len(f) < 2:
            raise SystemExit(f'{a.batch}:{lineno}: need at least a 474 id and a local name')
        f += ['-'] * (7 - len(f))
        nid, name, ready, walk, atk, dfn, dth = f[:7]
        n = npcs.get(int(nid))
        if n is None:
            raise SystemExit(f'{a.batch}:{lineno}: no npc {nid} in this cache')
        names.append(name)

        def readable(ids, what):
            """474 holds a MIX of model formats and the 377 client only reads the older one. A
            model that ends 0xffff is the newer one, and there is no converter for it - osrs2ob2 is
            for OSRS's layout and decodes these to nothing - so it is left out rather than copied as
            bytes the client cannot parse. The Lady Zay's crew are the case that found this: every
            pirate on that ship carries a newer-format chathead FIRST and an older one after it, so
            taking the list as it comes gives all of them a face that cannot be drawn."""
            out = []
            for mid in ids:
                blob = st.read(7, mid)
                if blob is None:
                    raise SystemExit(f'{name}: 474 model {mid} missing from the cache')
                if blob[-2:] == b'\xff\xff':
                    print(f"# NOTE {name}: {what} {mid} is 474's newer model format - left out")
                    continue
                out.append(mid)
            return out

        def local(mid, slot):
            """The local name this 474 model already has, or a new one that copies it."""
            if mid in shared:
                return shared[mid]
            nm = f'npc_{name}_{slot}'
            shared[mid] = nm
            newmodels[nm] = st.read(7, mid)
            return nm

        models = readable(n['models'], 'model')
        heads = readable(n.get('heads') or [], 'chathead')
        if not models:
            raise SystemExit(f"{name}: every one of 474 npc {nid}'s models is the newer format, so "
                             f"it has nothing to wear - give it another npc's look in the batch")
        L = [f'[{name}]', f'// rev 474 npc {nid}', f'name={n.get("name")}', f'desc={n.get("name")}.']
        for i, mid in enumerate(models, start=1):
            L.append(f'model{i}={local(mid, i)}')
        for i, mid in enumerate(heads, start=1):
            L.append(f'head{i}={local(mid, f"head{i}")}')
        if n.get('size'):    L.append(f'size={n["size"]}')
        if ready != '-':     L.append(f'readyanim={ready}')
        if walk != '-':      L.append(f'walkanim={walk}')
        if n.get('resizeh'): L.append(f'resizeh={n["resizeh"]}')
        if n.get('resizev'): L.append(f'resizev={n["resizev"]}')
        for k, v in sorted((n.get('ops') or {}).items()):
            L.append(f'op{k + 1}={v}')
        # A .npc config writes RGB15 and the packer converts to HSL16, so each cache recolour goes
        # back through the same preimage table import474.py uses for objs.
        for i, (s_, d_) in enumerate(n.get('recol') or [], start=1):
            (sv, ok1), (dv, ok2) = hsl16_to_rgb15(s_), hsl16_to_rgb15(d_)
            if not (ok1 and ok2):
                print(f'# WARNING {name} recol{i} has no RGB15 preimage (src={s_} dst={d_}) '
                      f'- emitted raw, check it in game')
            L += [f'recol{i}s={sv}', f'recol{i}d={dv}']
        if n.get('vislevel'): L.append(f'vislevel={n["vislevel"]}')
        for k, v in (('attack_anim', atk), ('defend_anim', dfn), ('death_anim', dth)):
            if v != '-':
                L.append(f'param={k},{v}')
        out += L + ['']
        print(f'# {name} <- 474 npc {nid}: {len(models)} models, {len(heads)} heads')

    print(f'# {len(names)} npc(s), {len(newmodels)} distinct models '
          f'(one per 474 model id, however many npcs wear it)')
    if a.dry_run:
        print('# dry run - nothing written')
        return

    assigned, _ = pack_append(os.path.join(a.content, 'pack', 'model.pack'), sorted(newmodels))
    os.makedirs(mdir, exist_ok=True)
    for nm, blob in newmodels.items():
        open(os.path.join(mdir, f'{nm}.ob2'), 'wb').write(blob)
    if newmodels:
        print(f'#   model.pack {min(assigned.values())}-{max(assigned.values())}')
    npcids, _ = pack_append(os.path.join(a.content, 'pack', 'npc.pack'), names)
    print(f'#   npc.pack {min(npcids.values())}-{max(npcids.values())}')
    open(a.out, 'w', newline='').write('\r\n'.join(out))
    print(f'#   wrote {a.out}')


if __name__ == '__main__':
    main()
