#!/usr/bin/env python3
"""Decode an interface component in 474's NEW ("if3") format, and load whole 474 interfaces.

474 keeps 455 of its interfaces in the old format (if1_474.py) and the rest - Prayer, Magic, the
Quest list, Friends, Ignore, Emotes among them - in the format that is still OSRS's today, driven
by client scripts. A component in this format starts with the byte 0xff, which is how load() tells
the two apart; an interface is never a mix.

THE LAYOUT, which is today's with four things not there yet. It was found by trying the obvious
variants over every one of the 5,082 new-format components in the cache and keeping the one that
consumes all of them exactly:

  * no width/height/x/y MODE bytes after the size - positions are plain pixels from the parent;
  * a layer (type 0) is scroll width and scroll height, with no "no click through" byte;
  * a model (type 6) ends at the orthographic flag - no trailing short, no height override;
  * a line (type 9) is width and colour, with no direction byte.

Then the part both eras share: click mask (u24), name, ops, drag settings, target verb, eighteen
listener slots (each a script id and its arguments - these are what fill in the text and colours at
run time, which is why a ported tab has to do that some other way), and the var/inv/stat triggers.

    python tools/models/if3_474.py "caches/474 cache" 271      # dump one interface
"""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LISTENERS = ['onLoad', 'onMouseOver', 'onMouseLeave', 'onTargetLeave', 'onTargetEnter', 'onVarTransmit',
             'onInvTransmit', 'onStatTransmit', 'onTimer', 'onOp', 'onMouseRepeat', 'onClick', 'onClickRepeat',
             'onRelease', 'onHold', 'onDrag', 'onDragComplete', 'onScrollWheel']


class R:
    def __init__(s, d):
        s.d, s.p = d, 0

    def g1(s):
        v = s.d[s.p]; s.p += 1; return v

    def g2(s):
        v = struct.unpack_from('>H', s.d, s.p)[0]; s.p += 2; return v

    def g2s(s):
        v = struct.unpack_from('>h', s.d, s.p)[0]; s.p += 2; return v

    def g3(s):
        v = int.from_bytes(s.d[s.p:s.p + 3], 'big'); s.p += 3; return v

    def g4(s):
        v = struct.unpack_from('>i', s.d, s.p)[0]; s.p += 4; return v

    def gstr(s):
        e = s.d.index(b'\x00', s.p)
        v = s.d[s.p:e].decode('cp1252', 'replace'); s.p = e + 1; return v


def _listener(b):
    n = b.g1()
    if n == 0:
        return None
    out = []
    for _ in range(n):
        t = b.g1()
        if t == 0:
            out.append(b.g4())
        elif t == 1:
            out.append(b.gstr())
        else:
            raise ValueError('listener argument type %d' % t)
    return out


def _triggers(b):
    return [b.g4() for _ in range(b.g1())]


def decode(d):
    b = R(d)
    if b.g1() != 0xff:
        raise ValueError('not a new-format component')
    c = {'if3': True}
    t = c['type'] = b.g1()
    c['contenttype'] = b.g2()
    c['x'] = b.g2s()
    c['y'] = b.g2s()
    c['width'] = b.g2()
    c['height'] = b.g2s() if t == 9 else b.g2()
    p = b.g2()
    c['parent'] = None if p == 0xFFFF else p
    c['hidden'] = b.g1() == 1
    if t == 0:
        c['scrollwidth'] = b.g2()
        c['scrollheight'] = b.g2()
    if t == 5:
        c['sprite'] = b.g4()
        c['rotation'] = b.g2()
        c['tiling'] = b.g1() == 1
        c['opacity'] = b.g1()
        c['border'] = b.g1()
        c['shadow'] = b.g4()
        c['vflip'] = b.g1() == 1
        c['hflip'] = b.g1() == 1
    if t == 6:
        m = b.g2()
        c['model'] = None if m == 0xFFFF else m
        c['offx'] = b.g2s()
        c['offy'] = b.g2s()
        c['xan'] = b.g2()
        c['zan'] = b.g2()
        c['yan'] = b.g2()
        c['zoom'] = b.g2()
        a = b.g2()
        c['anim'] = None if a == 0xFFFF else a
        c['ortho'] = b.g1() == 1
    if t == 4:
        f = b.g2()
        c['font'] = None if f == 0xFFFF else f
        c['text'] = b.gstr()
        c['lineheight'] = b.g1()
        c['xalign'] = b.g1()
        c['yalign'] = b.g1()
        c['shadowed'] = b.g1() == 1
        c['colour'] = b.g4()
    if t == 3:
        c['colour'] = b.g4()
        c['fill'] = b.g1() == 1
        c['opacity'] = b.g1()
    if t == 9:
        c['linewidth'] = b.g1()
        c['colour'] = b.g4()
    c['clickmask'] = b.g3()
    c['name'] = b.gstr()
    c['ops'] = [b.gstr() for _ in range(b.g1())]
    c['dragzone'] = b.g1()
    c['dragtime'] = b.g1()
    c['dragrender'] = b.g1() == 1
    c['targetverb'] = b.gstr()
    for name in LISTENERS:
        c[name] = _listener(b)
    c['vartriggers'] = _triggers(b)
    c['invtriggers'] = _triggers(b)
    c['stattriggers'] = _triggers(b)
    if b.p != len(d):
        raise ValueError('%d bytes left over' % (len(d) - b.p))
    return c


class Cache:
    """A 474 cache's interfaces: load(id) -> {file: component}, either format."""

    def __init__(self, folder):
        from dat2 import Store
        from reftable import RefTable
        self.store = Store(folder)
        self.ref = RefTable(self.store.read(255, 3))

    def load(self, gid):
        from reftable import split_group
        import if1_474
        fids = self.ref.file_ids[gid]
        data = self.store.read(3, gid)
        parts = split_group(data, len(fids)) if len(fids) > 1 else [data]
        out = {}
        for fid, raw in zip(fids, parts):
            if not raw:
                continue
            if raw[0] == 0xff:
                out[fid] = decode(raw)
            else:
                c = if1_474.decode(raw)
                c['if3'] = False
                # the old format's parent is its layer link, 0xffff for none
                c['parent'] = None if c.get('overlayer', 0xFFFF) == 0xFFFF else c['overlayer'] & 0xFFFF
                out[fid] = c
        return out


if __name__ == '__main__':
    cache = Cache(sys.argv[1])
    for fid, c in sorted(cache.load(int(sys.argv[2])).items()):
        brief = {k: v for k, v in c.items() if v not in (None, [], '', False) and k not in LISTENERS}
        print(fid, brief)
