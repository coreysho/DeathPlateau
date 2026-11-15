# ::wipebank - two patches, because this session could not push to the other two repos

`::wipebank` empties the staff member's own bank in one command. The work is split the way
`::bank` is: the command is the engine's, the bank semantics are content's. So it is a commit in
each of those repos, and **neither of them is this one** - the cloud session that wrote it was
only authorised to push to `coreysho/DeathPlateau`, so the two commits are parked here as
patches rather than as branches on their own repos.

Apply them from `C:\LostCityServer`:

```
cd content
git checkout -b claude/wipebank-command
git am "../Claude outputs/notes/wipebank/content-bank_wipe.patch"
```

```
cd Engine-TS
git checkout -b claude/wipebank-command
git am "../Claude outputs/notes/wipebank/engine-wipebank.patch"
```

Then `npm run build` in `Engine-TS` and start the server as usual. Delete this folder once both
are pushed - it is a delivery mechanism, not a record worth keeping.

## What the two commits are

| repo | file | what |
|---|---|---|
| DeathPlateau-Content | `scripts/interface_bank/scripts/bank_wipe.rs2` (new) | `[proc,bank_wipe]` - the confirm, the PIN check, `inv_clear(bank)`, the eight tab counts |
| DeathPlateau-Engine | `src/network/game/client/handler/ClientCheatHandler.ts` | the `cmd === 'wipebank'` branch, in the `staffModLevel >= 3` block next to `::bank` |
| DeathPlateau-Engine | `src/network/game/client/handler/ClientCheatCommands.ts` | the `::commands` line for it, which `tools/sim/commandslist.ts` insists on |
| DeathPlateau-Engine | `tools/sim/wipebank.ts` (new) | the sim: 35 checks |

## What it does

- `::wipebank` - "Permanently delete all 342 items in your bank?" / Yes / No.
- `::wipebank confirm` - skips the box, for wiping, refilling and wiping again while testing.
- Administrator (3) and up. A moderator gets exactly what they get for a command that does not
  exist: nothing.
- A set bank PIN is still asked for first, the way `::bank` asks for one.
- Works with the bank window open, which is when it gets typed.
- The eight `%banktab_c*` counts and the viewed tab go with the items, so the filing describes
  what is actually there rather than waiting for `~banktab_validate` to clamp it on the next open.

## Why not ::~clearinv bank, which already existed

Two reasons, and both of them matter:

1. It is a `[debugproc,]`, and `ClientCheatHandler` only dispatches the debugproc character inside
   its "staffModLevel >= 5, or 4 off production" block - so an administrator on live cannot run
   one at all.
2. `inv_clear` on its own leaves the tab counts behind. A tab is not a tag on an item, it is a
   count of a contiguous range of the one 1410-slot list, so `%banktab_c1..c8` would go on
   claiming items that are no longer there.

## What was run

In a cloud container, with both repos cloned beside each other:

- `python3 ../tools/rs2check.py interface_bank/scripts/bank_wipe.rs2` - 0 ERROR, 0 CHECK
- `npm run build` in the engine - packs clean, so the new script compiles
- `npx tsx tools/sim/wipebank.ts` - **35 ok, 0 FAIL**
- `NODE_PRODUCTION=false NODE_MIN_STAFF_LEVEL=3 npx tsx tools/sim/commandslist.ts` - **37 ok, 0
  FAIL**, and `::wipebank` is in the administrator's list
- `npx eslint`, `npx prettier --check`, `npx tsc --noEmit` on the changed files - clean

Not run: the command typed into a real client. Everything above is the real engine and the real
content, but nobody has looked at the confirm box on a screen.
