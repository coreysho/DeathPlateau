#!/usr/bin/env python3
"""Draw the login screen's logo, content/title/logo.png, for the server's name: "Death Plateau".

The 377 logo spells RuneScape on nine grey pebbles, one letter each, in two staggered rows with a
sword threaded between them. This draws the same thing for another name: a pebble per letter, cut
as a rounded, slightly irregular stone, grained with horizontal streaks and lit from the top left
the way 377's are, a black outline, and the letter in 377's own hand-painted capitals.

THE LETTERS are lifted from 377's logo (logo377.png beside this script, the content's logo before
this one replaced it): each is the ink on its stone - the three blacks the letters are painted in,
holes closed. RuneScape has R U N E S C A P, and Death Plateau needs D T H L as well, so those four
are put together from the strokes of 377's E and C: L is E's stem and foot, T its top stroke over
its stem, H two of its stems and its middle stroke, D its stem against C turned round.
Every stroke on the logo is Jagex's brushwork, just not every letter. The colours are 377's own - its logo's stone greys,
blacks and golds - and every pixel is snapped to them, so the new logo sits in the title screen
exactly as the old one did. Same canvas (444x142), same magenta background.

    python tools/models/genlogo.py [--content=<content checkout>] [--preview=<png, drawn 2x>]

The pebbles are seeded, so a rerun draws the same logo.
"""
import os, random, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CONTENT = os.path.join(ROOT, 'content')

ROWS = ['DEATH', 'PLATEAU']
ROW_X = [4, 153]          # the second row starts further right, as SCAPE does under RUNE
ROW_Y = [4, 76]
# where 377's sword goes, relative to where it is in 377's logo
SWORD_DX, SWORD_DY = 30, -10
W, H = 444, 142
KEY = (255, 0, 255)

# 377's logo palette, dark to light
STONE = [(35, 37, 37), (47, 49, 54), (61, 62, 71), (72, 74, 82), (78, 80, 93), (86, 88, 101), (93, 96, 111),
         (100, 104, 119), (109, 112, 125), (121, 124, 139), (137, 141, 157), (153, 156, 174), (169, 171, 189),
         (185, 186, 203), (201, 202, 219), (226, 227, 238)]
GOLD = [(51, 50, 38), (60, 60, 3), (90, 87, 19), (156, 156, 31), (203, 202, 43), (247, 246, 65), (241, 242, 160)]
BLACK, INK, INK_EDGE = (1, 1, 1), (15, 16, 13), (25, 28, 28)


def smooth_noise(rng, h, w, cell_y, cell_x):
    """Value noise: a coarse random grid, bilinearly stretched - streaks when cell_x > cell_y."""
    gy, gx = h // cell_y + 2, w // cell_x + 2
    g = Image.fromarray((rng.random((gy, gx)) * 255).astype(np.uint8))
    return np.asarray(g.resize((gx * cell_x, gy * cell_y), Image.BILINEAR), np.float32)[:h, :w] / 255.0


def pebble_mask(rng, w, h):
    """A rounded stone: a superellipse whose radius wanders a little, so no two are the same."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx - (w - 1) / 2) / (w / 2), (yy - (h - 1) / 2) / (h / 2)
    ang = np.arctan2(ny, nx)
    wobble = 1 + sum(rng.uniform(-0.05, 0.05) * np.sin(k * ang + rng.uniform(0, 6.3)) for k in (2, 3, 5))
    r = (np.abs(nx) ** 2.2 + np.abs(ny) ** 2.2) ** (1 / 2.2)
    return r <= 0.97 * wobble


def depth(mask, steps=14):
    """How far each pixel is inside the stone, by repeated erosion (0 at the edge, steps inside)."""
    im = Image.fromarray(mask.astype(np.uint8) * 255)
    d = np.zeros(mask.shape, np.float32)
    for _ in range(steps):
        d += np.asarray(im, np.float32) / 255
        im = im.filter(ImageFilter.MinFilter(3))
    return d


def ramp(values, colours):
    idx = np.clip((values * (len(colours) - 1)).round().astype(int), 0, len(colours) - 1)
    return np.array(colours, np.uint8)[idx]

LOGO377 = os.path.join(HERE, 'logo377.png')
# where each letter sits in logo377.png (x0, y0, x1, y1), a pixel or two outside its ink
SOURCE = {'R': (11, 29, 37, 58), 'U': (57, 26, 83, 55), 'N': (113, 20, 141, 51), 'E': (172, 29, 196, 59),
          'S': (183, 93, 206, 125), 'C': (226, 88, 253, 119), 'A': (289, 82, 313, 115), 'P': (348, 89, 373, 122)}


def source_glyph(letter):
    """377's letter as RGBA: its ink pixels in their own colours, pinholes in the paint closed."""
    src = Image.open(LOGO377).convert('RGB').crop(SOURCE[letter])
    a = np.asarray(src)
    # the paint: the darkest of the palette (its three blacks and the darkest stone grey, which the
    # brush's texture dips into); the stone's own shadows start lighter than that
    ink = (a.astype(np.int32).sum(-1) < 115).astype(np.uint8)
    m = Image.fromarray(ink * 255).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    m = Image.fromarray(np.asarray(m) & (keep_largest(np.asarray(m) > 0) * 255).astype(np.uint8))
    g = src.convert('RGBA')
    g.putalpha(m)
    # the closed pinholes take the ink colour rather than the stone showing through
    fill = Image.new('RGBA', g.size, INK_EDGE + (255,))
    fill.alpha_composite(g)
    fill.putalpha(m)
    return fill.crop(m.getbbox())


def keep_largest(mask):
    """The biggest 8-connected piece of a mask, and anything within two pixels of it (R's leg)."""
    from collections import deque
    h, w = mask.shape
    seen = np.zeros_like(mask); best = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = True; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for ny in (cy - 1, cy, cy + 1):
                        for nx in (cx - 1, cx, cx + 1):
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; q.append((ny, nx))
                if len(pts) > len(best):
                    best = pts
    out = np.zeros_like(mask)
    for y, x in best:
        out[y, x] = True
    near = np.asarray(Image.fromarray(out.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
    return mask & near


def part(g, box):
    """A piece of a glyph: its pixels inside box (x0, y0, x1, y1), on a canvas the glyph's size."""
    out = Image.new('RGBA', g.size, (0, 0, 0, 0))
    out.paste(g.crop(box), box[:2])
    return out


def glyph(letter):
    if letter in SOURCE:
        return source_glyph(letter)
    e = source_glyph('E')
    w, h = e.size
    stem = part(e, (0, 0, 8, h))
    if letter == 'L':
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        out.alpha_composite(stem)
        out.alpha_composite(part(e, (0, h - 8, w, h)))
    elif letter == 'T':
        out = Image.new('RGBA', (w + 2, h), (0, 0, 0, 0))
        out.alpha_composite(part(e, (0, 5, 8, h)), ((w + 2 - 8) // 2, 0))
        out.alpha_composite(part(e, (0, 0, w, 8)), (1, 0))
    elif letter == 'H':
        out = Image.new('RGBA', (w + 1, h), (0, 0, 0, 0))
        out.alpha_composite(stem)
        out.alpha_composite(stem.transpose(Image.FLIP_LEFT_RIGHT).crop((w - 8, 0, w, h)), (w + 1 - 8, 0))
        out.alpha_composite(part(e, (6, h // 2 - 4, w - 5, h // 2 + 4)), (0, 0))
    elif letter == 'D':
        bowl = source_glyph('C').transpose(Image.FLIP_LEFT_RIGHT)  # its opening now to the left
        bowl = bowl.resize((bowl.width, h), Image.NEAREST)
        out = Image.new('RGBA', (bowl.width + 3, h), (0, 0, 0, 0))
        out.alpha_composite(bowl, (3, 0))
        out.alpha_composite(stem)
    else:
        raise SystemExit('no way to draw %r' % letter)
    return out


def pebble(rng, letter, font):
    w, h = rng.randint(41, 45), rng.randint(54, 59)
    m = pebble_mask(rng, w, h)
    d = depth(m)
    # lit from the top left: a rounded dome, brighter where its slope faces the light
    dome = np.sqrt(np.clip(d / 14, 0, 1))
    gy, gx = np.gradient(np.asarray(Image.fromarray((dome * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255)
    light = np.clip(0.45 + 9.0 * (-gx * 0.75 - gy * 0.65), 0, 1)
    grain = 0.6 * smooth_noise(rng, h, w, 2, 9) + 0.4 * smooth_noise(rng, h, w, 4, 4)
    v = 0.05 + 0.7 * light + 0.3 * grain - 0.1 * (1 - dome)
    # 377's pebbles catch the light in a bright rim just inside the outline on their lit side, and
    # darken to their shadowed edge
    facing = -gx * 0.75 - gy * 0.65
    rim = (d >= 1) & (d <= 2.5)
    v = np.where(rim & (facing > 0.004), 0.97, v)
    v = np.where(rim & (facing < -0.004), v - 0.2, v)
    rgb = ramp(np.clip(v, 0, 1), STONE)
    img = Image.fromarray(rgb, 'RGB').convert('RGBA')
    alpha = Image.fromarray(m.astype(np.uint8) * 255)
    img.putalpha(alpha)
    # the letter, 377's own, a little off true
    g = glyph(letter)
    # a size up from 377's, whose letters fill more of a smaller stone than these do
    g = g.resize((round(g.width * 1.1), round(g.height * 1.1)), Image.NEAREST)
    g = g.rotate(rng.uniform(-5, 5), resample=Image.NEAREST, expand=True)
    gx0 = int(round((w - g.width) / 2 + rng.uniform(-1, 1)))
    gy0 = int(round((h - g.height) / 2 + rng.uniform(-1, 1)))
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    lay.alpha_composite(g, (gx0, gy0))
    la = np.asarray(lay.getchannel('A')) & np.asarray(alpha)
    lay.putalpha(Image.fromarray(la))
    img.alpha_composite(lay)
    # a black outline two pixels wide
    out = Image.new('RGBA', (w + 4, h + 4), (0, 0, 0, 0))
    grown = Image.new('L', (w + 4, h + 4), 0)
    grown.paste(alpha, (2, 2))
    grown = grown.filter(ImageFilter.MaxFilter(5))
    out.paste(Image.new('RGBA', (w + 4, h + 4), BLACK + (255,)), (0, 0), grown)
    out.alpha_composite(img, (2, 2))
    return out


def sword_377():
    """377's own sword, cut out of logo377.png: the hilt (its horseshoe guard, round boss, bound grip
    and pommel) from the corner it has to itself, and the blade as the strip between its two black
    edges - 6-7 pixels either side of a straight line in 377, and over bare background near the
    point, where the magenta says exactly where it stops. It lies in front of every stone there, so
    nothing of a stone comes with it. Returned on its own canvas with its hilt's corner at 0, 0."""
    a = np.asarray(Image.open(LOGO377).convert('RGBA')).copy()
    key = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    h, w = key.shape
    m = np.zeros((h, w), bool)
    hilt = np.zeros((h, w), bool)
    hilt[66:135, 40:128] = ~key[66:135, 40:128]
    m |= keep_largest(hilt)                                       # the hilt, not the stone edge in its corner
    for x in range(118, 358):                                     # the blade
        c = 50.5 + (250 - x) * 0.306
        if x >= 250:
            ys = [y for y in range(int(c) - 12, int(c) + 12) if 0 <= y < h and not key[y, x]]
            if ys:
                m[min(ys):max(ys) + 1, x] = True
        else:
            m[int(round(c - 6.5)):int(round(c + 6.5)) + 1, x] = True
    m &= ~key
    a[..., 3] = m * 255
    img = Image.fromarray(a)
    return img.crop(img.getbbox()), img.getbbox()[:2]


def snap(img):
    """Every pixel onto 377's logo palette (the stone greys, blacks and golds), the rest magenta."""
    pal = np.array([BLACK, INK, INK_EDGE] + STONE + GOLD, np.int32)
    a = np.asarray(img.convert('RGBA'), np.int32)
    rgb, alpha = a[..., :3], a[..., 3]
    dist = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    out = pal[dist.argmin(-1)].astype(np.uint8)
    out[alpha < 128] = KEY
    return Image.fromarray(out, 'RGB')


def main():
    global CONTENT
    preview = None
    for a in sys.argv[1:]:
        if a.startswith('--content='):
            CONTENT = os.path.abspath(a.split('=', 1)[1])
        elif a.startswith('--preview='):
            preview = a.split('=', 1)[1]
    rng_py = random.Random(1142)
    rng = np.random.default_rng(1142)
    class R:   # one generator for both kinds of draw
        randint = staticmethod(rng_py.randint)
        uniform = staticmethod(rng_py.uniform)
        random = staticmethod(lambda shape: rng.random(shape))
    font = None
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rows = []
    for text, x0, y0 in zip(ROWS, ROW_X, ROW_Y):
        stones, x = [], x0
        for ch in text:
            st = pebble(R, ch, font)
            stones.append((st, x, y0 + rng_py.randint(-3, 3) - (st.height - 60) // 2))
            x += st.width - 7
        rows.append(stones)
    for st, x, y in rows[0]:
        canvas.alpha_composite(st, (x, y))
    for st, x, y in rows[1]:
        canvas.alpha_composite(st, (x, y))
    # 377's sword, in front of the stones as it is there: hilt low on the left, under the first row
    # and before the second, the point high on the right past the end of the first
    blade, (sx, sy) = sword_377()
    canvas.alpha_composite(blade, (sx + SWORD_DX, sy + SWORD_DY))
    img = snap(canvas)
    path = os.path.join(CONTENT, 'title', 'logo.png')
    img.save(path)
    print('wrote %s (%dx%d, %d colours)' % (path, W, H, len(set(img.getdata())) - 1))
    if preview:
        img.resize((W * 2, H * 2), Image.NEAREST).save(preview)


if __name__ == '__main__':
    main()
