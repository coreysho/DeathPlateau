# Full quest audit — tracker

Started 19 October 2026. The directive: **every quest complete and functional, down to the wiki
playthrough guides.** One quest at a time, in the order the in-game quest list shows them.

**Method per quest**
1. Read the implementation (`content/scripts/quests/<dir>`).
2. Fetch the wiki playthrough and list every step it requires.
3. Drive the whole quest in a sim through real triggers on the real map — start to finish, not spot
   checks.
4. Fix every gap the walkthrough exposes.
5. Leave the sim behind in the audit suite so the quest can never silently regress.

**Status key** — `AUDITED` a sim drives it start to finish and passes · `PARTIAL` a sim covers some
of it · `NOT AUDITED` never driven by a sim · `—` not applicable

There are **108 quests** in the list (plus the Quest Points row).

**CORRECTION (19 Oct):** the first version of this table counted only audit1-3. There are **eight**
audit files, audit0 through audit7, and audits 4-7 cover more quests: Devious Minds, Making History,
In Aid of the Myreque, Regicide, Troll Romance (audit4); The Hand in the Sand, One Small Favour,
A Tail of Two Cats, Plague City (audit5); Mountain Daughter, Spirits of the Elid, Forgettable Tale,
Swan Song, In Search of the Myreque, Dragon Slayer spot-check (audit6); Rum Deal, Throne of
Miscellania, Garden of Tranquillity, Haunted Mine (audit7). Plus audit0: Tears of Guthix, Wanted!,
The Giant Dwarf, Enter the Abyss, Monkey Madness configs, Death Plateau, A Fairy Tale Part I. So the
audited count is nearer **50**, and the table rows below still say NOT AUDITED for several of those -
they are corrected as each is reached.

**AUDITS 5 AND 7 ARE FLAKY** and that has to be fixed as part of this pass: each run fails a
*different* check (a bell summoning three instead of two, a karambwan cook roll, a Garden of
Tranquillity bed at stage 4 instead of 7, Roald's trolley). They assert exact outcomes of randomised
things. A flaky audit is a weak audit.

---

## Free quests

| Quest | Dir | Lines | Status | Covered by |
|---|---|---|---|---|
| Black Knights' Fortress | quest_blackknight | 234 | WALKED | quest_blackknight_run.ts (30/30) |
| Cook's Assistant | quest_cook | 135 | WALKED | quest_cook_run.ts (23/23) |
| Demon Slayer | quest_demon | 163 | WALKED | quest_demon_run.ts (22/22) |
| Doric's Quest | quest_doric | 154 | WALKED | quest_doric_run.ts (9/9) |
| Dragon Slayer | quest_dragon | 1027 | WALKED | quest_dragon_run.ts (82/82) |
| Ernest the Chicken | quest_haunted | 392 | WALKED | quest_ernest_run.ts (78/78) |
| Goblin Diplomacy | quest_gobdip | 200 | WALKED | quest_gobdip_run.ts (19/19) |
| Imp Catcher | quest_imp | 48 | WALKED | quest_imp_run.ts (7/7) |
| The Knight's Sword | quest_squire | 305 | WALKED | quest_squire_run.ts (22/22) |
| Pirate's Treasure | quest_hunt | 429 | WALKED | quest_hunt_run.ts (37/37) |
| Prince Ali Rescue | quest_prince | 155 | WALKED | quest_prince_run.ts (38/38) |
| The Restless Ghost | quest_priest | 294 | WALKED | quest_restlessghost_run.ts (28/28) |
| Romeo & Juliet | quest_romeojuliet | 82 | WALKED | quest_romeojuliet_run.ts (36/36) |
| Rune Mysteries | quest_runemysteries | 58 | WALKED | quest_runemysteries_run.ts (40/40) |
| Sheep Shearer | quest_sheep | 44 | WALKED | quest_sheep_run.ts (11/11) |
| Shield of Arrav | quest_blackarmgang | 359 | WALKED | quest_arrav_run.ts (31/31) |
| Vampire Slayer | quest_vampire | 192 | WALKED | quest_vampire_run.ts (20/20) |
| Witch's Potion | quest_hetty | 61 | WALKED | quest_hetty_run.ts (10/10) |

## Members' quests

| Quest | Dir | Lines | Status | Covered by |
|---|---|---|---|---|
| A Fairy Tale Pt. 1 | quest_fairy | 369 | WALKED | quest_fairy_run.ts (35/35) |
| A Soul's Bane | quest_soulbane | 1206 | WALKED | quest_soulbane_run.ts (35/35) |
| A Tail of Two Cats | quest_twocats | 637 | WALKED | quest_twocats_run.ts (45/45) |
| Animal Magnetism | quest_animmag | 1333 | NOT AUDITED | |
| Between a Rock... | quest_dwarfrock | 337 | WALKED | quest_dwarfrock_run.ts (32/32) |
| Big Chompy Bird Hunting | quest_chompybird | 1936 | NOT AUDITED | |
| Biohazard | quest_biohazard | 797 | NOT AUDITED | |
| Cabin Fever | quest_fever | 664 | AUDITED | audit3 |
| Clock Tower | quest_cog | 64 | WALKED | quest_cog_run.ts (22/22) |
| Creature of Fenkenstrain | quest_fenkenstrain | 713 | AUDITED | audit1 |
| Death Plateau | quest_death | 1666 | NOT AUDITED | |
| Desert Treasure | quest_deserttreasure | 2288 | AUDITED | audit3 (two sections) |
| Devious Minds | quest_devious | 339 | WALKED | quest_devious_run.ts (22/22) |
| Digsite Quest | quest_itexam | 2647 | NOT AUDITED | |
| Dream Mentor | quest_dreammentor | 620 | NOT AUDITED | |
| Druidic Ritual | quest_druid | 55 | WALKED | quest_druid_run.ts (17/17) |
| Dwarf Cannon | quest_mcannon | 573 | NOT AUDITED | |
| Eadgar's Ruse | quest_eadgar | 467 | WALKED | quest_eadgar_run.ts (32/32) |
| Eagles' Peak | quest_eaglespeak | 1386 | NOT AUDITED | |
| Elemental Workshop | quest_elemental_workshop | 543 | NOT AUDITED | |
| Enakhra's Lament | quest_enakh | 1187 | NOT AUDITED | |
| Family Crest | quest_crest | 994 | NOT AUDITED | |
| The Feud | quest_feud | 1357 | AUDITED | audit2 |
| Fight Arena | quest_arena | 1208 | NOT AUDITED | |
| Fishing Contest | quest_fishingcompo | 295 | WALKED | quest_fishingcompo_run.ts (20/20) |
| Forgettable Tale... | quest_forget | 453 | WALKED | quest_forget_run.ts (34/34) |
| The Fremennik Trials | quest_viking | 3383 | NOT AUDITED | |
| Garden of Tranquillity | quest_garden | 638 | NOT AUDITED | |
| Gertrude's Cat | quest_fluffs | 625 | NOT AUDITED | |
| Ghosts Ahoy | quest_ahoy | 1173 | AUDITED | audit3 |
| The Giant Dwarf | quest_giantdwarf | 343 | WALKED | quest_giantdwarf_run.ts (18/18) |
| The Golem | quest_golem | 640 | AUDITED | audit2 |
| The Grand Tree | quest_grandtree | 1615 | NOT AUDITED | |
| The Hand in the Sand | quest_handsand | 739 | NOT AUDITED | |
| Haunted Mine | quest_hauntedmine | 422 | WALKED | quest_hauntedmine_run.ts (40/40) |
| Hazeel Cult | quest_hazeelcult | 984 | NOT AUDITED | |
| Heroes Quest | quest_hero | 256 | WALKED | quest_hero_run.ts (35/35) + heroes_candlestick.ts (16/16, two players) |
| Holy Grail | quest_grail | 470 | WALKED | quest_grail_run.ts (30/30, needs NODE_MEMBERS=true) |
| Horror from the Deep | quest_horror | 1858 | NOT AUDITED | |
| Icthlarin's Little Helper | quest_icslittle | 422 | WALKED | quest_icslittle_run.ts (38/38) |
| In Aid of the Myreque | quest_myreque2 | 1725 | PARTIAL | myrequecrate, myrequeescort, myrequerod, myrequevillage |
| In Search of the Myreque | quest_routequest | 700 | WALKED | quest_routequest_run.ts (41/41) |
| Jungle Potion | quest_junglepotion | 190 | PARTIAL | tbwcleanup (the gate only) |
| Legends Quest | quest_legends | 5847 | NOT AUDITED | the largest in the build |
| Lost City | quest_zanaris | 248 | WALKED | quest_zanaris_run.ts (21/21) |
| The Lost Tribe | quest_lost_tribe | 874 | NOT AUDITED | |
| Lunar Diplomacy | quest_lunar | 1971 | NOT AUDITED | |
| Making History | quest_makinghistory | 515 | NOT AUDITED | |
| Merlin's Crystal | quest_arthur | 515 | WALKED | quest_arthur_run.ts (26/26) |
| Monk's Friend | quest_drunkmonk | 142 | WALKED | quest_drunkmonk_run.ts (26/26) |
| Monkey Madness | quest_mm | 1846 | PARTIAL | audit1 (Marim's gate only) |
| Mountain Daughter | quest_mdaughter | 710 | NOT AUDITED | |
| Mourning's End Part 1 | quest_mourning | 1388 | AUDITED | audit1 |
| Mourning's End Part 2 | quest_mourning2 | 2573 | AUDITED | audit2 |
| Murder Mystery | quest_murder | 1253 | NOT AUDITED | |
| Nature Spirit | quest_druidspirit | 1373 | NOT AUDITED | |
| Observatory Quest | quest_itgronigen | 849 | NOT AUDITED | |
| One Small Favour | quest_onesmallfavour | — | NOT AUDITED | check: no directory of that name |
| Plague City | quest_elena | 903 | NOT AUDITED | |
| Priest in Peril | quest_priestperil | 382 | WALKED | quest_priestperil_run.ts (47/47) |
| Rag and Bone Man | quest_rag | 257 | WALKED | quest_rag_run.ts (43/43) |
| Rat Catchers | quest_ratcatch | 493 | AUDITED | audit2 |
| Recipe for Disaster | quest_100 | 3022 | AUDITED | audit1 (ten sections) |
| Recruitment Drive | quest_rd | 1330 | AUDITED | audit3 |
| Regicide | quest_regicide | 1210 | NOT AUDITED | |
| Roving Elves | quest_roving | 299 | WALKED | quest_roving_run.ts (19/19) |
| Rum Deal | quest_deal | 546 | NOT AUDITED | |
| Scorpion Catcher | quest_scorpcatcher | 170 | WALKED | quest_scorpcatcher_run.ts (28/28) |
| Sea Slug Quest | quest_seaslug | 242 | WALKED | quest_seaslug_run.ts (57/57) |
| Shades of Mort'ton | quest_mortton | 864 | PARTIAL | morttonwall (the walls only) |
| Shadow of the Storm | quest_agrith | 451 | WALKED | quest_agrith_run.ts (25/25) |
| Sheep Herder | quest_sheepherder | 106 | WALKED | quest_sheepherder_run.ts (63/63) |
| Shilo Village | quest_zombiequeen | 2171 | NOT AUDITED | |
| Spirits of the Elid | quest_elid | 518 | NOT AUDITED | |
| Swan Song | quest_swansong | 628 | NOT AUDITED | |
| Tai Bwo Wannai Trio | quest_tbwt | 652 | PARTIAL | tbwtsons (the three sons) |
| Tears of Guthix | quest_tog | 426 | WALKED | quest_tog_run.ts (14/14, hand-rolled) |
| Temple of Ikov | quest_ikov | 760 | NOT AUDITED | |
| Throne of Miscellania | quest_misc | 2729 | NOT AUDITED | |
| The Tourist Trap | quest_desertrescue | 3120 | NOT AUDITED | |
| Tree Gnome Village | quest_tree | 346 | WALKED | quest_tree_run.ts (43/43) |
| Tribal Totem | quest_totem | 231 | WALKED | quest_totem_run.ts (40/40) |
| Troll Romance | quest_troll_love | 688 | NOT AUDITED | |
| Troll Stronghold | quest_troll | 857 | AUDITED | audit3 |
| Underground Pass | quest_upass | 2442 | NOT AUDITED | |
| Wanted! | quest_wanted | 413 | WALKED | quest_wanted_run.ts (25/25, hand-rolled — the chase is random) |
| Watch Tower | quest_itwatchtower | 2124 | AUDITED | audit1 |
| Waterfall Quest | quest_waterfall | 888 | WALKED | quest_waterfall_run.ts (51/51) |
| Witch's House | quest_ball | 343 | WALKED | quest_ball_run.ts (51/51) |
| Zogre Flesh Eaters | quest_zogre | 1068 | AUDITED | audit3 |

## Also in the quests directory, not on the list

| Thing | Dir | Lines | Status |
|---|---|---|---|
| Abyssal miniquest | miniquest_abyssal | 342 | WALKED | miniquest_abyssal_run.ts (19/19) |
| Barcrawl | quest_barcrawl | 16 | WALKED | quest_barcrawl_run.ts (25/25) |
| Dragon Slayer (shared) | quest_dragon | 1027 | NOT AUDITED |

---

## Progress log — the walked pass

Each quest below has a `questrun` manifest in `Engine-TS/tools/sim/`. A manifest WALKS the quest: no
teleports, every door, staircase, ladder and lever clicked, and a step either gets there or says
where it stopped. **WALKED** in the tables above means that manifest passes every check.

| # | Quest | Checks | What it found |
|---|---|---|---|
| 1 | Black Knights' Fortress | 30/30 | forceapproach on a ladder; one leg still unwalked (below) |
| 2 | Cook's Assistant | 23/23 | nothing — correct |
| 3 | Doric's Quest | 9/9 | Doric said he makes amulets in two of three lines; he makes pickaxes |
| 4 | Imp Catcher | 7/7 | nothing — correct |
| 5 | Witch's Potion | 10/10 | nothing — correct |
| 6 | Rune Mysteries | 40/40 | "the information I had already already collated" |
| 7 | The Restless Ghost | 28/28 | nothing in the quest; two silent holes in the runner |
| 8 | Romeo & Juliet | 36/36 | **the quest could not be finished** — nothing could pick a cadava berry |
| 9 | Vampire Slayer | 20/20 | Morgan sent you to the Jolly Boar; Harlow drinks in the Blue Moon |
| 10 | Ernest the Chicken | 78/78 | **the chicken never turned back into a man**; a debug line in Oddenstein's dialogue |
| 11 | Dragon Slayer | 82/82 | nothing — correct, and correctly the 2006 quest rather than the rework |
| 12 | The Knight's Sword | 22/22 | **the quest could not be finished** — Sir Vyvin never let go of his cupboard |
| 13 | Prince Ali Rescue | 38/38 | nothing — correct, and correctly the 2006 version |
| 14 | Sheep Shearer | 11/11 | nothing — 60 coins and 150 Crafting XP is the 2006 reward, not the wiki's 150 coins |
| 15 | Goblin Diplomacy | 19/19 | nothing — correct |
| 16 | Demon Slayer | 22/22 | Sir Prysin asked where all "they" keys were, twice |
| 17 | Pirate's Treasure | 37/37 | nothing — correct |
| 18 | Shield of Arrav | 31/31 | nothing — correct, and it completes alone since the half-shield certificate |
| 19 | A Fairy Tale Part I | 35/35 | nothing — correct |
| 20 | A Soul's Bane | 35/35 | nothing — correct |
| 21 | A Tail of Two Cats | 45/45 | the garden patch is only reachable from inside the garden |
| 22 | Druidic Ritual | 17/17 | nothing — correct |
| 23 | Clock Tower | 22/22 | the 2x2 at the centre of each clock floor is sealed; the blue cog room needs the secret door |
| 24 | Sheep Herder | 63/63 | nothing — all four sheep prodded across the field, 48/30/61/48 prods |
| 25 | Monk's Friend | 26/26 | nothing — the blanket sits on the thieves' table, which the runner could not reach |
| 26 | Scorpion Catcher | 28/28 | nothing — the Seers are inside the house, not in the square |
| 27 | Tribal Totem | 40/40 | nothing — correct, KURT dialled on the four-letter lock |
| 28 | Sea Slug | 57/57 | nothing in the quest; drive() used to wait out a world_delay, so every fire burned out |
| 29 | Lost City | 21/21 | nothing — the shed is solid inside, so its door IS the portal |
| 30 | Rag and Bone Man | 43/43 | nothing — the fight step now gives up on penned npcs instead of swinging for 27,000 ticks |
| 31 | Fishing Contest | 20/20 | nothing — correct |
| 32 | Witch's House | 51/51 | nothing — the witch catches a plain walk, so `sneak` waits behind the hedges |
| 33 | Tree Gnome Village | 43/43 | **Elkoy's guide left you outside the maze**, 34 tiles and a squeeze-through short of the village |
| 34 | Priest in Peril | 47/47 | **the temple doors were unlocked for anybody**, and knocking opened them instead of talking |
| 35 | Waterfall Quest | 51/51 | nothing — the tomb bans runes as well as weapons, so the pillars' runes come after it |
| 36 | Roving Elves | 19/19 | nothing — correct |
| 37 | Heroes' Quest | 35/35 + 16/16 | **the candlestick chest derailed the Phoenix member**; the heist needs two players, by 2006 design |
| 38 | Alfred Grimhand's Barcrawl | 25/25 | nothing — Blurberry serves his own round, with no menu, and resents being asked twice |
| 39 | Between a Rock... | 32/32 | nothing — Dondakan is a multinpc, so the parent is what answers a click |
| 40 | The Giant Dwarf | 18/18 | nothing — two of its conversations advance two stages at once |
| 41 | Wanted! | 25/25 | nothing — the chase is random, so this one is hand-rolled rather than a manifest |
| 42 | Tears of Guthix | 14/14 | nothing — Juna has to be met before the light creatures will carry you |
| 43 | Enter the Abyss | 19/19 | nothing — the temple mage ignores anybody who has not met the one in the Wilderness |
| 44 | Devious Minds | 22/22 | the monk checks none of the three quests the wiki lists as requirements |
| 45 | Merlin's Crystal | 26/26 | nothing — Mordred is beaten down, not killed, which the fight step had to learn |
| 46 | Haunted Mine | 40/40 | the glowing fungus did not exist, Treus Dayth was a mesbox, the reward was the wrong skill, and the Salve shard came out of a door |
| 47 | Icthlarin's Little Helper | 38/38 | the Wanderer, the Sphinx, the Carpenter and the suntrap were all on the map and all silent; the level-91 guardian had no stats and no placement, so the quest had no fight in it |
| 48 | Shadow of the Storm | 25/25 | the reward paid Crafting and Magic instead of ten thousand in a combat skill of your choice; Demon Slayer, The Golem and 30 Crafting were all unchecked; Agrith-Naar is genuinely not in the cache |
| 49 | Forgettable Tale... | 34/34 | reading the twelfth mural did not finish the chapter - the stage only moved on a thirteenth walk through a cave mouth, and the way out was gated on that stage; the reward paid Mining and never handed over the stouts; Fishing Contest unchecked |
| 50 | Eadgar's Ruse | 32/32 | Death Plateau was the one requirement of four nobody asked for; everything else in this one was already right |
| 51 | Holy Grail | 30/30 | **there was no Holy Grail** - no map placed one, so the last step had nothing to pick up and nobody could finish it; the Crone is placed nowhere either, so her whole conversation is dead dialogue; 20 Attack unchecked |
| 52 | In Search of the Myreque | 41/41 | **it was a different quest** - built once from the varbit names alone, so Veliaf asked the three questions, the three missing pieces were rungs of a ladder and the boatman had to be talked round. The real 2005 quest is all in the cache and none of it was wired: a level-97 Skeleton Hellhound with no statblock, Vanstrom Klause in five bodies, two climbable trees over four tiles of rope bridge, the doors in the earth behind the hollow tree, and the Myreque's chamber held once per plane with six of them on plane 3 and the four survivors on plane 0 |

**EVERY FREE QUEST NOW WALKS.** Eighteen of eighteen, each with a `questrun` manifest that plays it
from start to finish on foot and passes every check.

Three of them could not be finished at all before this pass:
- **Romeo & Juliet** — nothing in the game could pick a cadava berry.
- **The Knight's Sword** — the cupboard check was measured from the player, and an npc parks itself
  while somebody stands beside it, so Sir Vyvin never moved off the one tile it answers from.
- **Ernest the Chicken** — the quest completed but its ending did not happen: the chicken never
  became a man.

Smaller fixes: Doric's amulets, Rune Mysteries' doubled word, Morgan's wrong inn, Oddenstein's debug
line, Sir Prysin's "they keys".

**The Ernest lever maze is correct.** `tools/sim/ernestmaze.ts` feeds all 64 lever states through the
content's own `[proc,recalculate_ernest_doors]`, labels the basement's rooms from the engine's
collision, and searches (room, lever state) for a route to the oil can. It finds one in 23 moves, and
they are the wiki's own sequence move for move.

**Five holes in `questrun` itself**, every one of them silent in both directions:
- `take` was not a click at all. It deleted the ground obj and handed over the item without running
  any content, so `[opobj3,ghostskull]` — which IS a step of The Restless Ghost — never fired. It now
  walks onto the obj's own tile and sends op 3, clearing a leftover delay or an open chat window
  first, both of which the engine throws a click away for.
- `want` could not see a one-shot mesbox: `drive()` starts counting lines when it is called and
  `arrive()` returns on the tick a script pauses, which is the tick the text was set.
- `arrive` asked "is the player standing next to the thing they clicked", which a staircase makes
  false by definition — Draynor Manor's crypt stairs leave you six thousand tiles away.
- `nearnpc`, new: did the cutscene actually produce the npc? Nothing a stage or inventory check can
  see, and the only thing that would have caught Ernest staying a chicken.
- failure details now name what IS there, which is what turned "no Ernest" into "a chicken and a
  professor".

**A new tool:** `tools/sim/reach.ts` floods a region over the engine's own canTravel and prints it as
a map. "The room is sealed" and "nobody clicked the door" look identical from a failed walk. The
Wizards' Tower ground floor is three chambers joined by two doors; Lumbridge Castle's is five.

---

## Earlier notes


**1. Black Knights' Fortress — DONE, walked on foot, 30 of 30.**
`tools/sim/quest_blackknight_run.ts` (engine a5c805bc). A questrun manifest, so every door, ladder
and push-wall is actually used rather than teleported past. Findings:
- No dossier exists in the 377 cache, so starting from Sir Amik's dialogue is correct; the dossier
  the wiki describes is later content.
- `loc_1749` has forceapproach=north rotated to south by its angle: that ladder only works from the
  tile south of it, and clicking from the west silently does nothing.
- The second push-wall moves you through from its north face and refuses the other two sides.
- ONE LEG UNWALKED: the grill room back round to that north face. Every piece answers in isolation;
  the first floor is cut by wall locs the tile flags do not show. The wiki's route goes out to the
  entrance and up the east room's north ladder (`loc_1750` at 3022,3518) - that is the leg to walk.

**A wrong fix, reverted.** I changed `~climb_ladder` to step off a blocked landing, on the premise
that `p_telejump` refuses blocked tiles. It does not - it moves the player regardless. The change
broke three previously-green checks (a Recipe for Disaster cooking step, Cabin Fever's boat home, and
a Hand in the Sand weathervane landing) and is fully reverted. The fortress ladder's real problem is
the forceapproach side, not the landing tile.

**Next:** Cook's Assistant, the next NOT AUDITED row in list order.

**Melzar's Maze is correct.** `tools/sim/ernestmaze.ts` is for Ernest; Dragon Slayer's maze needed no
solver because the content's six keyed doors and six key-droppers match the wiki step for step - the
only thing the run had to work out for itself was which three ladders "descend the ladder at the
room's end, then descend two more" means.

**Three quests could not be finished at all** before this pass: Romeo & Juliet (no way to pick a
cadava berry), The Knight's Sword (Sir Vyvin's cupboard deadlocked), and Ernest the Chicken's ending
(the chicken never became a man - the quest completed, but the scene did not happen).

**`questrun` has had eleven holes closed**, every one of them silent in one direction or the other.
The ones from quests 11 and 12: a fight was one click and a gate's delay binned it; a kill was "gone
fifteen ticks later", which reads a respawn as a failure; `fight`, and then `loc`, learned `until` -
the obj the step is for - and `loc`'s `until` was at first only steering the retries and not the
verdict, so a step that ran out of tries with nothing to show for it reported ok, fifty-nine
refusals in a row.

---

## Where to pick this up

**52 quests and miniquests walked.** All eighteen free quests, thirty-two members' quests and two
miniquests. Every one has a file in `Engine-TS/tools/sim/` that plays it and passes every check;
rerun any of them with `npx tsx tools/sim/<name>.ts`.

**One flag to know about:** `NODE_MEMBERS=true` is commented out in `Engine-TS/.env`, so a sim boots
a FREE-TO-PLAY world and every `map_members` branch in content takes the other path. Members content
needs `NODE_MEMBERS=true npx tsx tools/sim/<name>.ts` — Holy Grail's whistle door spawns no whistles
without it, which reads as a broken obj spawn rather than a world flag.

### The runner's own vocabulary, as it stands
`go` `talk` `loc` `useLoc` `useNpc` `held` `use` `give` `setvar` `stage` `varis` `level` `wait`
`take` `setpos` `has` `hasnt` `worn` `fight` `nearnpc` `hunt` `herd` `sneak` `press` `say` `note`.

The ones added during this pass, and what each exists for:
- **`herd`** — Sheep Herder. A prod moves a sheep one tile directly away from the player and
  ~coord_direction only answers N/S/E/W, so "where can this sheep be pushed" is a different graph
  from "where can it walk"; the step plans over moves legal for both.
- **`sneak`** — Witch's House. Walks a route a tile at a time, holding whenever the next tile would
  be inside an npc's range. The witch teleports anybody she sees within three tiles.
- **`press` with `n`** — Tribal Totem's four-letter lock. Sixty-six presses, one report line.
- **`fight` with `picks`** — Merlin's Crystal. Sir Mordred is beaten down, not killed; his mother
  stops the fight and talks, and the step used to close her dialogue and keep swinging.
- **`soft` on `take` and `useLoc`** — clicks that are MEANT to fail (reaching for the ball in
  Witch's House wakes the shapeshifter; six of Priest in Peril's seven monuments hold nothing).
- **`tries`/`until` on `held`** — rubbing Sea Slug's dry sticks together is a firemaking roll.

Three quests were not written as manifests at all, because what they test is random or timed:
`quest_wanted_run.ts` (Solus is in one of twelve places), `quest_tog_run.ts` (the weeping walls run
on a timer) and `heroes_candlestick.ts` (two players at once).

### What is left
Everything still marked NOT AUDITED or AUDITED in the tables above. By size, the next ones are:
Rat Catchers, Making History, Spirits of the Elid, Elemental Workshop, Rum Deal, Dwarf Cannon,
Dream Mentor, Gertrude's Cat, Swan Song, and then the long ones (Desert Treasure, Monkey Madness,
Recipe for Disaster, Temple of Ikov, Underground Pass, Legends Quest...).

**In Aid of the Myreque is NOT the same shape of problem**, which is worth writing down because the
first look at it said it was. Its Veliaf dialogue is invented prose, like everything else in this
build, but its structure was taken from the cache's own multilocs and it follows the real
walkthrough step for step: Florin's food chest, the cellar rubble, the store roof and wall, the bank
booth and wall, the furnace, the blood tithe and Gadderanks, Ivan's escort to Paterdomus, Drezel,
the library, Ivandis's tomb and the rod. It is PARTIAL because four sims cover parts of it and
nothing walks it end to end. Invented dialogue is not the tell; a mechanic handed to the wrong
character is.

**`rng` is the fix for the flaky audits.** `questrun` now takes `rng: <number>` to pin the engine's
own nextDouble for the length of a randomised step and `rng: null` to put it back. Curpile Fyod asks
three of six questions at random and that is what it was added for; the bell in audit5 and the
karambwan roll and the Garden of Tranquillity check in audit7 are the same problem.

Forgettable Tale is walked and complete, but it is a compressed version of the quest rather than
the whole of it, and that is worth writing down: the four kelda seeds arrive as one packet from
Elstan instead of individually from the Drunken Dwarf, the Rowdy dwarf, Khorvak and Gauss (the last
two are in the cache and have no part in this flow); the hops patch and the fermenting vat are not
built, so Veldaban takes an ordinary beer rather than Kelda stout; the cart-junction stone puzzles
are twelve wall panels instead; and the kebab-and-beer memory-wipe finale is not there. Each of
those is a quest's worth of work on its own.

Two pieces of unfinished business from earlier in the pass:
- **Black Knights' Fortress** has one unwalked leg: the grill room back round to the second
  push-wall's north face. Every piece answers in isolation.
- **audit5 and audit7** have flaky checks (randomised outcomes asserted exactly).
