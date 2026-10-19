#!/usr/bin/env python3
"""Decode OSRS model formats (trailing marker FF FE = type 2, FF FD = type 3).

Layouts follow RuneLite's ModelLoader (cache/.../loaders/ModelLoader.java, BSD-2).
Every decode is checked by reconciliation: the section walk must land exactly on the
header, or the model is rejected rather than half-read.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class P:
    def __init__(s, b, pos=0): s.b, s.pos = b, pos
    def g1(s):
        v = s.b[s.pos]; s.pos += 1; return v
    def g1s(s):
        v = s.b[s.pos]; s.pos += 1; return v - 256 if v > 127 else v
    def g2(s):
        v = (s.b[s.pos] << 8) | s.b[s.pos+1]; s.pos += 2; return v
    def gsmart(s):
        return s.g1() - 64 if s.b[s.pos] < 128 else s.g2() - 49152


def version(b):
    if len(b) < 3: return None
    if b[-1] == 0xFD and b[-2] == 0xFF: return 3
    if b[-1] == 0xFE and b[-2] == 0xFF: return 2
    if b[-1] == 0xFF and b[-2] == 0xFF: return 1
    return 0


def _layout1(b):
    """Revision 474's "new" model format - the one whose footer is FF FF.

    Neither importer could read these. import474map.py refuses them outright ("model N is the
    newer format") and osrsmodel only knew types 2 and 3, so every loc built from one was dropped
    at import; the God Wars doors lost the five locs that flank them that way.

    Derived from the cache rather than from a specification, against the 110 version-1 models the
    474 cache holds. The header sits at len-23 and reads

        vc g2, fc g2, tc g1, f0 g1, pri g1, f2 g1, f3 g1, f4 g1, f5 g1,
        xl g2, yl g2, zl g2, fil g2, misc g2

    and the sections follow in the order below, with ONE trailing byte after the last of them
    (type 2 has the same byte). What each flag costs was solved by subtracting the known sections
    from the body across the whole corpus and grouping by flag pattern: f0, f2 and f3 are each one
    byte per FACE, f5 is one per VERTEX, and pri costs a face byte only when it reads 255 - the
    same shape type 2 has. f0 sits between the vertex flags and the face types, which is the one
    position that puts the face data where the indices come out inside the vertex array; it is
    also the only placement under which the vertex-flag bytes stay inside their three bits.

    102 of the 110 reconcile and have every face index in range. The other eight all set f4, a
    variable-length per-vertex section this does not model, and they are refused rather than
    guessed at - which is what the caller's walked != body check does with the None below.
    """
    h = P(b, len(b) - 23)
    vc, fc = h.g2(), h.g2()
    tc = h.g1()
    f0 = h.g1(); pri = h.g1(); f2 = h.g1(); f3 = h.g1(); f4 = h.g1(); f5 = h.g1()
    xl, yl, zl, fil, misc = h.g2(), h.g2(), h.g2(), h.g2(), h.g2()

    if f4:
        return None                      # vertex groups: length not modelled, so refuse it

    o = 0
    vflag = o;  o += vc
    frt   = o
    if f0: o += fc
    ftype = o;  o += fc
    fpri  = o
    if pri == 255: o += fc
    tskin = o
    if f3: o += fc
    misc_sec = o; o += misc    # the var22-equivalent section; nothing here reads inside it
    vlabel = o
    if f5: o += vc
    falpha = o
    if f2: o += fc
    fdata = o;  o += fil
    colour = o; o += fc * 2
    tex   = o;  o += tc * 6
    xo    = o;  o += xl
    yo    = o;  o += yl
    zo    = o;  o += zl
    o += 1                               # the trailing byte, as in type 2
    del misc_sec                         # walked for its length only
    return dict(ver=1, vc=vc, fc=fc, tc=tc, body=len(b) - 23, walked=o,
                vflag=vflag, ftype=ftype, fpri=fpri, frt=frt, falpha=falpha,
                fdata=fdata, colour=colour, tex=tex, xo=xo, yo=yo, zo=zo,
                vgroup=vlabel, has_vgroup=f5 == 1,
                tskin=tskin, has_tskin=f3 == 1, has_ftex=False,
                has_rtype=f0 == 1, has_pri=pri == 255, pri=pri,
                has_alpha=f2 == 1, has_zoff=False)


def _layout2(b):
    """RuneLite decodeType2. Note two things the offset block alone does not tell you:
    packedVertexGroups is read from INSIDE the var22 section (not a section of its own),
    and after every section there is a trailing hasOffsets byte plus, if set, one byte
    per face. Both were needed to make the walk reconcile."""
    h = P(b, len(b) - 23)
    vc, fc = h.g2(), h.g2()
    tc = h.g1(); f_rtype = h.g1(); pri = h.g1(); f_alpha = h.g1()
    f_tskin = h.g1(); f_vgroup = h.g1(); f_animaya = h.g1()
    xl, yl, zl, fil, misc_len = h.g2(), h.g2(), h.g2(), h.g2(), h.g2()

    o = 0
    vflag = o;  o += vc
    ftype = o;  o += fc
    fpri  = o
    if pri == 255: o += fc
    tskin = o
    if f_tskin == 1: o += fc
    frt   = o
    if f_rtype == 1: o += fc
    misc  = o;  o += misc_len          # vertex groups + animaya live here
    falpha = o
    if f_alpha == 1: o += fc
    fdata = o;  o += fil
    colour = o; o += fc * 2
    tex   = o;  o += tc * 6
    xo    = o;  o += xl
    yo    = o;  o += yl
    zo    = o;  o += zl
    end = o
    has_zoff = end < len(b) - 23 and b[end] == 1
    o += 1
    if has_zoff: o += fc
    return dict(ver=2, vc=vc, fc=fc, tc=tc, body=len(b) - 23, walked=o,
                vflag=vflag, ftype=ftype, fpri=fpri, frt=frt, falpha=falpha,
                fdata=fdata, colour=colour, tex=tex, xo=xo, yo=yo, zo=zo,
                vgroup=misc, has_vgroup=f_vgroup == 1,
                tskin=tskin, has_tskin=f_tskin == 1, has_ftex=False,
                has_rtype=f_rtype == 1, has_pri=pri == 255, pri=pri,
                has_alpha=f_alpha == 1, has_zoff=has_zoff)


def _layout3(b):
    """RuneLite decodeType3. Same trailing hasOffsets convention as type 2."""
    h = P(b, len(b) - 26)
    vc, fc = h.g2(), h.g2()
    tc = h.g1(); f_rtype = h.g1(); pri = h.g1(); f_alpha = h.g1()
    f_tskin = h.g1(); f_texcoord = h.g1(); f_vgroup = h.g1(); f_animaya = h.g1()
    xl, yl, zl, misc_len, fil, tskin_len = (h.g2() for _ in range(6))

    simple = complexn = cube = 0
    for i in range(tc):
        t = b[i]
        if t == 0: simple += 1
        if 1 <= t <= 3: complexn += 1
        if t == 2: cube += 1

    o = tc
    vflag = o;  o += vc
    frt   = o
    if f_rtype == 1: o += fc
    ftype = o;  o += fc
    fpri  = o
    if pri == 255: o += fc
    tskin = o
    if f_tskin == 1: o += fc
    vgroups = o; o += tskin_len          # var33: packed vertex groups
    falpha = o
    if f_alpha == 1: o += fc             # var34
    fdata = o;  o += misc_len            # var35: face index DATA (not var37)
    ftexture = o
    if f_texcoord == 1: o += fc * 2      # var36: face textures
    texcoord = o; o += fil               # var37: texture coords
    colour = o; o += fc * 2              # var38
    xo    = o;  o += xl
    yo    = o;  o += yl
    zo    = o;  o += zl
    tex   = o;  o += simple * 6
    o += complexn * 6 + complexn * 6 + complexn * 2 + complexn
    o += complexn * 2 + cube * 2
    # trailing block: a flag byte (+10 more bytes if non-zero: 3 shorts and an int),
    # then a hasOffsets byte and, if set, one byte per face.
    end = o
    flag = b[o]; o += 1
    if flag != 0: o += 10
    has_zoff = o < len(b) - 26 and b[o] == 1
    o += 1
    if has_zoff: o += fc
    return dict(ver=3, vc=vc, fc=fc, tc=tc, body=len(b) - 26, walked=o,
                vflag=vflag, ftype=ftype, fpri=fpri, frt=frt, falpha=falpha,
                fdata=fdata, colour=colour, tex=tex, xo=xo, yo=yo, zo=zo,
                vgroup=vgroups, texcoord=texcoord, ftexture=ftexture,
                has_vgroup=f_vgroup == 1,
                tskin=tskin, has_tskin=f_tskin == 1, has_ftex=f_texcoord == 1,
                has_rtype=f_rtype == 1, has_pri=pri == 255, pri=pri,
                has_alpha=f_alpha == 1, has_zoff=has_zoff,
                simple=simple, complexn=complexn)


def layout(b):
    v = version(b)
    if v == 1: return _layout1(b)
    if v == 2: return _layout2(b)
    if v == 3: return _layout3(b)
    return None


def reconciles(b):
    try:
        L = layout(b)
    except Exception:
        return False
    return L is not None and L['walked'] == L['body']


if __name__ == '__main__':
    from flatcache import Store
    import collections
    st = Store(sys.argv[1])
    gs = st.groups(7)
    step = max(1, len(gs) // int(sys.argv[2] if len(sys.argv) > 2 else 2000))
    res = collections.Counter(); off = collections.Counter(); n = 0
    for g in gs[::step]:
        b = st.read(7, g)
        if not b: continue
        n += 1
        v = version(b)
        try: L = layout(b)
        except Exception as e:
            res[f'v{v} EXC']  += 1; continue
        if L is None: res[f'v{v} unhandled'] += 1; continue
        if L['walked'] == L['body']: res[f'v{v} ok'] += 1
        else:
            res[f'v{v} MISMATCH'] += 1
            off[(v, L['walked'] - L['body'])] += 1
    print(f'{n} models sampled')
    for k, c in sorted(res.items()): print(f'   {k}: {c}  ({c/n:.0%})')
    if off: print('   walked-minus-body deltas:', off.most_common(8))
