#!/usr/bin/env python3
"""Parse a synth (jagfx) sound effect the way the 377 client's Wave/Tone/Envelope/Filter read it, to
check a file is in that format. parse(data) returns the number of bytes a synth takes, or raises."""


class _R:
    def __init__(s, b):
        s.b, s.p = b, 0

    def g1(s):
        v = s.b[s.p]; s.p += 1; return v

    def g2(s):
        v = (s.b[s.p] << 8) | s.b[s.p + 1]; s.p += 2; return v

    def g4(s):
        s.p += 4

    def smart_s(s):     # Packet.gsmart: signed
        return s.g1() - 64 if s.b[s.p] < 128 else s.g2() - 49152

    def smart_u(s):     # Packet.gsmarts
        return s.g1() if s.b[s.p] < 128 else s.g2() - 32768


def _envelope(r):
    r.g1(); r.g4(); r.g4()
    _points(r)


def _points(r):
    n = r.g1()
    for _ in range(n):
        r.g2(); r.g2()


def _filter(r):
    v = r.g1()
    pairs = [v >> 4, v & 15]
    if v == 0:
        return
    unity = [r.g2(), r.g2()]
    mask = r.g1()
    for d in range(2):
        for _ in range(pairs[d]):
            r.g2(); r.g2()
    for d in range(2):
        for k in range(pairs[d]):
            if mask & (1 << (d * 4) << k):
                r.g2(); r.g2()
    if mask != 0 or unity[1] != unity[0]:
        _points(r)


def _tone(r):
    _envelope(r); _envelope(r)
    for _ in range(3):
        if r.b[r.p] != 0:
            _envelope(r); _envelope(r)
        else:
            r.g1()
    for _ in range(10):
        v = r.smart_u()
        if v == 0:
            break
        r.smart_s(); r.smart_u()
    r.smart_u(); r.smart_u(); r.g2(); r.g2()
    _filter(r)


def parse(data):
    r = _R(data)
    for _ in range(10):
        if r.b[r.p] != 0:
            _tone(r)
        else:
            r.g1()
    r.g2(); r.g2()
    return r.p
