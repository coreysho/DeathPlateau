# Which client to build on

Two candidates. The spike was built on the second one because it was the one that was already
revision 377; this is the comparison that should have come first.

    Client-TS   github.com/LostCityRS/Client-TS, branch 274, last commit 2026-07-16
    ts377       github.com/89wc/runescape-web-client-37789 @ 7582d03, last commit 2023-02-23

They are the same size - 90 files and 37,223 lines against 89 and 37,887 - and almost nothing else
about them is the same.

## Code

    obfuscated-style identifiers    Client-TS 0        ts377 3,769

ts377 is a machine translation of decompiled Java and reads like one: `method77`, `aClass18_1206`,
`anInt1234`. Its packet dispatch is a chain of comparisons against bare numbers. Client-TS is a
hand-written port with real names and a `ServerProt` enum, and it is still being worked on -
upstream commits four months ago against three and a half years ago.

For a project whose largest phase is porting a 222-class plugin sidebar into it, that difference
compounds every week.

## Revision

This is where ts377 looked unbeatable, and it is less decisive than it appears.

**Config decoders.** Compared against our own Java client, which is the ground truth for a 377
cache, Client-TS is short by thirteen opcodes across eight types:

    ObjType 115 · LocType 10 77 · NpcType 106 107 108 · SeqType 12 13 · FloType 7 · VarpType 12 13 14

ts377 matches ours exactly - 33 of 33 on ObjType. But thirteen opcodes is a day, not a quarter.

**Protocol.** The opcode numbers are completely different: `IF_OPENCHAT` is 109 for our engine and
166 in Client-TS; `IF_CLOSE` is 29 against 171. Jagex renumbered between revisions as a matter of
course. What matters is whether the packets behind those numbers are the same.

> **Corrected 2026-11-16, after doing the port.** What this section originally said - 54 of 56
> packets are "renumber only, handler logic untouched" - was wrong, and wrong in the direction
> that flattered Client-TS. Two mistakes. I read only `ServerGameProt.ts` and missed
> `ServerGameZoneProt.ts`, so the engine sends 84 server packets, not 73. And I treated equal
> payload *size* as equal payload *layout*. It is not. See "The byte order problem" below.

    engine server packets            84   (73 top-level + 11 zone)
    shared by name with Client-TS    69   (3 of them under a different name)
      identical payload size         67
      different size                  2   LAST_LOGIN_INFO, MIDI_JINGLE

Three are the same packet under two names: the engine's `LOC_MERGE` is Client-TS's `P_LOCMERGE`
(the engine source carries a todo to rename it), `RESET_CLIENT_VARCACHE` is `VARP_SYNC`, and
`REPORT_ABUSE` is `SEND_SNAPSHOT` - byte-identical, `g8` offender, `g1` reason, `gbool` mute.

Of the fifteen our engine sends that Client-TS has no handler for, **nine neither client has**,
because they are ours:

    IF_SETINVBREAKS · IF_SETINVOP · IF_SETINVWINDOW · MESSAGE_CLAN · PING
    P_DIALOGPROMPT · SET_LOGIN_TOKEN · UPDATE_CLANCHANNEL · VARP_BATCH

Those nine have to be written whichever client is chosen, so they do not separate the two.

## The byte order problem

Equal size does not mean equal layout. Our engine writes many fields in byte orders the 377
protocol calls for, and `src/io/Packet.ts` in the engine names them `_alt1`, `_alt2`, `_alt3`:

| engine | what it writes | |
|---|---|---|
| `p1_alt1` | `v + 128` | |
| `p1_alt2` | `0 - v` | |
| `p1_alt3` | `128 - v` | |
| `p2_alt1` | little-endian | `p2` is big-endian |
| `p2_alt2` | high byte, then `v + 128` | |
| `p2_alt3` | `v + 128`, then high byte | |

**42 of the engine's 83 server encoders use them. Client-TS cannot read a single one** - its
`Packet` has `g1 g2 g3 g4 g8` and nothing else, and the string `_alt` does not appear anywhere in
its source. The sizes match because byte order does not change length.

`UPDATE_PID` is the clearest case. The engine writes `pbool(members)` then `p2_alt1(uid)`.
Client-TS reads `g2()` as the slot and `g1()` as the members flag - the fields transposed *and*
the two-byte field read in the wrong order. Three bytes either way, so the stream stays in sync
and nothing looks broken; the client just believes the wrong numbers.

Counting only the packets Client-TS already handles:

    handled, byte order matches        32
    handled, byte order DIFFERS        35   <- field reads must change, after new Packet readers
    not handled, plain byte order       9
    not handled, alt byte order         7

The 35 include the ones that matter most: `UPDATE_ZONE_PARTIAL_ENCLOSED`,
`UPDATE_ZONE_FULL_FOLLOWS`, `UPDATE_ZONE_PARTIAL_FOLLOWS`, `REBUILD_NORMAL`, `VARP_SMALL`,
`VARP_LARGE`, `UPDATE_STAT`, `UPDATE_INV_FULL`, every `IF_SET*`, and every zone packet.

**ts377 does not have this problem, and cannot.** It is the 377 client, so its `Buffer` already
carries the whole vocabulary - `getUnsignedLEShort`, `getLittleShortA`, `getByteAdded`,
`getByteNegated`, `getByteSubtracted`, `getBytesReverse` - and its reads match our engine's
writes by construction, because our engine was written to feed it.

This is real evidence against the recommendation below, and it is not small. It does not reverse
it on its own: Client-TS still has the mobile input, the cache routes and a live upstream, and
ts377 still freezes on boot with the cause unknown. But "the protocol gap is a table, not a
rewrite" was not true, and the table turned out to be the easy half.

## What each gives you for free

| | Client-TS | ts377 |
|---|---|---|
| our engine's HTTP cache routes | **already speaks them** | had to be written (done, ~40 lines) |
| mobile keyboard | **`MobileKeyboard.ts`** | none |
| touch input | **present** | none |
| upstream fixes | **yes** | repository archived |
| proven against our server | no | **authenticates, streams on-demand** |

## The honest cost of each

**Client-TS**: the opcode table is now ported and verified (see `tools/gen-protocol.mjs` and
`clientts-protocol.patch`). What that leaves: **35 handlers whose field reads are wrong** plus the
`Packet` readers they need, 15 handlers to write, 2 payload layouts to redo, 13 config opcodes to
add. The client-to-server side is now measured too - 86 engine packets, 77 of which Client-TS
already sends, 9 it never sends, and 5 decoy anticheat packets that had to be removed because our
engine closes the connection on an opcode it does not know.

**ts377**: living in machine-translated code for the length of the project, with no upstream. Six
bugs turned up in its loader in a single afternoon - a field never constructed, a music fetch that
blocks startup, wait loops with no escape, a preload nobody needs, a catch that hides every cause -
and one is still open. Nobody has run it against a live server past a login screen, and that is
not a coincidence: that is where its bugs start.

## Recommendation: Client-TS

The gap that made ts377 look obvious turns out to be a renumbering table whose answers are already
written down in our own engine. The gap the other way - readable, maintained code, with the mobile
work half done - is the one that gets more expensive every month.

ts377's real advantage is that it authenticates today. That is worth less than it sounds: it has
never drawn the game world, and its proven surface ends at the login screen.

## The experiment, run

Client-TS's own parsers, in node, over our eight live archives.

**The checksum table.** Its validation - `calc = 1234; for each of 9: calc = (calc << 1) + crc` -
produces `1696506262` against our `/crc`, which is exactly the word our engine sends. The format
is identical.

**The archives.** All eight parse. `config` carries all eight definition files, `interface`
unpacks from bzip2, `media` holds 621 files, `versionlist` all four indexes. The only one that
looked short was `title`, and that was my probe asking for `p11_full` when the file is
`p11_full.dat` - all four fonts are there.

**The indexes.** `11,518` objects, `5,131` npcs, `19,768` locs, read straight out of our cache.

**The decoders.** Real items, decoded by Client-TS from our `obj.dat`:

        995  Coins              1215  Dragon dagger
       1038  Red partyhat        385  Shark
       1050  Santa hat         11000  Bandos d'hide shield
       4151  Abyssal whip      11802  *** hangs ***

So the formats did **not** move between 274 and 377. Our cache is readable as it stands, custom
content included - `11000` is ours and decodes fine.

**And the thirteen-opcode gap is real, and bounded.** `11802` is the Armadyl godsword, imported
from OSRS. The decoder does not fail on it, it desyncs and loops: a field it has no case for is
read as the next opcode, and the stream is lost from there. That is precisely what a missing
opcode does, it is confined to the items that use one, and it is the same day of work the table
above predicted.

## Verdict

Client-TS. The revision gap is a renumbering table and thirteen opcodes, both measured, with our
own engine as the specification. The other direction - machine-translated code, no upstream, six
loader bugs in an afternoon - gets worse every month of a project whose largest phase is porting a
222-class sidebar.

Keep the spike regardless. It is the only thing that has authenticated against our server, and it
is the reference for what correct looks like when Client-TS gets there.
