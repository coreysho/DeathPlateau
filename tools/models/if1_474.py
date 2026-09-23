#!/usr/bin/env python3
"""Decode an interface component in 474's OLD ("if1") format.

This is a direct transcription of Component.decode in javaclient - the 377 client's own reader -
because 474 stores 455 of its 620 interfaces in exactly that layout. The only difference is the
container: 377 concatenates every component into one `data` file inside a jagfile, while 474 puts
one component per file in an idx3 group per interface. The bytes of a component are the same.

Five things did change, all found by decoding real bytes and checking that each component is
consumed EXACTLY - a reader that stops early looks like it works:

  * every component carries its own x/y. 377 keeps a child's position in its parent's list, so a
    474 layer has no child list at all and this reader must not look for one.
  * both layer links widened from one byte to two, 0xffff meaning none.
  * sprites and models are numeric ids, not "<sheet>,<index>" name strings. Importing a 474
    interface therefore means importing the sprites it points at, BY NUMBER.
  * a jstr terminates on NUL rather than 0x0a.
  * type 6's model/activemodel/anim/activeanim are u16 each, not 377's (hi-1<<8)+lo byte pairs.

  * text (types 1 and 4) is x alignment, y alignment, line height, a u16 FONT ID (the sprite group
    of the font: 494 p11, 495 p12, 496 b12, 497 q8) and the shadow flag - six bytes where 377 has
    three (centre, font index, shadow).

That last one was the "244 failures" this reader used to report. Reading 377's three bytes left the
line height and the font id at the front of the text, which decoded as garbage characters, and a font
id under 256 has a zero high byte, which ended the string early - those were the 244. Every one of
the 4,479 type-1 and type-4 components in the cache now consumes exactly.

    xalign 0 left, 1 centre, 2 right; yalign 0 top, 1 centre, 2 bottom
"""
import struct


class R:
    def __init__(s, d):
        s.d, s.p = d, 0

    def g1(s):
        v = s.d[s.p]; s.p += 1; return v

    def g2(s):
        v = struct.unpack_from('>H', s.d, s.p)[0]; s.p += 2; return v

    def g2b(s):
        v = struct.unpack_from('>h', s.d, s.p)[0]; s.p += 2; return v

    def g4(s):
        v = struct.unpack_from('>i', s.d, s.p)[0]; s.p += 4; return v

    def gjstr(s):
        # 377 terminates a jstr on 0x0a; 474 had already moved to NUL
        e = s.d.index(b'\x00', s.p)
        v = s.d[s.p:e].decode('cp1252', 'replace'); s.p = e + 1; return v


def decode(d):
    b = R(d)
    c = {}
    c['type'] = b.g1()
    c['buttontype'] = b.g1()
    c['clientcode'] = b.g2()
    # 474 carries the component's own position, which 377 keeps in its parent's child list
    c['x'] = b.g2b()
    c['y'] = b.g2b()
    c['width'] = b.g2()
    c['height'] = b.g2()
    c['trans'] = b.g1()
    # and widens both layer links to two bytes, 0xffff meaning none
    c['overlayer'] = b.g2()
    c['overlayer2'] = b.g2()

    n = b.g1()
    if n:
        c['comparators'] = [(b.g1(), b.g2()) for _ in range(n)]
    n = b.g1()
    if n:
        c['scripts'] = [[b.g2() for _ in range(b.g2())] for _ in range(n)]

    t = c['type']
    if t == 0:
        # no child list: 474 gives every component its own x/y, so a layer no longer has to
        # carry the positions of the things inside it
        c['scroll'] = b.g2()
        c['hide'] = b.g1() == 1
    if t == 1:
        c['field707'] = b.g2()
        c['field715'] = b.g1() == 1
    if t == 2:
        c['draggable'] = b.g1() == 1
        c['interactable'] = b.g1() == 1
        c['usable'] = b.g1() == 1
        c['swappable'] = b.g1() == 1
        c['marginx'] = b.g1()
        c['marginy'] = b.g1()
        slots = []
        for _ in range(20):
            if b.g1() == 1:
                slots.append((b.g2b(), b.g2b(), b.g4()))
            else:
                slots.append(None)
        c['slots'] = slots
        c['iop'] = [b.gjstr() for _ in range(5)]
    if t == 3:
        c['fill'] = b.g1() == 1
    if t in (1, 4):
        c['xalign'] = b.g1()
        c['yalign'] = b.g1()
        c['lineheight'] = b.g1()
        c['font'] = b.g2()
        c['shadowed'] = b.g1() == 1
        c['center'] = c['xalign'] == 1
    if t == 4:
        c['text'] = b.gjstr()
        c['activetext'] = b.gjstr()
    if t in (1, 3, 4):
        c['colour'] = b.g4()
    if t in (3, 4):
        c['activecolour'] = b.g4()
        c['overcolour'] = b.g4()
        c['activeovercolour'] = b.g4()
    if t == 5:
        # sprites are numeric in 474, not "<sheet>,<index>" strings; -1 is none
        c['graphic'] = b.g4()
        c['activegraphic'] = b.g4()
    if t == 6:
        # 474 widened all four to u16 with 0xffff for none; 377 packs them as (hi-1<<8)+lo pairs
        c['model'] = b.g2()
        c['activemodel'] = b.g2()
        c['anim'] = b.g2()
        c['activeanim'] = b.g2()
        c['zoom'] = b.g2()
        c['xan'] = b.g2()
        c['yan'] = b.g2()
    if t == 7:
        c['center'] = b.g1() == 1
        c['font'] = b.g1()
        c['shadowed'] = b.g1() == 1
        c['colour'] = b.g4()
        c['marginx'] = b.g2b()
        c['marginy'] = b.g2b()
        c['interactable'] = b.g1() == 1
        c['iop'] = [b.gjstr() for _ in range(5)]
    if t == 8:
        c['text'] = b.gjstr()
    if c['buttontype'] == 2 or t == 2:
        c['targetverb'] = b.gjstr()
        c['targettext'] = b.gjstr()
        c['targetmask'] = b.g2()
    if c['buttontype'] in (1, 4, 5, 6):
        c['option'] = b.gjstr()
    c['_consumed'] = b.p
    c['_len'] = len(d)
    return c
