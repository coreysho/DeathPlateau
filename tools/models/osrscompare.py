#!/usr/bin/env python3
"""A shipped worn model against the OSRS model it was imported from.

WHY THIS EXISTS. Three rounds of cape fixes in October each measured the change against a render
of our own build and each came out worse in game, because there was nothing to be right ABOUT. A
worn model's priorities are not a free choice: the artist set them against a body, and the only
thing that says what they should be is the model the import came from. This is that reference.

WHAT IT FOUND, run on 31 October. The import is faithful - the clue hunter garb, a torso, comes
through from OSRS 31630 byte-for-byte identical in its priorities, so 377 and OSRS really do share
the 0-11 scheme the importer assumes. The capes do not, and all of them differ in one way:

    clue hunter cloak   OSRS 31626   {0: 78, 6: 382}                  ours {6: 382, 10: 78}
    infernal max cape   OSRS 33102   {0: 61, 1: 70, 4: 204, 5: 260,   ours {4: 204, 5: 260,
                                      6: 34, 7: 16}                         6: 34, 7: 16, 10: 131}

Every face OSRS puts at priority 0 or 1 - painted FIRST, under the body, which is where the artist
put the collar and the shoulder on purpose - has been moved into group 10, where the client
interleaves by depth and a face can be drawn in FRONT of the body instead. That is content commit
1e84179fe and tools/capecollar.py, 13 October: 140 cape models, and in 135 of them the only change
is exactly 0 -> 10 and 1 -> 10.

So the cape over the armour is not something the import got wrong and not something the renderer
does to OSRS geometry. It is one edit, applied to one slot, that took faces out of the group that
was hiding them.

    python3 tools/models/osrscompare.py obj_infernal_max_cape_manwear=33102
    python3 tools/models/osrscompare.py --variants          # every Max cape variant in the spec
    python3 tools/models/osrscompare.py --sweep --quiet     # the whole wardrobe, differences only

--sweep needs no ids at all: objconfig474.load_all reads the modern cache's own item table, so
our item NAME finds OSRS's record and its model slots pair up with ours. 2,793 worn models in
three seconds, 31 October:

     2572  identical, face for face and label for label
      190  different mesh (two items sharing a name)
       18  priorities differ
       14  labels differ

GEOMETRY IS COMPARED EVEN THOUGH NOTHING HERE CARES ABOUT IT. Without that, two different items
with the same face count read as a model whose priorities have drifted, and the first run of this
called 36 models divergent when half of them were this build's 2006 Red cape being held up
against Old School's. A pair whose vertices differ is reported as a different mesh instead.

A difference is a QUESTION, not a fault. Some of these are deliberate: OSRS numbers a shield's
bones 161 where this build uses 28, and a held item 50 where this uses 27, so the dragon defender
and the fishing rod being relabelled is a port rather than a slip. Others are the same shape as
the cape lining fault - the pirate diving backpack has 28 faces OSRS puts under the body and we
put in the depth-sorted group - and those are worth looking at.

Exit status is 1 if any pair differs, so it can be a check rather than a report.
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from flatcache import Store
from osrsmodel import layout
from osrs2ob2 import parse_ob2, decode

# what each priority group means for a worn model, as Model.method382 paints it
WHERE = {0: 'under the body', 1: 'under the body', 2: 'under the body',
         3: 'with the body', 4: 'over the body', 5: 'over the body',
         6: 'over the body', 7: 'over the body', 8: 'over the body', 9: 'over the body',
         10: 'depth-sorted', 11: 'depth-sorted'}


def osrs_model(store, mid):
    """Geometry, face priorities and vertex labels, through the importer's own decoder.

    GEOMETRY MATTERS HERE even though nothing compares it for its own sake: without it, two
    different items that happen to share a face count read as a model whose priorities have
    drifted. A sweep keyed on item NAME turns up plenty of those - this build's Red cape is the
    2006 one and OSRS's is not the same mesh - and 36 "divergences" in the first run were mostly
    that.
    """
    try:
        m = decode(store.read(7, mid))
    except Exception:
        return None
    if m is None:
        return None
    # decode leaves pri None when the model carries ONE priority for all its faces, in the
    # header rather than a per-face section; 377 stores that the same way and parse_ob2 expands
    # it, so expand it here too or the two sides are not comparable
    pri = m['pri'] if m['pri'] is not None else [m['priority']] * m['fcount']
    return {'fcount': m['fcount'], 'vcount': m['vcount'], 'pri': pri, 'vlab': m['vlab'],
            'geom': (m['vx'], m['vy'], m['vz'], m['fa'], m['fb'], m['fc'])}


def ours_model(name):
    for sub in ('obj', 'idk'):
        p = os.path.join(ROOT, 'content', 'models', sub, name + '.ob2')
        if os.path.exists(p):
            m = parse_ob2(open(p, 'rb').read())
            return {'fcount': m['fcount'], 'vcount': len(m['vx']),
                    'pri': m['pri'], 'vlab': m['vlab'],
                    'geom': (m['vx'], m['vy'], m['vz'], m['fa'], m['fb'], m['fc'])}
    return None


def hist(pri):
    return dict(sorted(collections.Counter(pri).items()))


WEAR_KEYS = (('manwear', 'manwear'), ('manwear2', 'manwear2'), ('womanwear', 'womanwear'),
             ('womanwear2', 'womanwear2'), ('manhead', 'manhead'), ('womanhead', 'womanhead'))


# DELIBERATE DEPARTURES, so they do not read as drift for ever. A line here is a model this
# build has knowingly changed from its OSRS original, and the reason it was changed. Anything
# not listed that differs is still a finding.
_DEAD_BONE = ('a label with no bone behind it in this skeleton: the vertices followed nothing. '
              'Remapped to the 377 bone that owns that part of the body')
ADAPTED = dict(
    [(n, '161 -> 28, ' + _DEAD_BONE + ' - every one of the 2006 cache\'s sixteen shields uses 28')
     for n in ('obj_falador_shield_1_womanwear', 'obj_falador_shield_2_womanwear',
               'obj_falador_shield_3_womanwear', 'obj_falador_shield_4_womanwear')] +
    [(n, '157 -> 1, ' + _DEAD_BONE + ' - the whole hat was on 157 and never moved at all')
     for n in ('obj_crier_hat_manwear', 'obj_crier_hat_womanwear',
               'obj_farmers_strawhat_manwear')] +
    [(n, '166/167/168 -> 44/43/39, ' + _DEAD_BONE + ' - the robe\'s trim tore at the hip')
     for n in ('obj_ancient_robe_legs_womanwear', 'obj_armadyl_robe_legs_womanwear',
               'obj_bandos_robe_legs_womanwear', 'obj_guthix_robe_legs_womanwear',
               'obj_saradomin_robe_legs_womanwear', 'obj_zamorak_robe_legs_womanwear',
               'obj_eye_bottoms_manwear', 'obj_eye_bottoms_womanwear',
               'obj_hunter_legs_manwear', 'obj_hunter_legs_womanwear',
               'obj_third_age_druidic_robe_bottoms_manwear',
               'obj_third_age_druidic_robe_bottoms_womanwear',
               'obj_zealots_bottom_manwear', 'obj_zealots_bottom_womanwear')]
)


def models_2006():
    """Every worn model the 2006 cache's own item table names.

    OSRS IS NOT THE REFERENCE FOR THESE. The unpacked 377 configs are this build's source for
    them, their files have one commit apiece - the bulk import - and Old School has had twenty
    years to change its own copy. The pirate diving backpack has 28 faces at priority 1 in OSRS
    and 10 here, and 10 is what Jagex shipped in 2006; "fixing" it would have been importing a
    later revision of someone else's game into a 377 server. Twenty-one of the first sweep's
    thirty-one differences were this.
    """
    p = os.path.join(ROOT, 'content', 'scripts', '_unpack', '377', 'all.obj')
    if not os.path.exists(p):
        return set()
    txt = open(p, encoding='utf-8', errors='replace').read()
    out = set()
    for k in ('manwear', 'manwear2', 'womanwear', 'womanwear2', 'manhead', 'womanhead'):
        out.update(m.split(',')[0].strip() for m in re.findall(r'^%s=(.+)$' % k, txt, re.M))
    return {n for n in out if n}


def our_items():
    """Every worn item this build ships: name -> {slot key: local model name}."""
    content = os.path.join(ROOT, 'content')
    out = {}
    for root, _, files in os.walk(content):
        if os.sep + '.git' in root:
            continue
        for f in files:
            if not f.endswith('.obj'):
                continue
            name, worn = None, {}
            def flush():
                if name and worn:
                    out.setdefault(name.lower(), worn)
            for ln in open(os.path.join(root, f), encoding='utf-8', errors='replace'):
                ln = ln.strip()
                if ln.startswith('['):
                    flush(); name, worn = None, {}
                elif ln.startswith('name='):
                    name = ln.split('=', 1)[1].strip()
                else:
                    k = ln.split('=', 1)[0]
                    if k in [a for a, _ in WEAR_KEYS]:
                        v = ln.split('=', 1)[1].split(',')[0].strip()
                        if v:
                            worn[k] = v
            flush()
    return out


def sweep_pairs(cache):
    """Match our worn items to OSRS's by item name, and pair model slot for model slot.

    NAME IS THE ONLY KEY THERE IS. The import records no OSRS id against most of what it
    brought over, so the item table's own names are what joins the two. A name that matches
    the wrong item is caught downstream: a pair whose face counts disagree is reported as a
    different mesh rather than as a divergence.
    """
    from objconfig474 import load_all
    osrs = {}
    for i, o in load_all(cache).items():
        nm = (o.get('name') or '').lower()
        if nm and nm != 'null':
            osrs.setdefault(nm, o)
    pairs, unmatched = [], 0
    for nm, worn in sorted(our_items().items()):
        o = osrs.get(nm)
        if o is None:
            unmatched += 1
            continue
        for ours_key, osrs_key in WEAR_KEYS:
            if ours_key in worn and o.get(osrs_key):
                pairs.append((worn[ours_key], o[osrs_key]))
    # one local model can be named by several items; compare each once
    seen, out = set(), []
    for n, m in pairs:
        if (n, m) not in seen:
            seen.add((n, m)); out.append((n, m))
    return out, unmatched


def variants_from_spec():
    """The Max cape variants, whose OSRS worn model ids the spec records as provenance."""
    spec = json.load(open(os.path.join(ROOT, 'content', 'tools', 'maxcapevariantspec.json')))
    out = []
    for v in spec['variants']:
        for part in ('cape', 'hood'):
            blk = v.get(part) or {}
            for slot in ('manwear', 'womanwear'):
                mid = blk.get(slot)
                if not mid:
                    continue
                out.append(('obj_%s_max_%s_%s' % (v['key'], 'cape' if part == 'cape' else 'hood',
                                                  slot), mid))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs', nargs='*', metavar='name=osrs_id')
    ap.add_argument('--cache', default=os.path.join(ROOT, 'caches', 'osrs'))
    ap.add_argument('--variants', action='store_true',
                    help='every Max cape variant whose OSRS id the spec records')
    ap.add_argument('--sweep', action='store_true',
                    help='every worn model whose item name matches an OSRS item, by that name')
    ap.add_argument('--quiet', action='store_true', help='only print models that differ')
    a = ap.parse_args()

    jobs = [(p.split('=')[0], int(p.split('=')[1])) for p in a.pairs]
    if a.variants:
        jobs += variants_from_spec()
    if a.sweep:
        pairs, unmatched = sweep_pairs(a.cache)
        jobs += pairs
        print('# %d worn models matched to an OSRS item by name; %d of our items have no '
              'OSRS item of that name' % (len(pairs), unmatched))
    if not jobs:
        ap.error('give at least one name=osrs_id, or --variants, or --sweep')

    store = Store(a.cache)
    native = models_2006()
    bad = 0
    tally = collections.Counter()
    for name, mid in jobs:
        o = osrs_model(store, mid)
        n = ours_model(name)
        lines = []
        def out(line):
            lines.append(line)
        if n is None:
            # a god Max cape variant has no mesh of its own: it is the plain cape with a config
            # recolour, so there is nothing here to compare and that is not a fault
            tally['no mesh of its own'] += 1
            if not a.quiet:
                print('%-46s no mesh of its own (a config recolour)' % name)
            continue
        if o is None:
            tally['OSRS model unreadable'] += 1
            print('%-46s OSRS %-6d unreadable' % (name, mid))
            continue
        fo, po, fn, pn = o['fcount'], o['pri'], n['fcount'], n['pri']
        out('%s' % name)
        out('   OSRS %-6d %4df  %s' % (mid, fo, hist(po)))
        out('   ours        %4df  %s' % (fn, hist(pn)))

        if fo != fn or o['geom'] != n['geom']:
            # a name collision, not a fault: two different items called the same thing. The
            # priorities of two different meshes are not comparable at all.
            out('   DIFFERENT MESH (%d faces against %d, geometry %s) - not comparable'
                % (fn, fo, 'differs' if fo == fn else 'n/a'))
            tally['different mesh (name collision)'] += 1
            if not a.quiet:
                for l in lines:
                    print(l)
            continue

        moves = collections.Counter((x, y) for x, y in zip(po, pn) if x != y)
        for (src, dst), k in sorted(moves.items(), key=lambda kv: -kv[1]):
            out('   %4d faces moved %d -> %d   (%s -> %s)'
                % (k, src, dst, WHERE.get(src, '?'), WHERE.get(dst, '?')))

        # VERTEX LABELS ARE THE OTHER HALF. A priority says what covers what; a label says which
        # bone a vertex follows, and two models sharing a vertex POSITION but not its label come
        # apart the moment the limb bends. That is what a gap at a wrist is, and no draw order
        # closes one.
        lo, ln = o.get('vlab'), n.get('vlab')
        labdiff = False
        if lo is None and ln is None:
            pass
        elif lo is None or ln is None or len(lo) != len(ln):
            out('   vertex labels: OSRS %s, ours %s'
                % ('none' if lo is None else len(lo), 'none' if ln is None else len(ln)))
            labdiff = True
        else:
            lmoves = collections.Counter((x, y) for x, y in zip(lo, ln) if x != y)
            for (src, dst), k in sorted(lmoves.items(), key=lambda kv: -kv[1]):
                out('   %4d vertices relabelled %d -> %d' % (k, src, dst))
            labdiff = bool(lmoves)

        if moves or labdiff:
            if name in ADAPTED:
                tally['deliberately adapted'] += 1
                if not a.quiet:
                    for l in lines:
                        print(l)
                    print('   adapted on purpose: %s' % ADAPTED[name])
                continue
            if name in native:
                # a 2006 model: our source is the 377 cache, not Old School's later copy of it
                tally["2006 model, OSRS has changed its copy since"] += 1
                if not a.quiet:
                    for l in lines:
                        print(l)
                        print('   (2006 model - OSRS is not the reference for this one)')
                continue
            bad += 1
            tally['priorities differ'] += bool(moves)
            tally['labels differ'] += bool(labdiff)
            for l in lines:
                print(l)
        else:
            tally['identical'] += 1
            if not a.quiet:
                for l in lines:
                    print(l)
                print('   identical, face for face and label for label')

    if a.sweep or a.quiet:
        print()
        for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
            print('%6d  %s' % (v, k))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
