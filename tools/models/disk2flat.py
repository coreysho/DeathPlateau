#!/usr/bin/env python3
"""Convert an OSRS disk store (main_file_cache.dat2 + idxN) into the .flatcache dump the OSRS
import tools read (flatcache.py).

OpenRS2 (archive.openrs2.org) serves every cache as disk.zip, but importosrs.py, animconvosrs.py
and the rest were written against a .flatcache dump, so a cache fetched from there needs this
step once. Only the lines flatcache.Store reads are written - id=, contents=, file= - plus the
header and per-group metadata so the output also opens in anything else that reads the format.

    python3 tools/models/disk2flat.py caches/osrs-disk caches/osrs

Map groups (idx5) are copied as they are; XTEA-encrypted landscape files stay encrypted.
"""
import base64, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dat2 import Store
from reftable import RefTable


def main(src, dst):
    st = Store(src)
    os.makedirs(dst, exist_ok=True)
    for i in sorted(k for k in st.idx if k != 255):
        meta = st.read(255, i)
        if meta is None:
            print(f'idx{i}: no reference table, skipped'); continue
        rt = RefTable(meta, strict=False)
        n = missing = 0
        with open(os.path.join(dst, f'{i}.flatcache'), 'w') as out:
            out.write(f'protocol={rt.protocol}\nrevision={rt.revision}\ncompression=0\ncrc=0\nnamed={1 if rt.flags & 1 else 0}\n')
            for g in rt.group_ids:
                raw = st.raw(i, g)
                if raw is None:
                    missing += 1; continue
                out.write(f'id={g}\nnamehash={rt.group_names.get(g, 0)}\nrevision=0\ncrc=0\n')
                out.write('contents=' + base64.b64encode(raw).decode() + '\n')
                out.write(f'compression={raw[0]}\n')
                names = rt.file_names.get(g, {})
                for f in rt.file_ids.get(g, []):
                    out.write(f'file={f}={names.get(f, 0) if isinstance(names, dict) else 0}\n')
                n += 1
        print(f'idx{i}: {n} groups' + (f', {missing} missing' if missing else ''))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
