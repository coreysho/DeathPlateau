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
course. What matters is whether the packets behind those numbers are the same, and they are:

    engine server packets            73
    shared by name with Client-TS    56
      identical payload size         54   <- renumber only, handler logic untouched
      different size                  2   LAST_LOGIN_INFO, MIDI_JINGLE

So the protocol gap is a table, not a rewrite - and `src/network/game/server/ServerGameProt.ts`
in the engine is the table. Of the seventeen our engine sends that Client-TS has no name for,
**eight ts377 already handles** and **nine neither client has**, because they are ours:

    IF_SETINVBREAKS · IF_SETINVOP · IF_SETINVWINDOW · MESSAGE_CLAN · PING
    P_DIALOGPROMPT · SET_LOGIN_TOKEN · UPDATE_CLANCHANNEL · VARP_BATCH

Those nine have to be written whichever client is chosen, so they do not separate the two.

## What each gives you for free

| | Client-TS | ts377 |
|---|---|---|
| our engine's HTTP cache routes | **already speaks them** | had to be written (done, ~40 lines) |
| mobile keyboard | **`MobileKeyboard.ts`** | none |
| touch input | **present** | none |
| upstream fixes | **yes** | repository archived |
| proven against our server | no | **authenticates, streams on-demand** |

## The honest cost of each

**Client-TS**: 54 packets renumbered, 2 payloads fixed, 8 handlers written, 13 config opcodes
added - plus the same exercise for the 47 client-to-server packets, which has not been measured.

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

**Before committing, run one experiment.** The config decoders being thirteen opcodes apart says
the formats are close, but the map, model and interface formats have not been compared at all.
Point Client-TS at our cache - the same `/crc` then `/<name><crc>` fetch the spike already does in
40 lines - and see whether it parses our eight archives. A day, and it decides this properly:

- **it parses** - Client-TS is the base, and the protocol table is the first task
- **it does not** - the formats really did move between 274 and 377, ts377's revision advantage is
  real after all, and the answer flips

Either way, keep the spike. It is the only thing that has talked to our server, and it is the
reference for what correct looks like.
