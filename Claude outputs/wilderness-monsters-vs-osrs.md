# What OSRS has in the Wilderness that this build does not

Measured 9 October 2026. The local side is a census of every npc spawn inside the build's own
Wilderness rectangles (`wilderness_zones.dbrow`: x 2944-3391 z 3520-3967 on the surface, plus the
Edgeville dungeon section at z 9920-12799) read straight out of the `.jm2` map files — **81 distinct
npcs, 703 spawns**. The OSRS side is Krystilia's assignment table plus the wiki's own Wilderness
page, with every release date checked against the wiki infobox rather than remembered.

---

## 1. Missing entirely — no npc config, no pack id, nothing to place

These would be **import jobs** (`importosrsnpc.py`), not map edits.

> **Two of these were built on 9 October 2026 and are struck from the list: the Ankou (imported
> from the rev 474 cache, 21 of them in the Forgotten Cemetery) and the Lava dragon (built from
> this build's own dragon mesh, 8 on the isle). What follows is the list as it stands after that.**

| Monster | OSRS released | Note |
|---|---|---|
| Ent (level 101) | 13 Mar 2014 | the Woodcutting Guild ent is a different, 2016 monster |
| ~~Ankou~~ | — | **built 9 Oct 2026**, from the 474 cache |
| ~~Lava dragon~~ | 13 Mar 2014 | **built 9 Oct 2026**, from this build's own dragon |
| Runite golem | 13 Mar 2014 | guards the Resource Area's runite rocks, which also do not exist here |
| Callisto, and Artio | 13 Mar 2014 / 2023 rework | |
| Venenatis, Spindel, Venenatis' spiderling | 13 Mar 2014 / 2023 rework | |
| Vet'ion, Calvar'ion | 13 Mar 2014 / 2023 rework | |
| Scorpia | 13 Mar 2014 | |
| Chaos Fanatic | 13 Mar 2014 | |
| Crazy archaeologist | 13 Mar 2014 | |
| Revenants (all forms) | Revenant Caves, 2017 | the Dec 2007 Wilderness removal is what put them there in the first place |
| Revenant maledictus | 2021 | |

**Six of the seven classic "Wilderness bosses" landed on one day — 13 March 2014** — along with the
lava dragons, the ents, the runite golems and the mammoths. That single update is most of this
table, and it is a coherent thing to take or leave as a unit rather than piecemeal.

> **A name collision worth knowing about.** This build *does* have an npc called
> `skeleton_hellhound` — but it is **Vanstrom's**, from In Aid of the Myreque ("A creature summoned
> by Vanstrom to kill the remaining Myreque"), it has no map spawn, and it is not Vet'ion's minion.
> Searching the npc table for the name will tell you we have it. We do not.

---

## 2. Exists in this build, just not in our Wilderness

These need **a spawn, not an import** — the npc, model, stats and combat scripts are all built.
This is by far the cheaper half of the list.

| Monster | Where it is here | Where OSRS also puts it |
|---|---|---|
| **Mammoth** (`mammoth`, id 135) | one spawn at 3109,3353, near Al Kharid | south-east of Ferox Enclave, 13 Mar 2014 |
| Abyssal demon (`slayer_abyssal`) | Slayer Tower | Wilderness Slayer Cave, 2021 |
| Dust devil (`slayer_dustdevil`) | Smoke Dungeon | Wilderness Slayer Cave |
| Nechryael (`slayer_nechryael`) | Slayer Tower | Wilderness Slayer Cave |
| Jelly (`slayer_jelly_1..6`) | Fremennik Slayer Dungeon | Wilderness Slayer Cave |
| Bloodveld (`slayer_bloodveld`) | Slayer Tower | Wilderness Slayer Cave |
| Aviansie (`gwd_aviansie_1..15`) | God Wars Dungeon | Wilderness God Wars Dungeon |
| Spiritual creatures (`gwd_spiritual_*`, 12 of them) | God Wars Dungeon | Wilderness God Wars Dungeon |

> **The mammoth is the pleasing one.** `mammoth` is npc **id 135** — a low id, which means it is in
> the **2006 cache already**, with its own walk and ready animations. OSRS's 2014 Wilderness mammoth
> is that same creature given a new home. So putting mammoths in our Wilderness is **a map edit and
> nothing else**: no import, no model work, no era argument to have. If you want one cheap thing
> off this entire document, it is that.

---

## 3. What we already have up there

For completeness, the census found these monsters inside the rectangles (spawn counts in brackets):

green dragons (24), **lava dragons (8)**, black dragons (2), **ankou (21)**, hellhounds (5),
greater demons (7), lesser
demons (8), black demons (3), earth warriors (11), chaos druids (11), elder chaos druids (8), dark
warriors (15), rogues (22), thugs (18), bandits (10 across two kinds), black knights (11), chaos
dwarves (11), magic axes (9), pirates (12), ice warriors (26), ice giants (9), hill giants (12),
moss giants (3), fire giants (5), giant skeletons (7), skeletons (57 across two kinds), zombies
(21), ghosts (17), scorpions (17), king scorpions (4), rats and giant rats (43), spiders of five
kinds (153), bats (7), bears (11), wolves and white wolves (12), black unicorns (12), dark wizards
(8), black salamanders (6), Chronozon, the three Mage Arena mages, and the **Chaos Elemental** at
3261,3927.

The **King Black Dragon** is built and scripted (`area_wilderness/scripts/king_black_dragon.rs2`)
but lives at 2269,4697 — his own lair map, outside the Wilderness rectangles, exactly as in
RuneScape.

**The Wilderness red dragons are gone as of 9 October 2026.** Lava Dragon Isle was Red Dragon Isle
until 13 March 2014, and Old School replaced the red dragons with lava dragons - two of its eight
lava dragon spawns are, to the tile, two of the red dragon spawns this build had. The same swap has
now been made here, so **no red dragon stands in the Wilderness any more** and the red dragon
Slayer task is completed in Brimhaven Dungeon, where the other six live.

---

## 4. What this means for the wilderness slayer master

Cross-referencing against Krystilia's 37-task table (`wilderness-slayer-options.md`):

- **She could be built on what exists today** for roughly 13 of her tasks, once the five untagged
  monsters standing up there get a `slayer_category` — chaos druids, chaos druid warriors, dark
  warriors, rogues, highwaymen.
- **Spawning the eight monsters in section 2 adds eight more** for the price of map edits. That
  takes her from a thin table to a real one without importing a single npc.
- **Only then is importing worth it**, and the order I would go in is: Ankou first (2006 creature,
  genuinely missing, and the one people expect), then nothing else unless you want the 13 March
  2014 update as a package.

So the honest headline: **the gap between our Wilderness and Old School's is mostly one 2014 update
and a handful of missing spawns, not a missing bestiary.**
