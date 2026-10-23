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
| Biohazard | quest_biohazard | 797 | WALKED | quest_biohazard_run.ts (81/81) |
| Cabin Fever | quest_fever | 664 | WALKED | quest_fever_run.ts (81/81) |
| Clock Tower | quest_cog | 64 | WALKED | quest_cog_run.ts (22/22) |
| Creature of Fenkenstrain | quest_fenkenstrain | 713 | WALKED | quest_fenkenstrain_run.ts (75/75) |
| Death Plateau | quest_death | 1666 | NOT AUDITED | |
| Desert Treasure | quest_deserttreasure | 2288 | AUDITED | audit3 (two sections) |
| Devious Minds | quest_devious | 339 | WALKED | quest_devious_run.ts (22/22) |
| Digsite Quest | quest_itexam | 2647 | NOT AUDITED | |
| Dream Mentor | quest_dreammentor | 620 | WALKED | quest_dreammentor_run.ts (86/86) |
| Druidic Ritual | quest_druid | 55 | WALKED | quest_druid_run.ts (17/17) |
| Dwarf Cannon | quest_mcannon | 573 | WALKED | quest_mcannon_run.ts (71/71) |
| Eadgar's Ruse | quest_eadgar | 467 | WALKED | quest_eadgar_run.ts (32/32) |
| Eagles' Peak | quest_eaglespeak | 1386 | NOT AUDITED | |
| Elemental Workshop | quest_elemental_workshop | 543 | WALKED | quest_elemental_run.ts (58/58) |
| Enakhra's Lament | quest_enakh | 1187 | WALKED | quest_enakh_run.ts (86/86) |
| Family Crest | quest_crest | 994 | WALKED | quest_crest_run.ts (76/76) |
| The Feud | quest_feud | 1357 | WALKED | quest_feud_run.ts (146/146) |
| Fight Arena | quest_arena | 1208 | WALKED | quest_arena_run.ts (34/34) |
| Fishing Contest | quest_fishingcompo | 295 | WALKED | quest_fishingcompo_run.ts (20/20) |
| Forgettable Tale... | quest_forget | 453 | WALKED | quest_forget_run.ts (34/34) |
| The Fremennik Trials | quest_viking | 3383 | NOT AUDITED | |
| Garden of Tranquillity | quest_garden | 638 | WALKED | quest_garden_run.ts (88/88) |
| Gertrude's Cat | quest_fluffs | 625 | WALKED | quest_fluffs_run.ts (41/41) |
| Ghosts Ahoy | quest_ahoy | 1173 | WALKED | quest_ahoy_run.ts (168/168) |
| The Giant Dwarf | quest_giantdwarf | 343 | WALKED | quest_giantdwarf_run.ts (18/18) |
| The Golem | quest_golem | 640 | WALKED | quest_golem_run.ts (65/65) |
| The Grand Tree | quest_grandtree | 1615 | NOT AUDITED | |
| The Hand in the Sand | quest_handsand | 739 | WALKED | quest_handsand_run.ts (53/53) |
| Haunted Mine | quest_hauntedmine | 422 | WALKED | quest_hauntedmine_run.ts (40/40) |
| Hazeel Cult | quest_hazeelcult | 984 | WALKED | quest_hazeelcult_run.ts (27/27) + quest_hazeelcult_evil_run.ts (47/47) - both sides |
| Heroes Quest | quest_hero | 256 | WALKED | quest_hero_run.ts (35/35) + heroes_candlestick.ts (16/16, two players) |
| Holy Grail | quest_grail | 470 | WALKED | quest_grail_run.ts (30/30, needs NODE_MEMBERS=true) |
| Horror from the Deep | quest_horror | 1858 | NOT AUDITED | |
| Icthlarin's Little Helper | quest_icslittle | 422 | WALKED | quest_icslittle_run.ts (38/38) |
| In Aid of the Myreque | quest_myreque2 | 1800 | WALKED | quest_myreque2_run.ts (81/81) |
| In Search of the Myreque | quest_routequest | 700 | WALKED | quest_routequest_run.ts (41/41) |
| Jungle Potion | quest_junglepotion | 190 | PARTIAL | tbwcleanup (the gate only) |
| Legends Quest | quest_legends | 5847 | NOT AUDITED | the largest in the build |
| Lost City | quest_zanaris | 248 | WALKED | quest_zanaris_run.ts (21/21) |
| The Lost Tribe | quest_lost_tribe | 874 | WALKED | quest_losttribe_run.ts (52/52) |
| Lunar Diplomacy | quest_lunar | 1971 | NOT AUDITED | |
| Making History | quest_makinghistory | 700 | WALKED | quest_makinghistory_run.ts (39/39) |
| Merlin's Crystal | quest_arthur | 515 | WALKED | quest_arthur_run.ts (26/26) |
| Monk's Friend | quest_drunkmonk | 142 | WALKED | quest_drunkmonk_run.ts (26/26) |
| Monkey Madness | quest_mm | 1846 | WALKED | quest_mm_run.ts (144/144) |
| Mountain Daughter | quest_mdaughter | 710 | WALKED | quest_mdaughter_run.ts (123/123) |
| Mourning's End Part 1 | quest_mourning | 1388 | AUDITED | audit1 |
| Mourning's End Part 2 | quest_mourning2 | 2573 | AUDITED | audit2 |
| Murder Mystery | quest_murder | 1253 | WALKED | quest_murder_run.ts (33/33) |
| Nature Spirit | quest_druidspirit | 1373 | NOT AUDITED | |
| Observatory Quest | quest_itgronigen | 849 | WALKED | quest_observatory_run.ts (49/49) |
| One Small Favour | quest_onesmallfavour | — | NOT AUDITED | check: no directory of that name |
| Plague City | quest_elena | 903 | WALKED | quest_plaguecity_run.ts (75/75) |
| Priest in Peril | quest_priestperil | 382 | WALKED | quest_priestperil_run.ts (47/47) |
| Rag and Bone Man | quest_rag | 257 | WALKED | quest_rag_run.ts (43/43) |
| Rat Catchers | quest_ratcatch | 1000 | WALKED | quest_ratcatch_run.ts (73/73) |
| Recipe for Disaster | quest_100 | 3022 | AUDITED | audit1 (ten sections) |
| Recruitment Drive | quest_rd | 1330 | WALKED | quest_rd_run.ts (69/69) |
| Regicide | quest_regicide | 1210 | NOT AUDITED | |
| Roving Elves | quest_roving | 299 | WALKED | quest_roving_run.ts (19/19) |
| Rum Deal | quest_deal | 490 | WALKED | quest_deal_run.ts (116/116) |
| Scorpion Catcher | quest_scorpcatcher | 170 | WALKED | quest_scorpcatcher_run.ts (28/28) |
| Sea Slug Quest | quest_seaslug | 242 | WALKED | quest_seaslug_run.ts (57/57) |
| Shades of Mort'ton | quest_mortton | 864 | PARTIAL | morttonwall (the walls only) |
| Shadow of the Storm | quest_agrith | 451 | WALKED | quest_agrith_run.ts (25/25) |
| Sheep Herder | quest_sheepherder | 106 | WALKED | quest_sheepherder_run.ts (63/63) |
| Shilo Village | quest_zombiequeen | 2171 | NOT AUDITED | |
| Spirits of the Elid | quest_elid | 700 | WALKED | quest_elid_run.ts (50/50) |
| Swan Song | quest_swansong | 628 | WALKED | quest_swansong_run.ts (109/109) |
| Tai Bwo Wannai Trio | quest_tbwt | 652 | PARTIAL | tbwtsons (the three sons) |
| Tears of Guthix | quest_tog | 426 | WALKED | quest_tog_run.ts (14/14, hand-rolled) |
| Temple of Ikov | quest_ikov | 760 | WALKED | quest_ikov_run.ts (86/86) |
| Throne of Miscellania | quest_misc | 2729 | NOT AUDITED | |
| The Tourist Trap | quest_desertrescue | 3120 | NOT AUDITED | |
| Tree Gnome Village | quest_tree | 346 | WALKED | quest_tree_run.ts (43/43) |
| Tribal Totem | quest_totem | 231 | WALKED | quest_totem_run.ts (40/40) |
| Troll Romance | quest_troll_love | 688 | WALKED | quest_troll_love_run.ts (63/63) |
| Troll Stronghold | quest_troll | 857 | WALKED | quest_trollstronghold_run.ts (28/28) |
| Underground Pass | quest_upass | 2442 | NOT AUDITED | |
| Wanted! | quest_wanted | 413 | WALKED | quest_wanted_run.ts (25/25, hand-rolled — the chase is random) |
| Watch Tower | quest_itwatchtower | 2124 | AUDITED | audit1 |
| Waterfall Quest | quest_waterfall | 888 | WALKED | quest_waterfall_run.ts (51/51) |
| Witch's House | quest_ball | 343 | WALKED | quest_ball_run.ts (51/51) |
| Zogre Flesh Eaters | quest_zogre | 1068 | WALKED | quest_zogre_run.ts (73/73) |

## Also in the quests directory, not on the list

| Thing | Dir | Lines | Status |
|---|---|---|---|
| Abyssal miniquest | miniquest_abyssal | 342 | WALKED | miniquest_abyssal_run.ts (19/19) |
| Barcrawl | quest_barcrawl | 16 | WALKED | quest_barcrawl_run.ts (25/25) |
| Dragon Slayer (shared) | quest_dragon | 1027 | WALKED | same directory as the free-quest row above - quest_dragon_run.ts (82/82) |

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
| 53 | In Aid of the Myreque | 81/81 | **it stopped at its second step** - the village leader's switch only knew ^m2_sent and you cannot reach her at ^m2_sent, so she never briefed anybody and the shop, the bank and the furnace are all gated on the stage she sets. Florin could not be talked to either: he stands three tiles inside his own gate and the gate is a wall. The Gadderanks fight was four lines of narration while the cache held an attackable Gadderanks, a wounded one with a fall-over animation and two Vampyre Juvinates; the rubble was one click while the cache held a three-stage bucket and a placed pile with no handler; the Gadderhammer was reachable from nowhere; and the four skill requirements were checked nowhere |
| 54 | Rat Catchers | 73/73 | **seven of its ten chapters were in the cache and wired to nothing** - it was built as Jimmy Dazzler, four rat holes and a party, and its own constant file called two of the items it needed "unused". Phingspet and Grimesquit, Hooknosed Jack, Pox, the King rat, the Apothecary, Smokin' Joe, the Face, the snake charmer and eight notes on the Port Sarim docks are all placed and named. Even the varbits are the chapters. Also found: the warehouse ladder takes a click from three sides and not the north, and vc_note_number is three bits so the tune's counter could not count to eight |
| 55 | Making History | 39/39 | **the four documents were wired to the wrong people**, and the cache's own descriptions settle it: a journal out of a buried chest, a timeline out of a ghost, one letter sealed to the king and one sealed to Jorral. The old version handed the timeline out at the start, made the journal a keepsake, turned both letters into family heirlooms in Rellekka and had no King Lathas chapter at all. Erin's key, Dron's fourteen questions and Melina's sapphire amulet were all missing; Priest in Peril and The Restless Ghost were checked nowhere; the 750 coins were missing and there was invented Smithing XP; and six of twelve coordinate constants were arithmetic errors |
| 56 | Spirits of the Elid | 50/50 | **four of its own items were wired to nothing** - two torn robes, the Ballad of Jareesh, Awusah's shoes and Awusah's soles, which are the needle-and-thread step, the shrine door's second condition and the genie's price. The cupboard handed out finished robes and the genie gave the statuette away for a kind word. All three golems had a level, an Attack op and no statblock, and the door walked you straight past a guardian that was still standing; 1,000 Magic XP was missing from the reward |
| 57 | Elemental Workshop I | 58/58 | **nothing wrong with the quest** - the first one in the pass that was already right end to end, bits and all. Both findings were in the runner: a `go` step that lands within two tiles said nothing about it, so "walk to 2715,3481 ok" meant a player standing outside a shut door and the bookcase took the blame; and the loc step spent drive()'s whole 600-tick guard on a fight an immune sim player and an aggressive npc cannot finish, outliving the 500-tick elemental it had just woken, three runs running |
| 58 | Rum Deal | 116/116 | **the fifth quest in this pass that was a different quest** - the holy wrench repaired the vat's tap instead of exorcising the controls, the level-150 Evil Spirit was two mesboxes and ~damage_self, the sluglings were bought off Captain Donnie as though he were a bait merchant, the output tap produced nothing, Donnie never drank the rum or named Rabid Jack, the six Zombie Protesters and eight Brewers had no handler, and the reward was Cooking and Slayer XP and Slayer gloves the Slayer shop sells for fifty points. Three multilocs the old version never touched said what the quest is |
| 59 | Dwarf Cannon | 71/71 | **nothing wrong with it**, and deliberately so: the quest was reworked on 13 June 2006 and this server's map, npcs and cache are the older ones, so the cannon is repaired through its Inspect menu - pipe, barrel, axle, shaft - rather than the three-tool minigame the modern wiki describes. broken_multicannon carries op1=Inspect and nothing else and there is no safety switch, spring or gear anywhere in the cache, so the earlier session that built it from RSC replays was right. The only work was the manifest: Lawgof's camp is a 1294-tile pocket behind a double gate that shuts itself, and both that gate and the cannon shed's door have to be reopened on every crossing |
| 60 | Dream Mentor | 86/86 | **two separate reasons it could not be played**. The Lunar Isle mine ladder carries forceapproach=west, the engine rotates that by the placement angle, and the entrance is placed at angle 2 - so the one legal side became the east, which is the one side with a wall on it. It refused a click from all twenty-four tiles within two. And ~dm_cyrisus_says used ~chatnpc, which suspends the script that calls it: that script is the one which counts each fear off and spawns the next, so The Everlasting did not appear until a chat window had been read in the middle of a fight with a level 343 monster. The Inadequacy's spawn tile also did not fit its 5x5 footprint |
| 61 | Gertrude's Cat | 41/41 | **Gertrude would only talk about rats**. Rat Catchers hooks her conversation through ~ratcatch_gertrude_wants and that returned true whenever Rat Catchers had not been started, which is every player who has never done it - so the quest that starts with her could not begin. That hook came out of this pass's own Rat Catchers rebuild, so it is a regression this audit put in and this audit caught. Also [label,fluffs_boy_single], the haggle for when you find only one of the two boys, was never jumped to by anything: Shilop and Wilough wander Varrock square separately, so most of the time there was no menu and no way to pay |
| 62 | Swan Song | 104/104 | **two reasons it could not be finished and one that it could not be started**. Herman Caranos was spawned on 2354,3683, a blocked tile inside the colony office, and the engine answered "I can't reach that!" from every clear tile around the building - so the three conversations that start the battle, report the queen and finish the quest were all unreachable from stage 90 on. The Sea Troll Queen was a paragraph: level 170, an Attack op, her own five animations, no statblock, and two mesboxes of ~damage_self in place of a fight. And the start checked none of its requirements - 100 quest points, One Small Favour, Garden of Tranquillity. 10,000 Prayer XP and 25,000 coins were missing from the reward, the Magic was 10,000 rather than 15,000, and the book wanted five bones not seven |
| 63 | Garden of Tranquillity | 86/86 | **nothing wrong with the quest**; all the work was in the walk. The nine beds are 1x1 locs in 2x2 blocks with hedges between them, and hedge edges do not show in a walkability grid - the pink rose bed has a clear tile either side of it in the same row and no route between them. A watering costs a dose and the can changes its obj name with it, so the ninth bed cannot be watered out of watering_can_8. The Ring of Charos half of the wiki's version is not buildable: the ring is enchanted by the Wise Old Man, who is placed nowhere on this server |
| 64 | The Golem | 65/65 | **the display cabinet key was unobtainable**. The curator's pickpocket was guarded by `%golem_a > ^golem_finished_b`, and that stage is exactly where the player stands when they need the key - Elissa names the museum and sets it, and the only stage above it is the one that wants the statuette already in hand. So the statuette never left Display Case 30 and the quest stopped three steps from the end. Also: the strange implement opens the golem's skull and the skull shut itself ten ticks later, which is six seconds to find the program in your inventory - it now shuts when the instructions go in |
| 65 | Cabin Fever | 81/81 | **both lockers on the battle ship were sealed**. Each one had an open model, a Search op and a Close op, and nothing anywhere swapped them in - `[oploc1]` handed the planks and the ramrod out through a closed lid and the lid never moved, so half the ops in the quest's own .loc were dead content. Also: Bill Teach signed on anyone who had finished Rum Deal, when the scroll wants Pirate's Treasure and four levels as well - and none of the five is optional once you are two hours out to sea - and the completion paid 7,000 Fishing, in a quest with no fishing in it, and none of the 10,000 coins |
| 66 | Troll Romance | 63/63 | **nothing wrong with it**. The first quest in a long run of these that needed no content fix at all: both sled rides, the ice troll cave, the crevasse, the plateau, the crash into the rocks and the tunnels out to Rellekka's side all play as the wiki and Sal's Realm describe them, and its own source comments say where each beat came from. The one thing worth proving was the arena - a 614-tile pocket whose only way out on foot is its own doors, which stay shut until Troll Stronghold is done. Troll Romance requires Troll Stronghold, so they open; the manifest walks out through them rather than assuming it |
| 67 | Mountain Daughter | 123/123 | **it was a different quest**. Not wrong in detail - wrong in the plot. Svidi was Hamal's daughter, Asleif was his dead wife, the quest opened by fetching three white pearls as a favour, her body was dug out of the roots by the mud pond with a spade, the Kendal was gated behind the burial, the half of the Ancient Rock went on top of the cairn, and the Shining pool answered "it bubbles, and smells of eggs". The cache said otherwise in its own words - the necklace belonged to "Asleif, DAUGHTER of the mountain camp chieftain", the 38 lake bubbles are a Shining pool with faint singing in it, the fruit's param is next_obj_stage,white_pearl_seed, the guarantee "grants Svidi safe passage", and mud_var / relations_var / food_var / brundt_done / bear_discovery / bear_mayattack were all unused. Rebuilt whole: the rope on the boulder, the mud on the tree, the plank on the stones, the pool's two errands in either order, the man in the bearskin, the necklace off Ragnar her fiance, and five rocks off the goat pen. The reward was also back to front - 2,000 Prayer and 1,000 Attack, not the reverse |
| 68 | Creature of Fenkenstrain | 75/75 | **the reward did not exist, and it broke another quest**. `ring_of_charos` is obj 4202, sitting in the middle of this quest's own obj block (4183-4204), and the quest handed out no ring at all - so Garden of Tranquillity's Ring of Charos leg was unreachable and the Wise Old Man had been waiting to enchant a ring nobody could own. The cache also carries `op3=Pickpocket` on the doctor's own model (the ending, unhandled), a `fenk_fireplace` with no ops flanked by two "Mmm.. scented candles" surrounds (where the conductor mould is, and why the wiki says sweep the centre not the mantelpiece), and `fenk_needle`/`fenk_threads_given` - the needle and five thread are handed to the DOCTOR, who cannot sew and says so. Before this the doctor handed over the brain, the cavern key and the mould, the amulet halves came off a bench and a ghost, the head was in a coffin, the brush hooked the shed key off a ledge from inside the shed it opens, and the quest ended with a journal and an argument. Rebuilt; `fenk_signpost` placed in Canifis for the first time |
| 70 | Temple of Ikov | 86/86 | **four separate things, any one of which made it unfinishable**. (1) The boots of lightness: two objs in the cache, 12oz pocketed and -10lb worn, and nothing referenced either - so the lava bridge, which refuses anybody not already weightless, could not be crossed. (2) The bridge trigger fired `inzone` on the lava gap itself, which no route-finder will enter (591 tiles east, 11 west, never touching); moved onto the two lips. (3) `~lucien_attack` gated the Armadyl ending on `map_members`, and Lucien's house is free-to-play ground, so that branch could never be true. (4) The Staff of Armadyl was spawned on the table's own blocked tile, so Take was refused for ever and the Lucien ending was shut too. Also completed: the cellar trapdoor south of the Ranging Guild, and `[ai_queue3,ikov_lucien2]` read a player varp and `npc_findhero` in one `&`. Walked by the Lucien ending; the Guardians' side goes as far as their pendant and is blocked at the last blow by `npc_findhero` coming back false |
| 71 | Biohazard | 81/81 | **no content fixes at all** - the quest is correct from Elena's distillator to King Lathas admitting the plague is a hoax. What it needed was tiles: the watchtower fence is a WALL loc in nine sections and the only clear tile that reaches any of them is the inside corner at 2563,3301, which is exactly the guide's "stand in the corner where the two spiked fences meet"; the mourners' stew yard is a 69-tile pocket joined to West Ardougne by one Squeeze-through fence at 2541,3331; the quarters have two doors and only the southern one reaches the street; and the nurse's cupboard takes a click from 2517,3275 and nowhere else |
| 72 | Observatory Quest | 49/49 | **no content fixes.** The professor, the three parts, the key chest, the kitchen gate, the lens casting, all twelve constellations with their twelve payouts, the assistant's wine and the Spirit of Scorpius's unholy mould all work. Two things the walk had to learn: the goblin guard must be dealt with BEFORE the gate, because opening it leaves an inviswall in the doorway and teleports you through, sealing him out for good (that is the guide's "or trap him"); and the constellation dialogue is a queue the telescope's own click started, which cannot run while the telescope interface is open - `canAccess()` gates `processQueue` on `busy()`. questrun gained a `close` step for it |
| 73 | Troll Stronghold | 28/28 | **no quest fixes.** Denulth's account, Dad yielding at twenty hitpoints instead of dying, the Troll General's prison key, both sleeping guards' pockets, both cell doors and Dunstan's law talisman all work. The one thing the walk needed: the three Troll Generals live in their own 336-tile half of the cave and the ONLY join is `troll_stronghold_interior_door` at 2838,10057 - a `door_closed`, handled generically, named by no script in the quest folder. Fixed in passing: Eadgar's cell door never said a key was wrong, because both arms of the use-on tested the same key |
| 74 | The Lost Tribe | 52/52 | **no content fixes** - the September rewrite holds end to end. Three map facts the walk needed: the Varrock palace library is a sealed 42-tile room whose north side is a map wall with no door loc, so a jump has to land inside; the west-wall bookcases are a solid column at x 3207, z 3495-3497, leaving 3208,3496 as the only tile touching the northernmost one; and Lumbridge castle's first-floor rooms do not join each other, so reaching Sigmund's chest from Sigmund means leaving his room and going back in. The goblin maze walks fine on a shortest path - every trap is in a dead end |
| 75 | Plague City | 75/75 | **two things, each of which stopped the quest dead.** (1) The picture of Elena was spawned on the round table's own tile at 2576,3334, and a ground obj can only be taken by standing on its tile - so Take was refused for ever, and that picture is the only thing in the whole of the content that makes Jethick recognise her. (2) The clerk looked for Bravek within seven tiles of the PLAYER, and that line is the only way out of ^quest_elena_spoke_to_plague_house: Bravek wanders the room behind a fifty-two tile office, so from the north end he never answered and the stage never advanced. Widened to sixteen |
| 76 | Hazeel Cult | 27/27 + 47/47 | **walked on BOTH sides** - the first quest in the pass where two endings are each proven rather than one standing in for the other. Ceril's side ends with the butler arrested after the cupboard search; Hazeel's with a Mahjarrat out of his coffin. The valve answer misleads: the valve the guide calls Valve 1, "north of the cave", is the cache's sewervalve3 at 2585,3245, and it is the only one turned LEFT - the content has it right. One content fix: the Carnillean cellar ladder (generic loc_1754, player tile + 6400) landed anyone approaching from the east at 2571,9667, which is solid rock with nothing adjacent to walk to |
| 77 | Family Crest | 76/76 | **no content fixes.** Caleb's five cooked fish, the gem trader's yellow cape, Avan's perfect gold, Boot, the three-lever door puzzle under Witchaven, the perfect gold rocks, smelting and casting the ring and necklace, Johnathon's poison, Chronozon refusing to die until every one of the four Blast spells has hit him, and the gauntlets. The lever order: N up, south room, S up, out, N down, north room, R up, out, N up, south room, S down, out. questrun gained a `cast` step (a named spell at a named npc, judged on whether it LANDED) and `slot` on `press` (the jewellery panel's rows are one inv each) |
| 78 | Zogre Flesh Eaters | 73/73 | **two things, and the second sealed the end of the quest off.** (1) Both sets of ogre stone doors in the burial tomb teleported the player up to the Jiggig surface, and they are the way IN - flood-filled on plane 2 of m38_147, the tomb is 2077 tiles, the passage behind the first pair is 44, the corridor behind the second is 123, and the three touch nowhere else, so the ceremonial chamber was unreachable. (2) Slash Bash was spawned at 2_38_147_8_50 - the tomb, one tile from the coffin landing - while the chamber is the LEVEL 0 plane of the same square, so the boss appeared behind the player at the tomb entrance and the chamber was empty. Also: questrun gained a `useObj` step, because the potion goes into a cup standing on Sithik's drawers and nothing else reached OPOBJU |
| 79 | Ghosts Ahoy | 168/168 | **no content fixes** - the 13 October rebuild holds end to end. The manifest was already written and already good (both energy barriers crossed from the right side, all four ahoy_harbour_door placements opened, the whole town on foot); what stopped it was a questrun bug, and it is the one the runner's own comments had blamed twice for eating Rune-Draw: the talk step's retry loop handed drive() the manifest's OWN picks array, and drive() shifts options off it, so every retry met the same menu with nothing to answer. A copy per attempt, and the quest walks |
| 80 | The Feud | 146/146 | **nothing** - the manifest was already written and passes. Its tracker row had never been updated |
| 81 | Monkey Madness | 144/144 | **nothing** - the manifest was already written and passes, all the way to Narnode. Its row said PARTIAL from an audit sweep that only reached Marim's gate |
| 82 | Enakhra's Lament | 86/86 | **the quest in the content was not the quest.** Built from the varbit names, it had the player carve the statue and walk out; the cache says otherwise - Enakhra's temple is sealed by four sigil doors, the obj descs name the four pieces of the shrine, and Akthanakos is the one who has to be freed. Rebuilt from the cache's own spawns and placements, and the sigil door's own tile is the only approach to it |
| 83 | Fight Arena | 34/34 | **no content fixes.** The uniform out of the chest, the Khali brew, the drunk guard's keys, Jeremy's cell, then the ogre, the scorpion, Bouncer and Khazard himself. One harness finding: `fight`'s `untilvar` compares with `===`, so a chained stage advance (9 to 10 to 11 in one death) overshoots the target and the step spins - the scorpion and Bouncer are one step with a type array and `to: 11` |
| 84 | Murder Mystery | 33/33 | **the fingerprints could never be lifted.** `[opheldu,_murder_flourobj]` read its two halves the wrong way round: in an opheldu script `last_item` is the half that carried the trigger, so the category script was testing the half it was already holding. The step before it worked by luck, through the decline path. Also walked: the flypaper, the dagger, the window thread, the barrel silver, the poison salesman and the compost heap, with the culprit pinned to Anna |
| 85 | Recruitment Drive | 69/69 | **no content fixes** - and the walk sits all SEVEN tests rather than the five a run draws, by clearing the completion bits after the draw. The bridge, the twelve statues, Sir Leye unarmed (a blade fails the room), Sir Tinley's thirteen ticks of not clicking anything, the acrostic, Miss Cheevers' lab and the logic riddle. No teleports between rooms: each exit door sends the player on. Two stale comments claiming rooms 1 and 6 "are not built yet" were corrected |

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

**85 quests and miniquests walked** of the 104 on the list, plus two miniquests: all eighteen free
quests and sixty-five of the eighty-six members' quests. Twenty-one members' quests to go. Every one has a file in `Engine-TS/tools/sim/` that plays it and passes every check;
rerun any of them with `npx tsx tools/sim/<name>.ts`.

**One flag to know about:** `NODE_MEMBERS=true` is commented out in `Engine-TS/.env`, so a sim boots
a FREE-TO-PLAY world and every `map_members` branch in content takes the other path. Members content
needs `NODE_MEMBERS=true npx tsx tools/sim/<name>.ts` — Holy Grail's whistle door spawns no whistles
without it, which reads as a broken obj spawn rather than a world flag.

**THE RUNNER HAD A SILENT FALSE PASS IN IT, found on 20 October.** The `loc` step has always judged
itself on what the handler said; `useLoc` never did - it reported ok on arrival alone and threw
`want` away, so every useLoc assertion in every manifest written before this was decoration. Rat
Catchers' King rat passed `want: 'size of a terrier'` three runs in a row while the handler it came
from was not running at all. It is fixed, and the two Myreque manifests - the most recent ones with
useLoc wants in them - were re-run against the stricter version and are still 41/41 and 81/81. The
older manifests have not been re-run and should be, one at a time, as the pass goes back over them.

### The runner's own vocabulary, as it stands

**`hop` on the loc and useLoc steps** (new, 21 Oct): for an op that teleports the player a few
tiles. `arrive()` passes as soon as the player has stood next to the loc at any point, which
covers everything you walk up to - but an approach op on a loc standing in water, clicked from
three tiles off and answered with a teleport to the far side, can never satisfy it. With `hop`
the step is judged on what the op said plus an exact walk after it, which is stronger anyway:
the tile it lands you on is one no route from this side can reach.
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

### What the Experiment cavern would need
**Creature of Fenkenstrain's cavern is not built**, and it is a map problem rather than a content
one. The cache has all of it - `fenk_experiment_1` is level 51 with "It has a key hanging from its
collar", `fenk_mausoleum_key` is called "Cavern key", the Experiments are spawned across two
underground squares and a locked mausoleum door and a chest stand among them - but the 377 map has
no way in and no way out: no memorial over the cave, no gate, no ladder. So the arms, legs and torso
come from the railed plot north-west of the castle, which the map does support in full, and the
cavern key stays unused. Building the cavern leg means inventing an entrance and an exit teleport
pair, which is a bigger invention than leaving it out.

### The Wise Old Man, and the one beat Swan Song still cannot build
**THE WISE OLD MAN IS PLACED NOW** (3088,3251, Draynor), on the owner's instruction, and the two
quests that had been written around his absence have their missing legs:
- **Garden of Tranquillity** unlocks the Ring of Charos through him - seven diplomacy questions, six
  of them right, on the scenarios the wiki's transcript gives. 88/88.
- **Swan Song** stops folding its own step. The letter goes out, you fetch him from Draynor with ten
  mist runes, ten lava and five blood, and he takes the morning boat himself. 109/109.

Npc 2253 was in the cache all along with a full model set, a walking stick, a head and op1=Talk-to,
and was spawned in no map square at all. **When a quest leg looks unbuildable because its npc "does
not exist", check whether it exists and is merely unplaced** - that is a jm2 line, not missing
content. What remains genuinely unbuildable in Swan Song is only the other beat:
- **the army chain** (Wizard Frumscone, then Malignius Mortifer, a brown apron, an airtight pot and
  the Crafting Guild pottery). Malignius does not exist in this cache at all, and neither does the
  airtight pot or a bone-seed pot. Arnold handing over the book and the packet out of the Wise Old
  Man's hand is as close as the cache allows.

### What is left
Everything still marked NOT AUDITED or AUDITED in the tables above - **twenty-one** of them, all
in the members' table, counting both NOT AUDITED and AUDITED (an AUDITED row was driven by one of
the audit sweeps but never walked end to end). By size, the smallest left are: Regicide (1210),
Animal Magnetism (1333), Nature Spirit (1373), Eagles' Peak (1386), Mourning's End
Part 1 (1388), The Grand Tree (1615), Death Plateau (1666), Horror from the Deep (1858),
Big Chompy Bird Hunting (1936), Lunar Diplomacy (1971), Watch Tower (2124), Shilo Village (2171). The
genuinely long ones - Legends Quest
(5847), The Fremennik Trials (3383), The Tourist Trap (3120), Recipe for Disaster (3022), Throne of
Miscellania (2729), Digsite (2647), Mourning's End Part 2 (2573), Underground Pass (2442), Desert
Treasure (2288) - are best taken one at a time with a fresh context.

### The re-run sweep, 22 Oct
**Twenty-one manifests re-run after this session's content changes, all green.** The one that
mattered was `scripts/player/scripts/equip.rs2`: the boots-of-lightness swap-back goes in
`[proc,on_unequip]`, which every unequip in the game funnels through, so the sweep deliberately
included quests that wear things.

  quest_garden 88/88 · quest_swansong 109/109 · quest_golem 65/65 · quest_fever 81/81 ·
  quest_mdaughter 123/123 · quest_fenkenstrain 75/75 · quest_handsand 53/53 · quest_deal 116/116 ·
  quest_dreammentor 86/86 · quest_fluffs 41/41 · quest_ratcatch 73/73 · quest_elemental 58/58 ·
  quest_mcannon 71/71 · quest_troll_love 63/63 · quest_cook 23/23 · quest_sheep 11/11 ·
  quest_vampire 20/20 · quest_doric 9/9 · quest_imp 7/7 · quest_prince 38/38 ·
  quest_restlessghost 28/28 · quest_romeojuliet 36/36

That is the oldest eight and the newest thirteen; the middle of the list is still to sweep, and it
is cheap - one line each, about a minute a manifest.

### Biohazard: scanned clean, and that is worth saying
First of the next batch, and the unused-cache scan came back with **nothing** - every `bio*` obj is
referenced by the quest, and the two locs the scan flagged are both fine: `biohazarddummy` is
scenery, and `bionursescupboardshut` (the hospital cupboard the doctor's gown is in) carries
`category=cupboard_closed` and `param=cupboard_other`, so the generic `[oploc1,_cupboard_closed]` in
general_use/scripts/cupboards.rs2 opens it. **A loc the quest folder never names is not an unhandled
loc** - check the category before believing the scan.

The stage spine also matches the real quest beat for beat: started, Jerico, the birdfeed, the
pigeons released, the ladder, the stew poisoned, the distillator found and given, the chemist, the
secret, reported to Elena. Seven npc files cover Jerico, the chemist, Guidor, Guidor's wife and all
three of Hops, Chancy and Da Vinci.

So Biohazard looks like one of the built ones rather than one of the invented ones, and what it
needs is a walk: Elena in West Ardougne, Jerico's cupboard and cage, the mourner HQ ladder, the
stew, the distillator, the gown out of the hospital cupboard, one of the three smugglers, Guidor in
Varrock and back. That is where the next session starts.

### Temple of Ikov: done, and it took four fixes
**86 of 86 by the Lucien ending.** Four separate faults, any one of which made the quest
unfinishable, and all four were invisible to reading the scripts:

1. **The boots of lightness.** Two objs in the cache - 12oz pocketed, **-10lb worn** - and nothing
   referenced either, so wearing them did nothing and the lava bridge (which refuses anybody not
   already weightless) could not be crossed. The boots, a knife and the web over them were all
   already in the map; only the swap was missing.
2. **The bridge trigger fired on the lava gap itself** (2648-2650 x 9828-9829), which no
   route-finder will enter: 591 tiles east, 11 west, never touching, no loc on the boundary. Moved
   onto the two lips, where the crossing already worked from.
3. **`~lucien_attack` gated the Armadyl ending on `map_members`**, and Lucien's house is between
   Edgeville and the Grand Exchange - free-to-play ground - so that branch could never be true.
4. **The Staff of Armadyl was spawned on the table's own blocked tile**, and a ground obj can only
   be taken by standing on it, so Take was refused for ever and the Lucien ending was shut as well.
   Moved one tile north, against the table.

Also completed on the way: the cellar trapdoor south of the Ranging Guild (`ikov_trapdoor_down` had
no handler while the ladder below it climbed out), and `[ai_queue3,ikov_lucien2]`, which read a
player varp and `npc_findhero` in a single `&` - both sides of which are read before either is
acted on, so the varp read happened with no active player.

**One thing is still open**: the Guardians' ending. It walks as far as their pendant and then Lucien
dies without the completion firing, because `npc_findhero` comes back false for him. The two endings
are exclusive and the Lucien one is equally canonical, so the quest is walked by that side; if
`npc_findhero` is ever chased down, the Armadyl branch is three steps from working too.

Three things the walk itself needed, all worth remembering: **twenty ice arrows, not one** (the
chest gives one to five a search and re-randomises which chest is loaded, so with the rng pinned it
is the same chest twenty times - one arrow was why the Fire Warrior looked unkillable); **twelve
ticks for a summoned npc to settle** before the fight step looks at him; and **wear something else
in the same slot** when a worn item has to come off, because nothing in the harness unequips.

### The Wise Old Man, and the one beat Swan Song still cannot build
**THE WISE OLD MAN IS PLACED NOW** (3088,3251, Draynor), on the owner's instruction, and the two
quests that had been written around his absence have their missing legs:
- **Garden of Tranquillity** unlocks the Ring of Charos through him - seven diplomacy questions, six
  of them right, on the scenarios the wiki's transcript gives. 88/88.
- **Swan Song** stops folding its own step. The letter goes out, you fetch him from Draynor with ten
  mist runes, ten lava and five blood, and he takes the morning boat himself. 109/109.

Npc 2253 was in the cache all along with a full model set, a walking stick, a head and op1=Talk-to,
and was spawned in no map square at all. **When a quest leg looks unbuildable because its npc "does
not exist", check whether it exists and is merely unplaced** - that is a jm2 line, not missing
content. What remains genuinely unbuildable in Swan Song is only the other beat:
- **the army chain** (Wizard Frumscone, then Malignius Mortifer, a brown apron, an airtight pot and
  the Crafting Guild pottery). Malignius does not exist in this cache at all, and neither does the
  airtight pot or a bone-seed pot. Arnold handing over the book and the packet out of the Wise Old
  Man's hand is as close as the cache allows.

### What is left
Everything still marked NOT AUDITED or AUDITED in the tables above - **twenty-one** of them, all
in the members' table, counting both NOT AUDITED and AUDITED (an AUDITED row was driven by one of
the audit sweeps but never walked end to end). By size, the smallest left are: Regicide (1210),
Animal Magnetism (1333), Nature Spirit (1373), Eagles' Peak (1386), Mourning's End
Part 1 (1388), The Grand Tree (1615), Death Plateau (1666), Horror from the Deep (1858),
Big Chompy Bird Hunting (1936), Lunar Diplomacy (1971), Watch Tower (2124), Shilo Village (2171). The
genuinely long ones - Legends Quest
(5847), The Fremennik Trials (3383), The Tourist Trap (3120), Recipe for Disaster (3022), Throne of
Miscellania (2729), Digsite (2647), Mourning's End Part 2 (2573), Underground Pass (2442), Desert
Treasure (2288) - are best taken one at a time with a fresh context.

### The re-run sweep, 22 Oct
**Twenty-one manifests re-run after this session's content changes, all green.** The one that
mattered was `scripts/player/scripts/equip.rs2`: the boots-of-lightness swap-back goes in
`[proc,on_unequip]`, which every unequip in the game funnels through, so the sweep deliberately
included quests that wear things.

  quest_garden 88/88 · quest_swansong 109/109 · quest_golem 65/65 · quest_fever 81/81 ·
  quest_mdaughter 123/123 · quest_fenkenstrain 75/75 · quest_handsand 53/53 · quest_deal 116/116 ·
  quest_dreammentor 86/86 · quest_fluffs 41/41 · quest_ratcatch 73/73 · quest_elemental 58/58 ·
  quest_mcannon 71/71 · quest_troll_love 63/63 · quest_cook 23/23 · quest_sheep 11/11 ·
  quest_vampire 20/20 · quest_doric 9/9 · quest_imp 7/7 · quest_prince 38/38 ·
  quest_restlessghost 28/28 · quest_romeojuliet 36/36

That is the oldest eight and the newest thirteen; the middle of the list is still to sweep, and it
is cheap - one line each, about a minute a manifest.

### Biohazard: scanned clean, and that is worth saying
First of the next batch, and the unused-cache scan came back with **nothing** - every `bio*` obj is
referenced by the quest, and the two locs the scan flagged are both fine: `biohazarddummy` is
scenery, and `bionursescupboardshut` (the hospital cupboard the doctor's gown is in) carries
`category=cupboard_closed` and `param=cupboard_other`, so the generic `[oploc1,_cupboard_closed]` in
general_use/scripts/cupboards.rs2 opens it. **A loc the quest folder never names is not an unhandled
loc** - check the category before believing the scan.

The stage spine also matches the real quest beat for beat: started, Jerico, the birdfeed, the
pigeons released, the ladder, the stew poisoned, the distillator found and given, the chemist, the
secret, reported to Elena. Seven npc files cover Jerico, the chemist, Guidor, Guidor's wife and all
three of Hops, Chancy and Da Vinci.

So Biohazard looks like one of the built ones rather than one of the invented ones, and what it
needs is a walk: Elena in West Ardougne, Jerico's cupboard and cage, the mourner HQ ladder, the
stew, the distillator, the gown out of the hospital cupboard, one of the three smugglers, Guidor in
Varrock and back. That is where the next session starts.

### Temple of Ikov: two things, either of which made it unfinishable
The unused-thing scan found it in one pass: `ikov_bootsoflightness` and `ikov_bootsoflightnessworn`
were referenced nowhere in the quest. They differ only in weight - 12oz pocketed, **-10lb worn** -
and the lava bridge refuses anybody whose weight is not already negative, so **the bridge could not
be crossed and the quest could not be finished**. Both the boots and a knife and the slashable web
over them were already in the map; only the swap was missing. It is in now, on the way on
(`[opheld2,ikov_bootsoflightness]`) and on the way off (`[proc,on_unequip]`, the hook the greegrees
use), and measured at 340g pocketed against -4,535g worn.

**And the bridge fired on tiles nobody can stand on.** The crossing is a per-tick timer testing
`inzone(2648,9828 .. 2650,9829)` - the lava gap itself. `joinpocket` from either side: 591 tiles
east, 11 tiles west, never touching, and no loc on the boundary; the route-finder refuses the one
step from 2651,9828 to 2650,9828. So the trigger could never fire, the lever across the gap was
unobtainable, the bracket had nothing to take, the south room never opened, there were no ice
arrows, and the Fire Warrior - who takes damage from nothing else - could not be hurt. The crossing
itself already worked from either lip, so the zone moved onto the lips (2647 and 2651) and the gap
constants stay, because the forcemove is still measured from them.

Also completed: `ikov_trapdoor_down` (2637,3408) had no handler while the ladder at the bottom of it
climbs back out - a one-way pair. That is the cellar of crates south of the Ranging Guild, NOT the
temple: the temple's own entrance is `loc_1754` at 2677,3405 and is handled generically.

**The walk is WIP at 52 of 53, as far as the Fire Warrior of Lesarkus arriving.** Proven: Lucien's
interview, the temple ladder (`loc_1754` at 2677,3405), the dark stairs, the web, the boots and
their swap, the pendant, the gate of fear, the lava gap, the double door at the end of the far ledge
(`loc_1516`/`loc_1519` at 2645,9828-9), the lever off the floor, the bracket (a shape-7 wall fitting
- east or north of it, never west), the mended lever, the south gate, an ice arrow out of the right
chest (forceapproach 14 leaves only its south side), both gates re-opened on the way back, the
trapped lever searched and pulled, and the door it unbolts.

**The walk is at 85 of 86 - everything but the last blow.** The Fire Warrior was never unkillable:
the run was carrying ONE ice arrow. The chest gives one to five a search and re-randomises which
chest is loaded, so with the rng pinned the run searches the same one twenty times and he dies in 77
ticks. After him: Winelda's twenty limpwurt roots and the Guardians' pendant.

Two things the walk turned up on the way:
- **The Guardians really do refuse to talk to a player wearing Lucien's pendant**, which is the
  wiki's warning and is implemented. There is no harness call for unequipping, so the pendant comes
  off the way the engine takes it off: **wear something else in the same slot** and `~try_equip`
  pops the old one into the pack. Worth remembering for any quest that needs a worn item removed.
- **Lucien dies four times at the end and the stage stays at 70.** `[ai_queue3,ikov_lucien2]` only
  queues the completion when `npc_findhero = true & %ikov = ^ikov_helping_armadyl`. The stage is 70,
  so `npc_findhero` is coming back false and he falls through to an ordinary death instead. Whether
  that is the damage tracking, `~lucien_attack`'s `map_members` check in a free-to-play Edgeville, or
  the harness, is the ONE thing left on this quest - and it is the next thing to look at.

Two things that cannot be exercised by a sim player at all, both worth knowing for other quests:
the lava crossing (its timer reads `weight`, and nothing calls `calculateRunWeight()` outside
NetworkPlayer, so a sim player always weighs zero and would be thrown in), and anything else that
reads weight. Probes that need it must call `calculateRunWeight()` themselves, as
`tools/sim/ikovboots.ts` does.

**Watch for files going missing.** Part way through this session `maps/ignore.csv` and
`scripts/areas/area_lumbridge/scripts/man.rs2` showed up deleted in the content worktree, with
nothing in this session having touched either. rs2check caught it: the script count fell from 2069
to 2068. Both were restored with `git checkout --` before committing. **Check `git status` for `D`
lines before every commit** - the count in rs2check's last line is a cheap canary.

**THREE REBUILDS IN A ROW, AND THE SAME TELL EACH TIME: AN UNUSED THING IN THE CACHE.** Mountain
Daughter had six varbits nothing read. Creature of Fenkenstrain had `op3=Pickpocket` on the doctor's
own model and a reward obj sitting in its own id block. The Hand in the Sand had a multiloc state
describing a vial on Betty's counter, a pocketful of sand with no use, and an npc called Mazion
standing on the Entrana sand heap for one line of flavour. **The unused thing is the missing step.**
Grep every name in a quest's configs for a reader before reading the scripts, because the scripts
will read as finished either way.

**A QUEST CAN BE WRONG IN THE PLOT AND STILL LOOK FINISHED.** Mountain Daughter had 822 lines, a
journal with a line for every stage, source comments, and a completion scroll - and it was a
different story from the one the quest tells. The cache is what settles it, and it settles it in
plain English: an obj's `desc` names who the necklace belonged to, a loc's `name` says the pool is a
Shining pool with singing in it rather than sulphur gas, a `param=next_obj_stage` says eating the
fruit leaves a seed, and **a varbit nothing reads is a step nobody built** - mud_var, relations_var,
food_var, brundt_done, bear_discovery and bear_mayattack were all unused, and all six are beats of
the real quest. Before touching the scripts, read every `name=` and `desc=` in the quest's own
configs and grep each varbit for a reader.

**A TELEPORT INTO A FIGHT IS A QUESTION ABOUT GETTING OUT AGAIN.** Troll Romance's duel teleports
both of you into the Troll Arena, which floods to 614 tiles and touches nothing else on foot: the
only way out is its own doors, and those stay shut until Troll Stronghold is done. It is, because
Troll Romance requires it - but that is an argument, not a check, and the manifest walks out through
the doors instead. **Whenever a script teleports the player somewhere to fight, flood that
destination and find the exit before calling the quest finished.**

**AN OP ON A LOC NOTHING EVER PLACES IS A DEAD OP, AND IT READS AS FINISHED CONTENT.** Cabin Fever's
two lockers each had a second loc - open model, Search, Close - and no `loc_change` anywhere in the
quest to put it on the map. Reading the scripts top to bottom shows a locker that opens and a locker
that searches and nothing looks wrong; the giveaway is that the `_open` name appears only in its own
`[oploc1]` header. **Grep every loc name in a quest's .loc for a `loc_change` to it** - a name with
no writer is either dead or the step that is missing.

**A LOC OFTEN STANDS ON THE BLOCKED TILE, NOT BESIDE IT.** Four of the last five manifests lost a
run to a `go ... exact` aimed at the loc's own coordinate: Uzer's staircase is a 3x3 block of
blocked tiles, the temple stairs sit in an alcove row where only one tile is cardinally beside them,
Swan Song's crawl-hole blocks its own tile and lands you on the next one, and every farming patch in
the palace garden is blocked by definition. `wherelocs.ts` gives the loc's coordinate, which is what
the `at:` wants; the tile to stand on is a separate question and `blockfit.ts` answers it.

**AN NPC ON A BLOCKED TILE IS NOT NECESSARILY REACHABLE, AND beside.ts DOES NOT SAY SO.** It lists
the standable tiles around an npc and the pocket each belongs to, which is a different question from
"will the engine let the op through from there". Herman Caranos had one standable tile beside him and
every tile around his building was refused. When a `talk` step says nothing at all, put a player on
each candidate tile and send the op - five lines of probe - rather than trusting the stand list.

**ONE QUEST'S HOOK INTO ANOTHER QUEST'S NPC IS WORTH CHECKING FROM A BLANK SAVE.** Rat Catchers'
hook on Gertrude fired at `%ratcatch_var = ^ratcatch_not_started` - true for everybody who has not
done it - and silently took over the npc that starts Gertrude's Cat. A `~x_wants` proc that keys on
"not started" claims the npc for ever, and these hooks are now all over the tree (Rat Catchers on
Gertrude and the Apothecary, Making History on Erin and King Lathas, Dream Mentor on Jack and the
Oneiromancer). The pattern to want is "while MY quest is at the step that needs this npc", never
"while my quest has not begun". Walking a quest from a blank save is what finds these, which is the
whole argument for the manifests.

**THREE PROBES NOW ANSWER THE THREE QUESTIONS A FAILED STEP ACTUALLY RAISES**, and all three were
written because the answer was guessed at first:
- `joinpocket.ts` - "NO WALKABLE ROUTE from A to B": floods both tiles and names the loc standing
  where the two pockets touch. The line that names a loc is the door; the lines with no loc on
  either tile are the building's walls, which the loc listing does not return.
- `reachsides.ts` - "the op said nothing": the four neighbours with their wall flags, the rotated
  forceapproach mask, and the engine's own reach test with the mask and without it.
- `blockfit.ts` - "the npc was there and then it was not": where an NxN footprint fits.

**"NO WALKABLE ROUTE" IS USUALLY A DOOR, AND `tools/sim/joinpocket.ts` NAMES IT.** It floods from
both tiles and prints every pair of adjacent tiles where the two pockets touch, with the loc
standing on each - so the answer to "why can the player not get from the camp to the watchtower" is
one line, not an engine boot spent guessing. Three of the last four manifests needed it: the Seers'
house door, Lawgof's double gate, and the cannon shed. All three shut themselves again after a few
hundred ticks, so a crossing made twice needs the click twice, and the second click is `soft`
because the door is sometimes still standing open.

**A MULTILOC TABLE IS THE QUEST'S OWN DESIGN DOCUMENT, AND IT IS IN THE CACHE.** Rum Deal was
rebuilt out of three of them without guessing at anything: a multiloc with no op in any state is
used WITH an item, a lever whose down state says "This lever can't be operated right now." is
counting something, and a cupboard described as "Probably where the farming kit is stored" holds the
rake and the dibber. Read `multivar`/`multiloc` lines and the children's `desc` and `op` before
reading the quest script, not after.

**A LOC TRIGGER CAN MATCH A CATEGORY, NOT ONLY A NAME.** `[oploc1,_door_closed]` is matched by
every loc carrying `category=door_closed`, which is how 882 placements of 61 locs that have no
content name of their own still open and shut. An hour went into "Elemental Workshop I cannot be
started because its house has one door and that door has no handler", and the door was fine. What
questrun cannot do is OPEN one - it walks on canTravel, so a shut door is a wall - and
`~open_door`'s replacement expires after a few hundred ticks, so a room with one way out needs
short steps while you are inside it.

**THE SAME THREE THINGS KEEP COSTING AN ENGINE BOOT EACH**, so they are written down here as well
as in the commits:
1. **An npc with a level, an Attack op and no statblock** is one a script is supposed to spawn, and
   there have now been five of them (the Skeleton Hellhound, Gadderanks, the King rat, and all three
   Elid golems). Give it a statblock before anything else.
2. **A fight is over before the next step runs.** Anything spawned with huntmode aggressive_melee
   inside a conversation is dead a few ticks later against a maxed sim player, so a following `fight`
   step reports it missing while its death trigger has already fired. Assert the varbit, not the
   fight.
3. **A wall-straight door takes a click from exactly two tiles** - the ones it separates - and the
   engine's own approach will happily walk you to a third and then refuse. `tools/sim/opfrom.ts`
   sends the op from every tile within two and prints which ones ran a script.

**FOUR OF THE FIVE QUESTS WALKED ON 20 OCTOBER WERE THE WRONG QUEST**, not a broken one: In Search
of the Myreque, Rat Catchers and Making History were each built from the varbit names or the item
list without anybody checking where the cache puts things, and each came out plausible, playable and
different. In Aid of the Myreque was the right quest and could not be played past its second step.
The lesson for the rest of the pass is to probe the map before reading the implementation: every
clickable loc in the quest's map squares, every npc spawn of its own name prefix, and the obj
descriptions, which in Making History's case named the sender and recipient of both letters.

**In Aid of the Myreque was not the same shape of problem**, which is worth writing down because the
first look at it said it was. Its structure was taken from the cache's own multilocs and it follows
the real walkthrough step for step. What it had instead was a dead switch case two steps in - the
village leader only knew ^m2_sent and you cannot be standing in front of her at ^m2_sent - so the
quest could not be played past Florin's gate, and nothing had ever walked it to find that out.
Invented dialogue is not the tell; a mechanic handed to the wrong character is, and so is a stage
nobody can be standing in when the script that reads it runs.

**Two things in it are still short of the walkthrough and are written down rather than fixed:** the
cellar rubble is cleared after Gadderanks rather than before the repairs (the stages are
self-consistent in that order and reordering them would desync anybody mid-quest), and there is no
silver-weapon requirement on the juvinates, because this build has no vampyre damage rules anywhere
and adding them is a combat subsystem rather than a quest fix. Temple Trekking, which this quest
unlocks, is parked with the non-quest backlog.

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
