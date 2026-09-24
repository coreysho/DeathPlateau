#!/usr/bin/env python3
"""Charter ships, from 474: the moored ships and their piers, Trader Stan and his crew, and the
charter map. Everything the hand-written scripts (content scripts/charter/scripts/charter.rs2) stand on.

    python tools/models/gencharter474.py "caches/474 cache" --content=<content checkout>

Charter ships came in on 22 August 2006 (https://oldschool.runescape.wiki/w/Charter_ship), three
months after this build's cache. 474 (October 2007) has all of it, so all of it comes from there:

THE DOCKS. The charter update did not just add npcs - it built a pier and moored a ship at every
port, and those are MAP changes: where the crew stand in 474 is open water here. Diffing each port's
map square, 474 against this build, leaves one compact block per port - the pier (level-1 bridge
tiles, overlay 42, over the water) and the ship beside it - and nothing else nearby, so each block is
copied whole: every tile on all four levels and every loc inside PORTS' rectangles, replacing what
was there. The rectangles are the bounding boxes of that diff (terrain other than heights, or any
loc), found by clustering the differing tiles; everything outside them is left exactly as it was,
line for line. A 474 loc id is resolved the way import474map.py resolves one - reused where this
build has the same object, imported as loc474_<id> where it does not - except the gangplanks. 474
gives each ship two, an even id on the pier and the odd one after it on the ship's side (the pair
Musa Point's Karamja boat has too, sarimshipplank_on/_off), and they become charter_gangplank_on and
charter_gangplank_off: general_use's gangplank_board and gangplank_disembark, so Cross works as it
does on every other ship.

  left out  Mos Le'Harmless - its charter pier is in m57_45, which this build does not have at all;
            Corsair Cove - not in 474 (2016) and not in this map. Port Tyras's square also differs
            from 474 over the whole of the land east of the pier (474 re-flagged the forest), so
            only the pier-and-ship block is taken there, like everywhere else.

THE CREW are 474's npcs 4650 (Trader Stan) and 4651-4656 (the six crewmembers), with their models,
chat heads and recolours. Model files are shared by content name where this build already has the
same bytes, and copied as npc_trader_<474 model> where it does not. The crewmembers are numbered as
the OSRS wiki numbers them (Trader_Crewmember, versions 1-6), matched by their models, so each has
its own examine. Two stand on each pier, on the tiles the wiki's LocLines give, and Trader Stan
beside them on Port Sarim's; they are written into the maps' NPC sections.

THE MAP is 474 interface 95: the map of the seas (a model, 474's 17361), a port marker (17360, lit
17359 under the mouse) and label for each port, and the close X. 95's port buttons are layers; here
each port is a layer <port>_port holding its marker, its label and one click box over both, whose
hover layer is the lit marker - so one trigger per port, [if_button,charter:<port>], and the script
hides a port by hiding its layer. Mos Le'Harmless is left out with its port. Crandor is kept: it is
on 474's map, and the crew have a line for anyone who asks to go there.

Also written: charter/configs/charter_docks.constant - each port's landing tile, on the deck beside
the ship's gangplank, which is where a charter put you in 2007 (RS3 moved it to the dock in 2017:
https://runescape.wiki/w/Charter_ship, update history).
"""
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
CONTENT = os.path.join(ROOT, 'content')

IF_GID = 95
MAP_MODEL, PORT_MODEL, PORT_LIT = 17361, 17360, 17359

# key: (474 interface 95's button layer, the map rectangles [(square, x0, x1, z0, z1) local, inclusive],
#       the 474 id of the pier-side gangplank)
PORTS = {
    # Port Sarim's block also takes in the ship that was already moored north of it (x 24-36, z 59-63),
    # which 474 recoloured; only the new pier's jetty (x 22-23) is taken past z 58, and that ship is
    # left as this build has it
    'sarim':     (28, [('47_49', 22, 42, 49, 58), ('47_49', 22, 23, 59, 63), ('47_50', 22, 25, 0, 2)], 17404),
    'catherby':  (23, [('43_53', 27, 52, 18, 28)], 17394),
    'brimhaven': (26, [('43_50', 7, 21, 24, 50)], 17400),
    'musa':      (25, [('46_49', 9, 16, 11, 34)], 17398),
    'khazard':   (27, [('41_49', 45, 62, 1, 12)], 17402),
    'phasmatys': (22, [('57_54', 53, 61, 41, 59)], 17392),
    'shipyard':  (24, [('46_47', 50, 58, 11, 35)], 17396),
    'tyras':     (21, [('33_48', 22, 42, 48, 57)], 17408),
}
# on the map but not a port of this build (see the docstring)
MAP_ONLY = {'crandor': 30}
GANGPLANKS = range(17392, 17410)

# 474 npc -> (content name, examine from the OSRS wiki)
NPCS = [
    (4650, 'trader_stan', 'With the prices he charges, no wonder he can afford to look so sharp.'),
    (4655, 'trader_crewmember_1', 'High heels on a ship? What is she thinking?'),
    (4652, 'trader_crewmember_2', 'That suit looks a little briny around the edges.'),
    (4653, 'trader_crewmember_3', 'First storm he is in that hat will blow away.'),
    (4656, 'trader_crewmember_4', 'The effect is sort of spoiled by all those tattoos.'),
    (4654, 'trader_crewmember_5', "She'll never be able to climb rigging in that."),
    (4651, 'trader_crewmember_6', "It's going to be hard to climb rigging dressed like that."),
]
# who stands where: world x, z on 474's pier - the wiki's Trader Crewmember LocLines, and Trader Stan
# beside them on Port Sarim's (level 0 - the pier is a bridge over the water)
SPAWNS = {
    'sarim':     [('trader_stan', 3041, 3193), ('trader_crewmember_2', 3039, 3193), ('trader_crewmember_1', 3042, 3192)],
    'catherby':  [('trader_crewmember_3', 2796, 3415), ('trader_crewmember_4', 2797, 3415)],
    'brimhaven': [('trader_crewmember_5', 2759, 3239), ('trader_crewmember_6', 2760, 3239)],
    'musa':      [('trader_crewmember_2', 2954, 3156), ('trader_crewmember_1', 2954, 3157)],
    'khazard':   [('trader_crewmember_6', 2673, 3144), ('trader_crewmember_5', 2675, 3144)],
    'phasmatys': [('trader_crewmember_4', 3701, 3502), ('trader_crewmember_3', 3701, 3503)],
    'shipyard':  [('trader_crewmember_1', 3001, 3033), ('trader_crewmember_2', 3001, 3034)],
    'tyras':     [('trader_crewmember_5', 2145, 3122), ('trader_crewmember_6', 2144, 3122)],
}
HUMAN_WALK = 'human_walk_f,human_walk_b,human_walk_l,human_walk_r'


def out_dir(*parts):
    p = os.path.join(CONTENT, 'scripts', 'charter', *parts)
    os.makedirs(os.path.dirname(p) if os.path.splitext(p)[1] else p, exist_ok=True)
    return p


def write(path, lines):
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines) + '\n')


def content_models():
    """sha1 of every content model file -> its name, so a 474 model this build already has is shared."""
    out = {}
    for base, _, files in os.walk(os.path.join(CONTENT, 'models')):
        for fn in files:
            if fn.endswith('.ob2'):
                out.setdefault(hashlib.sha1(open(os.path.join(base, fn), 'rb').read()).hexdigest(), fn[:-4])
    return out


# ---------------------------------------------------------------- the crew

def npcs(store, have):
    from npcconfig474 import load_all
    from import474 import hsl16_to_rgb15
    from animconv474 import pack_append
    defs = load_all(store.path)
    mdir = os.path.join(CONTENT, 'models', 'npc')
    os.makedirs(mdir, exist_ok=True)
    new_models = []

    def model(mid):
        data = store.st.read(7, mid)
        h = hashlib.sha1(data).hexdigest()
        if h in have:
            return have[h]
        name = 'npc_trader_%d' % mid
        open(os.path.join(mdir, name + '.ob2'), 'wb').write(data)
        have[h] = name
        new_models.append(name)
        return name

    lines = ['// Trader Stan and his crew - 474 npcs 4650-4656, GENERATED by LostCityServer',
             '// tools/models/gencharter474.py; regenerate rather than edit. Examines are the OSRS wiki\'s; the',
             '// crewmembers are numbered as the wiki numbers them (matched by their models). Scripts:',
             '// charter/scripts/charter.rs2 (Talk-To, Charter) and the Trading Post (Trade).']
    for nid, key, examine in NPCS:
        d = defs[nid]
        lines += ['', '[%s]' % key, 'name=%s' % d['name'], 'desc=%s' % examine]
        for i, mid in enumerate(d['models'], 1):
            lines.append('model%d=%s' % (i, model(mid)))
        for i, mid in enumerate(d.get('heads') or [], 1):
            lines.append('head%d=%s' % (i, model(mid)))
        for i, (s, t) in enumerate(d.get('recol') or [], 1):
            (sv, ok1), (tv, ok2) = hsl16_to_rgb15(s), hsl16_to_rgb15(t)
            if not (ok1 and ok2):
                print('  note: %s recol%d has no RGB15 preimage (%d -> %d), written raw' % (key, i, s, t))
            lines += ['recol%ds=%d' % (i, sv), 'recol%dd=%d' % (i, tv)]
        # 474's 808 and 819-822, which are this build's own human stance and walk
        assert (d['readyanim'], d['walkanim']) == (808, 819), key
        lines += ['readyanim=human_ready', 'walkanim=' + HUMAN_WALK]
        for k, v in sorted(d['ops'].items()):
            lines.append('op%d=%s' % (k + 1, v))
        # the crew keep to their pier
        lines += ['wanderrange=1', 'category=charter_trader']
    write(os.path.join(out_dir('configs'), 'charter.npc'), lines)
    pack_append(os.path.join(CONTENT, 'pack', 'model.pack'), new_models)
    ids, _ = pack_append(os.path.join(CONTENT, 'pack', 'npc.pack'), [k for _, k, _ in NPCS])
    return ids, new_models


# ---------------------------------------------------------------- the docks

def loc_line(lid, lv, x, z, shape, rot):
    if shape == 10 and rot == 0:
        return '%d %d %d: %d' % (lv, x, z, lid)
    if rot == 0:
        return '%d %d %d: %d %d' % (lv, x, z, lid, shape)
    return '%d %d %d: %d %d %d' % (lv, x, z, lid, shape, rot)


def patch_square(path, rects, tiles, locs, spawns, charter_npc_ids):
    """Rewrite one .jm2 in place: inside rects, the MAP tiles and LOCs become 474's; the NPC section
    loses every charter npc and gets `spawns`. Every other line is left exactly as it was, and new
    lines go at the end of their section."""
    import jm2
    raw = open(path, newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    inside = lambda x, z: any(x0 <= x <= x1 and z0 <= z <= z1 for x0, x1, z0, z1 in rects)
    lines = raw.split(nl)
    trailing = lines[-1] == ''
    if trailing:
        lines = lines[:-1]
    secs = [[None, []]]
    for l in lines:
        if l.startswith('===='):
            secs.append([l, []])
        else:
            secs[-1][1].append(l)
    name = lambda h: h.strip('= ').strip() if h else None
    if spawns and not any(name(h) == 'NPC' for h, _ in secs):
        at = next(i for i, (h, _) in enumerate(secs) if name(h) == 'LOC') + 1
        secs.insert(at, ['==== NPC ====', []])
    done = set()
    pending = list(locs)
    for sec in secs:
        kind, body, keep = name(sec[0]), sec[1], []
        for l in body:
            m = re.match(r'(\d) (\d+) (\d+):(.*)', l)
            if m:
                lv, x, z, rest = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4).split()
                if kind == 'MAP' and (lv, x, z) in tiles:
                    done.add((lv, x, z))
                    t = jm2.tile_text(tiles[(lv, x, z)])
                    if t:
                        keep.append('%d %d %d: %s' % (lv, x, z, t))
                    continue
                if kind == 'LOC' and inside(x, z):
                    # a loc 474 has too stays as the line it was, so the diff is only what changed
                    p = [int(v) for v in rest]
                    same = (p[0], lv, x, z, p[1] if len(p) > 1 else 10, p[2] if len(p) > 2 else 0)
                    if same in pending:
                        pending.remove(same)
                        keep.append(l)
                    continue
                if kind == 'NPC' and int(rest[0]) in charter_npc_ids:
                    continue
            keep.append(l)
        new = []
        if kind == 'MAP':
            new = ['%d %d %d: %s' % (k[0], k[1], k[2], jm2.tile_text(tiles[k])) for k in sorted(tiles)
                   if k not in done and jm2.tile_text(tiles[k])]
        elif kind == 'LOC':
            new = [loc_line(*l) for l in sorted(pending, key=lambda l: (l[1], l[2], l[3], l[0]))]
        elif kind == 'NPC':
            new = ['%d %d %d: %d' % (lv, x, z, nid) for nid, lv, x, z in spawns]
        k = len(keep)
        while k and keep[k - 1] == '':
            k -= 1
        blanks = keep[k:]
        # a section that is not the last is closed by a blank line, as the files have them
        if sec is not secs[-1] and sec[0] is not None and not blanks:
            blanks = ['']
        sec[1] = keep[:k] + new + blanks
    out = []
    for h, body in secs:
        if h is not None:
            out.append(h)
        out.extend(body)
    text = nl.join(out) + (nl if trailing else '')
    open(path, 'w', newline='').write(text)


def docks(npc_ids):
    from import474map import Cache474, Resolver, import_loc
    from osrslocimport import Content377
    from animconv474 import pack_append
    c = Cache474(CACHE)
    # this file is rewritten below; a rerun must not mistake its own last imports for someone else's
    mine = os.path.join(out_dir('configs'), 'charter_docks.loc')
    if os.path.exists(mine):
        os.remove(mine)
    c3 = Content377(CONTENT)
    R = Resolver(c, c3)

    # gather 474's tiles and locs inside every rectangle
    per_square = {}
    for key, (_, rects, plank) in PORTS.items():
        for reg, x0, x1, z0, z1 in rects:
            per_square.setdefault(reg, []).append((x0, x1, z0, z1))
    plan, square_data = {}, {}
    for reg, rects in per_square.items():
        land = c.terrain(reg)
        inside = lambda x, z: any(x0 <= x <= x1 and z0 <= z <= z1 for x0, x1, z0, z1 in rects)
        tiles = {k: v for k, v in land.items() if inside(k[1], k[2])}
        locs = [l for l in c.locs_of(reg) if inside(l[2], l[3])]
        square_data[reg] = (rects, tiles, locs)
        for l in locs:
            if l[0] not in plan and l[0] not in GANGPLANKS:
                plan[l[0]] = R.resolve(l[0])

    # loc474_<id> already imported by another generator is that generator's; use it
    for oid, (k, v) in list(plan.items()):
        if k == 'import' and 'loc474_%d' % v in c3.cfg:
            plan[oid] = ('reuse', next(i for i, n in c3.ids.items() if n == 'loc474_%d' % v))

    lines = ['// The charter ships\' piers and moored ships, from 474 - GENERATED by LostCityServer',
             '// tools/models/gencharter474.py; regenerate rather than edit. The locs 474 had and this build',
             '// did not, and the two gangplanks every charter ship has.', '']
    # the gangplanks: 474's model 1844, which is this build's too
    plank_model = HAVE[hashlib.sha1(c.model(1844)).hexdigest()]
    # a loc names its model without the shape suffix the file carries (_8, a centrepiece)
    plank_model = re.sub(r'_8$', '', plank_model)
    for key, cat, desc in (('on', 'gangplank_board', 'Handy for boarding boats.'),
                           ('off', 'gangplank_disembark', 'Handy for leaving boats.')):
        lines += ['[charter_gangplank_%s]' % key, 'name=Gangplank', 'desc=%s' % desc, 'model=%s' % plank_model,
                  'op1=Cross', 'active=yes', 'sharelight=yes', 'category=%s' % cat, '']
    model_files, notes, newname = {}, [], {}
    for oid, (k, v) in sorted(plan.items()):
        if k == 'import' and v not in newname:
            newname[v] = import_loc(c, v, lines, model_files, notes)
    for n in notes:
        print('  note:', n)
    write(os.path.join(out_dir('configs'), 'charter_docks.loc'), lines)
    names = ['charter_gangplank_on', 'charter_gangplank_off'] + [newname[k] for k in sorted(newname)]
    locids, _ = pack_append(os.path.join(CONTENT, 'pack', 'loc.pack'), names)
    pack_append(os.path.join(CONTENT, 'pack', 'model.pack'), sorted(model_files))
    os.makedirs(os.path.join(CONTENT, 'models', 'loc'), exist_ok=True)
    for n, b in model_files.items():
        open(os.path.join(CONTENT, 'models', 'loc', n + '.ob2'), 'wb').write(b)

    def lid(oid):
        if oid in GANGPLANKS:
            return locids['charter_gangplank_on' if oid % 2 == 0 else 'charter_gangplank_off']
        k, v = plan[oid]
        return v if k == 'reuse' else locids[newname[v]] if k == 'import' else None

    # the crew, by square
    spawns = {}
    for port, who in SPAWNS.items():
        for key, x, z in who:
            reg = '%d_%d' % (x // 64, z // 64)
            # the pier is a level-1 bridge, which the engine folds down to level 0 for tiles and locs
            # but not for npcs (GameMap.loadNpcs): an npc on it is written on level 0
            spawns.setdefault(reg, []).append((npc_ids[key], 0, x % 64, z % 64))
    charter_ids = set(npc_ids.values())
    dropped = 0
    for reg in sorted(set(square_data) | set(spawns)):
        rects, tiles, locs = square_data.get(reg, ([], {}, []))
        out = []
        for l in locs:
            i = lid(l[0])
            if i is None:
                dropped += 1
                continue
            out.append((i, l[1], l[2], l[3], l[4], l[5]))
        patch_square(os.path.join(CONTENT, 'maps', 'm%s.jm2' % reg), rects, tiles, out, spawns.get(reg, []), charter_ids)
        print('  m%s: %d tiles, %d locs from 474; %d crew' % (reg, len(tiles), len(out), len(spawns.get(reg, []))))
    print('  locs: %d reused, %d imported, %d dropped' % (sum(1 for k, _ in plan.values() if k == 'reuse'), len(newname), dropped))

    # where a charter lands you: the deck tile gangplank_board would put you on from the pier-side plank
    const = ['// Where a charter ship puts you down: on the deck beside each ship\'s gangplank, as in 2007.',
             '// GENERATED by LostCityServer tools/models/gencharter474.py from 474\'s gangplank positions.', '']
    for key, (_, rects, plank) in PORTS.items():
        for reg, *_ in rects:
            hit = [l for l in square_data[reg][2] if l[0] == plank]
            if hit:
                break
        _, lv, x, z, shape, rot = hit[0]
        bx, bz = int(reg.split('_')[0]) * 64, int(reg.split('_')[1]) * 64
        # gangplank.rs2: west/north boards +1, east/south -1; the deck is one level up, two tiles on
        d = 1 if rot in (0, 1) else -1
        ax, az = (x + 2 * d, z) if rot in (0, 2) else (x, z - 2 * d)
        # the plank sits on the bridge (file level 1 = level 0 in the world); the deck is level 1
        level = lv
        const.append('^charter_%s_arrive = %d_%d_%d_%d_%d' % (key, level, (bx + ax) // 64, (bz + az) // 64, (bx + ax) % 64, (bz + az) % 64))
    write(os.path.join(out_dir('configs'), 'charter_docks.constant'), const)


# ---------------------------------------------------------------- the map

def interface(store):
    from port474if import Converter, content_sprite_index
    from animconv474 import pack_append
    conv = Converter(store, IF_GID, 'charter', {}, {}, 'layer')
    conv.index = content_sprite_index(os.path.join(CONTENT, 'sprites'))
    c = conv.comps
    mdir = os.path.join(CONTENT, 'models', 'com')
    os.makedirs(mdir, exist_ok=True)
    mnames = {MAP_MODEL: 'com_charter_map', PORT_MODEL: 'com_charter_port', PORT_LIT: 'com_charter_port_lit'}
    for mid, name in mnames.items():
        open(os.path.join(mdir, name + '.ob2'), 'wb').write(store.model(mid))
    pack_append(os.path.join(CONTENT, 'pack', 'model.pack'), sorted(mnames.values()))

    lines = ["// 474's charter map (474 interface 95), GENERATED by LostCityServer tools/models/gencharter474.py -",
             '// regenerate it rather than editing by hand. Each port is a layer, <port>_port, with a click box',
             '// [if_button,charter:<port>]; charter/scripts/charter.rs2 hides the ones you cannot sail to.']

    def com(name, kv):
        lines.append('')
        lines.append('[%s]' % name)
        lines.extend('%s=%s' % (k, v) for k, v in kv)

    m = c[0]
    com('map', [('type', 'model'), ('x', m['x']), ('y', m['y']), ('width', m['width']), ('height', m['height']),
                ('model', mnames[MAP_MODEL]), ('zoom', m['zoom']), ('xan', m['xan']), ('yan', m['yan'])])
    ports = dict((k, v[0]) for k, v in PORTS.items())
    ports.update(MAP_ONLY)
    for key, fid in sorted(ports.items(), key=lambda kv: kv[1]):
        lay = c[fid]
        kids = [k for k, v in c.items() if v.get('parent') == fid]
        marker = next(c[k] for k in kids if c[k]['type'] == 6)
        label = next(c[k] for k in kids if c[k]['type'] == 4)
        hover = c[lay['overlayer2']]
        lit = next(v for v in c.values() if v.get('parent') == lay['overlayer2'] and v['type'] == 6)
        # the port's own layer: 474's button layer, grown to take in the marker it draws above itself
        top = min(0, marker['y'])
        left = min(0, marker['x'])
        w = max(lay['width'], marker['x'] + marker['width']) - left
        h = max(lay['height'], marker['y'] + marker['height']) - top
        px, py = lay['x'] + left, lay['y'] + top
        com('%s_port' % key, [('type', 'layer'), ('x', px), ('y', py), ('width', w), ('height', h)])
        com('%s_marker' % key, [('layer', '%s_port' % key), ('type', 'model'), ('x', marker['x'] - left),
                                ('y', marker['y'] - top), ('width', marker['width']), ('height', marker['height']),
                                ('model', mnames[marker['model']]), ('zoom', marker['zoom']), ('xan', marker['xan']),
                                ('yan', marker['yan'])])
        text = label['text'].strip()
        com('%s_label' % key, [('layer', '%s_port' % key), ('type', 'text'), ('x', label['x'] - left),
                               ('y', label['y'] - top), ('width', label['width']), ('height', label['height']),
                               ('font', 'p12_full'), ('shadowed', 'yes'), ('text', text),
                               ('colour', '0x%06X' % (label['colour'] & 0xFFFFFF))])
        # the click box is 474's button exactly - its layer's own rectangle, the label's row. Grown to
        # take in the marker as well, neighbouring ports' boxes would overlap (Crandor sits between
        # Catherby and Brimhaven, Karamja just under Port Sarim). 474's buttons carry no op text, so
        # the port's name is the menu line.
        com(key, [('layer', '%s_port' % key), ('type', 'text'), ('x', -left), ('y', -top), ('overlayer', '%s_hover' % key),
                  ('buttontype', 'normal'), ('width', lay['width']), ('height', lay['height']), ('font', 'p12_full'),
                  ('text', ''), ('option', text)])
        # 474's hover layer: the lit marker, over the unlit one
        com('%s_hover' % key, [('type', 'layer'), ('x', lay['x'] + hover['x']), ('y', lay['y'] + hover['y']),
                               ('width', hover['width']), ('height', hover['height']), ('hide', 'yes')])
        com('%s_hover_marker' % key, [('layer', '%s_hover' % key), ('type', 'model'), ('x', lit['x']), ('y', lit['y']),
                                      ('width', lit['width']), ('height', lit['height']),
                                      ('model', mnames[lit['model']]), ('zoom', lit['zoom']), ('xan', lit['xan']),
                                      ('yan', lit['yan'])])
    # 474's X (539), and its lit copy (540) in a layer shown under the mouse; the lit one closes too,
    # since this client never lets you click through a hidden layer's area to what is under it
    x, lay, litx = c[49], c[51], c[50]
    com('close_frame', [('type', 'graphic'), ('x', x['x']), ('y', x['y']), ('overlayer', 'close_layer'),
                        ('buttontype', 'close'), ('width', x['width']), ('height', x['height']),
                        ('graphic', conv.sprite(x['graphic']))])
    com('close_layer', [('type', 'layer'), ('x', lay['x']), ('y', lay['y']), ('width', lay['width']),
                        ('height', lay['height']), ('hide', 'yes')])
    com('close', [('layer', 'close_layer'), ('type', 'graphic'), ('x', litx['x']), ('y', litx['y']), ('buttontype', 'close'),
                  ('width', litx['width']), ('height', litx['height']), ('graphic', conv.sprite(litx['graphic']))])
    write(os.path.join(out_dir('interfaces'), 'charter.if'), lines)
    return conv


class Store474:
    """The two things this needs from the cache: its folder and the model reader."""
    def __init__(self, path):
        from dat2 import Store
        from if3_474 import Cache
        self.path = path
        self.st = Store(path)
        self.store = self.st
        self.ifs = Cache(path)
        self.load = self.ifs.load

    def model(self, mid):
        return self.st.read(7, mid)


def main():
    global CONTENT, CACHE, HAVE
    args = [a for a in sys.argv[1:] if not a.startswith('--content=')]
    for a in sys.argv[1:]:
        if a.startswith('--content='):
            CONTENT = os.path.abspath(a.split('=', 1)[1])
    CACHE = os.path.abspath(args[0])
    store = Store474(CACHE)
    HAVE = content_models()
    ids, new_models = npcs(store, HAVE)
    print('npcs: %s; %d new models' % (', '.join('%s=%d' % kv for kv in sorted(ids.items())), len(new_models)))
    conv = interface(store)
    new = conv.write_sprites(os.path.join(CONTENT, 'sprites'))
    print('interface: charter.if; sprites new: %s' % (' '.join(new) or '-'))
    for n in conv.notes:
        print('  note:', n)
    docks(ids)
    subprocess.check_call([sys.executable, os.path.join(CONTENT, 'tools', 'ifids.py'), 'charter'])


if __name__ == '__main__':
    main()
