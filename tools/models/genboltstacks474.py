#!/usr/bin/env python3
"""Give the 2006 bolts, bolt tips and unfinished bolts their stack pictures from 474's.

    python tools/models/genboltstacks474.py "caches/474 cache" --content content

An inventory slot holding 2, 3, 4 or 5+ bolts shows 2, 3, 4 or 5 of them: the obj config's count1-4
name a stack variant per threshold, and the client draws the variant's model in place of the
parent's. 377's own bolts (bolt, opal_bolt, pearl_bolt, barbed_bolt) always had them; the 39 474 ports
below were imported by import474.py, which writes no count lines, so every stack of them showed one
bolt. 474 carries all of it, and this copies it:

  the models      each variant's model, byte for byte (474 kept the old model format for these),
                  named after the parent's model with the count: obj_metalbolt474_2 .. _5,
                  obj_gembolt474_2 .. _4, obj_boltunf474_2 .. _5, obj_bolttips474_2 .. _5. The gem
                  bolts' five-bolt picture (474 model 16871) is already here as obj_enchantbolts474,
                  imported by genenchantbolts474.py for the Enchant Crossbow Bolt window; it is reused
                  (and checked to be the same bytes), not copied twice
  the variants    [<parent>_2] .. [<parent>_5], as 377 named Karil's (barrows_karil_ammo_2): no name,
                  no ops, the stack model and the PARENT'S camera and recolours as content has them.
                  474's variants carry the same camera and recolours as its parents (checked below);
                  its (e) variants add an ambient the parents here do not have, which is left out so
                  one bolt and five look alike. They go in a generated <parent file>_stacks.obj
                  beside each parent file - the packer resolves count targets by name through
                  obj.pack, so they need not share a file
  the thresholds  count1..count4 on each parent, from 474's own (2, 3, 4, 5 for all of them), put
                  after the parent's appearance lines. Any count lines already there are replaced

Rerunning rewrites the same files and appends nothing to pack/model.pack or pack/obj.pack.
377's opal and pearl bolt tips keep 377's single-tip model, which never had stack variants.
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

# parent file (under scripts/) -> [(content obj, 474 obj id)]
PARENTS = {
    'skill_combat/configs/ranged/crossbows.obj': [
        ('blurite_bolts', 9139), ('iron_bolts', 9140), ('steel_bolts', 9141), ('mithril_bolts', 9142),
        ('adamant_bolts', 9143), ('runite_bolts', 9144),
        ('jade_bolts', 9335), ('topaz_bolts', 9336), ('sapphire_bolts', 9337), ('emerald_bolts', 9338),
        ('ruby_bolts', 9339), ('diamond_bolts', 9340), ('dragon_bolts', 9341), ('onyx_bolts', 9342),
        ('opal_bolts_e', 9236), ('jade_bolts_e', 9237), ('pearl_bolts_e', 9238), ('topaz_bolts_e', 9239),
        ('sapphire_bolts_e', 9240), ('emerald_bolts_e', 9241), ('ruby_bolts_e', 9242),
        ('diamond_bolts_e', 9243), ('dragon_bolts_e', 9244), ('onyx_bolts_e', 9245),
    ],
    'skill_fletching/configs/crossbows/crossbow_parts.obj': [
        ('bronze_bolts_unf', 9375), ('blurite_bolts_unf', 9376), ('iron_bolts_unf', 9377),
        ('steel_bolts_unf', 9378), ('mithril_bolts_unf', 9379), ('adamant_bolts_unf', 9380),
        ('runite_bolts_unf', 9381),
        ('jade_bolttips', 9187), ('topaz_bolttips', 9188), ('sapphire_bolttips', 9189),
        ('emerald_bolttips', 9190), ('ruby_bolttips', 9191), ('diamond_bolttips', 9192),
        ('dragon_bolttips', 9193), ('onyx_bolttips', 9194),
    ],
}
# 474 models already in content under another name
KNOWN = {16871: 'obj_enchantbolts474'}
# the lines that make up an obj's picture, copied from parent to variant
LOOK = re.compile(r'^(model|2d[xy]of|2dzoom|2d[xyz]an|recol\d+[sd]|retex\d+[sd]|resize[xyz]|ambient|contrast)=')


def blocks(lines):
    """[name] -> (first line, end line) of each block."""
    out, cur = {}, None
    for i, l in enumerate(lines):
        m = re.match(r'^\[(.+)\]\s*$', l)
        if m:
            if cur: out[cur[0]] = (cur[1], i)
            cur = (m.group(1), i)
    if cur: out[cur[0]] = (cur[1], len(lines))
    return out


def append_pack(path, names):
    """Append the names not yet in a .pack, re-reading it first (other tools append to it too)."""
    text = open(path, newline='').read()
    nl = '\r\n' if '\r\n' in text else '\n'
    have = set(re.findall(r'(?m)^\d+=(\S+?)\r?$', text))
    nxt = max(int(i) for i in re.findall(r'(?m)^(\d+)=', text)) + 1
    new = []
    for n in names:
        if n in have: continue
        new.append('%d=%s' % (nxt, n)); have.add(n); nxt += 1
    if new:
        with open(path, 'w', newline='') as f:
            f.write(text.rstrip('\r\n') + nl + nl.join(new) + nl)
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache')
    ap.add_argument('--content', default=os.path.join(ROOT, 'content'))
    a = ap.parse_args()
    content = os.path.abspath(a.content)

    from dat2 import Store
    from objconfig474 import load_all
    st = Store(a.cache)
    objs = load_all(a.cache)
    model_dir = os.path.join(content, 'models', 'obj')

    models = {}         # 474 model id -> content name
    new_models, new_objs = [], []
    for rel, parents in PARENTS.items():
        path = os.path.join(content, 'scripts', *rel.split('/'))
        text = open(path, newline='').read()
        nl = '\r\n' if '\r\n' in text else '\n'
        lines = text.replace('\r\n', '\n').split('\n')
        out = ['// The stack pictures of the bolts in %s: count1-4 there name these.' % os.path.basename(rel),
               '// GENERATED by LostCityServer tools/models/genboltstacks474.py from the rev 474 cache',
               '// - regenerate it rather than editing by hand.']
        for name, oid in parents:
            p474 = objs[oid]
            where = blocks(lines).get(name)
            if not where:
                raise SystemExit('%s: no [%s]' % (rel, name))
            s, e = where
            body = [l for l in lines[s + 1:e] if not re.match(r'^count\d+=', l)]
            look = [l for l in body if LOOK.match(l)]
            pmodel = next(l.split('=', 1)[1] for l in look if l.startswith('model='))
            # the parent must be 474's parent, or its stack models are someone else's
            if open(os.path.join(model_dir, pmodel + '.ob2'), 'rb').read() != st.read(7, p474['model']):
                raise SystemExit('%s: %s is not 474 model %d' % (name, pmodel, p474['model']))
            if 'stackable=yes' not in body:
                raise SystemExit('%s is not stackable' % name)
            stacks = p474.get('stackids') or []
            if len(stacks) > 10:
                raise SystemExit('%s: more stack variants than count1-10' % name)
            counts = []
            for n, (vid, count) in enumerate(stacks, start=1):
                v = objs[vid]
                for k in ('zoom2d', 'xan2d', 'yan2d', 'zan2d', 'xof2d', 'yof2d', 'recol', 'retex'):
                    if v.get(k) != p474.get(k):
                        print('  note: %s x%d: 474 variant %d has its own %s, parent\'s used' % (name, count, vid, k))
                mid = v['model']
                mname = KNOWN.get(mid) or models.get(mid) or '%s_%d' % (pmodel, count)
                if models.setdefault(mid, mname) != mname:
                    raise SystemExit('474 model %d named both %s and %s' % (mid, models[mid], mname))
                data = st.read(7, mid)
                if data[-2:] == b'\xff\xff':
                    raise SystemExit('474 model %d (%s) is new-format and needs converting' % (mid, name))
                mfile = os.path.join(model_dir, mname + '.ob2')
                if mid in KNOWN:
                    if open(mfile, 'rb').read() != data:
                        raise SystemExit('%s is not 474 model %d' % (mname, mid))
                elif not os.path.exists(mfile) or open(mfile, 'rb').read() != data:
                    open(mfile, 'wb').write(data)
                if mname not in new_models: new_models.append(mname)
                vname = '%s_%d' % (name, count)
                new_objs.append(vname)
                counts.append('count%d=%s,%d' % (n, vname, count))
                out += ['', '[%s]' % vname, 'model=' + mname]
                out += [l for l in look if not l.startswith('model=')]
                out.append('stackable=yes')
            # count lines after the parent's last appearance line
            at = max(i for i, l in enumerate(body) if LOOK.match(l)) + 1
            body[at:at] = counts
            lines[s + 1:e] = body
        new = nl.join(lines)
        if new != text:
            with open(path, 'w', newline='') as f: f.write(new)
            print('updated', path)
        gen = path[:-len('.obj')] + '_stacks.obj'
        with open(gen, 'w', newline='') as f: f.write(nl.join(out) + nl)
        print('wrote', gen)

    for pack, names in (('model', new_models), ('obj', new_objs)):
        for l in append_pack(os.path.join(content, 'pack', pack + '.pack'), names):
            print('  %s.pack %s' % (pack, l))


if __name__ == '__main__':
    main()
