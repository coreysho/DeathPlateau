# The suggestion list, measured against the tree

> ## BUILT, 12-13 October 2026: eleven done, and half of a twelfth.
>
> On branch `claude/awesome-bohr-h61pym` in **Content** and **Engine**. 37 items imported from OSRS,
> 13 enchant rows, one hand-placed loc, one farming rule, nine recolours, one instanced minigame,
> 27 measured teleport destinations and a vote currency. **343 checks** passing against the real
> engine and the real map: `jewellery.ts` 120, `voteshop.ts` 69, `farmtele.ts` 57, `graceful.ts` 52,
> `pestsolo.ts` 45. Merged up to `377-wip` (content `75d8dfb9`, engine `d8da1e4`, this repo
> `93c679b`) — the Undertaker's outfit, cape, Gravedigger kit, max cape and collection log page, and
> the worn-model depth-sort work.
>
> | # | Built | Notes against what this document predicted |
> |---|---|---|
> | 4 | Emerald necklace → **Binding necklace** | One line, as predicted |
> | 5 | Ruby necklace → **Digsite pendant** | One destination; Fossil Island and Lithkren do not exist here |
> | 6 | Diamond necklace → **Phoenix necklace** | Heals 30% below 20% HP, off the ring-of-life hook |
> | 7 | Dragonstone necklace → **Skills necklace** | **Four** guilds, not six — see the correction below |
> | 8 | **Amulet of nature** | The whole chain was already in the cache, as predicted. **+3% yield when worn**, added on Corey's word after this document argued against it |
> | 18 | **Autoweed** at 65 Farming | One early return in `~farming_regrow_weeds` |
> | 2 | **Jade and red topaz jewellery** | Much cheaper than predicted — see the correction below |
> | 11 | **Amulet of eternal glory** + Fountain of Rune | 1/250, placed at Wilderness 48 |
> | 20 | **Graceful recolours** | Built. Nine colours, one per rooftop course, 50 marks a kit from Grace. Marks finally have a sink |
> | 1 | **Pest Control, solo** | Built. 54 npcs given stats from the OSRS cache, every coordinate scanned off the island's collision. The "PC event" half is still not built — there is no world-event scheduler |
> | 9 | **The patch-run teleport**, on Explorer's ring 4 | Built. 27 destinations — one per farming site, not per patch — on the ring's own `Teleport` option, which had nothing behind it. 57 checks (`engine/tools/sim/farmtele.ts`) |
> | 14 | **The vote shop** — half of it | Built: vote tickets, the one-way redeem into bound vote points, and the Vote clerk at the Edgeville bank selling Explorer's ring 4 for 50 points. **Claiming is not built** — that still needs a vote site chosen, which is the blocker this document named. 69 checks (`engine/tools/sim/voteshop.ts`) |
>
> **Three things this document got wrong, corrected by building it:**
>
> 1. **Old School DOES have jade and topaz jewellery.** This document said "there are none in Old
>    School either, so there is nothing to import". Wrong: jade gives the ring of returning, necklace
>    of passage, flamtaer bracelet and amulet of chemistry; topaz gives Efaritay's aid, the necklace
>    of faith, the bracelet of slaughter and the burning amulet. All of it was in the OSRS cache. So
>    #2 was never "net-new art" — it was an import plus a window, and it is built. (No bracelets: the
>    377 cache has no bracelet mould and no bracelet item, so that slot does not exist here.)
> 2. **The skills necklace cannot teleport to the Farming Guild.** This document twice said it
>    would, and called it "the one that puts a Farming Guild teleport in the game". The Farming Guild
>    and the Woodcutting Guild are both in Great Kourend, which this build does not have at all. It
>    goes to the four guilds that exist — Fishing, Mining, Crafting, Cooking. Shortening a herb run
>    needed its own item, and #9 is now that item — not a new ring, but the farm menu on Explorer's
>    ring 4.
> 3. **Glories could already be recharged.** The Fountain of Heroes has done it all along
>    (`areas_heroes_guild/scripts/fountain_of_heroes.rs2`). The Fountain of Rune is not fixing a
>    broken chain; it is there because the eternal glory has to come from somewhere, and because a
>    reason to carry jewellery into deep Wilderness is the Death token's own argument.
>
> **What the 113 checks caught that reading the code did not:** the three crafting strips were
> 7-slot inventories, so the new slot 7 threw the moment the gem window opened; and
> `map_findsquare(coord, 0, 2, ...)` picks a tile at *random* from the ring, which moved a
> destination that was already fine.
>
> **One recommendation in this document was overruled, and it was right to be.** The entry for #8
> argued that a yield bonus on the amulet of nature was "a balance change rather than an item",
> because it would be a third stacking multiplier on top of magic secateurs (+10%) and the Farming
> cape (+5%). Corey asked for it anyway and it is built at **3%, worn only** — below the cape,
> because the cape costs 99 Farming and the amulet costs 27 Magic, and worn rather than carried so
> that it costs the neck slot. Both halves of the argument survive in the code: the size is one
> constant with the ordering written beside it, and the sim holds that carrying it in the pack does
> nothing.
>
> **This document's cost estimate for Pest Control was right about the shape and wrong about the
> risk.** It called it "a week of work, not an afternoon" and recommended solo first; solo took an
> afternoon, and the work was not where the estimate pointed. The scripting was ordinary. What cost
> the time was four bugs that no compile can see — a `p_finduid` in a timer that already holds
> protected access, a `~mesbox` that paused before the cleanup so the game could not end itself,
> `instance_delete` leaving its npcs behind so the next game counted eight portals, and a portal
> and a Void Knight that both wandered off their tiles for want of a `wanderrange`. Every one was
> found by running the game, not by reading it.
>
> **Two corrections from building the recolours.** This document said the job was "a stock list and
> one op line" — that is true of the *shop*, and the shop was indeed two lines, but the colours
> themselves could not be imported at all: all fourteen of Old School's house gracefuls share one
> worn model and carry no recolour fields, so there was nothing in the cache to copy and the
> palettes had to be authored against the meshes. It also said to ride the ornament-kit framework;
> nine colours met its three slots, so the pairing is a two-param lookup instead.
>
> **Also: the agility plugin (#19) is already implemented** — Corey's, not from this list. The entry
> below is stale.
>
> **#14's model, since this document did not propose one.** Corey's: *"should receive vote tickets
> that are tradeable. you should be able to redeem them from your inventory if you plan to use them
> instead of selling them."* So there are two things and they are deliberately different. A **vote
> ticket** is a stackable, tradeable item — bankable, sellable to another player, losable. A **vote
> point** is a varp: what a redeemed ticket becomes, one for one, with no slot, no trade and no way
> back. The one-way redeem is what makes it a choice rather than a formality; without it the reward
> shop would just be a gp shop with extra steps.
>
> **This document's own warning about #14 does not bite, and that was designed for.** It said *"a
> vote currency that buys anything tradeable is a vote currency that sets your economy's prices.
> Cosmetics, or nothing."* The one thing on the shelf is untradeable, `~can_sell_obj` refuses every
> item at a points shop (so no purchase can ever be reversed into points), and the ticket carries a
> new `shop_will_not_buy` param because five of this build's shops are `allstock=yes` and would
> otherwise have bought vote tickets for gp at a fixed rate — which is exactly the faucet the
> warning is about, arriving by the back door.
>
> **Two bugs the vote shop's sim found, and one of them was in a shop that shipped the day before.**
> A purchase leaves a shop slot holding the obj at count 0 rather than emptying it, and restocking
> called `inv.add`, which for a **non-stackable** item looks for a *null* slot — so it skipped that
> placeholder and restocked into some unrelated square further down the grid, or, in a shop with no
> spare slots, did nothing at all. Grace's nine graceful recolour kits were in the second case: each
> colour was buyable **exactly once per world**, forever. Their restock rate was also 0, which makes
> the engine's `tick % stockrate == 0` a NaN comparison that can never be true. Both are fixed —
> `World.processCleanup` now tops the slot up directly, which also stops every bought-out general
> store slowly shuffling its own shelves — and both are now asserted.
>
> **Corey had hit the same wall on the Undertaker's shelf, hours earlier and from the other side.**
> `377-wip` fixed it in config — a thousand a row at restock rate 1 with `stackall=yes`, on the
> grounds that *"a shop whose stock is the limit is a race; the limit here is meant to be how many
> tokens you have earned"*. That reasoning applies verbatim to a vote reward and to a mark-priced
> recolour kit, so the vote shop and Grace's shelf now carry the same idiom on top of the engine
> fix. The engine fix is still the thing that makes `stackall=no` shops restock at all; the idiom is
> what removes the one-tick race between two players buying at once.
>
> **#9 did not need a new ring.** The entry below proposed one. Explorer's ring 4 was already in
> the build with `iop3=Teleport` and nothing behind it, so the farm menu went there instead. Two
> things that only came out of building it: the **arrival tiles are measured, not chosen** — each
> is the standable tile, out of what the engine's own collision map allows, that minimises the
> longest walk to the patches at that site, and the sim re-measures all 27 on every run so a map
> import that shifts a patch fails the test instead of landing somebody in a hedge; and the
> **Entrana hops patch needed a gate**, because a teleport there would otherwise have been the one
> way onto the island in a rune platebody. It reuses the Port Sarim monk's own search.
>
> **Explorer's ring 4 has a source now.** Yesterday's entry said the ring worked but was
> unobtainable, because the achievement diary that should hand it out is not implemented. The vote
> shop is that source, and the two features were built a day apart for each other.
>
> **Still open from the original list:** #14's claiming half, plus #12, #15, #16 (whip colours) and
> #21's wave-skip, unchanged. The **PC event** half of #1 is dropped on Corey's word. The order
> below still stands for those.


**12 October 2026.** Twenty-two suggestions, checked against what is actually in
`coreysho/DeathPlateau-Content@377-wip`, `-Engine@377-wip` and `-Client@dev-logging` rather than
against memory of either this build or Old School. Nothing here is implemented; this is the
triage.

Three things turned up that change the shape of the list, so they go first:

1. **Three of these are already built.** Hunter is a finished skill. The Jad-cape gamble exists in
   full. Queen's secateurs are in the game *and already spent by a quest*.
2. **The worry attached to the Jad suggestion does not apply.** `fightcave.constant` says it in
   so many words: *"the Fight Cave is not a slayer task in this build, so there is no task to be
   on"*. There is no Jad slayer task to make insane, and nothing on this list proposes one.
3. **The 48 achievement diary items already exist and are unobtainable.** They are modelled,
   statted and sitting in `general/configs/diary_rewards.obj` with nothing in the tree referencing
   them. The ask is not "add the items" — it is "give them a source", which is a different and much
   larger job.

---

## Verdict table

| # | Suggestion | Verdict | Where it lands |
|---|---|---|---|
| 1 | PC event / PC solo | **Biggest item here** | Everything but the game exists; solo is the easier build *and* the better call |
| 2 | Jade & topaz jewellery | Net-new art | No moulds, no items, in any cache here |
| 3 | Hunter? | **Already built** | 22 scripts, full skill, stat slot in the client |
| 4 | Emerald necklace a purpose | **One line** | Binding necklace already exists and already works |
| 5 | Ruby necklace → digsite pendant | Moderate | The Dig Site is built; the item needs art |
| 6 | Diamond necklace → phoenix | Moderate | Mechanically `ring_of_life.rs2` reshaped |
| 7 | Dragonstone necklace a purpose | **Do this one** | Skills necklace; also answers #9 |
| 8 | Amulet of nature | **Do this first** | 2005 content, whole chain already in the cache |
| 9 | Farming teleport jewellery | Covered by #7, mostly | Skills necklace reaches the *guild*, not the patches |
| 10 | Wildy manta/turtle spot | Moderate, needs a decision | Changes where the skill's top fish come from |
| 11 | Eternal glory | Three new pieces for one amulet | Your 1/250 instinct is right — OSRS is 1/25,000 |
| 12 | Nail beasts → wildy slayer | **Recommend no** | 2007 import, and the wildy master was decided against |
| 13 | Best RuneLite plugins | Doable, framework exists | Pick against what `PluginContext` already exposes |
| 14 | Vote shop + claiming | **Shop built**; claiming still blocked on a decision | Engine already runs Fastify and Prisma |
| 15 | Diary items, royal seed pod | **Already there / weakest fit** | 48 items exist unobtainable; seed pod is 2016 |
| 16 | Custom whip colours | **Data-only** | Recolour fields + the ornament-kit framework |
| 17 | Queen's secateurs upgrade | **Already in game, already spent** | A Fairy Tale I deletes them for the magic pair |
| 18 | Autoweed | **~10 lines** | One proc, one stat check, one varbit |
| 19 | Agility plugin | Doable without touching client core | Every obstacle coord is already written down |
| 20 | Marks of grace → graceful recolours | **Best value on the list** | Marks drop already; Grace's shop is mothballed, not missing |
| 21 | Refight Jad for a cape | **Gamble built; shortcut is tiny** | `%fightcave_wave = 63` behind a completion flag |
| 22 | Reducing patch times | **Pure data** | A per-family minutes dict in the generator |

---

## Already built — close these out

### #3 Hunter

`scripts/skill_hunter` is 22 scripts and 30-odd config files: box traps, deadfalls, net traps, bird
snares, falconry, implings with their own loot tables, butterflies, chinchompas, salamanders,
tar, tracking, the Hunting expert, plus every area (Feldip, Canifis, desert, Karamja, Rellekka,
Piscatoris, Puro-Puro). There is a skill guide (`hunter_guide.rs2`), it is wired into the stats tab
(`interfaces/stats.rs2:89`) and `WORKFLOW.md` records the client's Hunter stat slot as the reason
the java client builds from `dev-logging` rather than `377`.

Nothing to do. If the question was "is Hunter in", the answer is yes, completely.

### #21, the gamble half

`minigames/game_fightcave/scripts/fightcave_exchange.rs2` is TzHaar-Mej-Jal taking a Fire cape and
rolling a ladder, rarest first, stopping at the first hit:

| Rung | Rate | Notes |
|---|---|---|
| Infernal cape | 1/300 | broadcast + collection log |
| TzRek-Jad → JalRek-Jad metamorphosis | 1/50 | only offered if you own TzRek-Jad and not JalRek |
| TzRek-Jad | 1/25 | only offered if you own neither |
| Tokkul | otherwise | 500–1,000, flat |

The constant file records that these were retuned on your word from 1/100, 1/50, 1/50, and that the
whole exchange is deliberately not an Old School mechanic — it exists because a player ends up with
a drawer of Fire capes and nothing to do with them. The metamorphosis works whether the pet is
following you, in your pack or in your bank, and `~pet_owned` counts one waiting at Probita's.

So the gamble is done. **What is missing is only the shortcut**, below.

### #17 Queen's secateurs

They are not absent — they are *consumed*. `fairy_queen_secateurs` is in the 377 cache with its own
model and wear models, A Fairy Tale Part I is built, and the quest uses them exactly as Old School
does: Tanglefoot drops them, you use them on the fairy skull, and `quest_fairy.rs2:238` runs
`inv_del(inv, fairy_queen_secateurs, 1)` before handing over the magic secateurs at line 169.

The Old School wiki is also explicit that they are *purely a quest item* and refuse to farm —
using them on a grown patch gives "Those look a bit too delicate to use for farming." So "an
upgrade from magic sec" is a custom buff on an item this build already defines as the ingredient
*for* the magic secateurs.

**Recommendation: don't.** If you want a tier above magic secateurs, mint a new item rather than
re-purposing the one the quest eats — otherwise the quest either has to stop consuming them (and
A Fairy Tale I loses its reward step) or has to hand back a second pair, which reads as a bug.

---

## The cheap shelf — data-only or near enough

These are worth doing as one batch because they touch four files between them.

### #8 Amulet of nature — the standout

**This is 2005 content and the entire chain is already in the cache.** It is the only item on the
list that is both in period and nearly free.

| Piece | State |
|---|---|
| `magic_string` | **Already craftable** — spin magic roots at 19 Crafting (`skill_crafting/scripts/spinning/spinning.rs2:59`) |
| `magic_strung_emerald_amulet` ("Emerald amulet", *"strung with the root of a Magic Tree"*) | In the 377 cache, line 76345, with model and recolours |
| `nature_amulet` ("Amulet of nature") | In the 377 cache, line 76323, `iop1=Rub`, `iop2=Wear`, model and wear models |
| Lvl-2 Enchant | Built; `magic_spells.dbrow:13` is one dbrow with `convertobj` lines |
| The farming state machine it would read | Built; `farming_state.rs2` / `farming_core.rs2` |

So the work is: one crafting line (string the amulet with magic string), **one `data=convertobj`
line** on `magic_spell_enchant_level2`, one obj config, one varp for the bound patch, and a Rub
handler that reads the patch state the farming tick already maintains.

**On the 2-5% yield or xp ask.** In Old School the amulet of nature gives no yield or xp bonus at
all — it binds to one patch and tells you when the crop is diseased, dead or grown. Two separate
points:

* The notification job is worth more here than the bonus. **Nothing in this build reports patch
  state remotely.** A player's only way to know a herb patch finished is to walk to it. That is the
  one genuinely tedious thing left in a skill that is otherwise complete.
* A yield bonus is cheap if you want it — `farming_actions.rs2:162` is where magic secateurs apply
  11/10 to chance-to-save and the skillcape applies 21/20 right after. A third multiplier slots in
  at line 164. But it would be the **third** stacking yield bonus, and the two that exist are both
  already above Old School's numbers.

**Recommendation: build the Old School job, treat the bonus as a separate decision.** If you want
the bonus anyway, 2% (261/256 on the CTS scale) stacks politely; 5% starts to matter.

### #4 Emerald necklace — one line

The Binding necklace is **already in the game and already works.** `magic_emerald_necklace` is in
the cache (line 69466, named "Binding necklace"), it drops from the three abyssal creatures
(`drop_tables/configs/npc_drops.dbrow:25`), and `skill_runecraft/scripts/runecraft_combo_runes.rs2:32`
checks for it in the front slot when you make combination runes.

The only thing missing is the enchant route. One line on `magic_spell_enchant_level2`:

```
data=convertobj,emerald_necklace,magic_emerald_necklace,human_enchantamuletlvl2,enchant_amulet_lvl2,enchant_emerald_amulet
```

plus widening that row's `additional_reqmessage` from "emerald rings and amulets" to include
necklaces, the way the sapphire row already reads. **Do this regardless of what else you decide.**

### #22 Reducing farming patch times — pure data

`tools/farming/crops.py` holds a per-family minutes-per-stage dict:

```python
CYCLE = {ALLOT:10, HOPS:10, FLOWER:5, HERB:20, BUSH:20, TREE:40, FRUIT:160,
         CACTUS:80, CALQUAT:160, MUSH:40, BELLA:80, SPIRIT:320}
```

Change the numbers, run `gen.py`, and the constants and params regenerate. There is also already a
global knob — `^farming_speed_divisor` in `farming.constant`, documented as a test switch where 10
turns a 40-minute allotment into 4 minutes.

**Recommendation: cut the long tail, not the short end.** Allotments at 40 minutes a crop and herbs
at 80 are fine. Fruit trees and calquat at 160 minutes a stage (about 16 hours a tree) and spirit
trees at 320 are what make a player stop planting them. Halving `FRUIT`, `CALQUAT`, `CACTUS`,
`BELLA` and `SPIRIT` and leaving the rest alone changes the skill's feel without touching the part
people actually farm.

### #18 Autoweed — about ten lines

`farming_regrow_weeds` in `farming_core.rs2:266` is the whole mechanism: state 3 is bare soil, 2/1/0
are one, two and three weeds, and it counts down every `^farming_weed_regrow_minutes` (100). Make it
return early when the unlock bit is set, and raking is never needed again.

Your instinct to gate it is right, and 65 or 70 Farming is a reasonable number. Worth knowing:
**auto-weed is an RS3 feature, not an Old School one** — there is no OSRS price or level to copy, so
whatever you pick is the number. One varbit, one `stat(farming)` check.

### #16 Custom whip colours — data-only, and it rides a framework that already exists

Two facts make this much cheaper than it sounds:

* **A recolour is pure config, not art.** `recol1s`/`recol1d` pairs are used throughout the tree —
  burnt bones, lava dragon bones, half the cooking items. No model import, no cache needed, and
  `tools/ob2render.py` warns when a recolour source matches no face on the mesh, so a wrong source
  is caught rather than shipped.
* **`obj_abyssal_whip.ob2` and `obj_abyssal_whip_manwear.ob2` are both in the content repo**
  (`models/obj/`), so the source colours can be read and the variants rendered without the 474 or
  OSRS caches.

And the delivery mechanism is built: `minigames/game_trail/scripts/ornament_kit.rs2` is sixteen
reversible kits driven entirely by `param=ornament_kit` / `ornament_into` / `ornament_from` on the
items, and its own header says *"Adding a seventeenth kit is a config change and nothing here has to
know."* Every kit result copies the base item's stats, so a whip recolour **cannot** sell power even
if wired carelessly — which is the Undertaker shop's rule satisfied by construction.

### #20 Marks of grace → graceful recolours — the best value on the list

Everything needed is already standing:

* **All nine rooftop courses are built** — Draynor, Al Kharid, Varrock, Canifis, Falador, Seers',
  Pollnivneach, Rellekka, Ardougne, each with its own script and constants.
* **Marks of grace already drop on them.** `agility_marks.obj` defines `mark_of_grace`, untradeable,
  stackable, examine text *"You can exchange these for rewards at the Rogues' Den."*
* **Grace exists**, in the Rogues' Den where Old School puts her, and already counts your marks.
* **Her shop is mothballed, not missing.** `grace.rs2`'s own header: *"Her shop held the Graceful
  outfit for Marks of Grace; the owner is implementing Graceful another way, so the stock is gone,
  her Trade option with it... The shop plumbing is still in `grace.npc` and `grace.inv` — restoring
  it is a stock list and one op line, not a rewrite."*
* **All six graceful pieces exist** (`skilling_outfits/configs/outfits.obj`, enum vals 42-47), with
  their own weight-reduction and run-energy params.

Her dialogue even promises it today: *"Hold on to them. I will have something worth your while
before long."* Right now marks are a currency with no sink, which is the one state worse than not
having them.

**Recommendation: kits, not a second set of items.** A recolour kit per colour rides the
ornament-kit framework (reversible, stat-copying, one config change each) and avoids minting six new
items per colour. Six colours × six pieces as separate items is 36 objs; six kits is six.

### #21 The refight shortcut — small

`fightcave_enter` (`fightcave.rs2:17`) sets `%fightcave_wave = 1` and spawns wave 1. A "fight Jad
only" route is `%fightcave_wave = ^fightcave_jad_wave` and `~fightcave_spawn_wave(63)`.

One real wrinkle: **there is no persistent record that you have completed the cave.** All four
fightcave varps are `temp` and the file says so deliberately — *"an instance does not survive a
restart, so neither may anything pointing into one."* So this needs one new non-temp varbit set on
the first Jad kill (or a `~collection_log_has(tzhaar_cape_fire)` check, since `fightcave_reward`
already logs the cape).

**And the objection you raised is already answered by the build.** `fightcave.constant`:
> 1 in 200, which is the rate the wiki gives for a plain kill. It also gives 1 in 100 on a Slayer
> task, and that is NOT implemented here: **the Fight Cave is not a slayer task in this build**, so
> there is no task to be on and a second rate would be a number nothing can reach.

No slayer master assigns TzTok-Jad here, and `slayer_master_tasks.dbrow` has no Jad row. The
insane-xp-per-hour problem cannot occur unless someone deliberately adds the task — so the only
thing to decide is whether to keep it that way. **Recommendation: keep it that way**, and let the
shortcut be about the cape and the pets, which is what you actually asked for.

---

## The necklace family, taken together

Old School's answers, confirmed against the wiki rather than remembered:

| Gem | Necklace | What it does | State here |
|---|---|---|---|
| Sapphire | Games necklace | 8 teleports | **Built** (`magic_spells.dbrow:10`, `necklace_of_minigames.rs2`) |
| Emerald | Binding necklace | 100% combination runes, 16 uses | Item built, **enchant route missing** |
| Ruby | Digsite pendant | Dig Site / Fossil Island / Lithkren, 5 uses | Nothing |
| Diamond | Phoenix necklace | Heals 30% of max when HP drops below 20%, 1 use | Nothing |
| Dragonstone | Skills necklace | Fishing / Farming / Mining / Crafting / Cooks' / Woodcutting guilds, 4 teleports | Nothing |
| Onyx | Berserker necklace | +7 str, +3 prayer, obsidian damage | **Built** (`magic_spells.dbrow:78`) |

So the gap is exactly the three you named — ruby, diamond, dragonstone — and each is a `convertobj`
line plus an item.

**#7 dragonstone → skills necklace, and why it mostly answers #9.** You asked separately for
"a farming ring that tele's to all patches, can [be] purposed with some jewellery?" The Old School
answer to that is the skills necklace, and it is the dragonstone enchant — so the two suggestions
are one item. Two caveats:

* It reaches the **Farming Guild**, not the patches. A ring that hits the patches themselves
  (Falador, Catherby, Ardougne, Canifis, Trollheim, the Gnome Stronghold) is a *different*,
  **custom** item, and it is the one that actually shortens a herb run.
* The teleport-menu plumbing is already built twice over — `necklace_of_minigames.rs2` is a
  destination menu on a charged necklace, and `amulet_of_glory.rs2` is a charged four-way teleport
  with its own interface. Either is the pattern; neither needs writing again.

**Recommendation: build both, in this order.** The skills necklace gives the dragonstone necklace
its Old School purpose (cheap, in-pattern, and a Farming Guild teleport is useful on its own). Then,
if herb runs are the real target, a patch-run teleport item is the thing that fixes them — and it
should probably be a **ring**, as you said, so it doesn't fight the glory for the neck slot.

**#5 ruby → digsite pendant.** The Dig Site itself is built (`quests/quest_itexam`, with the
archaeological expert and the exam), so the pendant has somewhere to go. Fossil Island and Lithkren
do not exist here, so it would be a one-destination pendant, which is thin. Your "or some other use"
is the better instinct — a ruby necklace that does something this build actually has.

**#6 diamond → phoenix necklace.** Mechanically this is `ring_of_life.rs2` reshaped: the same
"HP crosses a threshold" hook, healing instead of teleporting, consumed on use. That script exists.
The item needs art.

---

## Moderate, clearly doable

### #19 Agility plugin, and #13 RuneLite plugins generally

**The client has a RuneLite-shaped plugin framework already.** `jagex2/client/plugin/` holds
`Plugin` with `startUp`/`shutDown`, `@Subscribe` handlers, `@ConfigItem` settings, overlays, an
event bus, a plugin loader, a plugin hub and a sidebar. Fifteen builtins ship with it — ground
items, tile indicators, NPC indicators, mouse highlight, menu swapper, XP drops, boosts, idle
notifier, anti-drag, Barrows doors. The README says the shape is deliberate: *"what you know from
writing one there carries over. It is not RuneLite and is not compatible with it... Porting a plugin
means keeping its logic and replacing its ids and widget lookups."*

So "the best plugins RuneLite has to offer" is a real project with a real runway. The constraint
worth knowing before picking a list: **`PluginContext` exposes no scene-object access.** There is
`getNpcs()`, `getPlayers()`, `getGroundItemPiles()`, the menu, the hover tile, projection and
overlays — but no `getLocs()`. Any plugin whose job is "highlight that door / tree / obstacle"
needs either a client-core addition or a different route.

**For agility specifically there is a different route, and it is better.** Every obstacle coordinate
in the game is already written down in the content repo — `skill_agility/configs/*_course.constant`
holds the landing coord and start coord of every obstacle on all nine courses, measured off the
grafted roofs and verified by a simulator that walks each lap. `shortcuts.rs2` has 23 handlers.
So an agility plugin can carry a generated coordinate table and draw with the existing
`projectTile`/`isInScene`/overlay API, with no engine or client-core change at all — and the table
can be generated from the constants rather than typed, so it cannot drift from the courses.

**STRUCK, 14 October 2026.** The agility plugin was already implemented - Corey's own - so this
recommendation was stale when written and stayed stale through two later repeats of it. The
`getLocs()` observation below is left in place because it is still true of `PluginContext` and is
the thing to read first if the broader plugin list is ever picked up; it is not an open item.

**Recommendation:** build the agility plugin against the coordinate table. Separately, if you want
the broader plugin list, adding `getLocs()` to `PluginContext` unlocks a whole class of them at once
and is the single highest-leverage client change on this list.

### #14 Vote shop and integrated claiming

More feasible than it looks, because the infrastructure is there:

* **The engine already runs a web server** — `src/web.ts` is Fastify with views, static files and
  websockets, and there is a separate `ManagementWeb.ts` with its own routes. A vote-site callback
  endpoint is a route on something already listening.
* **There is a database** — `prisma/singleworld/schema.prisma` and a multiworld twin, with `account`,
  `hiscore`, `session` and friends. A `vote_claim` model fits straight in.
* **Shops are a solved pattern** — `scripts/shop/scripts/shop.rs2` plus a `.inv`, and `~openshop`
  takes a price multiplier as an argument.

The blocker is not code, it is two decisions:

1. **Which vote site(s)**, because the callback contract is theirs, not yours. Each has its own
   token scheme and its own idempotency story, and the endpoint has to be written against a real
   one.
2. **What the shop sells.** The Undertaker's laundry rule applies here with more force, not less:
   *"an untradeable currency buying tradeable goods makes the shop's price the trading-post price
   and the token stops meaning anything."* A vote currency that buys anything tradeable is a vote
   currency that sets your economy's prices. Cosmetics, or nothing.

### #10 Wilderness manta ray and sea turtle

Today both are **Trawler-only** and the build says so out loud: `fishing_guide.rs2:3` — *"Sea turtle
and manta ray come from the Fishing Trawler, not from a spot"* — and the Fishing level-up messages
at 79 and 81 tell the player exactly that. The Trawler is built (1,128 lines).

Mechanically a wilderness spot is in-pattern: `skill_fishing/scripts/fishing_spots/` already holds
eight spot scripts (fresh, salt, rare, member, lava, waterfall, barbarian), so a ninth is a spot npc,
a script and the coords. The xp and yield increase is the easy part — it is numbers in the spot's
own struct.

What needs deciding first is **what it does to the skill's shape**. Right now 79+ Fishing means the
Trawler, and the Trawler is a minigame with its own rhythm. A wilderness spot with better rates
doesn't add an option so much as replace one — nobody trawls if the risky spot pays more. That may be
exactly what you want (a reason to fish in the Wilderness is a reason to be in the Wilderness, which
is the Death token's whole argument), but it is a real trade and not a free addition.

**Recommendation: build it, and tune it as a sidegrade rather than an upgrade** — higher xp per catch
and better yield, but no noting and nothing to stop a PKer, so the Trawler stays the safe way to the
same fish. That is the same opt-in-to-risk structure `wilderness-slayer-options.md` argues for and
the Undertaker already runs on.

---

## Expensive, tangled, or recommend no

### #1 Pest Control — the biggest item on the list

Everything except the game exists, and the absence is documented rather than accidental.
`game_pest/configs/pest.constant`:

> **NOT BUILT: the Pest Control minigame itself.** `pest_squire_lander` stands beside a fully
> modelled lander boat on the outpost (`pest_lander_boat_*` locs on both island squares, plus a
> hatch and a ladder), and m41_40 south of it is the pest island proper with its watchtowers. None
> of that has a script.

What *is* there: the outpost island (previously one of three fully isolated map squares, now
reachable by ship from Port Sarim), 18 npcs, three wired shops, a bank, four Void Knights, the
seven pieces of void knight equipment (`void_knight.obj`), the lander, the pest island with its
watchtowers, and every monster — shifters, ravagers, spinners, torchers, defilers, brawlers and
splatters in all five tiers, plus the portals, as 49 npc records in the 377 cache. The commendation-point exchange is an `op3=Exchange`
on all four Void Knights that answers in world because there are no points to spend.

Two close precedents exist, so this is a known shape rather than an unknown one: **Castle Wars**
(1,935 lines — a team minigame with a lobby, a timer and objectives) and the **Fishing Trawler**
(1,128 lines — a timed multiplayer boat with a failure state). It is still a week of work, not an
afternoon.

**On solo versus event.** These pull in opposite directions and the cheaper one is also the better
one:

* **Solo is the easier build and the right call for this server.** Old School requires five players
  to start a game, which on a small population means the lander never fills and the content is
  decorative. A solo variant has no lobby, no player-count gate, no team to balance — one player,
  one instance (the Fight Cave already shows how a 64×64 square gets instanced zone by zone), and
  the knight's HP and portal count scaled for one. It is less work than the real thing *and* it is
  the version that actually gets played.
* **"PC event" is the expensive one**, because there is **no world-event scheduler in this build.**
  Nothing in the tree fires content on a clock; `broadcast.rs2` announces things that already
  happened. A recurring timed event is a new piece of engine-adjacent machinery, and it would be the
  first of its kind here.

**Recommendation: solo first, and treat "event" as a separate project** — one that is worth having
for its own sake (it would serve every future event, not just this one) but should not be the
reason Pest Control slips.

### #11 Eternal glory

Your parenthetical is right, and by more than you probably meant: **Old School's rate is 1 in
25,000** recharges at the Fountain of Rune. 1/250 is a hundred times kinder and still rare enough
to be a story.

The cost is that it is three new pieces for one amulet:

1. **The Fountain of Rune does not exist here** — nothing in the tree mentions it, and the glory
   recharge path (`general/scripts/enchanted_jewellry/amulet_of_glory.rs2`, four charge states plus
   a dead one) has no recharge location at all. So this needs a fountain somewhere in the
   Wilderness, which is a loc, a script and a map question.
2. **The item needs importing** — `amulet_of_eternal_glory` is not in the 377 cache.
3. **The rate and the gate** — straightforward once 1 and 2 exist.

**I could not work out what "and rc" meant** — see the open questions below. If the thought was
that the Fountain of Rune sits near the Wilderness runecrafting altars and the trip should pay
twice, that is a coherent design and changes where the fountain goes, so it is worth saying before
anything is built.

**Recommendation: park it until the fountain is wanted for its own sake.** A glory recharge point in
the Wilderness is a decent thing to have regardless; the eternal glory is then a 1/250 on top of it,
and nearly free.

### #12 Nail beasts in Wilderness Slayer — recommend no

Three separate problems, and the third is the one that settles it:

1. **Not in any cache here.** No `nail_beast` npc in the 377 dump — only snails and fingernails.
   They are 13 March 2007 content (Burgh de Rott Ramble), so they would need an OSRS import.
2. **They are not a Slayer monster in Old School either.** No slayer level, no category, no master
   assigns them. They live in Temple Trekking, which this build has only in fragments — the trekking
   zombie, shades and ghasts exist as npcs with drop tables; the minigame does not.
3. **There is no Wilderness Slayer master, by decision.** `Useful Stuff/wilderness-slayer-options.md`,
   12 October, in your words: *"i dont think we need a wildy slayer master."* Krystilia is not being
   built.

So "add to wildy slayer" has nothing to add them to. The only coherent route is the one that document
already recommends for ankou and lava dragons — **give them to Duradel as an unlock-only row**,
behind a purchase, the way red dragons sit behind Seeing Red. That keeps the opt-in-to-risk shape.
But it means an import, a spawn, a drop table and a task row for a monster whose only claim is that
it is unusual, while **ankou and lava dragons are already built and still dormant**, waiting for
exactly that treatment.

**Recommendation: wire up ankou and lava dragons first.** They are built, they carry
`param=slayer_category` already, and they are the Wilderness monsters this build actually has. If
unlock-only wilderness tasks turn out to be fun, nail beasts are a candidate afterwards.

### #15 Achievement diary items and the royal seed pod

**The items are already there, and that is the finding.** `general/configs/diary_rewards.obj` holds
**all 48** — four tiers each of the Ardougne cloak, desert amulet, Falador shield, Fremennik sea
boots, Kandarin headgear, Karamja gloves, explorer's ring, Morytania legs, Varrock armour, western
banner and wilderness sword, plus the four Rada's blessings (which are Kourend favour rewards in
Old School, not a diary tier, but ship in the same file). Imported from OSRS, modelled, with their cache stats
and their right-click options (`iop3=Monastery Teleport` on the Ardougne cloak, and so on).

**Nothing in the tree references any of them.** No shop, no drop table, no quest, no script. They are
48 complete items with no source and no effects — the file says so: *"The items only: their effects
— teleports, daily recharges, gathering bonuses — are a later round, one set at a time."*

So the ask is really two much larger asks:

* **A source.** Properly that means an achievement diary system: twelve regions × four tiers, each
  tier a list of tasks to check, plus an interface to show them. That is a big, self-contained
  project — bigger than Pest Control.
* **The effects.** Twelve sets of unrelated perks, each hooking a different skill.

**Recommendation: don't do the diary. Do the effects, one set at a time, and hand the items out some
other way.** The file's own plan is right. The Karamja gloves and explorer's ring are the two whose
effects are worth the most for the least work, and either could hang off something that already
exists rather than waiting for a diary that may never be built.

**The royal seed pod is the weakest fit on the entire list.** Released 6 May 2016, rewarded by King
Narnode for completing **Monkey Madness II** — which does not exist here (`quest_mm` is Monkey
Madness I; `quest_grandtree` has Narnode). No seed pod of any kind, grand or royal, is in the 377
cache. The item itself is trivial — an unlimited-charge Grand Tree teleport that works to
Wilderness 30 — but it would be a 2016 item imported for a quest that isn't built, and this build
already has glory, games necklace and a full teleport spellbook.

### #2 Jade and topaz jewellery

Jade and red topaz exist here only as **gems and bolt tips**: `uncut_jade`, `jade`, `uncut_red_topaz`,
`red_topaz` in the cache, and `jade_bolttips` / `topaz_bolttips` with their stack variants in
`skill_fletching/configs/crossbows/crossbow_parts.obj`. There are **no jade or topaz jewellery items
and no moulds** in any cache this build draws on — and there are none in Old School either, so there
is nothing to import. This is genuinely net-new.

The cost is art, not logic. A full family is 2 gems × (ring, necklace, amulet, bracelet) × (plain +
enchanted) = up to 16 items plus moulds, all needing models. The jewellery pipeline itself is cheap
once art exists — a `convertobj` line per enchant and a crafting row per mould.

**Recommendation: if you want this, do one item each, not a family.** Pick the two effects first and
build only those. And note the cheaper near-neighbour: the *enchanted necklaces* above are three
items that already have Old School answers, and they scratch the same itch — "gems that currently
do nothing useful" — for a fraction of the work.

---

## One practical constraint, worth recording

**CORRECTED, same day: a cloud session can do OSRS and 474 imports after all.** The first version
of this section said it could not, on the grounds that `caches/` is gitignored and this container
started without it. That was true and beside the point — the caches are one download away:

* **archive.openrs2.org is already reachable** from the cloud environment. No allowlist change was
  needed.
* The four commands in `WORKFLOW.md` are the whole job. 31 MB and 182 MB down, well under a minute
  each; `disk2flat.py` then converts the OSRS disk store in about a minute.
* **Verified by doing it**: `importosrs.py caches/osrs --item "Skills necklace" --dry-run` returned
  obj 11113 with 3 models round-trip verified and its wearpos out of the cache.

So nothing on this list is gated on being at the Windows box. The one real caveat is
**persistence**: the container is reclaimed eventually and `caches/` is gitignored, so the download
repeats once per session unless the commands go in the environment's Setup script.

`WORKFLOW.md` now records the measured sizes and this result.

---

## Suggested order

> **CLOSED, 14 October 2026, except #14.** Everything below has shipped. Corey: *"vote claiming is
> the only remaining thing and i will mention it when im ready to do it"* - so #14 waits on him
> naming the vote site, because the callback contract is the site's and cannot be written against a
> guess. The agility plugin and `getLocs()` are struck from the list: the plugin is Corey's own and
> was already built, which the corrections block near the top of this document has said all along -
> it was recommended twice afterwards anyway, from reading the verdict table and not that block.
> The order below is kept as the record of what was done in what sequence.

**First, one batch — a day's work between them, all data or near it:**

1. Emerald necklace → binding necklace (one line)
2. Amulet of nature (the Old School job: bind, rub, notify)
3. Graceful recolours through Grace's shop, as kits
4. Autoweed, gated at 65 Farming
5. Farming cycle times — halve the long tail only
6. The Jad refight shortcut, behind a completion varbit
7. Whip colour kits

**Then, the things worth a proper sitting:**

8. Skills necklace, and then a patch-run ring if herb runs are the real target
9. ~~The agility plugin, off a generated obstacle table~~ - already implemented, Corey's own
10. ~~`getLocs()` on `PluginContext`~~ - struck with it; it was only ever a way to reach #19
11. Ankou and lava dragons as Duradel unlock-only rows — built content currently dormant
12. Vote shop, once the site is chosen
13. Wilderness manta/turtle spot, tuned as a sidegrade

**Then the big one:**

14. Pest Control, solo variant

**Recommend not doing, and why, in one line each:**

* Queen's secateurs as an upgrade — already in the game and already eaten by A Fairy Tale I
* Nail beasts — an import for a task type that was decided against, while ankou sit dormant
* The achievement diary system — bigger than Pest Control; do the item effects instead
* Royal seed pod — 2016 item, quest not built, and the build is not short of teleports
* A Jad slayer task — nobody asked for one, and its absence is what makes #21 safe

---

## Open questions I could not answer from the tree

1. **#11, "for useage and rc".** What is the runecrafting connection? If the thought is that the
   Fountain of Rune should sit near the Wilderness altars so one trip pays twice, that changes where
   it goes and is worth settling before it is placed.
2. **#10.** Is the intent a risk-reward *alternative* to the Trawler, or should manta and sea turtle
   move off the Trawler entirely? The first is a sidegrade; the second retires a built minigame.
3. **#14.** Which vote site? The callback contract is theirs, so the endpoint cannot be written
   against a guess.
4. **#2.** What should jade and topaz jewellery *do*? The art is the cost, so the effects decide
   whether it is two items or sixteen.
5. **#8.** Do you want the 2-5% yield bonus on top of the Old School notification job, knowing it
   would be the third stacking yield multiplier and the two existing ones are already above Old
   School's numbers?

---

# Round two — the 26 October list, measured the same way

Nineteen more, numbered on from the first list. Everything below was checked against the tree today
rather than remembered: what already exists, what the source npc is, and what is actually missing.

## Verdict table

| # | Suggestion | Verdict | The one thing that decides it |
|---|---|---|---|
| 23 | Hunter store icon, Yanille | **Two lines of map** | Aleck's Hunter Emporium is built; it just has no minimap icon |
| 24 | Agility Pyramid | **Best value on this list** | Every obstacle is modelled and placed. Nothing is scripted |
| 25 | Pyramid Plunder + pharaoh sceptre | Whole minigame | Nothing of it exists: no rooms, no guard mummies, no sceptre |
| 26 | Clue caskets, rebuilt the Old School way | **Approved: one casket per tier** | OSRS has six reward caskets; this build has 103 |
| 27 | Zaros mage arena cape + ornament kit | **Approved: import 29448** | The model is OSRS's own "Imbued mage arena cape" |
| 28 | Slayer gem: Check for kill count | **~5 lines** | `%slayer_count` already exists and the gem already reads it aloud |
| 29 | Bone weapons from the cave goblins | Import + drops | Two of them already exist (`cave_goblin_bone_club`, `_spear`) |
| 30 | Hill giant club | Import + one drop line | The npc is `giant`; the item is absent |
| 31 | Belle's folly from metal dragons / KBD | Import + drop lines | OSRS id 31248, and a tarnished version at 31245 |
| 32 | Arkan blade from lava dragons | **Item already built** | `arkan_blade` exists here with its own spec; it needs a drop |
| 33 | Rum Deal + barrelchest anchor | **Approved: build the quest** | Anchor is OSRS 10887; the quest is the real work |
| 34 | Abyssal bludgeon, three pieces, no dupes | Import + a small state machine | The demon is `slayer_abyssal`; the no-duplicate rule needs varbits |
| 35 | Dragon warhammer from KQ or KBD | Import + one drop line | Both are built — the KBD is the npc `king_dragon` |
| 36 | Staff of the dead from K'ril | Import + one drop line | K'ril is built |
| 37 | Saradomin's light from Zilyana | Import + one drop line | Zilyana is built |
| 38 | Staff of light, combining the two | One script, after 36 and 37 | Nothing to import; it is a combine |
| 39 | Granite hammer from gargoyles | Import + one drop line | `slayer_gargoyle` is built, with a superior |
| 40 | Granite longsword from gargoyles | Import + one drop line | Same table as 39 — do them together |
| 41 | Dragon sword from every dragon | Import + a scaled table | 30 dragon npcs; "better rate on bigger dragons" is the design |

## The cheap shelf

**#28, the slayer gem's Check.** The gem carries one op today, `iop1=Activate`, and that path already
reads `%slayer_count` out loud through the master's dialogue. A Check op is the same number without
the phone call: one `iop`, one `[opheld]`, one message. The smallest thing on the list.

**#23, the Hunter shop icon.** Aleck is built, in `skill_hunter/configs/hunter_emporium.npc`, and so
are Leon's shop and the one in Nardah. What Yanille has not got is the minimap icon. Only two places
in the whole tree set `mapfunction` outside the cache's own locs — the trading post and Pest Control
— and the trading post's config records the rule that cost somebody an afternoon: **the client only
reads `mapfunction` off ground decoration (shape 22)**, which is why Jagex marked shops with an
invisible `general_store_icon` loc rather than on the building. So: one invisible loc on Aleck's
tile, one `mapfunction` line, and a hunter icon added to `sprites/mapfunction.png` if none of the
existing ones fit.

**#26, stackable caskets.** 103 objs have "casket" in the name and every one is `stackable=no`. The
flag itself is data. The design call underneath it is not: caskets here are per-clue objs, so making
them stackable stacks *identical* caskets, not "all your easy caskets". If the intent is a pile of
loot to open at the bank, that is one obj per tier and a rewrite of how caskets are handed out.

## The one with everything built except the script

**#24, the Agility Pyramid.** This is the standout. All 114 `agility_pyramid_*` locs exist, they are
**placed on the map** (m52_44 and m47_73), Simon Templeton is built, and so are the two waterfall
npcs. Nothing in `skill_agility/scripts/` mentions any of it — the only script that references the
pyramid at all is `stairs.rs2`. The whole thing is standing there as scenery: climbing rocks,
ledges, gaps, doors, the lot, with no course behind them. That is the same shape as the rooftop
courses this build already has nine of, and those have the hard parts — landings, obstacle spans,
the client-side camera check — already solved and written down.

## The drop-table family, #29 to #41

Eleven of the nineteen are one job repeated: import an item from the OSRS cache, hang it on a drop
table that already exists. The tree is in good shape for it — `slayer_abyssal`, `slayer_gargoyle`,
`kril`, `zilyana`, `kalphite_queen`, `lava_dragon`, `giant`, the three metal dragons and 30 dragon
npcs in all are built, and `tools/models/importosrs.py` takes an item by name.

Two are blocked on something only you can answer:

* **#31 and #32.** I cannot identify "Belle's folly" or the "Arkan blade" — neither is a 2006 item
  and neither resolves in the OSRS cache under those names. Say what they look like or where they
  come from and they become the same one-line job as the rest.
* **#35, and half of #31.** There is **no King Black Dragon in this build.** `black_dragon` is the
  ordinary one; there is no KBD npc, no lair, no table. A KBD drop is really "build the KBD first",
  so the dragon warhammer should come off the Kalphite Queen, who is built.

And one needs a home rather than a model:

* **#33, the barrelchest anchor.** The item is absent and so is Rum Deal — there is no pirate or rum
  quest in `scripts/quests/`. "Given by quest completion" needs a quest that exists; name one and it
  is a reward line.

**#34 deserves its own note.** The no-duplicate-pieces rule is the interesting part, not the item: the
drop roll has to read what you already own and pick from the pieces you are missing, which is a
varbit per piece and a check in the demon's table. Worth doing properly, because that pattern is
what any other "collect three" item would want afterwards.

**#38 is free once #36 and #37 are in** — the staff of light is a combine, not an import.

**#41 is the only one with a design in it.** "All dragons, better rate on bigger ones" means a
per-npc rate rather than one line: bronze through to the lava dragon, each with its own number. That
is one table and a param on each dragon.

## Corrections to this round, 26 October

Three of the entries above were wrong when written, and two of them were wrong because I searched
for the wrong string rather than because the thing was missing. Recorded here because the same
mistake is easy to repeat:

1. **The Arkan blade is already in this build.** `scripts/general/configs/osrs_items_2.obj` holds
   `[arkan_blade]`, and it has a special attack (`skill_combat/.../specs/scripts/arkan_blade.rs2`),
   burn-stack varps and a level-60 requirement. My scan searched for a list of words I had chosen in
   advance and "arkan" was not one of them. Only the drop is missing.
2. **The King Black Dragon is in this build.** The npc is `king_dragon` - the 2006 name - with a
   full drop table in `drop_tables/scripts/king_black_dragon.rs2` and a boss pet. I searched for
   `king_black_dragon` and `kbd` among npc names and concluded it was absent; the file was named
   that all along and the npc was not.
3. **Belle's folly is a real Old School item**, id 31248, with a tarnished version at 31245. The
   name did not resolve because `importosrs.py` matches whole names, not substrings - a substring
   search over the cache finds it at once.

**Answered, and now scheduled:**

* **#33** - Rum Deal comes in with the anchor. The quest is the work; the anchor is OSRS 10887.
* **#26** - caskets follow Old School: one reward casket per tier (beginner, easy, medium, hard,
  elite, master - OSRS 23245, 20546, 20545, 20544, 20543, 19836), replacing the 103 per-clue objs.
* **#27** - the cape is Old School's **Imbued mage arena cape**, id 29448, imported as the model.

## What I would do first

1. **#28** — five lines, today.
2. **#23** — one loc and an icon.
3. **#39 + #40** — one gargoyle table, two items, and it proves the import-and-drop loop for the
   other nine.
4. **#36, #37, #38** — the God Wars staves together, since the third is free.
5. **#24, the Agility Pyramid** — the biggest return on the list, and the course machinery exists.
6. **#34** — the bludgeon, properly, with the no-duplicate rule.
7. **#25** — Pyramid Plunder, a minigame-sized job that should be costed on its own.

## Open questions on this round

1. **#31, #32** — what are "Belle's folly" and the "Arkan blade"? Neither name resolves here.
2. **#33** — which quest should hand over the barrelchest anchor, given Rum Deal is not built?
3. **#26** — stack identical caskets, or one casket obj per tier? The second is the bigger change.
4. **#27** — a Zaros cape needs art that does not exist in 2006. Recolour of an existing god cape,
   or a new model?
5. **#35** — confirm the Kalphite Queen as the dragon warhammer's source, since there is no KBD.
