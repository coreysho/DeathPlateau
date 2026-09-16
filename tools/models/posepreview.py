#!/usr/bin/env python3
"""Pose a converted OSRS npc with a converted OSRS animation, and render the frames.

The "look at it before you ship it" step for ANIMATION, the way ob2render.py is for a model.
importosrsnpc.py takes a ready/walk/attack/defend/death seq per npc on trust; the cache states
ready and walk in the npc record, but the combat three are the config author's guess. This is how
that guess stops being one: it applies the frame's own transforms to the npc's own mesh and draws
the result, so a wrong seq is a picture of a dragon folded inside out rather than a surprise in
game.

  python3 posepreview.py "<newest cache>" --npc 239 --seq 90 --out /tmp/kbd_ready.png
  python3 posepreview.py "<newest cache>" --npc 239 --seq 91 --frames 0,3,6,9 --cols 4

Transform types are the client's: 0 sets the pivot from the listed vertex groups' centroid plus
the frame's delta, 1 translates, 2 rotates about the pivot, 3 scales about it, 5 is alpha (drawn
as-is here, since a preview has no blending). Every one of them is applied in skeleton order.
"""
import argparse, io, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from flatcache import Store
from osrsnpc import load_osrs_npcs
from osrs2ob2 import decode as decode_osrs_model, encode as encode_ob2, SHARED_TEXTURES
from osrslocimport import bake
from osrsseq import decode_osrs_seq
from reftable import split_group
from animconv474 import parse_474_frame, parse_474_skeleton
from animconvosrs import parse_osrs_framemap
import ob2render

SINE = [int(32768.0 * np.sin(i * 0.0030679615)) for i in range(2048)]
COSINE = [int(32768.0 * np.cos(i * 0.0030679615)) for i in range(2048)]


def vertex_labels(b):
    """The vertex label byte per vertex, which ob2render skips because a still does not need it."""
    n = len(b)
    h = ob2render.P(b, n - 18)
    vcount = h.g2(); fcount = h.g2(); tcount = h.g1()
    f_tex, f_pri, f_alpha, f_flabel, f_vlabel = h.g1(), h.g1(), h.g1(), h.g1(), h.g1()
    if f_vlabel != 1:
        return None, vcount
    o = vcount + fcount                                  # vertex flags + face types
    if f_pri == 255: o += fcount
    if f_flabel == 1: o += fcount
    if f_tex == 1: o += fcount
    return list(b[o:o + vcount]), vcount


def groups_of(labels, vcount):
    """The label byte IS the transform group index - there is no minus-one and 0 is a real group.

    Checked by rendering the King Black Dragon's idle frame both ways: read as l-1 the body
    stretches and a wing spike swings out, read as l it stands with its wings folded. The wrong
    one is still a dragon at a glance, which is exactly why it had to be looked at.
    """
    out = {}
    for v, l in enumerate(labels or []):
        out.setdefault(l, []).append(v)
    return {g: np.array(v, np.int64) for g, v in out.items()}


def apply_frame(m, groups, base, flags, vals):
    """base: (size, types, counts, labels). flags/vals: one 377 frame, read as the client reads it."""
    size, types, counts, glabels = base
    ox = oy = oz = 0
    p = 0
    def nxt():
        nonlocal p
        v = vals[p]
        if v < 128:
            p += 1; return v - 64
        v = ((vals[p] << 8) | vals[p + 1]) & 0x7FFF
        p += 2
        return v - 16384
    for i, f in enumerate(flags):
        if f == 0:
            continue
        t = types[i]
        # A scale axis the frame does not mention is 128 (unity), NOT 0. Getting this wrong
        # collapses every scaled group onto its pivot, which draws as a folded-up mesh - the
        # first thing this tool caught was itself.
        dflt = 128 if t == 3 else 0
        dx = nxt() if f & 1 else dflt
        dy = nxt() if f & 2 else dflt
        dz = nxt() if f & 4 else dflt
        idx = np.concatenate([groups[g] for g in glabels[i] if g in groups]) \
            if any(g in groups for g in glabels[i]) else None
        if t == 0:
            if idx is not None and len(idx):
                ox = int(m.vx[idx].mean()) + dx
                oy = int(m.vy[idx].mean()) + dy
                oz = int(m.vz[idx].mean()) + dz
            else:
                ox, oy, oz = dx, dy, dz
        elif idx is None or not len(idx):
            continue
        elif t == 1:
            m.vx[idx] += dx; m.vy[idx] += dy; m.vz[idx] += dz
        elif t == 2:
            x = m.vx[idx] - ox; y = m.vy[idx] - oy; z = m.vz[idx] - oz
            if dz:
                s, c = SINE[(dz & 0xff) * 8], COSINE[(dz & 0xff) * 8]
                x, y = (y * s + x * c) >> 15, (y * c - x * s) >> 15
            if dx:
                s, c = SINE[(dx & 0xff) * 8], COSINE[(dx & 0xff) * 8]
                y, z = (y * c - z * s) >> 15, (y * s + z * c) >> 15
            if dy:
                s, c = SINE[(dy & 0xff) * 8], COSINE[(dy & 0xff) * 8]
                x, z = (x * c + z * s) >> 15, (z * c - x * s) >> 15
            m.vx[idx] = x + ox; m.vy[idx] = y + oy; m.vz[idx] = z + oz
        elif t == 3:
            x = m.vx[idx] - ox; y = m.vy[idx] - oy; z = m.vz[idx] - oz
            m.vx[idx] = (x * dx) // 128 + ox
            m.vy[idx] = (y * dy) // 128 + oy
            m.vz[idx] = (z * dz) // 128 + oz
    return p


class Merged:
    """The client merges an npc's models into one before it animates them; so does this."""
    def __init__(s, parts):
        s.vx = np.concatenate([p.vx for p in parts])
        s.vy = np.concatenate([p.vy for p in parts])
        s.vz = np.concatenate([p.vz for p in parts])
        off = np.cumsum([0] + [p.vcount for p in parts[:-1]])
        s.fa = np.concatenate([p.fa + o for p, o in zip(parts, off)])
        s.fb = np.concatenate([p.fb + o for p, o in zip(parts, off)])
        s.fc = np.concatenate([p.fc + o for p, o in zip(parts, off)])
        s.colour = np.concatenate([p.colour for p in parts])
        s.finfo = None
        if any(p.finfo is not None for p in parts):
            s.finfo = np.concatenate([p.finfo if p.finfo is not None
                                      else np.zeros(p.fcount, np.int32) for p in parts])
        s.vcount = int(sum(p.vcount for p in parts)); s.fcount = int(len(s.fa))
        s.tcount = 0
    def height(s): return int(max(0, -int(s.vy.min())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cache'); ap.add_argument('--npc', type=int, required=True)
    ap.add_argument('--seq', type=int, required=True)
    ap.add_argument('--frames', default=None, help='comma-separated frame indexes (default: spread)')
    ap.add_argument('--count', type=int, default=6)
    ap.add_argument('--cols', type=int, default=6)
    ap.add_argument('--size', type=int, default=200)
    ap.add_argument('--yan', type=int, default=512)
    ap.add_argument('--xan', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    st = Store(a.cache)
    npcs, _ = load_osrs_npcs(st)
    d = npcs[a.npc]
    print('npc %d %r: models %s' % (a.npc, d.get('name'), d.get('models')))

    parts = []
    for mid in d['models']:
        m = decode_osrs_model(st.read(7, mid))
        bake(m, d.get('recol'), d.get('retex'), SHARED_TEXTURES)
        ob2 = encode_ob2(m)
        path = os.path.join('/tmp', 'pose_%d_%d.ob2' % (a.npc, mid))
        open(path, 'wb').write(ob2)
        part = ob2render.Model(path)
        lbl, vc = vertex_labels(ob2)
        part._labels = lbl
        parts.append(part)
    labels = []
    for p in parts:
        labels += (p._labels if p._labels is not None else [0] * p.vcount)
    print('merged: %d vertices, %d labelled' % (len(labels), sum(1 for l in labels if l)))

    sq = decode_osrs_seq(split_group(st.read(2, 12), len(st.reftable(2).file_ids[12]))
                         [st.reftable(2).file_ids[12].index(a.seq)])
    fr = sq['frames']
    print('seq %d: %d frames, priority %s' % (a.seq, len(fr), sq.get('priority')))

    want = ([int(x) for x in a.frames.split(',')] if a.frames else
            sorted({int(i * (len(fr) - 1) / max(1, a.count - 1)) for i in range(a.cols)}))
    tiles = []
    for fi in want:
        gf = fr[fi]; g, f = gf >> 16, gf & 0xFFFF
        ids = st.reftable(0).file_ids[g]
        blob = dict(zip(ids, split_group(st.read(0, g), len(ids))))[f]
        sk, n, flg, vls = parse_474_frame(blob)
        size, types, counts, glab, extra = parse_osrs_framemap(st.read(1, sk))
        fresh = []
        for mid, p in zip(d['models'], parts):
            q = ob2render.Model(os.path.join('/tmp', 'pose_%d_%d.ob2' % (a.npc, mid)))
            q._labels = p._labels
            fresh.append(q)
        mm = Merged(fresh)
        used = apply_frame(mm, groups_of(labels, mm.vcount), (size, types, counts, glab), flg, vls)
        if used != len(vls):
            print('  frame %d: WARNING read %d of %d value bytes' % (fi, used, len(vls)))
        img = ob2render.render(mm, size=a.size, yan=a.yan, xan=a.xan)
        tiles.append((fi, img))
        print('  frame %2d (file %d, skeleton %d): posed' % (fi, f, sk))

    cols = min(a.cols, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * a.size, rows * a.size), (24, 24, 27))
    for i, (fi, img) in enumerate(tiles):
        sheet.paste(img, ((i % cols) * a.size, (i // cols) * a.size))
    sheet.save(a.out)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
