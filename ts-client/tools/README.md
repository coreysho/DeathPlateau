# tools

## gen-protocol.mjs

Generates Client-TS's `src/io/ServerProt.ts` and `src/io/ClientProt.ts` from the engine's prot
files. The engine is the only place these numbers are authoritative, so the tables are generated
rather than hand-copied - re-run it when the engine changes instead of editing the output.

    node gen-protocol.mjs <engine-dir> <clientts-src-dir> [--write]

Without `--write` it reports and touches nothing. It is idempotent: a second run is byte-identical.

### What it reads

| file | holds |
|---|---|
| `src/network/game/server/ServerGameProt.ts` | top-level server packets |
| `src/network/game/server/ServerGameZoneProt.ts` | packets nested inside `UPDATE_ZONE_*` |
| `src/network/game/client/ClientGameProt.ts` | what the client sends |

The zone packets share the top-level 0-255 opcode space (verified: no collisions), so they belong
in one enum and one size table, which is how Client-TS already had them.

Which names Client-TS "has" is decided by scanning its handler code for `ServerProt.NAME`, not by
reading the enum. A name in the enum proves only that a constant exists, and this tool overwrites
the enum, so reading it back would just be reading the last run.

### Three things it is careful about

**Aliases.** Three packets are the same on both sides under different names, so they are mapped
rather than duplicated. Client-TS's name wins, because its handlers are written against it.

    engine LOC_MERGE              = Client-TS P_LOCMERGE      (the engine carries a todo to rename)
    engine RESET_CLIENT_VARCACHE  = Client-TS VARP_SYNC       (both size 0, both "reset to server")
    engine REPORT_ABUSE           = Client-TS SEND_SNAPSHOT   (g8 offender, g1 reason, gbool mute)

**Inbound orphans are parked.** A name Client-TS handles that our engine never sends is dead code,
but its constant must exist or the client will not compile. Leaving it on its 274 opcode is a trap:
if the engine later uses that number, a stale handler fires on a live packet. So they are moved to
opcodes the engine does not use. Currently `IF_SETICON` and `IF_SHOWICON`.

**Outbound orphans are not.** The engine closes the connection on an opcode it does not know
(`NetworkPlayer.ts`: `if (!packetType) { close() }`), so a name Client-TS *sends* that our engine
lacks cannot be parked - that would disconnect the player the moment the client sent it. Those are
left out of the enum, so the build fails at the send sites and someone has to decide about each.
Five turned up this way: `ANTICHEAT_OPLOGIC6` through `9` and `ANTICHEAT_CYCLELOGIC7`, decoy
packets the 274 client sends that 377 has no concept of. They were removed from `Client.ts`.

### What it does not fix

Equal payload size is not equal payload layout. 42 of the engine's 83 encoders write byte orders
(`_alt1/2/3`) that Client-TS's `Packet` cannot read, and 35 of those are packets Client-TS already
handles - right length, wrong fields. See "The byte order problem" in `../COMPARISON.md`.
