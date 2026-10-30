#!/usr/bin/env python3
"""Count the pixels one worn model paints onto another, with the CLIENT'S OWN renderer.

WHY THIS EXISTS. content/tools/wearrender.py answers the same question by reimplementing
Model.method382 in python, and in October 2026 it was wrong about it five times running: eight
passes of worn-model priorities shipped on its numbers and every one was reported still clipping
from the game, until the lot was reverted. This does not reimplement anything. It drives
PlayerRender, which merges and draws through the real client classes, and counts pixels.

HOW IT DECIDES. It draws the kit twice - once whole, once with the cape's faces hidden through the
client's own "do not draw this one" switch - and counts the pixels that differ INSIDE the armour's
own silhouette. A cape beside the player is not counted; a cape on top of the armour is. Zero is
the only passing number.

  python3 tools/models/wearpoke.py --over obj_infernal_max_cape_manwear \
      --under obj_saradomin_platebody_manwear,obj_saradomin_plateskirt_manwear
  ... --faces          also bisects to the individual faces doing it
  ... --priority 10    reports what it would be if those faces were depth-sorted instead

Needs the render directory PlayerRender wants (config.jag, textures.jag, anims/) and the built
client classes; --dir and --classes point at them.
"""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osrs2ob2 import parse_ob2
from PIL import Image

BG = (0x14, 0x14, 0x14)


def faces_of(model, objdir):
    return parse_ob2(open(os.path.join(objdir, model + '.ob2'), 'rb').read())['fcount']


class Scene:
    def __init__(self, a):
        self.a = a
        self.over_n = faces_of(a.over, a.objdir)
        self.parts = [a.over] + a.under.split(',')
        self.base = self.shot(hide=[(0, self.over_n - 1)], tag='base')
        self.bp = self.base.load()
        self.mask = [(x, y) for y in range(self.base.size[1]) for x in range(self.base.size[0])
                     if self.bp[x, y] != BG]

    def shot(self, hide=None, repri=None, tag='t'):
        out = os.path.join(self.a.tmp, f'wearpoke_{tag}.png')
        cmd = ['java', '-cp', f'{self.a.classes}:{self.a.tools}', 'jagex2.client.PlayerRender',
               self.a.dir, out]
        for p in self.parts:
            cmd += ['--part', os.path.join(self.a.objdir, p + '.ob2')]
        cmd += ['--frame', str(self.a.frame), '--yan', str(self.a.yan),
                '--dist', str(self.a.dist), '--size', str(self.a.size)]
        if hide:
            cmd += ['--hide', ','.join(f'{x}:{y}' for x, y in hide)]
        if repri:
            cmd += ['--repri', repri]
        subprocess.run(cmd, capture_output=True, check=True)
        img = Image.open(out).convert('RGB')
        return img.crop(self.a.box) if self.a.box else img

    def on_armour(self, img):
        q = img.load()
        return [(x, y) for (x, y) in self.mask
                if max(abs(q[x, y][i] - self.bp[x, y][i]) for i in range(3)) > 24]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--over', required=True, help='the model that should not show through')
    ap.add_argument('--under', required=True, help='comma-separated models it is drawn against')
    ap.add_argument('--dir', default='/tmp/render')
    ap.add_argument('--classes', default='javaclient/build/classes/java/main')
    ap.add_argument('--tools', default='.')
    ap.add_argument('--objdir', default='content/models/obj')
    ap.add_argument('--tmp', default='/tmp')
    ap.add_argument('--frame', type=int, default=2422, help='a walk frame; 0 is the base pose')
    ap.add_argument('--yan', type=int, default=0, help='0 faces the camera, 1024 is the back')
    ap.add_argument('--dist', type=int, default=150)
    ap.add_argument('--size', type=int, default=700)
    ap.add_argument('--box', type=int, nargs=4, default=[150, 350, 560, 760], metavar=('L', 'T', 'R', 'B'))
    ap.add_argument('--faces', action='store_true', help='also name the faces doing it')
    ap.add_argument('--priority', type=int, default=None, help='report the count at this priority too')
    a = ap.parse_args()
    a.box = tuple(a.box)

    s = Scene(a)
    hits = s.on_armour(s.shot(tag='full'))
    print(f'{a.over} over {a.under}: {len(hits)} px on {len(s.mask)} px of armour')
    if a.priority is not None:
        n = len(s.on_armour(s.shot(repri=f'0:{s.over_n - 1}={a.priority}', tag='repri')))
        print(f'  with every face at priority {a.priority}: {n} px')
    if a.faces and hits:
        total = len(hits)
        hidden = []
        while total > 0 and len(hidden) < 24:
            lo, hi = 0, s.over_n - 1
            if len(s.on_armour(s.shot(hide=hidden + [(lo, hi)]))) >= total:
                break
            while lo < hi:                      # bisect to one face whose removal helps
                mid = (lo + hi) // 2
                if len(s.on_armour(s.shot(hide=hidden + [(lo, mid)]))) < total:
                    hi = mid
                else:
                    lo = mid + 1
            after = len(s.on_armour(s.shot(hide=hidden + [(lo, lo)])))
            if after >= total:
                print(f'  the rest is layered: no single face accounts for the last {total} px')
                break
            print(f'  face {lo:4d}  -{total - after:4d} px')
            hidden.append((lo, lo))
            total = after


if __name__ == '__main__':
    main()
