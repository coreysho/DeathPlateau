#!/usr/bin/env python3
"""Pull jagfile archives and on-demand models out of the 377 client's own file store.

    python3 extract.py "C:\\.file_store_32" 16481 16482 9638

Writes config.jag, textures.jag, versionlist.jag and models/<id>.ob2 next to this script. The
store is main_file_cache.dat plus one .idx per index: 520-byte blocks, an 8-byte header on each
(file id, part, next block, index id). Index 0 holds the jagfiles; index 1 the models, gzipped.
"""
import os, sys, zlib

def reader(store):
    dat = open(os.path.join(store, 'main_file_cache.dat'), 'rb').read()
    def read(index, fid):
        idx = open(os.path.join(store, 'main_file_cache.idx%d' % index), 'rb').read()
        off = fid * 6
        if off + 6 > len(idx):
            return None
        size = int.from_bytes(idx[off:off + 3], 'big')
        block = int.from_bytes(idx[off + 3:off + 6], 'big')
        if size == 0 or block == 0:
            return None
        out = bytearray()
        while size > 0 and block > 0:
            p = block * 520
            nxt = int.from_bytes(dat[p + 4:p + 7], 'big')
            n = min(512, size)
            out += dat[p + 8:p + 8 + n]
            size -= n
            block = nxt
        return bytes(out)
    return read

def gunzip(b):
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    return d.decompress(b) + d.flush()

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    store = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    read = reader(store)
    for fid, name in ((2, 'config'), (5, 'versionlist'), (6, 'textures')):
        b = read(0, fid)
        open(os.path.join(here, name + '.jag'), 'wb').write(b)
        print('%s.jag: %d bytes' % (name, len(b)))
    os.makedirs(os.path.join(here, 'models'), exist_ok=True)
    for arg in sys.argv[2:]:
        mid = int(arg)
        b = read(1, mid)
        if b is None:
            print('model %d is not in this store yet - log in and look at the thing first' % mid)
            continue
        raw = gunzip(b)
        open(os.path.join(here, 'models', '%d.ob2' % mid), 'wb').write(raw)
        print('model %d: %d bytes' % (mid, len(raw)))

main()
