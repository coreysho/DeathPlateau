# Bringing OSRS (and 474) assets into the 377 build

Everything here is run from `tools/models`. Paths in the examples are relative to that directory,
which is why they all read `../../content`.

A model is the easy half. The hard half is step 6, and it is the one that takes the time.

---

## 0. Check the cache before you spend time on it

There are three under `caches/`: `474 cache`, `newest cache` (OSRS) and `rev236 cache`.

```
python cacheid.py "../../caches/newest cache"
```

It works out the store layout, parses every reference table, samples each index and finishes on the
only question that matters: **do the models parse as the 317-family format the 377 client reads?**
Run it first on any cache you have not used before, including one you just downloaded.

## 1. Find what you are importing

**Items can be named.** `importosrs.py --item "Slayer helmet"` searches the cache itself.

**NPCs, locs and graphics need the numeric OSRS id.** The wiki's infobox carries it. `seqfind474.py`
helps for 474 sequences.

Every importer takes `--dry-run`. Use it: it prints what would be written and touches nothing.

## 2. Import

Four importers, one per kind of asset. All of them re-encode models through `osrs2ob2.py` - OSRS
uses model formats the 377 client cannot read - and **every conversion is round-trip verified
before it is written**, so a model that survives the import is a model the client can draw.

### An item

```
python importosrs.py "../../caches/newest cache" \
    --item "Slayer helmet" \
    --dir ../../content/scripts/skill_slayer \
    --content ../../content --dry-run
```

`--item` also takes `id:<obj id>`, and `name=local_name` to choose the name it lands under. For more
than a couple, use `--batch` with a file of `Cache Name=local_name` lines (`#` comments allowed) -
see `batches/batch_gwd.txt`.

Items are the one kind where the OSRS cache is clearly better than 474: it carries
`wearpos`/`wearpos2`/`wearpos3`, and 474 carries none of them. The first 94 items imported from 474
all clipped through the player and had to be fixed by hand.

### An NPC

Models, chathead models, animations, `npc.pack`/`model.pack` entries, and a `.npc` + `.seq`
skeleton.

```
python importosrsnpc.py "../../caches/newest cache" \
    --batch batches/mynpcs.txt \
    --content ../../content \
    --out ../../content/scripts/areas/area_foo/configs/foo
```

Batch lines are `<osrs npc id> <local name> [ready=X] [walk=X] [attack=X] [defend=X] [death=X]`,
where `X` is either a 377 seq name used as is, or `osrs:<seq id>` to convert that OSRS sequence
(it lands as `osrs_seq_<id>`).

The cache gives you stats and combat level. It does **not** give you hunt mode, drops, max hit or
defence bonuses - those are yours to write.

### A loc

For scenery a script spawns or swaps in. Things placed on a map square go through
`importosrsmap.py` instead.

```
python importosrslocs.py "../../caches/newest cache" \
    --loc 23958 --no-anim \
    --content ../../content \
    --out areas/area_foo/configs/foo
```

`--loc` repeats. `--loc-props props.txt` appends extra config lines per loc, as `<osrs id> key=value`.

**Use `--no-anim` unless a script drives the animation.** An animated 377 loc loops its sequence for
ever: the Warriors' Guild dummies are meant to rise once, not pump continuously.

### A graphic (spotanim)

```
python importosrsspot.py "../../caches/newest cache" \
    --spot 1211:ags_spec_spot \
    --seq 7644:osrs_ags_spec \
    --content ../../content \
    --out areas/area_foo/configs/foo
```

The model lands in `models/spot/spot_<name>.ob2`. Extra `--seq` entries - the player animation that
goes with the graphic, usually - are converted into the same `.seq` file. Spotanims and seqs are
separate namespaces, so both can share a name.

## 3. Register the pack ids if the build asks you to

The build normally registers new names itself. Its source-mtime check is unreliable in a worktree
and skips silently, and then the build fails with:

```
ERROR You may need to edit ../content/pack/loc.pack
```

Append `<max id + 1>=<name>` to that pack file by hand. The current maximum:

```
awk -F= '{if ($1+0 > m) m=$1+0} END {print m}' ../../content/pack/loc.pack
```

The same applies to `npc.pack`, `obj.pack`, `model.pack` and `category.pack`.

**Never delete a line from anything in `content/pack/`.** Several of those files are gitignored and
cannot be regenerated - deleting entries breaks the build with errors that do not name the cause
(`animset: anim_0 is missing an ID line`) and git cannot restore them.

When other work is happening in parallel, take ids from the range that round was given rather than
appending at the maximum, or two branches will both claim the same number.

## 4. Build clean

```
cd ../../Engine-TS && rm -rf data/pack && npm run build
```

**Always delete `data/pack` first.** A partial rebuild throws thousands of bogus "could not be
resolved to a symbol" errors that have nothing to do with what you changed.

## 5. Check

```
cd ../../content/scripts && python ../tools/rs2check.py
```

The baseline is **8 ERROR** - long-standing enum-default rows. Anything above 8 is yours.

## 6. Wire it up. The model alone does nothing.

This is the step that costs the time, and the one that gets forgotten.

The importer gives you a model and a config skeleton. It cannot give you behaviour. **Nothing you
import responds to a click until content answers it** - an `[oploc1]`, an `[opnpc1]`, an `[opheld1]`
by id or by category.

The Lunar Isle doors and ladders are the cautionary tale: they were imported cleanly, sat on the map
looking perfect, and did nothing at all for months, because no trigger existed for them. Nineteen
doors and eighteen ladders. `Engine-TS/tools/sim/lunarisle.ts dead` exists to list exactly this
class of thing - everything placed in an area with an op and no script behind it.

---

## Traps

- **Doors import as one half.** A door in this build is two loc records: `~open_door` deletes the
  closed one and adds `loc_param(next_loc_stage)` a tile over, turned a quarter. The open half is
  never placed on a map square, so a map import cannot see it - you write it by hand on the same
  model. The Keldagrim and Lunar Isle doors are both done this way.
- **Chatheads need both halves.** A hood-style helm keeps the bare head in `manhead` and the helmet
  in `manhead2`; a hat that hides the head slot does the reverse. Import one without the other and
  the chatbox shows a bald face or an empty hat. `importosrs.py` handles this now - it did not
  always, which is how it was found.
- **`<col=RRGGBB>` is OSRS markup.** 377 uses `@xxx@` tags. Text copied across from a modern cache
  prints the raw markup in the chatbox; `rs2check` rule 21 catches it.
- **An `[opnpcN]` for an op the npc's config does not declare** is dead code the client can never
  send. `rs2check` rule 20 catches that one.
- **Check what the thing actually is before wiring it.** Sequence ids are easy to mix up: Zulrah's
  dive and rise are the same 21 frames listed forwards and backwards, and two of the three colours
  "dived" by playing the rise - whose first frame is the snake not being there - until it was
  rendered and looked at.

## Verifying you got it right

A config that compiles is not a config that works. The sims under `Engine-TS/tools/sim` boot the
real engine against the built cache, and writing one for what you imported is usually quicker than
logging in to check. The pattern that catches the most is asserting **what the player ends up with**
rather than that the script ran - the Lunar Isle ladders all "worked" until the sim checked which
tile they put the player on, and two of ten were landing inside a wall.

For anything visual, `javaclient/tools/clienttests` drives the real client and takes screenshots,
which is the only way to check a model or an animation actually looks right.
