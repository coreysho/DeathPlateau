#!/usr/bin/env python3
"""Build the Gravedigger slayer helmet's meshes - the Undertaker's ornament kit result.

    python3 tools/models/gengravedigger.py --content content

WHY A REPAINT AND NOT A COLOUR. The Slayer helmet's fourteen colours are a different pipeline:
tools/slayerhelmspec.json imports OSRS's OWN authored meshes per colour - the red one has different
horns, the green one different spines - and anchors each to a geom block of vertex and face counts
recorded at import, which battery group 67 measures the shipped .ob2 against. A Gravedigger is not
an Old School colour, so there is no cache obj to import and nothing to anchor. It is this server's
own, so it is an ORNAMENT KIT instead: the pipeline for exactly that, with a Dismantle op, which
also keeps it in the token economy rather than straddling the Cosmetics tab's slayer points.

WHICH FACES ARE WHICH, LOOKED AT RATHER THAN GUESSED. The plain helmet has thirteen colours, and
every face whose hue AND saturation are zero is the crown and the spikes - rendered with that set
picked out in red to be sure before a single colour was changed. Everything else is the mask, the
jaw and the earmuffs. So:

    the crown goes BONE      - hue 7, a warm off-white, each face keeping its own lightness
    everything else OBSIDIAN - hue 0 saturation 0, darkened, the Death token's own black stone

which is the token's coin worn on a head: black stone with bone on it.

LIGHTNESS IS SCALED, NOT REPLACED. tint() keeps each face's own lightness and changes only hue and
saturation, so the mesh's shading survives - flattening it to one bone and one black would turn a
helmet into a silhouette at 32 pixels.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode, roundtrip

_ap = argparse.ArgumentParser()
_ap.add_argument('--content', default='content', help='the content checkout to write into')
C = _ap.parse_args().content
MODELS = os.path.join(C, 'models', 'obj')

# source mesh -> the name its repaint takes.
#
# BOTH SETS, because the imbued helmet is its OWN model in OSRS and not the plain one renamed - its
# eye is grey rather than red. Repainting the plain set twice would give an imbued Gravedigger a red
# eye and quietly undo the import that fixed exactly that.
PARTS = [(src, src.replace('obj_slayer_helm', 'obj_slayer_helm_gravedigger', 1))
         for src in ('obj_slayer_helm', 'obj_slayer_helm_manwear', 'obj_slayer_helm_womanwear',
                     'obj_slayer_helm_manhead', 'obj_slayer_helm_womanhead')]
PARTS += [(src, src.replace('obj_slayer_helm_i', 'obj_slayer_helm_gravedigger_i', 1))
          for src in ('obj_slayer_helm_i', 'obj_slayer_helm_i_manwear', 'obj_slayer_helm_i_womanwear',
                      'obj_slayer_helm_i_manhead', 'obj_slayer_helm_i_womanhead')]
# and the kit itself: a cache ornament kit repainted to match what it makes
PARTS += [('obj_dragon_boots_ornament_kit', 'obj_gravedigger_kit')]
KIT = 'obj_gravedigger_kit'

BONE_HUE, BONE_SAT, BONE_SCALE = 7, 2, 1.15
DARK_HUE, DARK_SAT, DARK_SCALE = 0, 0, 0.85


def hsl(h, s, l):
    return (h << 10) | (s << 7) | l


# WHICH FACES GO BONE, and it is NOT one rule for all three meshes - the first version tried that
# and two of them came out wrong, which is why this is written down.
#
#   the helmets   lightness >= 30. On the plain mesh the crown runs 39..103 and the mask 6..18, so
#                 "hue and saturation are both zero" picked the crown out exactly. On the IMBUED
#                 mesh it does not: that one's mask is hue 0 saturation 0 lightness 24, 187 faces of
#                 it, so the same rule painted the whole mask bone. Brightness separates crown from
#                 mask on both, which hue does on neither.
#   the kit       saturation >= 3. A cache ornament kit is gold - 95% of its faces carry hue 6 or 7
#                 at saturation 6 - so a brightness rule leaves it a dark slab, which is what the
#                 first attempt shipped. Its gold is the part that should read as bone.
# The cut is PER MESH, because the two helmets are two different authored meshes with two different
# palettes - verified by rendering each with its bone set picked out in red, not by reading counts.
# 30 is right on the plain one (crown 39..103, mask 6..18) and WRONG on the imbued one, where it
# takes the cheek plates too and leaves a helmet that is nearly all bone. 60 keeps the imbued one to
# its crown and spikes.
BONE_BY_LIGHT, BONE_BY_SAT = 'light', 'sat'


def repaint(m, rule, cut=30):
    for i in range(m['fcount']):
        c = m['colour'][i]
        s, l = (c >> 7) & 7, c & 0x7F
        bone = (l >= cut) if rule == BONE_BY_LIGHT else (s >= 3)
        if bone:
            m['colour'][i] = hsl(BONE_HUE, BONE_SAT, max(0, min(127, int(l * BONE_SCALE))))
        else:
            m['colour'][i] = hsl(DARK_HUE, DARK_SAT, max(0, min(127, int(l * DARK_SCALE))))
    return m


def main():
    index = {}
    for root, _dirs, files in os.walk(os.path.join(C, 'models')):
        for f in files:
            if f.endswith('.ob2'):
                index.setdefault(f[:-4], os.path.join(root, f))

    made = []
    for src, name in PARTS:
        if src not in index:
            raise SystemExit('missing source mesh: ' + src)
        m = repaint(parse_ob2(open(index[src], 'rb').read()),
                    BONE_BY_SAT if name == KIT else BONE_BY_LIGHT,
                    cut=60 if '_gravedigger_i' in name else 30)
        b = encode(m)
        ok, why = roundtrip(b, m)
        if not ok:
            raise SystemExit('%s does not survive a round trip: %s' % (name, why))
        open(os.path.join(MODELS, name + '.ob2'), 'wb').write(b)
        made.append(name)
    print('wrote models:', ', '.join(made))

    pack = os.path.join(C, 'pack', 'model.pack')
    lines = open(pack, encoding='utf-8').read().replace('\r\n', '\n').rstrip('\n').split('\n')
    have = {l.split('=', 1)[1] for l in lines if '=' in l}
    nxt = max(int(l.split('=', 1)[0]) for l in lines if '=' in l) + 1
    added = []
    for name in made:
        if name in have:
            continue
        lines.append('%d=%s' % (nxt, name))
        added.append('%d=%s' % (nxt, name))
        nxt += 1
    open(pack, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('model.pack:', ', '.join(added) or 'nothing new')


if __name__ == '__main__':
    main()
