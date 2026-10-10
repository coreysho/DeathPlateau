#!/usr/bin/env python3
"""Build the Lava dragon's models out of THIS BUILD'S OWN DRAGON, and register them.

    python3 tools/models/genlavadragon.py --content content

WHY THIS IS NOT AN IMPORT
  Old School's lava dragon was graphically updated on 7 February 2024, and the model it has now is
  a modern high-poly mesh with a baked lava texture - in a 2006 game it would stand beside the
  green, red, black and blue dragons looking like it came out of a different decade. The version
  before that (13 March 2014 - 7 February 2024) was the 2007 HD dragon mesh with a lava retexture:
  black body, glowing orange limbs, wings, spine and head, white horns and claws, red eyes.

  This server's dragons are the 2006 mesh, and ALL FIVE OF THEM ARE THE SAME TWO MODELS -
  npc_king_dragon (body, legs, tail, wings) and npc_red_dragon (head and neck) - told apart by a
  single recolour pair in the npc config. So the honest way to have a lava dragon here is the way
  this build already has a black one: the same mesh, dressed differently. What it cannot be is a
  config recolour, because a config recolour maps one source colour and the whole point of a lava
  dragon is that it is two colours at once.

WHAT THE MESH GIVES US TO WORK WITH. Both models are greyscale, and their lightness bands are
already the parts you would want to paint separately:

    l61   608 faces   the scales - body, neck, tail, legs
    l41    50 faces   the wing membranes
    l127   88 faces   claws, toes and the wing finger-bones
    l115   24 faces   the head's horns and spikes
    l0      6 faces   the eyes

so the bands carry the horns, claws and membranes, and a HEIGHT GRADIENT carries the lava: black
along the back, cooling to ember down the flanks, glowing at the feet and the underside of the jaw,
which is where it sits on the real thing. The gradient is measured over the two models TOGETHER -
the head model's y range sits entirely above the body's, so a per-model gradient would have given
the head its own full sweep and left it glowing at the brow.
"""
import os, sys, glob, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2, encode, roundtrip

_ap = argparse.ArgumentParser()
_ap.add_argument('--content', default='content', help='the content checkout to write into')
C = _ap.parse_args().content


def hsl(h, s, l):
    return (h << 10) | (s << 7) | l


# Cooled basalt through to running lava. The hot end is bright because a 2006 model has no
# emissive anything - a "glow" is just a face the shading cannot drag down far.
BLACK = hsl(0, 0, 20)      # the back, and everything in shadow
CHAR = hsl(3, 4, 38)       # the flanks
EMBER = hsl(4, 6, 58)      # where the crust is cracking
LAVA = hsl(6, 7, 100)      # the feet, the lowest limbs, under the jaw
MEMBRANE = hsl(0, 0, 14)   # wing membranes stay dark; the v1 dragon's are near-black
CLAW = hsl(7, 1, 100)      # horns, claws, toes, wing finger-bones - bone white on the real one
EYE = hsl(6, 7, 118)       # red-hot

PARTS = [('npc_king_dragon', 'npc_lava_dragon_1'), ('npc_red_dragon', 'npc_lava_dragon_2')]

# band -> fixed colour, for the bands that are not scales
BANDS = {41: MEMBRANE, 127: CLAW, 115: CLAW, 0: EYE}
# how far down the figure each scale colour takes over (0 = the very top of the head, 1 = ground)
STOPS = [(0.28, BLACK), (0.52, CHAR), (0.78, EMBER), (1.01, LAVA)]

# THE WING STRUTS, which the height gradient alone would leave black because they are up at the
# top of the figure. Measured rather than guessed: out past this, the body model holds 20 faces of
# the scale band (the arm and finger bones) and 20 of the membrane band, and nothing else - so
# "scale band, outboard" is exactly the wing's bones and they can glow while the skin between them
# stays dark. The l127 band is NOT part of this: all 88 of its faces are toe claws down at the
# ground, so the first version's rule for lighting wing bones out of that band did nothing at all.
WING_X = 150


def find(name):
    return glob.glob(os.path.join(C, 'models', '**', name + '.ob2'), recursive=True)[0]


def main():
    srcs = [parse_ob2(open(find(a), 'rb').read()) for a, _b in PARTS]
    # one gradient over both models, so the head and the body agree about where "down" is
    ymin = min(min(m['vy']) for m in srcs)
    ymax = max(max(m['vy']) for m in srcs)
    span = ymax - ymin

    made = []
    for m, (src, dst) in zip(srcs, PARTS):
        for i in range(m['fcount']):
            band = m['colour'][i] & 0x7F
            if band in BANDS:
                m['colour'][i] = BANDS[band]
                continue
            if max(abs(m['vx'][m[v][i]]) for v in ('fa', 'fb', 'fc')) > WING_X:
                m['colour'][i] = LAVA
                continue
            cy = (m['vy'][m['fa'][i]] + m['vy'][m['fb'][i]] + m['vy'][m['fc'][i]]) / 3.0
            t = (cy - ymin) / span          # 0 at the top of the head, 1 at the feet
            for stop, colour in STOPS:
                if t < stop:
                    m['colour'][i] = colour
                    break
        b = encode(m)
        ok, why = roundtrip(b, m)
        if not ok:
            raise SystemExit(f'{dst} does not survive a round trip: {why}')
        open(os.path.join(C, 'models', 'npc', dst + '.ob2'), 'wb').write(b)
        made.append(dst)
    print('wrote models:', ', '.join(made))

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


main()
