#!/usr/bin/env python3
"""Give content's locs 474's area sounds - the fountains, fires, ranges, machinery, birds and wind the
474 client played around you - and bring the sounds with them.

    python tools/models/importlocsounds474.py "caches/474 cache"

474's loc configs carry two kinds (osrsloc.py decodes both with rev474=True):

  bgsound      opcode 78: one synth the loc makes all the time, heard within a range in tiles
  randomsound  opcode 79: now and then, one of a list of synths, the wait picked between two
               delays in client cycles

They are written into each loc's own config as bgsound=synth,range and
randomsound=mindelay,maxdelay,range,synth,... - the Engine-TS packer sends them to the client in
locsound.dat, not in loc.dat, so a client that has not updated reads its locs unchanged.

Which loc is which: a loc 377 already had keeps its id in 474, so it is matched by id where the names
agree (or differ only as 474 renamed them - the house's ranges and portals, the troll stew). A loc
that is 474's own is in content as loc474_<474 id>. Locs 474 added that content never imported are not
in any map here, so they are skipped.

The synths are 474's, byte for byte - 474 kept 377's format (jagfx.py reads both) but not its
numbering, so each is matched to content by its bytes, and one content lacks is written to
synth/atmospherics/474/area474_<474 id>.synth and appended to pack/synth.pack and pack/synth.order.

Re-running replaces the lines it wrote; it touches nothing else.
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')
SYNTH_DIR = os.path.join(CONTENT, 'synth', 'atmospherics', '474')

# same id, different object in 474 (Crandor's rocks where content has its doors; a fire where content
# has a pile of eggs)
NOT_THE_SAME = {2586, 2607, 2608, 2916, 14169}


def pack_names(kind):
    text = open(os.path.join(CONTENT, 'pack', kind + '.pack'), encoding='utf-8').read()
    return {int(k): v for k, v in re.findall(r'(?m)^(\d+)=(\S+)', text)}


def append_lines(path, lines):
    if not lines:
        return
    text = open(path, newline='').read()
    nl = '\r\n' if '\r\n' in text else '\n'
    with open(path, 'w', newline='') as f:
        f.write(text.rstrip('\r\n') + nl + nl.join(lines) + nl)


def loc_sounds(cache):
    from dat2 import Store
    from reftable import RefTable, split_group
    from osrsloc import decode_osrs_loc
    st = Store(cache)
    rt = RefTable(st.read(255, 2))
    ids = rt.file_ids[6]
    out = {}
    for i, f in zip(ids, split_group(st.read(2, 6), len(ids))):
        if not f:
            continue
        d = decode_osrs_loc(f, rev474=True)
        if 'bgsound' in d or 'randomsound' in d:
            out[i] = d
    return st, out


def content_locs():
    """name -> (file, display name) for every loc block in content"""
    out = {}
    for path in glob.glob(os.path.join(CONTENT, 'scripts', '**', '*.loc'), recursive=True):
        text = open(path, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'(?ms)^\[(\w+)\]\s*\n(.*?)(?=^\[|\Z)', text):
            nm = re.search(r'(?m)^name=(.*?)\s*$', m.group(2))
            out[m.group(1)] = (path, nm.group(1) if nm else None)
    return out


def match_locs(sounds, locs):
    pack = pack_names('loc')
    first_import = min(k for k, v in pack.items() if v.startswith(('loc474_', 'osrsloc_')))
    by474 = {int(v[7:]): v for v in pack.values() if re.match(r'loc474_\d+$', v)}
    out = {}
    for i, d in sorted(sounds.items()):
        if i in by474:
            out[by474[i]] = d
        elif i < first_import and i in pack and i not in NOT_THE_SAME and pack[i] in locs:
            out[pack[i]] = d
    return out


def import_synths(st, ids):
    from jagfx import parse
    pack = pack_names('synth')
    files = {os.path.basename(p)[:-6]: p for p in glob.glob(os.path.join(CONTENT, 'synth', '**', '*.synth'), recursive=True)}
    by_bytes = {}
    for name, path in files.items():
        by_bytes.setdefault(open(path, 'rb').read(), name)
    names, new_pack, new_order = {}, [], []
    nxt = max(pack) + 1
    have = set(pack.values())
    os.makedirs(SYNTH_DIR, exist_ok=True)
    for sid in sorted(ids):
        data = st.read(4, sid)
        if parse(data) != len(data):
            raise SystemExit('474 synth %d is not in the 377 format' % sid)
        if data in by_bytes:
            names[sid] = by_bytes[data]
            continue
        name = 'area474_%d' % sid
        with open(os.path.join(SYNTH_DIR, name + '.synth'), 'wb') as f:
            f.write(data)
        by_bytes[data] = name
        names[sid] = name
        if name not in have:
            new_pack.append('%d=%s' % (nxt, name))
            new_order.append(str(nxt))
            nxt += 1
    append_lines(os.path.join(CONTENT, 'pack', 'synth.pack'), new_pack)
    append_lines(os.path.join(CONTENT, 'pack', 'synth.order'), new_order)
    return names, len(new_pack)


def write_locs(matched, locs, synth):
    by_file = {}
    for name, d in matched.items():
        by_file.setdefault(locs[name][0], {})[name] = d
    for path, entries in by_file.items():
        raw = open(path, 'rb').read().decode('utf-8')
        nl = '\r\n' if '\r\n' in raw else '\n'
        text = raw.replace('\r\n', '\n')
        for name, d in entries.items():
            m = re.search(r'(?ms)^\[%s\]\n(.*?)(?=\n\[|\n*\Z)' % re.escape(name), text)
            old = m.group(1)
            trailing = old[len(old.rstrip('\n')):]
            body = re.sub(r'(?m)^(bgsound|randomsound)=.*\n?', '', old).rstrip('\n')
            add = []
            if 'bgsound' in d:
                sid, rng = d['bgsound']
                add.append('bgsound=%s,%d' % (synth[sid], rng))
            if 'randomsound' in d:
                lo, hi, rng, ids = d['randomsound']
                add.append('randomsound=%d,%d,%d,%s' % (lo, hi, rng, ','.join(synth[s] for s in ids)))
            text = text[:m.start(1)] + body + '\n' + '\n'.join(add) + trailing + text[m.end(1):]
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text.replace('\n', nl))
    return len(by_file)


def main():
    st, sounds = loc_sounds(sys.argv[1])
    locs = content_locs()
    matched = match_locs(sounds, locs)
    ids = set()
    for d in matched.values():
        if 'bgsound' in d:
            ids.add(d['bgsound'][0])
        if 'randomsound' in d:
            ids.update(d['randomsound'][3])
    synth, new = import_synths(st, ids)
    files = write_locs(matched, locs, synth)
    print('474 locs with sounds: %d; in content: %d, across %d files; synths: %d, %d new'
          % (len(sounds), len(matched), files, len(ids), new))


if __name__ == '__main__':
    main()
