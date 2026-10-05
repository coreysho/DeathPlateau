#!/usr/bin/env python3
"""Render a piece of the live map with the real client code, so a visual fault can be LOOKED at.

Written after an afternoon of trying to diagnose rooftop graphics from coordinates. Every data
check came back identical to Old School - locs on the same tiles, heights exact, models converted,
forcedecor and forceapproach matching - while the game still looked wrong. Coordinates cannot show
you a roof you can see through, a wall drawn beside the tile you walk on, or two surfaces fighting
over the same pixels. A picture can.

SceneRender.java has been able to do this since the Warriors' Guild import; what it never had was
anything to feed it. This assembles the directory it wants out of a BUILT content tree:

  config.jag / textures.jag   the client archives the engine packs      (Engine-TS/data/pack/client)
  models.txt                  "<model id> <path to .ob2>", from         (content/pack/model.pack)
  maps/<mx>_<mz>.land/.loc    the client map squares, gunzipped         (.cache/maps-client.zip)

then runs the renderer for each view asked for.

  python3 tools/models/renderscene.py --engine ../Engine-TS --content ../content \\
      --square 48_50 --square 48_51 --out /tmp/draynor \\
      --view wall:3089:3263:900:0:300:3:3

A view is name:tileX:tileZ:cameraHeight:yaw:pitch:topLevel:groundLevel - yaw 0 looks north and 1536
east, pitch 128 is flat and 383 straight down, and topLevel 3 draws the roofs. The tile is absolute;
the base square is worked out from the squares given.
"""
import argparse, gzip, os, shutil, subprocess, sys, zipfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', required=True, help='the Engine-TS checkout, already built')
    ap.add_argument('--content', required=True)
    ap.add_argument('--javaclient', default=r'C:/LostCityServer/javaclient/build/classes/java/main')
    ap.add_argument('--square', action='append', required=True, metavar='MX_MZ')
    ap.add_argument('--view', action='append', required=True,
                    help='name:tileX:tileZ:camHeight:yaw:pitch:topLevel:groundLevel')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, 'maps'), exist_ok=True)

    # 1. the two client archives, under the names SceneRender expects
    for src, dst in (('config', 'config.jag'), ('textures', 'textures.jag')):
        p = os.path.join(a.engine, 'data', 'pack', 'client', src)
        if not os.path.exists(p):
            raise SystemExit(f'{p} is missing - build the engine first, it is packed from content')
        shutil.copyfile(p, os.path.join(out, dst))

    # 2. models.txt: every model the client could draw, by id, pointing at the .ob2 on disk.
    #    model.pack is the id <-> name map; the files live under content/models, in a few folders.
    roots = [os.path.join(a.content, 'models'), os.path.join(a.content, 'models', 'loc'),
             os.path.join(a.content, 'models', 'obj'), os.path.join(a.content, 'models', 'npc')]
    found = {}
    for r in roots:
        if not os.path.isdir(r):
            continue
        for f in os.listdir(r):
            if f.endswith('.ob2'):
                found.setdefault(f[:-4], os.path.join(r, f))
    lines, missing = [], 0
    with open(os.path.join(a.content, 'pack', 'model.pack'), encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if '=' not in ln:
                continue
            i, nm = ln.split('=', 1)
            p = found.get(nm)
            if p:
                lines.append(f'{i} {p}')
            else:
                missing += 1
    with open(os.path.join(out, 'models.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print(f'# models.txt: {len(lines)} models ({missing} named in model.pack with no .ob2 on disk)')

    # 3. the map squares, gunzipped out of the client archive
    zp = os.path.join(a.engine, 'data', 'pack', '.cache', 'maps-client.zip')
    z = zipfile.ZipFile(zp)
    for sq in a.square:
        for pre, ext in (('m', 'land'), ('l', 'loc')):
            name = f'{pre}{sq}'
            if name not in z.namelist():
                raise SystemExit(f'{name} is not in {zp}')
            blob = z.read(name)
            if blob[:2] == b'\x1f\x8b':
                blob = gzip.decompress(blob)
            with open(os.path.join(out, 'maps', f'{sq}.{ext}'), 'wb') as fh:
                fh.write(blob)
        print(f'# {sq}: land and loc written')

    # 4. the base of the 104x104 scene: the south-west square, minus a square of margin
    mxs = sorted(int(s.split('_')[0]) for s in a.square)
    mzs = sorted(int(s.split('_')[1]) for s in a.square)
    base_x, base_z = mxs[0] * 64, mzs[0] * 64

    cp = os.pathsep.join([a.javaclient, os.path.dirname(os.path.abspath(__file__))])
    cmd = ['java', '-cp', cp, 'jagex2.client.SceneRender', out, str(base_x), str(base_z)] + a.view
    print('#', ' '.join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit(f'SceneRender failed ({r.returncode})')
    for f in sorted(os.listdir(out)):
        if f.endswith('.png'):
            print(f'#   {os.path.join(out, f)}')


if __name__ == '__main__':
    main()
