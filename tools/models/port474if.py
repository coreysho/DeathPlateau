#!/usr/bin/env python3
"""Turn a rev-474 interface into a content .if file, and bring the art it uses with it.

    python tools/models/port474if.py "caches/474 cache" 550 friends --out out/474if/friends.if
    python tools/models/port474if.py "caches/474 cache" 550 friends --names 2=title,3=add

It does the part of porting a tab that is the same every time - positions, sizes, text, colours,
fonts, sprites, layers - and says what it could not do. It does NOT know what the tab is FOR: which
component a script sets text on, which button runs what. Those names are the content's (a script
says `[if_button,prayer:prayer_thickskin]`), so the output is a starting point that is merged by hand
into the existing .if, keeping every name the scripts use. --names renames components as they are
written so the merge is shorter.

EITHER FORMAT. if3_474.Cache.load hands back old-format components (if1_474) and new-format ones
(if3_474) alike. The old format is 377's own, so it converts field for field, client scripts
included. The new format is filled in at run time by client scripts this client does not have, so a
converted new-format tab is its static layout: text that a script would have written is whatever the
cache holds (often ""), and that is flagged.

WHAT CHANGES ON THE WAY

  sprites   474 numbers them; the content names them. A 474 sprite that is already in
            content/sprites - same pixels in the same place on the canvas, which most interface art
            is - is written by its existing name (steelborder,0). Anything new is written to
            content/sprites as i474_N.png on its full cache canvas (the packer crops it and keeps the
            offset) and named i474_N,0. Existing files are left alone.
  tiling    a new-format graphic can tile its sprite over its box; 377's cannot, so a tiled one
            becomes a row of copies named <name>_t0, _t1, ..., the last moved back to end on the
            box's edge the way 377's own frames overlap it.
  fonts     474 names a font by its sprite group: 494 p11, 495 p12, 496 b12, 497 q8.
  text      377 draws a line's baseline at y + font height, one font height per line, left or
            centred, never vertically centred. 474 has a line height of its own and top/centre/
            bottom alignment. So multi-line text whose line height differs, or any vertically
            aligned text, is split into one component per line (<name>_l1, _l2, ...) placed at the
            baselines 474 would draw - OSRS's AbstractFont.drawLines arithmetic, with 377's font
            heights as the ascent. <br> is a line break; <col=rrggbb> becomes the nearest of the
            17 colour tags 377's fonts know. Right-aligned text has no 377 form and is flagged.
  ops       a new-format component's first op becomes option= on a normal button; its name, if it
            has one, follows the op ("Activate @or1@Thick Skin", as the 474 menu showed it).
  scripts   old-format client scripts are decoded and written in the .if form (script1op1=...),
            with varps, varbits and objects by content name (pack/*.pack) and stats by name - 474
            has Hunter at 21 and Construction at 22, this server the other way round. A component
            link in inv_count/inv_contains is written by --links, or flagged.
"""
import argparse, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

FONTS = {494: 'p11_full', 495: 'p12_full', 496: 'b12_full', 497: 'q8_full'}
ASCENT = {'p11_full': 10, 'p12_full': 12, 'b12_full': 12, 'q8_full': 15}
DESCENT = 3

# 377's colour tags (PixFont.evaluateTag)
TAGS = {'red': 0xff0000, 'gre': 0x00ff00, 'blu': 0x0000ff, 'yel': 0xffff00, 'cya': 0x00ffff,
        'mag': 0xff00ff, 'whi': 0xffffff, 'bla': 0x000000, 'lre': 0xff9040, 'dre': 0x800000,
        'dbl': 0x000080, 'or1': 0xffb000, 'or2': 0xff7000, 'or3': 0xff3000, 'gr1': 0xc0ff00,
        'gr2': 0x80ff00, 'gr3': 0x40ff00}

# 474's stat order. This server has Construction at 21 and Hunter at 22.
STATS474 = ['attack', 'defence', 'strength', 'hitpoints', 'ranged', 'prayer', 'magic', 'cooking',
            'woodcutting', 'fletching', 'fishing', 'firemaking', 'crafting', 'smithing', 'mining',
            'herblore', 'agility', 'thieving', 'slayer', 'farming', 'runecraft', 'hunter', 'construction']

TYPES = {0: 'layer', 2: 'inv', 3: 'rect', 4: 'text', 5: 'graphic', 6: 'model', 7: 'invtext', 8: '8'}
BUTTONS = {1: 'normal', 2: 'target', 3: 'close', 4: 'toggle', 5: 'select', 6: 'pause'}
COMPARATORS = {1: 'eq', 2: 'lt', 3: 'gt', 4: 'neq'}
SCRIPT_OPS = {1: ('stat_level', 's'), 2: ('stat_base_level', 's'), 3: ('stat_xp', 's'),
              4: ('inv_count', 'co'), 5: ('pushvar', 'v'), 6: ('stat_xp_remaining', 's'), 7: ('op7', ''),
              8: ('op8', ''), 9: ('op9', ''), 10: ('inv_contains', 'co'), 11: ('runenergy', ''),
              12: ('runweight', ''), 13: ('testbit', 'vn'), 14: ('push_varbit', 'b'), 15: ('subtract', ''),
              16: ('divide', ''), 17: ('multiply', ''), 18: ('coordx', ''), 19: ('coordz', ''),
              20: ('push_constant', 'n')}


def nearest_tag(rgb):
    r, g, b = rgb >> 16 & 255, rgb >> 8 & 255, rgb & 255
    best = min(TAGS.items(), key=lambda kv: (r - (kv[1] >> 16 & 255)) ** 2 + (g - (kv[1] >> 8 & 255)) ** 2 + (b - (kv[1] & 255)) ** 2)
    return '@%s@' % best[0]


def tags(text):
    text = re.sub(r'<col=([0-9a-fA-F]{6})>', lambda m: nearest_tag(int(m.group(1), 16)), text)
    text = text.replace('</col>', '')
    return text


def load_pack(name):
    out = {}
    path = os.path.join(ROOT, 'content', 'pack', name + '.pack')
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            if '=' in line:
                i, n = line.rstrip('\r\n').split('=', 1)
                out[int(i)] = n
    return out


class Converter:
    def __init__(self, cache, gid, ifname, names, links, root_type):
        self.cache = cache
        self.gid = gid
        self.ifname = ifname
        self.names = names
        self.links = links
        self.root_type = root_type
        self.comps = cache.load(gid)
        self.sprites = set()
        self.crops = set()
        self.index = None
        self.notes = []
        self.varps = load_pack('varp')
        self.varbits = load_pack('varbit')
        self.objs = load_pack('obj')

    def name(self, fid):
        return self.names.get(fid, 'com_%d' % fid)

    def note(self, fid, text):
        self.notes.append('%s: %s' % (self.name(fid), text))

    # ---- one component -> one or more .if blocks

    def blocks(self, fid, c):
        name = self.name(fid)
        head = []
        if c['parent'] is not None:
            head.append('layer=%s' % self.name(c['parent']))
        t = c['type']
        if t == 9 and (c['width'] == 0 or abs(c['height']) == 0):
            # a straight line (the new format's type 9) is a filled rect one line-width thick
            lw = max(1, c.get('linewidth') or 1)
            w, h = max(c['width'], lw), max(abs(c['height']), lw)
            y = c['y'] + min(0, c['height'])
            kv = [('type', 'rect')] + [tuple(x.split('=', 1)) for x in head]
            kv += [('x', c['x']), ('y', y), ('width', w), ('height', h), ('fill', 'yes'),
                   ('colour', '0x%06X' % (c.get('colour', 0) & 0xffffff))]
            return [(name, kv)]
        if t not in TYPES:
            self.note(fid, 'type %d has no 377 form - skipped' % t)
            return []
        if t == 5 and c.get('if3') and c.get('tiling'):
            return self.tiled(fid, c, head)
        if t == 4 and self.needs_split(c):
            return self.split_text(fid, c, head)

        kv = [('type', TYPES[t])] + [(k, v) for k, v in (x.split('=', 1) for x in head)]
        kv += [('x', c['x']), ('y', c['y'])]
        kv += self.behaviour(fid, c)
        kv += [('width', c['width']), ('height', max(0, c['height']))]
        if not c.get('if3') and c.get('trans'):
            # an old-format component's own transparency - 255 is an invisible hit box, like the
            # special attack bar's rect
            kv.append(('trans', c['trans']))
        kv += self.body(fid, c)
        return [(name, kv)]

    def behaviour(self, fid, c):
        kv = []
        if c.get('if3'):
            if c['ops'] == ['Close']:
                # 474's close X is a one-op component; the old format's own close button does what
                # its script did, with no trigger to write
                kv.append(('buttontype', 'close'))
            elif c['ops']:
                label = c['ops'][0]
                if c.get('name'):
                    label += ' ' + tags(c['name'])
                kv += [('buttontype', 'normal'), ('_option', label)]
                if len(c['ops']) > 1:
                    self.note(fid, 'ops after the first dropped: %s' % c['ops'][1:])
            if any(c.get(k) for k in ('onLoad', 'onVarTransmit', 'onInvTransmit', 'onStatTransmit', 'onTimer')):
                self.note(fid, 'filled in by a client script at run time (%s)' % ', '.join(
                    k for k in ('onLoad', 'onVarTransmit', 'onInvTransmit', 'onStatTransmit', 'onTimer') if c.get(k)))
            return kv
        bt = c.get('buttontype', 0)
        if bt in BUTTONS:
            kv.append(('buttontype', BUTTONS[bt]))
        if c.get('clientcode'):
            kv.append(('clientcode', c['clientcode']))
            self.note(fid, 'clientcode %d is 474\'s meaning - check it against this client' % c['clientcode'])
        kv += self.scripts(fid, c)
        if c.get('option'):
            kv.append(('_option', tags(c['option'])))
        if bt == 2 or t_is_inv(c):
            if c.get('targetverb'):
                kv.append(('actionverb', c['targetverb']))
            if c.get('targettext'):
                kv.append(('action', tags(c['targettext'])))
            mask = c.get('targetmask', 0)
            flags = [n for bit, n in ((1, 'obj'), (2, 'npc'), (4, 'loc'), (8, 'player'), (16, 'heldobj')) if mask & bit]
            if flags:
                kv.append(('actiontarget', ','.join(flags)))
        return kv

    def scripts(self, fid, c):
        kv = []
        comps = c.get('comparators') or []
        for i, script in enumerate(c.get('scripts') or []):
            j = i + 1
            ops, k = [], 0
            while k < len(script):
                op = script[k]; k += 1
                if op == 0:
                    break
                if op not in SCRIPT_OPS:
                    self.note(fid, 'script op %d unknown' % op)
                    break
                opname, args = SCRIPT_OPS[op]
                parts = [opname]
                for a in args:
                    v = script[k]; k += 1
                    if a == 's':
                        parts.append(STATS474[v] if v < len(STATS474) else str(v))
                    elif a == 'v':
                        parts.append(self.varps.get(v) or self.flag(fid, 'varp %d has no content name' % v, 'varp_%d' % v))
                    elif a == 'b':
                        parts.append(self.varbits.get(v) or self.flag(fid, 'varbit %d has no content name' % v, 'varbit_%d' % v))
                    elif a == 'c':
                        parts.append(self.links.get(v) or self.flag(fid, 'component link %d:%d needs --links' % (v >> 16, v & 0xffff), 'link_%d' % v))
                    elif a == 'o':
                        parts.append(self.objs.get(v) or self.flag(fid, 'obj %d has no content name' % v, 'obj_%d' % v))
                    else:
                        parts.append(str(v))
                ops.append(','.join(parts))
            for n, op in enumerate(ops):
                kv.append(('script%dop%d' % (j, n + 1), op))
            if i < len(comps):
                cmp, val = comps[i]
                kv.append(('script%d' % j, '%s,%d' % (COMPARATORS.get(cmp, 'eq'), val)))
        return kv

    def flag(self, fid, text, value):
        self.note(fid, text)
        return value

    def body(self, fid, c):
        t = c['type']
        kv = []
        if t == 0:
            scroll = c.get('scrollheight', c.get('scroll', 0))
            if scroll:
                kv.append(('scroll', scroll))
            if c.get('hidden') or c.get('hide'):
                kv.append(('hide', 'yes'))
        elif t == 3:
            if c.get('fill'):
                kv.append(('fill', 'yes'))
            kv.append(('colour', '0x%06X' % (c.get('colour', 0) & 0xffffff)))
            for k in ('activecolour', 'overcolour', 'activeovercolour'):
                if c.get(k):
                    kv.append((k, '0x%06X' % (c[k] & 0xffffff)))
            if c.get('opacity'):
                kv.append(('trans', c['opacity']))
        elif t == 4:
            kv += self.text_fields(fid, c, tags(c.get('text', '')).replace('<br>', '\\n'))
        elif t == 5:
            g = c.get('sprite') if c.get('if3') else c.get('graphic')
            if g is not None and g >= 0:
                kv.append(('graphic', self.sprite(g)))
            ag = c.get('activegraphic', -1)
            if ag is not None and ag >= 0:
                kv.append(('activegraphic', self.sprite(ag)))
            if c.get('if3') and (c.get('hflip') or c.get('vflip') or c.get('rotation')):
                self.note(fid, 'flip/rotation has no 377 form')
        elif t == 6:
            self.note(fid, 'model %s - set model= by hand' % c.get('model'))
            for k in ('zoom', 'xan', 'yan'):
                if c.get(k) is not None:
                    kv.append((k, c[k]))
        elif t == 2:
            self.note(fid, 'inventory - port by hand')
        elif t == 8:
            # a hover tooltip: its box is where the mouse has to be, its text what it says
            kv.append(('text', tags(c.get('text', '')).replace('<br>', '\\n')))
        return kv

    def text_fields(self, fid, c, text):
        font = FONTS.get(c.get('font'))
        if font is None:
            self.note(fid, 'font %s unknown - using p12_full' % c.get('font'))
            font = 'p12_full'
        kv = []
        if c.get('xalign') == 1 or c.get('center'):
            kv.append(('center', 'yes'))
        if c.get('xalign') == 2:
            self.note(fid, 'right-aligned text has no 377 form - drawn left-aligned')
        kv.append(('font', font))
        if c.get('shadowed'):
            kv.append(('shadowed', 'yes'))
        kv.append(('text', text))
        kv.append(('colour', '0x%06X' % (c.get('colour', 0) & 0xffffff)))
        for k in ('activecolour', 'overcolour', 'activeovercolour'):
            if c.get(k):
                kv.append((k, '0x%06X' % (c[k] & 0xffffff)))
        if c.get('activetext'):
            kv.append(('activetext', tags(c['activetext']).replace('<br>', '\\n')))
        return kv

    # ---- text 377 cannot place itself

    def needs_split(self, c):
        font = FONTS.get(c.get('font'), 'p12_full')
        lines = c.get('text', '').split('<br>')
        lh = c.get('lineheight') or ASCENT[font]
        return c.get('yalign', 0) != 0 or (len(lines) > 1 and lh != ASCENT[font])

    def split_text(self, fid, c, head):
        name = self.name(fid)
        font = FONTS.get(c.get('font'), 'p12_full')
        asc = ASCENT[font]
        lines = c.get('text', '').split('<br>')
        lh = c.get('lineheight') or asc
        h = c['height']
        n = len(lines)
        ya = c.get('yalign', 0)
        if ya == 0:
            base = asc
        elif ya == 1:
            base = (h - asc - DESCENT - lh * (n - 1)) // 2 + asc
        else:
            base = h - DESCENT - lh * (n - 1)
        # the active text, if any, splits line for line with it, and every line keeps the client
        # script that chooses between them ("Auto Retaliate / (Off)" against "... / (On)")
        active = c.get('activetext', '').split('<br>') if c.get('activetext') else None
        out = []
        for i, line in enumerate(lines):
            nm = name if i == 0 else '%s_l%d' % (name, i)
            y = c['y'] + base + i * lh - asc
            kv = [('type', 'text')] + [tuple(x.split('=', 1)) for x in head]
            kv += [('x', c['x']), ('y', y)]
            if i == 0:
                kv += self.behaviour(fid, c)
            elif active and not c.get('if3'):
                kv += self.scripts(fid, c)
            kv += [('width', c['width']), ('height', asc + DESCENT)]
            one = dict(c)
            one['activetext'] = active[i] if active and i < len(active) else ''
            kv += self.text_fields(fid, one, tags(line))
            out.append((nm, kv))
        if n > 1 and c.get('onLoad'):
            self.note(fid, 'split into %d lines, but a script sets its text - one line may be wanted' % n)
        return out

    def tiled(self, fid, c, head):
        import osrssprite
        name = self.name(fid)
        g = c['sprite']
        d = osrssprite.decode(self.cache.store.read(8, g))
        sw, sh = d['width'], d['height']
        out, k = [], 0
        W, H = max(1, c['width']), max(1, c['height'])
        for y in self.steps(H, sh):
            for x in self.steps(W, sw):
                w, h = min(sw, W - x), min(sh, H - y)
                # 474 clips a tile to its box; a 377 graphic cannot. The last tile of a row is moved
                # back to end on the box's edge, overlapping the one before - what 377's own frames
                # do (friends.if's top edge has a tile at 112 after the one at 100). Only a box
                # smaller than one tile needs a cropped copy (i474_N_WxH).
                graphic = self.sprite(g) if (w, h) == (sw, sh) else self.cropped(g, w, h)
                kv = [('type', 'graphic')] + [tuple(p.split('=', 1)) for p in head]
                kv += [('x', c['x'] + x), ('y', c['y'] + y), ('width', w), ('height', h), ('graphic', graphic)]
                out.append((name if k == 0 else '%s_t%d' % (name, k), kv))
                k += 1
        return out

    @staticmethod
    def steps(total, step):
        if total <= step:
            return [0]
        out = list(range(0, total - step + 1, step))
        if out[-1] + step < total:
            out.append(total - step)
        return out

    def cropped(self, g, w, h):
        self.crops.add((g, w, h))
        return 'i474_%d_%dx%d,0' % (g, w, h)

    def sprite(self, g):
        found = self.existing(g)
        if found:
            return found
        self.sprites.add(g)
        return 'i474_%d,0' % g

    def existing(self, g):
        """The content sprite this 474 sprite already is, pixel for pixel, as 'sheet,index' - or None.

        474 kept most of 377's interface art and gave it numbers: the Friends tab's steel border,
        corner pieces and stone button are exactly steelborder, steelborder2, miscgraphics 2-3 and
        combatboxes 0. Importing them again as i474_N would be a second copy of every one. So a
        sprite is looked up by its opaque pixels AND where they sit on the canvas (the packer keeps
        that offset, so two images with the same pixels in different places would draw apart)."""
        if self.index is None:
            self.index = content_sprite_index(os.path.join(ROOT, 'content', 'sprites'))
        return self.index.get(signature(self.image(g)))

    # ---- the whole interface

    def convert(self):
        children = defaultdict(list)
        for fid, c in sorted(self.comps.items()):
            children[c['parent']].append(fid)
        order = []

        def walk(parent):
            for fid in children.get(parent, []):
                order.append(fid)
                walk(fid)
        walk(None)
        missing = set(self.comps) - set(order)
        for fid in sorted(missing):
            self.note(fid, 'parent %s is not in this interface - put at the top level' % self.comps[fid]['parent'])
            self.comps[fid]['parent'] = None
            order.append(fid)

        text = ['type=%s' % self.root_type]
        for fid in order:
            for name, kv in self.blocks(fid, self.comps[fid]):
                text.append('')
                text.append('[%s]' % name)
                option = None
                for k, v in kv:
                    if k == '_option':
                        option = v
                        continue
                    text.append('%s=%s' % (k, v))
                if option:
                    text.append('option=%s' % option)
        return '\n'.join(text) + '\n'

    def image(self, g):
        import osrssprite
        from PIL import Image
        d = osrssprite.decode(self.cache.store.read(8, g))
        s, pal = d['sprites'][0], d['palette']
        im = Image.new('RGB', (d['width'], d['height']), (255, 0, 255))
        px = im.load()
        for y in range(s['h']):
            for x in range(s['w']):
                v = s['px'][y * s['w'] + x]
                if v:
                    c = pal[v]
                    px[s['ox'] + x, s['oy'] + y] = (c >> 16 & 255, c >> 8 & 255, c & 255)
        return im

    def write_sprites(self, out_dir, force=False):
        written = []
        for g in sorted(self.sprites):
            path = os.path.join(out_dir, 'i474_%d.png' % g)
            if os.path.exists(path) and not force:
                continue
            self.image(g).save(path)
            written.append(str(g))
        for g, w, h in sorted(self.crops):
            path = os.path.join(out_dir, 'i474_%d_%dx%d.png' % (g, w, h))
            if os.path.exists(path) and not force:
                continue
            self.image(g).crop((0, 0, w, h)).save(path)
            written.append('%d_%dx%d' % (g, w, h))
        return written


def signature(im):
    """Opaque pixels plus their bounding box on the canvas - what the packer keeps of an image."""
    px = im.load()
    W, H = im.size
    x0, y0, x1, y1 = W, H, -1, -1
    for y in range(H):
        for x in range(W):
            if px[x, y] != (255, 0, 255):
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
    if x1 < 0:
        return None
    return (x0, y0, im.crop((x0, y0, x1 + 1, y1 + 1)).tobytes())


def content_sprite_index(folder):
    """signature -> 'sheet,index' for every tile of every content sprite (sheets by their .opt)."""
    from PIL import Image
    out = {}
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.png') or f.startswith('i474_'):
            continue
        name = f[:-4]
        im = Image.open(os.path.join(folder, f)).convert('RGB')
        tw, th = im.size
        opt = os.path.join(folder, 'meta', name + '.opt')
        if os.path.exists(opt):
            tw, th = map(int, open(opt).read().splitlines()[0].strip().split('x'))
        i = 0
        for y in range(0, im.size[1], th):
            for x in range(0, im.size[0], tw):
                sig = signature(im.crop((x, y, x + tw, y + th)))
                if sig and sig not in out:
                    out[sig] = '%s,%d' % (name, i)
                i += 1
    return out


def t_is_inv(c):
    return c.get('type') == 2


def parse_map(text, value=str):
    out = {}
    for part in (text or '').split(','):
        if '=' in part:
            k, v = part.split('=', 1)
            out[int(k)] = value(v)
    return out


def main():
    from if3_474 import Cache
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cache')
    ap.add_argument('id', type=int, help='474 interface id')
    ap.add_argument('ifname', help='content interface name, for the notes')
    ap.add_argument('--out', help='write the .if here (default: print it)')
    ap.add_argument('--names', help='fid=name,... renames as written')
    ap.add_argument('--links', help='474 component link=content name,... for inv_count/inv_contains, e.g. 9764864=inventory:inv')
    ap.add_argument('--root', default='overlay', help='the first line\'s type= (tabs are overlay)')
    ap.add_argument('--sprites', default=os.path.join(ROOT, 'content', 'sprites'), help='where i474_N.png go')
    ap.add_argument('--no-sprites', action='store_true')
    a = ap.parse_args()

    conv = Converter(Cache(a.cache), a.id, a.ifname, parse_map(a.names), parse_map(a.links), a.root)
    text = conv.convert()
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print('wrote %s' % a.out)
    else:
        sys.stdout.write(text)
    if not a.no_sprites:
        new = conv.write_sprites(a.sprites)
        print('sprites: %d used, %d new (%s)' % (len(conv.sprites) + len(conv.crops), len(new), ' '.join(new) or '-'), file=sys.stderr)
    for n in conv.notes:
        print('  note: ' + n, file=sys.stderr)


if __name__ == '__main__':
    main()
