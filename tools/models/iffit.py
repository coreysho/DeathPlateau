#!/usr/bin/env python3
"""Keep a spellbook hover panel's title inside its panel.

The panels are 474's: 174 pixels inside the frame, with the title in p12 - "Level 86 : Tele Group
Fishing Guild" is 191 of them, and 474's own long names ("Carrallangar Teleport", "Teleport to Ape
Atoll") are a pixel or two over. A title that does not fit in p12 drops to p11, the font the panel's
description is already in, rather than being shortened or wrapped: two lines would run into the
description under it. Widths are the client's own (content/tools/ifrender.py, PixFont's advances),
plus the one pixel the shadow adds.

portmagic474.py and genlunar474.py call fit_titles on everything they write.
"""


def title_font(text, width):
    from ifrender import font
    for name in ('p12_full', 'p11_full'):
        if font(name).width(text) + 1 <= width:
            return name
    raise SystemExit('%r is %d pixels in p11 and its box is %d' % (text, font('p11_full').width(text) + 1, width))


def fit_titles(blocks, get, put):
    """blocks: [(name, kv)] as the generators hold them. Every p12 'Level N : ...' text is refitted."""
    for n, kv in blocks:
        if not n or get(kv, 'type') != 'text' or get(kv, 'font') not in ('p12_full', 'p11_full'):
            continue
        text = get(kv, 'text') or ''
        if not text.startswith('Level '):
            continue
        put(kv, 'font', title_font(text, int(get(kv, 'width'))))
