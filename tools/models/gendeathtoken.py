#!/usr/bin/env python3
"""Build the Death token's model and the two wilderness characters' parts, and register them.

    python3 tools/models/gendeathtoken.py --content content

WHAT IT MAKES
  obj_death_token        a procedural fourteen-sided coin with the cache's skull pressed into the
                         face, merged into one mesh - this server's own currency
  npc_undertaker_*       the Undertaker's hat, coat, legs and cane, each a tinted copy
  npc_veteran_*          the one-armed veteran's armour, cape and boots, and his ONE arm

The token is a MERGED MESH - a procedural coin with the cache's skull pressed into its face - the
way tools/models/gentradingpostmodel.py builds the Trading Post out of parts.

The Undertaker is an ASSEMBLY, and his parts are TINTED COPIES rather than recolour pairs in the
npc config: a config carries at most six pairs and his coat, legs and hat have more distinct
colours than that between them. Tinting one part at a time keeps each model's vertex labels, which
is what the walk and ready animations deform - a merged figure would have none and would slide
about in a T-pose.

"""
import os, sys, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode, roundtrip

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument('--content', default='content', help='the content checkout to write into')
C = _ap.parse_args().content
MODELS = os.path.join(C, 'models', 'obj')

index = {}
for root, _dirs, files in os.walk(os.path.join(C, 'models')):
    for f in files:
        if f.endswith('.ob2'):
            index.setdefault(f[:-4], os.path.join(root, f))


def hsl(h, s, l):
    return (h << 10) | (s << 7) | l


def part(name):
    return parse_ob2(open(index[name], 'rb').read())


def blank():
    return dict(ver=2, vcount=0, fcount=0, vx=[], vy=[], vz=[], fa=[], fb=[], fc=[], colour=[],
                alpha=None, textured=0, priority=255, pri=[], tris=[], vlab=None, flab=None, finfo=None)


def transform(m, scale=1.0, dx=0, dy=0, dz=0):
    for i in range(m['vcount']):
        m['vx'][i] = int(round(m['vx'][i] * scale)) + dx
        m['vy'][i] = int(round(m['vy'][i] * scale)) + dy
        m['vz'][i] = int(round(m['vz'][i] * scale)) + dz
    return m


def scale3(m, sx, sy, sz):
    """Scale each axis on its own. A coin's device is struck in SHALLOW RELIEF - wide across the
    face, almost flat front to back - and a cache skull scaled evenly is a whole head glued on."""
    for i in range(m['vcount']):
        m['vx'][i] = int(round(m['vx'][i] * sx))
        m['vy'][i] = int(round(m['vy'][i] * sy))
        m['vz'][i] = int(round(m['vz'][i] * sz))
    return m


def tint(m, hue, sat, light_scale=1.0, skip=()):
    """Every face keeps its own lightness; only hue and saturation change, so the shading survives."""
    for i in range(m['fcount']):
        c = m['colour'][i]
        if c in skip:
            continue
        l = max(0, min(127, int((c & 0x7F) * light_scale)))
        m['colour'][i] = hsl(hue, sat, l)
    return m


def merge(parts):
    out = blank()
    any_alpha = any(p['alpha'] for p in parts)
    any_finfo = any(p.get('finfo') for p in parts)
    alpha, finfo = [], []
    for p in parts:
        vo, to = out['vcount'], len(out['tris'])
        out['vx'] += p['vx']; out['vy'] += p['vy']; out['vz'] += p['vz']
        out['fa'] += [a + vo for a in p['fa']]
        out['fb'] += [b + vo for b in p['fb']]
        out['fc'] += [c + vo for c in p['fc']]
        out['colour'] += p['colour']
        out['pri'] += [0] * p['fcount']
        alpha += p['alpha'] if p['alpha'] else [0] * p['fcount']
        fi = p.get('finfo') or [0] * p['fcount']
        finfo += [((f >> 2) + to) << 2 | (f & 3) if f & 2 else f for f in fi]
        out['tris'] += [tuple(v + vo for v in t) for t in (p.get('tris') or [])]
        out['vcount'] += p['vcount']
        out['fcount'] += p['fcount']
    if any_alpha:
        out['alpha'] = alpha
    if any_finfo:
        out['finfo'] = finfo
    return out


def _add(m, verts, faces, colour):
    base = m['vcount']
    for x, y, z in verts:
        m['vx'].append(int(round(x))); m['vy'].append(int(round(y))); m['vz'].append(int(round(z)))
    m['vcount'] += len(verts)
    for a, b, c in faces:
        m['fa'].append(a + base); m['fb'].append(b + base); m['fc'].append(c + base)
        m['colour'].append(colour); m['pri'].append(0)
    m['fcount'] += len(faces)
    return m


def coin(radius, thick, face, rim, sides=14):
    """A coin standing face-on: the n-gon is in the x/y plane and z is its axis.

    It is built face-on because that is the easy frame to press a stamp into - the skull is a
    standing model and its front is its -z - and then lie_flat() turns the finished coin over.
    """
    m = blank()
    ring_f = [(radius * math.cos(2 * math.pi * i / sides), radius * math.sin(2 * math.pi * i / sides), -thick / 2)
              for i in range(sides)]
    ring_b = [(x, y, thick / 2) for x, y, _ in ring_f]
    verts = ring_f + ring_b + [(0, 0, -thick / 2), (0, 0, thick / 2)]
    ct, cb = 2 * sides, 2 * sides + 1
    faces = [(ct, i, (i + 1) % sides) for i in range(sides)]
    faces += [(cb, sides + (i + 1) % sides, sides + i) for i in range(sides)]
    _add(m, verts, faces, face)
    base = m['vcount'] - (2 * sides + 2)
    for i in range(sides):
        j = (i + 1) % sides
        for a, b, c in ((i, sides + i, sides + j), (i, sides + j, j)):
            m['fa'].append(a + base); m['fb'].append(b + base); m['fc'].append(c + base)
            m['colour'].append(rim); m['pri'].append(0); m['fcount'] += 1
    return m


def lie_flat(m):
    """Tip a model that stands facing the camera onto its back, so its face points at the sky.

    (x, y, z) -> (x, z, -y). A proper rotation, so every face keeps its winding and nothing turns
    inside out. THE GROUND RENDER DRAWS THE MODEL AS IT IS BUILT - no 2d camera touches it - so a
    coin whose disc lies in the x/y plane stands on its edge in the world like a dropped wheel. A
    coin lies flat only if the mesh itself lies flat.
    """
    for i in range(m['vcount']):
        y, z = m['vy'][i], m['vz'][i]
        m['vy'][i] = z
        m['vz'][i] = -y
    return m


def sit_on_ground(m):
    """Drop a model so its lowest point is y=0 and it extends UPWARD into negative y.

    THIS IS WHAT CENTRES AN INVENTORY ICON, and it is not a convention worth breaking. The client
    aims the icon camera at model.minY / 2, where minY is max(-vy) - the model's height above the
    origin - because it assumes a model rests on the ground plane the way every cache model does.
    A mesh built symmetrically about y=0 gets a camera pointed at half its own half-height and
    renders low in the 32x32 frame, which is exactly what the first Death token did.
    """
    return transform(m, 1.0, 0, -max(m['vy']), 0)


def write(m, name):
    b = encode(m)
    ok, why = roundtrip(b, m)
    if not ok:
        raise SystemExit(f'{name} does not survive a round trip: {why}')
    open(os.path.join(MODELS, name + '.ob2'), 'wb').write(b)
    return name


# ---------------------------------------------------------------- the token
# Lightness 38, not 20: at 32 pixels on the inventory's own dark parchment a near-black disc is a
# hole, not a coin. The rim is lighter again so the edge catches and the shape reads as round.
# TUNED AGAINST THE CLIENT'S OWN ICON RENDER, not the offline previewer: ob2render.py lights a
# model more harshly than ObjType.method230 does, and a coin tuned to look right in the preview came
# out of the real renderer as pale stone with the skull washed off it. These numbers are what the
# CLIENT draws as black stone with a bone skull on it.
OBSIDIAN = hsl(0, 0, 40)
RIM = hsl(0, 0, 60)
FIELD = hsl(0, 0, 28)
BONE = hsl(7, 2, 100)


def centre(m, keep_z=False):
    """Put a part's own bounding box on the origin. A cache model is centred on whatever suited the
    item it was drawn for - the skull sits off to one side - and a stamp has to be centred on the
    coin, not on the modeller's convenience."""
    cx = (max(m['vx']) + min(m['vx'])) // 2
    cy = (max(m['vy']) + min(m['vy'])) // 2
    cz = 0 if keep_z else (max(m['vz']) + min(m['vz'])) // 2
    return transform(m, 1.0, -cx, -cy, -cz)


# THE COIN, and the stamp struck into it. The skull is a DEVICE, not an ornament: widened to fill
# the recessed field and flattened front to back so it reads as pressed stone, standing only a few
# units proud of the face. A cache skull at even scale is a whole head sitting on a disc, and at 32
# pixels it loses its eye sockets and becomes a pale smudge - which is the only thing that has to
# survive the size.
RADIUS, THICK = 32, 8
# Tuned against ObjIconRender at --mode 0 (a pack slot, not a cert's 1.5x), beside coins, bones and
# a tinderbox for scale: 1.55 fills the recessed field without climbing onto the rim, and the
# shallower 0.25 keeps the eye sockets black instead of letting the brow highlight flood them.
SKULL_XY, SKULL_DEPTH, SKULL_PROUD = 1.55, 0.25, 4


def death_token(xy=SKULL_XY, depth=SKULL_DEPTH, proud=SKULL_PROUD):
    c = coin(RADIUS, THICK, OBSIDIAN, RIM)
    # a recessed field for the skull to sit in, a touch darker than the face around it
    c = merge([c, coin(23, THICK - 1, FIELD, FIELD, sides=14)])
    skull = scale3(centre(part('obj_ghostskull')), xy, xy, depth)
    # push the stamp forward until its highest point stands `proud` above the coin's own face
    dz = int(round(-THICK / 2 - proud - min(skull['vz'])))
    skull = tint(transform(skull, 1.0, 0, 0, dz), 7, 2, light_scale=1.45)
    # Built standing, delivered lying down, resting on the ground: the first keeps the stamp easy to
    # place, the second is what the world render needs, the third is what the icon camera expects.
    return sit_on_ground(lie_flat(merge([c, skull])))


# ---------------------------------------------------------------- the Undertaker
# (source part, new name, hue, sat, lightness scale, colours left alone)
GOLD = hsl(10, 7, 86)
COAT = [
    ('obj_black_wizard_hat_g_manwear', 'npc_undertaker_hat', 0, 0, 0.55, ()),
    ('obj_black_elegant_shirt_manwear', 'npc_undertaker_coat', 0, 0, 0.60, ()),
    ('obj_black_elegant_shirt_manwear2', 'npc_undertaker_coat2', 0, 0, 0.60, ()),
    ('obj_black_elegant_legs_manwear', 'npc_undertaker_legs', 0, 0, 0.55, ()),
    ('obj_black_cane_manwear', 'npc_undertaker_cane', 0, 0, 0.70, ()),
    ('obj_black_wizard_hat_g_manhead', 'npc_undertaker_hat_head', 0, 0, 0.55, ()),
    # His beard, in the body and in the chathead, goes steel grey. It is one colour in the cache -
    # a dark brown the client lights up to tan - and a tan beard is the only warm thing on a man
    # whose whole design is black cloth with one gold band.
    ('idk_man_jaw_long', 'npc_undertaker_beard', 0, 0, 4.5, ()),
    ('idk_man_jaw_long_head', 'npc_undertaker_beard_head', 0, 0, 4.5, ()),
    # and boots, because he was standing in Edgeville barefoot
    ('obj_ikov_bootsoflightness_manwear', 'npc_undertaker_boots', 0, 0, 0.45, ()),
]


# ---------------------------------------------------------------- the one-armed veteran
# His arm is CUT, not implied: a *_manwear2 model is the pair of sleeves, symmetric about x, so
# dropping every face that lies on one side of the body leaves exactly one arm and the shoulder it
# hangs from. Named parts rather than a merge, for the same animation reason as the Undertaker.
VET = [
    ('obj_ancient_platebody_manwear', 'npc_veteran_body', 0, 0, 0.62),
    ('obj_macro_mime_legs_manwear', 'npc_veteran_legs', 0, 0, 0.55),
    ('obj_red_cape_manwear', 'npc_veteran_cape', 0, 6, 0.55),
    ('obj_ikov_bootsoflightness_manwear', 'npc_veteran_boots', 0, 0, 0.45),
]
# NO HEAD IN THAT LIST, ON PURPOSE. It used to hold obj_viking_helmet_manwear under the name
# npc_veteran_helm, on the strength of the name - and that model is NOT a helmet. The unpacker names
# a model after the first config that happened to reference it, and this one is the short-haired
# MAN'S HEAD (all.idk: man_head_shorthair model1). Tinting it hue 0 sat 1 at 0.62 did exactly what
# it says: it took a living man's face and made it grey. The npc now uses the cache head untinted
# and obj_pickpocket_guide_man as the chathead that goes with it, which is the pairing all.idk
# already states. A debugname is a label somebody's tool wrote, not a description - render it.


def cut_side(m, keep_negative=True, thresh=6, upper=None):
    """Drop every face whose three vertices all sit on one side of the body. Faces that straddle the
    middle are kept, so the chest and the shoulder survive and only the limb goes."""
    keep = []
    for i in range(m['fcount']):
        xs = [m['vx'][m['fa'][i]], m['vx'][m['fb'][i]], m['vx'][m['fc'][i]]]
        ys = [m['vy'][m['fa'][i]], m['vy'][m['fb'][i]], m['vy'][m['fc'][i]]]
        side = all(x > thresh for x in xs) if keep_negative else all(x < -thresh for x in xs)
        gone = side and (upper is None or all(y < upper for y in ys))
        if not gone:
            keep.append(i)
    for k in ('fa', 'fb', 'fc', 'colour', 'pri'):
        m[k] = [m[k][i] for i in keep]
    for k in ('finfo', 'flab', 'alpha'):
        if m.get(k):
            m[k] = [m[k][i] for i in keep]
    m['fcount'] = len(keep)
    return m


def main():
    made = []
    made.append(write(death_token(), 'obj_death_token'))
    src_name_of = {name: src for src, name, _h, _s, _l, _k in COAT}
    for src, name, hue, sat, ls, skip in COAT:
        if src not in index:
            print('   missing part:', src)
            continue
        m = tint(part(src), hue, sat, light_scale=ls, skip=skip)
        # the hat keeps its gold band: the brightest faces are the trim, and an undertaker's hat
        # with a gold band is the one touch of colour he is allowed
        if 'hat' in name:
            src = part(src_name_of[name])
            for i in range(m['fcount']):
                h = (src['colour'][i] >> 10) & 0x3F
                if 7 <= h <= 14:          # the trim's yellows, in the part's ORIGINAL colours
                    m['colour'][i] = GOLD
        made.append(write(m, name))
    for src, name, hue, sat, ls in VET:
        if src not in index:
            print('   missing part:', src)
            continue
        m = tint(part(src), hue, sat, light_scale=ls)
        # The pauldron goes with the arm. With it left on, a 377 platebody reads as a man standing
        # square on and the missing arm is invisible; taken off, the empty shoulder against the cape
        # is the first thing you see.
        if name == 'npc_veteran_body':
            m = cut_side(m, keep_negative=True, thresh=14, upper=-120)
        made.append(write(m, name))
    # the arms, with the right one taken off at the shoulder
    arms = tint(part('obj_ancient_platebody_manwear2'), 0, 0, light_scale=0.62)
    made.append(write(cut_side(arms, keep_negative=True), 'npc_veteran_arm'))
    print('wrote models:', ', '.join(made))

    # register, taking the next free ids
    pack = os.path.join(C, 'pack', 'model.pack')
    lines = open(pack, encoding='utf-8').read().replace('\r\n', '\n').rstrip('\n').split('\n')
    have = {l.split('=', 1)[1] for l in lines if '=' in l}
    nxt = max(int(l.split('=', 1)[0]) for l in lines if '=' in l) + 1
    added = []
    for name in made:
        if name in have:
            continue
        lines.append(f'{nxt}={name}')
        added.append(f'{nxt}={name}')
        nxt += 1
    open(pack, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(lines) + '\n')
    print('model.pack:', ', '.join(added) or 'nothing new')


if __name__ == '__main__':
    main()
