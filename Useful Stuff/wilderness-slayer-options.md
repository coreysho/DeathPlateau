# Wilderness Slayer: options for this server

> **Second review, 9 October 2026, and this one changes the answer's cost rather than its
> reasoning.** The Death token, the Undertaker and the one-armed veteran shipped on 8 October, for
> the separate reason that the Wilderness had no currency of its own. Between them they are the half
> of Option C this document called "the real remaining work". **The Undertaker is Larran's chest**,
> and he is better than one, because a shop is a chest you get to choose from. What is left of
> Option C is now almost entirely data.
>
> The objection has moved too, and the new one is sharper than the old. It is no longer *is this
> period* or *is this expensive*. It is **her task table would be thin** — see "The table is the
> real cost" below. Recommendation is unchanged in direction and changed in order: **build the task
> table first, the master second.**
>
> **Reviewed and corrected 8 October 2026.** The original was written before the Slayer reward
> system existed, and its central argument rested on that absence. The facts below are re-measured
> against the tree as it stands today; the four options survive, their costs and their tradeoffs do
> not. What changed, in one line: **this server now runs the whole OSRS points economy, so Krystilia
> would no longer be the first anachronism in the skill — she would be consistent with it.**
> Nothing here has been implemented — this is still a decision document.

## The core tension, restated

"Wilderness Slayer" as most people mean it — Krystilia, a dedicated slayer master in the Edgeville
jail who assigns wilderness-only tasks for points and unique drops — is not 2006 content. She was
released as a plain NPC on 11 July 2013 and only became a functioning slayer master on 13 April 2017,
more than a decade after this server's January 2006 cutoff.

The original framed the decision as *period accuracy versus a knowing break*. That framing is now
weaker, because the break has already been made deliberately and thoroughly:

* the **Slayer reward points economy** — points, streak, tasks completed, four block slots, cancel,
  block, unblock — is 2011 content and is built;
* **superior slayer monsters** and Bigger and Badder are 2015 content and are built;
* the **rewards window** (five tabs: Unlock, Extend, Buy, Tasks, Cosmetics), the **Scroll of
  imbuing**, the **slayer helmet recolours** and the **collection log** are all post-2006 and built;
* so are Zulrah, the Kraken, the God Wars Dungeon, the Dagannoth Kings and Horror from the Deep.

So the question is no longer "does this break the premise". It is plainly a design question: **do you
want a master whose whole point is forcing repeated time-at-risk in a PvP zone?**

## What already exists in this codebase today

Current as of 8 October 2026, measured rather than remembered.

### The five real 2006-era slayer masters

Exactly the classic five: Turael (Burthorpe, no requirement), Mazchna (Canifis, combat 20), Vannaka
(under Edgeville, combat 40), Chaeldar (Zanaris, combat 70), Duradel (Shilo Village, combat 100 + 50
Slayer). A Slayer cape skips every combat requirement. No Krystilia, no Nieve/Steve, no Konar.

Their pools are `configs/slayer_master_tasks.dbrow` (which tasks each master gives) and
`configs/slayer_tasks.dbrow` (weight and kill range per row): **170 rows, 77 distinct tasks**. Every
master also carries a **Rewards right-click** that opens the window directly.

### The reward economy the original said did not exist

It does now, and this is the single biggest correction to the document: 8 unlocks, 11 task
extensions, 4 items to buy, 3 helmet-recolour cosmetics, cancel at 30 points and block at 100, all
spent through one generated window. The original's line — *"no points gate it, which is itself
period-accurate, since OSRS's Slayer Reward Points system didn't launch until 2011"* — is simply no
longer the state of the tree.

### How much of Slayer already happens in the Wilderness

The original said four tasks. Measured against the build's own Wilderness rectangles
(`area_wilderness/configs`, x 2944-3391 z 3520-3967 on the surface, plus the Edgeville dungeon
section), **24 of the 77 tasks have monsters standing inside them**:

| | tasks |
|---|---|
| **Wilderness-defining** (most or all of the monster lives there) | green dragons, red dragons, earth warriors, black demons, black dragons, hellhounds, greater and lesser demons |
| **Also completable there** (the monster lives elsewhere too) | spiders, skeletons, rats, ice warriors, ice giants, hobgoblins, zombies, ghosts, scorpions, wolves, bears, hill giants, moss giants, fire giants, dwarves, bats |

Red dragons joined on 7 October behind the **Seeing Red** unlock (Duradel); four of the build's red
dragons stand in the Wilderness and the rest are in Brimhaven Dungeon. So "wilderness slayer, 2006
flavour" is already a real thing a player can choose to do — considerably more of one than the
original recorded.

### What is NOT in the task pools, corrected

Chaos druids, dark warriors, rogues and highwaymen all exist as npcs with combat behaviour and are
not slayer targets. **Ankou and lava dragons do not exist in this build at all** — no npc config, no
pack id — so wiring them in would be an import job, not a data edit. The original listed them
alongside the others as though they were merely unwired. Revenants and mammoths are correctly absent
as post-2006 content.

### The wilderness substrate

`~wilderness_level(coord)` (one level per 8 tiles, read from two rectangles with an exclusion table
for the underground pockets), the `%wilderness` zone flag, the six-obelisk network, the PK skull
system, a full PvP combat stack, the King Black Dragon, Bandit Camp, the Lava Maze chest. Multi-way
combat comes from the map's own flags rather than from script.

### And a rule that now guards the task tables

`tools/slayer_battery.py` fails unless **every task a master can hand out either has a monster that
counts and is spawned somewhere, or is refused outright**. That rule was written after an audit found
three tasks whose monsters counted for nothing; it is what would keep a sixth master's table honest
from its first commit.

## What the real Wilderness Slayer (Krystilia) actually is

**Who and where.** Krystilia stands in the Edgeville jail, northeast of the bank.

**Requirements.** Level 1 Slayer. She assigns any monster on her list regardless of combat level —
no gating of the Mazchna/Vannaka/Chaeldar/Duradel kind. One task at a time across all masters, so
taking a Turael task cancels a wilderness streak.

**The catch that defines it.** Only kills made while the player is physically in the Wilderness count.
That is the feature: extended, repeated time skulled and visible to anyone hunting slayer-task PKers.

**Points.** Nothing for the first four tasks, then 25 a task, with milestones at the 10th (125), 50th
(375), 100th (625), 250th (875) and 1,000th (1,250). Blocking costs 100. They spend in a dedicated
wilderness rewards shop, separate from the ordinary one.

**Unique drops.** Larran's key (opening Larran's chest, a wilderness-only loot table) and Slayer's
enchantment, rolled on top of each monster's own table. Her list runs to 40+ monsters, several gated
behind quests or Slayer levels up to 85.

## Options

**Option A — Do nothing; it is already there.** Twenty-four tasks can be completed in the Wilderness,
eight of them essentially wilderness-only, and a player chooses when to take that risk. Zero work.
The tradeoff is the same as before: no wilderness *identity* — nothing that reads as a feature.

**Option B — Broaden the five masters' pools.** Chaos druids, dark warriors, rogues and highwaymen
exist and could be wired in; ankou and lava dragons would have to be imported first.

> **A design objection the original did not make, and I would weigh it heavily.** Putting more
> wilderness monsters into the existing masters' tables takes away the player's *choice* to opt into
> risk. OSRS keeps that choice explicit precisely by putting them behind a separate master. With 24
> tasks already completable in the Wilderness by choice, B adds little and can actively annoy — a
> Turael task that forces a trip past level 20 is a worse experience than no task at all.

**Option C — Build Krystilia.** Much cheaper than the original estimated, because the expensive parts
were built for the ordinary masters in the meantime:

| Piece | State |
|---|---|
| the master and her task table | data — `slayer_new_target` switches on the npc and reads a dbrow; a sixth table is rows, and the battery keeps it honest |
| points, streak, milestones | `%slayer_points`, `%slayer_streak`, `%slayer_tasks_done`, `%slayer_task_master` all exist and are saved; her ramp is arithmetic on them |
| "only wilderness kills count" | one condition in `~check_progress_task`, using `~wilderness_level(coord)`, which exists |
| the rewards window / shop | generated from enums; a tab or a second row set is data plus a regenerate |
| **Larran's key and chest, Slayer's enchantment** | **the real remaining work**: new items, a loot table and a chest |

**Option D — A custom wilderness bounty system.** Same loop, built as this server's own thing rather
than a recreation: a bonus on tasks already assignable when they are completed at risk, say. Less
work than C and no claim to authenticity, but it is a design commitment rather than a port.

## The table is the real cost (added 9 October 2026)

Everything mechanical about a sixth master is small, and measured rather than estimated:

| Piece | What it actually is |
|---|---|
| the master | one `case` in `slayer_new_target`'s `switch_npc`, which has five today |
| her task table | one `slayer_task_table` dbrow plus one `slayer_master_task` row per task |
| her points | one `case` in `slayer_task_points`'s `switch_int`; streak, milestones and `%slayer_task_master` already work for whoever assigned |
| wilderness kills only | one condition in `[queue,progress_task]` — **beside `~death_token_roll`, which already asks that exact question** |
| her reward shop | built, placed and in character: the Undertaker |
| her currency | built: the Death token |

So the build is a day of data work. **What is not a day of data work is making her worth visiting.**

Measured 8 October: 24 of the 77 tasks have monsters standing inside the build's Wilderness
rectangles, **but only eight are wilderness-defining** — green dragons, red dragons, earth warriors,
black demons, greater demons, lesser demons, black dragons, hellhounds. The other sixteen are rats,
bats, bears, spiders, skeletons and the like: monsters nobody would ever travel north for. OSRS's
Krystilia assigns from forty-plus. **A master with eight real tasks and sixteen pieces of filler is
a master whose assignment you reroll**, and rerolling is the one thing a slayer master must not
make you want to do.

### What would fill it, re-checked 9 October

Five npcs stand in the Wilderness today with **no `param=slayer_category` at all**, which means a
kill on them counts for nothing anywhere:

* `chaos_druid`, `chaos_druid_warrior`
* `dark_warrior`
* `rogue`
* `highwayman`, `highwayman2`

Tagging them is the same small job the zygomites, mogres and fever spiders got on 8 October: a
param, a task constant, a `slayer_req` row if it should be gated, and the battery keeps it honest.
That takes her from eight to roughly thirteen real tasks without importing anything.

**Ankou and lava dragons still do not exist** — no npc config, no pack id — and ankou is the one
worth importing. `revenant` likewise absent, and correctly so.

**This work is worth doing whether or not she is ever built**, which is the test worth applying to
any prerequisite: more wilderness monsters that count towards Slayer is a good change on its own,
and it is Option B minus Option B's objection, because it adds *targets* without forcing anyone's
Turael task north.

## One decision to take now rather than later

**Do not make the Death token her currency.** It currently drops on any slayer task kill made in the
Wilderness, that rule shipped, and narrowing it would take something away from players who already
have it. Have her pay **a lump of tokens on task completion** instead, on top of the per-kill drip.
Choosing her is then rewarded, the existing rule never changes under anyone, and the token keeps
meaning "you did slayer up there" rather than "you used the right master".

## Where this leaves it

The accuracy argument that split A/B from C/D dissolved on 8 October; the cost argument dissolved on
the 9th, when the reward half turned out to have been built for another reason. What is left is the
honest design question, and it is worth stating plainly because it is the one that should decide it.

**A wilderness-only master is normally justified by risk, and risk needs a population.** On a quiet
server it fails in one of two directions: nobody hunts, so her tasks are ordinary tasks with a
longer walk and free points; or two or three people hunt constantly, and the content is dead for
everyone else. Neither is a disaster, but **neither is the reason to build her.**

**The reason to build her is identity and a ladder**: a named person who sends you north, a list
worth finishing, and a shop with something on the shelves at the end of it. That is a smaller claim
than "a risk loop", and it is one this server can actually deliver on. It also changes the design:
lean the cost on travel and time rather than on danger, keep the rewards cosmetic, and balance
nothing around being ganked.

**Recommended, in this order:**

1. **Tag the five monsters that already stand there and count for nothing.** Good on its own, and it
   is what makes step 3 worth doing.
2. **Import ankou.** The one genuinely missing wilderness slayer monster worth having.
3. **Build Krystilia** as a sixth master: her table, her points case, the wilderness-kills-only
   condition, and a lump of Death tokens on completion. The Undertaker is her reward shop.
4. **Larran's key and chest: don't.** The Undertaker already is that, and two wilderness loot
   dispensers in one town is one too many. If the key is wanted later it should open something of
   his.
