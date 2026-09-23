#!/usr/bin/env python3
"""Import spotanims (graphics) from the rev 474 cache into content: their models, their animations,
and a .spotanim config naming them.

    python tools/models/importspot474.py "caches/474 cache" --out content/scripts/x/configs/x.spotanim \
        749:bolt_opal_effect 750:bolt_pearl_effect ...

  models      old-format ones are 474's bytes, which the 377 client reads as they are; a new-format
              one is refused (osrs2ob2 does not read 474's variant yet). Written to models/spot/ as
              spot_<name>.ob2 and registered in pack/model.pack.
  animations  through animconv474.py, as <name>_anim in a .seq beside the .spotanim.
  the rest    resize, angle, ambient and contrast carry over; 474 and 377 number them the same.
"""
import argparse, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')


def decode_spot(b):
    out, p = {}, 0
    def g1():
        nonlocal p
        p += 1
        return b[p - 1]
    def g2():
        nonlocal p
        p += 2
        return (b[p - 2] << 8) | b[p - 1]
    while True:
        op = g1()
        if op == 0:
            return out
        if op == 1: out['model'] = g2()
        elif op == 2: out['anim'] = g2()
        elif op == 3: out['alpha'] = True
        elif op == 4: out['resizeh'] = g2()
        elif op == 5: out['resizev'] = g2()
        elif op == 6: out['angle'] = g2()
        elif op == 7: out['ambient'] = g1()
        elif op == 8: out['contrast'] = g1()
        elif 40 <= op < 50: g2(); g2()      # recolour pair
        else:
            raise SystemExit('spotanim opcode %d unknown' % op)


def register(pack, name):
    text = open(pack, newline='').read()
    nl = '\r\n' if '\r\n' in text else '\n'
    if re.search(r'(?m)^\d+=%s\r?$' % re.escape(name), text):
        return
    nxt = max(int(i) for i in re.findall(r'(?m)^(\d+)=', text)) + 1
    with open(pack, 'w', newline='') as f:
        f.write(text.rstrip('\r\n') + nl + '%d=%s' % (nxt, name) + nl)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('spots', nargs='+', help='474 spotanim id:name')
    ap.add_argument('--out', required=True, help='.spotanim to write (a .seq beside it gets the animations)')
    a = ap.parse_args()
    from dat2 import Store
    from reftable import RefTable, split_group
    st = Store(a.cache)
    rt2 = RefTable(st.read(255, 2))
    spots = dict(zip(rt2.file_ids[13], split_group(st.read(2, 13), rt2.file_counts[13])))

    lines = ['// Graphics from the rev 474 cache, by LostCityServer tools/models/importspot474.py: models byte for',
             '// byte, animations converted by animconv474.py into the .seq beside this file.', '']
    seqs = []
    for spec in a.spots:
        sid, name = spec.split(':')
        d = decode_spot(spots[int(sid)])
        data = st.read(7, d['model'])
        if data[-2:] == b'\xff\xff':
            raise SystemExit('spotanim %s: model %d is new-format' % (sid, d['model']))
        mname = 'spot_%s' % name
        open(os.path.join(CONTENT, 'models', 'spot', mname + '.ob2'), 'wb').write(data)
        register(os.path.join(CONTENT, 'pack', 'model.pack'), mname)
        lines += ['[%s]' % name, 'model=%s' % mname]
        if 'anim' in d:
            lines.append('anim=%s_anim' % name)
            seqs.append('%d:%s_anim' % (d['anim'], name))
        for k in ('resizeh', 'resizev', 'angle', 'ambient', 'contrast'):
            if k in d:
                lines.append('%s=%d' % (k, d[k]))
        lines.append('')
        register(os.path.join(CONTENT, 'pack', 'spotanim.pack'), name)
        print('%s %s: model %d%s' % (sid, name, d['model'], ', anim %d' % d['anim'] if 'anim' in d else ''))
    with open(a.out, 'w', newline='\r\n') as f:
        f.write('\n'.join(lines))
    if seqs:
        seq_out = os.path.splitext(a.out)[0] + '.seq'
        cmd = [sys.executable, os.path.join(HERE, 'animconv474.py'), a.cache, '--content', CONTENT, '--out', seq_out]
        for s in seqs:
            cmd += ['--seq', s]
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
