#!/usr/bin/env python3
"""Assemble the directory ObjIconRender wants, and nothing else.

renderscene.py already builds three of these four files, but it is a SCENE renderer: it insists on
map squares and camera views and then gunzips a map archive, none of which an inventory icon needs.
This is the same first half, plus the one file it has no reason to write.

  config.jag / textures.jag   the client archives                  (Engine-TS/data/pack/client)
  models.txt                  "<model id> <path to .ob2>"          (content/pack/model.pack)
  objs.txt                    "<obj id> <debugname>"               (content/pack/obj.pack)

  python3 tools/models/objicondir.py --engine Engine-TS --content content --out .cache/objicons

THE ENGINE MUST BE BUILT. config.jag and textures.jag are packed from content by the engine's own
build; an unbuilt tree simply has no client archives, and the first thing the renderer would do is
fail to read them.
"""
import argparse
import os
import shutil


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', required=True, help='the Engine-TS checkout, already built')
    ap.add_argument('--content', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    for src, dst in (('config', 'config.jag'), ('textures', 'textures.jag')):
        p = os.path.join(a.engine, 'data', 'pack', 'client', src)
        if not os.path.exists(p):
            raise SystemExit(f'{p} is missing - build the engine first, it is packed from content')
        shutil.copyfile(p, os.path.join(out, dst))
    print('# config.jag, textures.jag')

    # models.txt: every model the client could draw, by id, pointing at the .ob2 on disk. The
    # obj models are the ones that matter here, but an item can borrow any mesh, so all of them go in.
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

    # objs.txt: the same file as obj.pack with the = turned into a space, which is the only shape
    # ObjIconRender reads. Kept in id order, because --all renders in the order it is read.
    objs = []
    with open(os.path.join(a.content, 'pack', 'obj.pack'), encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if '=' in ln:
                i, nm = ln.split('=', 1)
                objs.append(f'{i} {nm}')
    with open(os.path.join(out, 'objs.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(objs))
    print(f'# objs.txt: {len(objs)} objs')
    print(out)


if __name__ == '__main__':
    main()
