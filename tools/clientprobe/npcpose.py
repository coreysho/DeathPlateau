#!/usr/bin/env python3
"""Draw and measure an npc's combat animations in the REAL client renderer.

content/tools/bossanims.py decides whether an animation CAN move a mesh: it compares the vertex
label groups the sequence transforms against the ones the mesh carries, because Model.method369
drops a transform for a group the mesh lacks and reports nothing. That test is static and it is
the right one, but it stops one question short. When the groups do line up, something moves - and
nothing so far could say whether it was the right something. A dive animation where an attack
belongs passes every check in that file.

This is the other half. NpcPose.java builds the npc through the client's own NpcType.method475,
poses it with the sequence the build actually has wired to it, and reports how far the mesh travels
from its base pose, frame by frame, in model units. Zero is a fact, not an opinion. The contact
sheet beside the numbers is for the cases a number cannot settle, which is most of the interesting
ones: you have to look at a swing to know it is a swing.

NOTHING IS HARDCODED HERE. The npc ids come from content/pack/npc.pack, the sequence ids from
content/pack/seq.pack, and which sequence each npc uses comes from bossanims.py's own config
parser - including combat.param's fallbacks for an npc that names none - so this is always
measuring what the build contains.

    python3 npcpose.py --out sheets                       # every npc above level 100
    python3 npcpose.py --out sheets --npc tgbr_barrelchest kalphite_queen_1
    python3 npcpose.py --out sheets --level 300 --measure  # numbers only, no pictures

Needs the client's sources compiled once; --build does it. The archives are the ones a content
build writes, so build the content first or the cache is the previous one's.
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))     # the super-repo, two up from tools/clientprobe
CONTENT = os.path.join(ROOT, 'content')
ENGINE = os.path.join(ROOT, 'Engine-TS')
CLIENT = os.path.join(ROOT, 'javaclient')

# the three a fighting npc can name, and what combat.param falls back to when it names none
PARAMS = ('attack_anim', 'defend_anim', 'death_anim')


def load_bossanims(content):
    """bossanims.py as a module, so there is ONE parser for what the configs say."""
    path = os.path.join(content, 'tools', 'bossanims.py')
    if not os.path.exists(path):
        sys.exit('no %s - that file is where the config parsing lives' % path)
    spec = importlib.util.spec_from_file_location('bossanims', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['bossanims'] = mod
    spec.loader.exec_module(mod)
    return mod


def plan(ba, content, want, level):
    """[(npc name, npc id, [(param, seq name, seq id)])] for the npcs asked for."""
    npc_ids = {n: i for i, n in ba.packmap('npc').items()}
    seq_ids = {n: i for i, n in ba.packmap('seq').items()}
    rows = []
    for name, body, _path in ba.config_blocks('npc'):
        if want and name not in want:
            continue
        if name not in npc_ids:
            continue
        lvl = int(body.get('vislevel', ['0'])[0]) if body.get('vislevel', ['0'])[0].isdigit() else 0
        if not want and lvl < level:
            continue
        # a fighting npc: something to attack, or stats to attack with
        if not want and not any(v.startswith('Attack') for v in body.get('op2', [])) \
                and 'hitpoints' not in body:
            continue
        seqs = []
        for param in PARAMS:
            got = None
            for v in body.get('param', []):
                if v.startswith(param + ','):
                    got = v.split(',', 1)[1].strip()
            if got == 'null':
                # switched off on purpose - there is nothing to draw and saying so beats a blank row
                seqs.append((param, '(null, switched off on purpose)', None))
                continue
            using = got or ba.FALLBACK[param]
            seqs.append((param, using + ('' if got else ' (fallback)'), seq_ids.get(using)))
        # its own stand, as the control: whatever is wrong with the rest, this one is the cache's
        for key in ('readyanim',):
            for v in body.get(key, []):
                s = v.split(',')[0].strip()
                seqs.insert(0, (key, s, seq_ids.get(s)))
        rows.append((name, npc_ids[name], seqs))
    rows.sort(key=lambda r: r[0])
    return rows


def spec_ids(seqs):
    """param=seqId=seqName per sequence: the probe can then tell a stand that is MEANT to hold
    still from an attack that is not moving, and print a readable line without this side's help."""
    return ['%s=%d=%s' % (p, sid, using.replace(',', ' ').replace(':', ' '))
            for p, using, sid in seqs if sid is not None]


def build_client(out):
    # BOTH source roots, as build.gradle's sourceSets has them: the world map window reaches into
    # the launcher's Theme, so src/main/java alone does not compile.
    srcs = []
    for root in ('src/main/java', 'launcher/src'):
        for dirpath, _d, files in os.walk(os.path.join(CLIENT, root)):
            srcs += [os.path.join(dirpath, f) for f in files if f.endswith('.java')]
    srcs.append(os.path.join(HERE, 'NpcPose.java'))
    listing = os.path.join(out, 'sources.txt')
    with open(listing, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(s.replace('\\', '/') for s in srcs))
    build = os.path.join(out, 'build')
    os.makedirs(build, exist_ok=True)
    # -encoding UTF-8 is not optional: build.gradle sets it, the sources are UTF-8, and javac on
    # Windows defaults to the system codepage - where WordPack's pound sign becomes two characters
    # and the file stops parsing. Eleven errors, none of them about anything that matters.
    r = subprocess.run(['javac', '-nowarn', '-encoding', 'UTF-8', '-d', build, '@' + listing],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit('javac failed:\n' + (r.stderr or r.stdout)[-4000:])
    return build


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='npcpose')
    ap.add_argument('--content', default=CONTENT)
    ap.add_argument('--engine', default=ENGINE)
    ap.add_argument('--npc', nargs='*', help='npc names; default is everything above --level')
    ap.add_argument('--level', type=int, default=100)
    ap.add_argument('--measure', action='store_true', help='numbers only, write no pictures')
    ap.add_argument('--per', type=int, default=6, help='frames drawn per sequence')
    ap.add_argument('--build', action='store_true', help='recompile the client and the probe')
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    cfg = os.path.join(a.engine, 'data/pack/client/config')
    tex = os.path.join(a.engine, 'data/pack/client/textures')
    for p in (cfg, tex):
        if not os.path.exists(p):
            sys.exit('no %s - run the content build first, that is what writes it' % p)

    ba = load_bossanims(a.content)
    rows = plan(ba, a.content, set(a.npc or []), a.level)
    if not rows:
        sys.exit('nothing to do')
    missing = set(a.npc or []) - {r[0] for r in rows}
    if missing:
        print('not in the build, or not in npc.pack: %s' % ', '.join(sorted(missing)))

    build = os.path.join(a.out, 'build')
    if a.build or not os.path.isdir(build):
        print('compiling the client and the probe...')
        build = build_client(a.out)

    print('%d npcs\n' % len(rows))

    # ONE JVM FOR THE WHOLE MEASURE PASS. Every start reads all 1,456 animation sets off disk
    # before it can pose anything, so a run over a hundred bosses spent almost all of its time
    # loading the same frames again. With no pictures to write there is nothing to separate.
    if a.measure:
        specs = []
        for name, npc_id, seqs in rows:
            ids = spec_ids(seqs)
            if ids:
                specs.append('%d:%s:%s' % (npc_id, name, ','.join(ids)))
        # THE SPECS GO IN A FILE. Three hundred bosses is longer than a Windows command line, and
        # the failure is "the filename or extension is too long" with nothing in it about
        # arguments. java's own @argfile is no help: this is Java 8, where that is a javac
        # feature only and `java @file` is read as a class name with the slashes turned to dots.
        # So NpcPose reads the list itself.
        listing = os.path.join(a.out, 'measure.specs')
        with open(listing, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(specs))
        r = subprocess.run(['java', '-Dpose.frames=%d' % a.per, '-cp', build + os.pathsep + HERE,
                            'NpcPose', cfg, tex, a.content, '-', '@' + listing],
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode:
            sys.stderr.write(r.stderr[-3000:])
        return 0

    for name, npc_id, seqs in rows:
        ids = spec_ids(seqs)
        # THE LEGEND BEFORE THE NUMBERS. The probe knows a sequence id; only this side knows which
        # param pointed at it, and a row of figures with no idea whether it is the attack or the
        # death is the thing that made the first run of this useless.
        for param, using, sid in seqs:
            if sid is None:
                print('    %-12s %-44s NOT PACKED - nothing to draw' % (param, using))
        if not ids:
            print('    nothing to pose\n')
            continue
        png = '-' if a.measure else os.path.join(a.out, name + '.png')
        r = subprocess.run(
            ['java', '-Dpose.frames=%d' % a.per, '-cp', build + os.pathsep + HERE, 'NpcPose',
             cfg, tex, a.content, png, '%d:%s:%s' % (npc_id, name, ','.join(ids))],
            capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode:
            sys.stderr.write(r.stderr[-2000:])
        if not a.measure and os.path.exists(png):
            print('    -> %s' % png)
        print('')


if __name__ == '__main__':
    sys.exit(main())
