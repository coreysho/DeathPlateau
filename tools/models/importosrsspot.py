#!/usr/bin/env python3
"""
Import OSRS spot animations (graphics) - model, animation and config - into the 377 build.

  python3 importosrsspot.py "<newest cache>" --spot 1211:ags_spec_spot [--spot ...] \
      [--seq 7644:osrs_ags_spec ...] --content ../../content \
      --out <area>/configs/<name>   (writes <name>.spotanim and <name>.seq)

For each spot: the OSRS model is re-encoded by osrs2ob2 (round-trip verified) into
models/spot/spot_<name>.ob2 and registered in model.pack; its animation is converted by
animconvosrs into anim_osrs_* sets and a seq called <name>; the .spotanim entry is also <name>
(spotanims and seqs are separate namespaces). Extra --seq entries (e.g. the player animation
that goes with the graphic) are converted into the same .seq file.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flatcache import Store
from osrsspot import decode_osrs_spot, load_osrs_spots
from osrs2ob2 import convert_checked, decode as decode_osrs_model, encode as encode_ob2, roundtrip, SHARED_TEXTURES
from osrslocimport import bake
from animconv474 import pack_append
from animconvosrs import convert_seqs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('--spot', action='append', required=True, help='OSRS spotanim id:local_name')
    ap.add_argument('--seq', action='append', default=[], help='extra OSRS seq id:local_name')
    ap.add_argument('--content', required=True)
    ap.add_argument('--out', required=True, help='config path without extension')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    st = Store(a.cache)
    spots = load_osrs_spots(st)
    seq_names = {}
    for spec in a.seq:
        i, _, n = spec.partition(':'); seq_names[int(i)] = n
    entries = []; models = {}
    for spec in a.spot:
        i, _, name = spec.partition(':'); i = int(i)
        d = decode_osrs_spot(spots[i])
        # A spot's recolours are BAKED into its model, as importosrsnpc.py bakes an npc's. They used
        # to be dropped with a warning, and that is not cosmetic: the trident's three graphics are
        # modelled near-black (HSL lightness 6) and only their spotanim recolour makes them blue,
        # so without it they drew black in game.
        m = decode_osrs_model(st.read(7, d['model']))
        if m is None: raise SystemExit(f'spot {i} model {d["model"]}: layout does not reconcile')
        bake(m, d.get('recol'), d.get('retex'), SHARED_TEXTURES)
        ob2 = encode_ob2(m); ok, why = roundtrip(ob2, m)
        if not ok: raise SystemExit(f'spot {i} model {d["model"]}: {why}')
        models[f'spot_{name}'] = ob2
        if 'anim' in d:
            # several spots can share one seq (the four catapult missiles all spin on 4165):
            # the first spot's name is the seq's name and the others point at it
            seq_names.setdefault(d['anim'], name)
        if d.get('recol') or d.get('retex'):
            print(f'# spot {i}: recolours/retextures baked in: {d.get("recol")} {d.get("retex")}')
        entries.append((i, name, d))
        print(f'# spot {i} -> {name}: model {d["model"]} ({m["vcount"]} verts, '
              f'{len(m.get("tris") or [])} tex triangles, {m["textured"]} flat stand-ins), '
              f'anim {d.get("anim")}')
    if a.dry_run:
        convert_seqs(st, seq_names, None); return

    C = a.content
    ids, _ = pack_append(os.path.join(C, 'pack', 'model.pack'), list(models))
    for n, b in models.items():
        open(os.path.join(C, 'models', 'spot', n + '.ob2'), 'wb').write(b)
        print(f'#   wrote models/spot/{n}.ob2 (model.pack {ids[n]})')
    seq_text = convert_seqs(st, seq_names, C)
    lines = ['// OSRS spot animations imported by tools/models/importosrsspot.py.',
             '// Models re-encoded by osrs2ob2.py, animations converted by animconvosrs.py.', '']
    for i, name, d in entries:
        lines.append(f'[{name}]')
        lines.append(f'// OSRS spotanim {i}')
        lines.append(f'model=spot_{name}')
        if 'anim' in d: lines.append(f"anim={seq_names[d['anim']]}")
        for k in ('resizeh', 'resizev', 'angle', 'ambient', 'contrast'):
            if k in d: lines.append(f'{k}={d[k]}')
        lines.append('')
    pack_append(os.path.join(C, 'pack', 'spotanim.pack'), [n for _, n, _ in entries])
    open(a.out + '.spotanim', 'w', newline='').write('\r\n'.join(lines))
    open(a.out + '.seq', 'w', newline='').write(seq_text)
    print(f'#   wrote {a.out}.spotanim and {a.out}.seq')

if __name__ == '__main__':
    main()
