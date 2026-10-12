# The suggestion list, measured against the tree

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
| 14 | Vote shop + claiming | Doable; blocked on a decision | Engine already runs Fastify and Prisma |
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

**A cloud session cannot do OSRS or 474 imports.** `WORKFLOW.md` records that `caches/` is
gitignored — tens of megabytes, present only on the machine that downloaded them — and this
container has no `caches/` directory at all. So anything routed through `importosrs.py`,
`import474.py` or `animconvosrs.py` has to be done on your machine, or the caches have to be pulled
from OpenRS2 first (`archive.openrs2.org` on the network allowlist, with the exact commands in
`WORKFLOW.md`).

That splits this list cleanly:

| Needs the cache | Does not |
|---|---|
| Skills necklace, phoenix necklace, digsite pendant art | Emerald → binding necklace (one line) |
| Eternal glory | Amulet of nature (both items already in the 377 cache) |
| Nail beast | Whip colours (`obj_abyssal_whip.ob2` is in the repo) |
| Royal seed pod | Graceful recolours (all six pieces exist) |
| Jade/topaz jewellery | Autoweed, patch times, Jad shortcut, agility plugin, vote shop |

Everything in the right-hand column can be built from here.

---

## Suggested order

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
9. The agility plugin, off a generated obstacle table
10. `getLocs()` on `PluginContext`, which unlocks the rest of the plugin list
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
