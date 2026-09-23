#!/usr/bin/env python3
"""Decode interfaces (index 3) and client scripts (index 12) out of a current OSRS cache.

    python tools/models/osrsif.py "caches/newest cache" if 320        # every component of 320
    python tools/models/osrsif.py "caches/newest cache" script 1234   # a client script, disassembled

The OSRS interface format is the new ('IF3') one if3_474.py reads, grown: sizes and positions carry
modes, a sprite can be tiled / flipped / bordered, a model can be animated. Only what the ports use is
kept by name; the rest is read past. Script opcodes are printed as numbers - naming them is left to
whoever reads the dump, with the constants (sprite ids, component hashes) being what the ports want.
"""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def open_store(folder):
    if any(f.endswith('.flatcache') for f in os.listdir(folder)):
        from flatcache import Store
    else:
        from dat2 import Store
    return Store(folder)


class Buf:
    def __init__(s, d):
        s.d, s.p = d, 0

    def u1(s):
        s.p += 1
        return s.d[s.p - 1]

    def s1(s):
        v = s.u1()
        return v - 256 if v > 127 else v

    def u2(s):
        s.p += 2
        return (s.d[s.p - 2] << 8) | s.d[s.p - 1]

    def s2(s):
        v = s.u2()
        return v - 65536 if v > 32767 else v

    def u3(s):
        s.p += 3
        return (s.d[s.p - 3] << 16) | (s.d[s.p - 2] << 8) | s.d[s.p - 1]

    def s4(s):
        s.p += 4
        return struct.unpack('>i', s.d[s.p - 4:s.p])[0]

    def string(s):
        e = s.d.index(0, s.p)
        v = s.d[s.p:e].decode('latin1')
        s.p = e + 1
        return v


def _listener(b):
    n = b.u1()
    if n == 0:
        return None
    out = []
    for _ in range(n):
        t = b.u1()
        out.append(b.s4() if t == 0 else b.string())
    return out


def _triggers(b):
    n = b.u1()
    return [b.s4() for _ in range(n)] if n else None


LISTENERS = ['onLoad', 'onMouseOver', 'onMouseLeave', 'onTargetLeave', 'onTargetEnter', 'onVarTransmit',
             'onInvTransmit', 'onStatTransmit', 'onTimer', 'onOp', 'onMouseRepeat', 'onClick', 'onClickRepeat',
             'onRelease', 'onHold', 'onDrag', 'onDragComplete', 'onScrollWheel']


def decode_if3(data):
    b = Buf(data)
    if b.u1() != 255:
        return {'if1': True}
    c = {'type': b.u1(), 'contenttype': b.u2(), 'x': b.s2(), 'y': b.s2(), 'width': b.u2()}
    c['height'] = b.s2() if c['type'] == 9 else b.u2()
    c['wmode'], c['hmode'], c['xmode'], c['ymode'] = b.s1(), b.s1(), b.s1(), b.s1()
    p = b.u2()
    c['parent'] = None if p == 65535 else p
    c['hidden'] = b.u1() == 1
    t = c['type']
    if t == 0:
        c['scrollwidth'], c['scrollheight'] = b.u2(), b.u2()
        c['noclickthrough'] = b.u1() == 1
    if t == 5:
        c['sprite'] = b.s4()
        c['angle'] = b.u2()
        c['tiling'] = b.u1() == 1
        c['opacity'] = b.u1()
        c['border'] = b.u1()
        c['shadow'] = b.s4()
        c['vflip'] = b.u1() == 1
        c['hflip'] = b.u1() == 1
    if t == 6:
        m = b.u2()
        c['model'] = None if m == 65535 else m
        c['xof'], c['yof'] = b.s2(), b.s2()
        c['xan'], c['zan'], c['yan'] = b.u2(), b.u2(), b.u2()
        c['zoom'] = b.u2()
        a = b.u2()
        c['anim'] = None if a == 65535 else a
        c['ortho'] = b.u1() == 1
        b.u2()
        if c['wmode'] != 0:
            b.u2()
    if t == 4:
        f = b.u2()
        c['font'] = None if f == 65535 else f
        c['text'] = b.string()
        c['lineheight'], c['xalign'], c['yalign'] = b.u1(), b.u1(), b.u1()
        c['shadowed'] = b.u1() == 1
        c['colour'] = b.s4()
    if t == 3:
        c['colour'] = b.s4()
        c['fill'] = b.u1() == 1
        c['opacity'] = b.u1()
    if t == 9:
        c['linewidth'] = b.u1()
        c['colour'] = b.s4()
        c['linedir'] = b.u1() == 1
    c['clickmask'] = b.u3()
    c['name'] = b.string()
    c['ops'] = [b.string() for _ in range(b.u1())]
    c['dragzone'], c['dragtime'], c['dragrender'] = b.u1(), b.u1(), b.u1()
    c['targetverb'] = b.string()
    for n in LISTENERS:
        c[n] = _listener(b)
    c['vartriggers'], c['invtriggers'], c['stattriggers'] = _triggers(b), _triggers(b), _triggers(b)
    return c


class Cache:
    def __init__(self, folder):
        self.store = open_store(folder)

    def files(self, index, gid):
        from reftable import split_group
        rt = self.store.reftable(index)
        fids = rt.file_ids[gid]
        data = self.store.read(index, gid)
        parts = split_group(data, len(fids)) if len(fids) > 1 else [data]
        return dict(zip(fids, parts))

    def load(self, gid):
        return {fid: decode_if3(b) for fid, b in self.files(3, gid).items()}

    def script(self, sid):
        return disassemble(self.store.read(12, sid))

    def sprite(self, gid, index=0, key=(255, 0, 255)):
        """A sprite on its full canvas, transparent pixels as the magenta key (content/sprites' own)."""
        import osrssprite
        from PIL import Image
        d = osrssprite.decode(self.store.read(8, gid))
        s, pal = d['sprites'][index], d['palette']
        im = Image.new('RGB', (d['width'], d['height']), key)
        px = im.load()
        for y in range(s['h']):
            for x in range(s['w']):
                v = s['px'][y * s['w'] + x]
                if v:
                    c = pal[v]
                    px[s['ox'] + x, s['oy'] + y] = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
        return im

    def enum(self, eid):
        """An enum from the config index (2, group 8): {key: value}."""
        b = Buf(self.files(2, 8)[eid])
        out, kt, vt = {}, None, None
        while True:
            op = b.u1()
            if op == 0:
                return out
            if op == 1:
                kt = chr(b.u1())
            elif op == 2:
                vt = chr(b.u1())
            elif op == 3:
                b.string()
            elif op == 4:
                b.s4()
            elif op in (5, 6):
                for _ in range(b.u2()):
                    k = b.s4()
                    out[k] = b.string() if op == 5 else b.s4()


def disassemble(d):
    b = Buf(d)
    sw_len = (d[-2] << 8) | d[-1]
    # current caches: a 16-byte footer (long locals and arguments were added), and the script's name
    # (empty) before the first instruction
    end = len(d) - 2 - sw_len - 16
    b.p = end
    head = {'count': b.s4(), 'ilocals': b.u2(), 'slocals': b.u2(), 'llocals': b.u2(), 'iargs': b.u2(),
            'sargs': b.u2(), 'largs': b.u2()}
    switches = []
    if sw_len:
        for _ in range(b.u1()):
            table = {}
            for _ in range(b.u2()):
                k = b.s4()
                table[k] = b.s4()
            switches.append(table)
    b.p = d.index(0) + 1
    ops = []
    while b.p < end:
        op = b.u2()
        if op == 3:
            v = b.string()
        elif op < 100 and op not in (21, 38, 39):
            v = b.s4()
        else:
            v = b.u1()
        ops.append((op, v))
    head['switches'] = switches
    return head, ops


def main():
    cache = Cache(sys.argv[1])
    what, n = sys.argv[2], int(sys.argv[3])
    if what == 'if':
        for fid, c in sorted(cache.load(n).items()):
            print(fid, {k: v for k, v in c.items() if v not in (None, '', [], False, 0)})
    else:
        head, ops = cache.script(n)
        print(head)
        for i, (op, v) in enumerate(ops):
            print(i, op, v)


if __name__ == '__main__':
    main()
