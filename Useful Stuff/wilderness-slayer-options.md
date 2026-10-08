# Wilderness Slayer: options for this server

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

## Where this leaves it

The accuracy argument that split A/B from C/D has mostly dissolved — the skill already runs OSRS's
own reward system, so the honest question is whether the *risk loop* is wanted, not whether it is
period.

**Recommended: a reduced C.** Krystilia as a sixth master, paying into the economy that already
exists, with the wilderness-kills-only rule, and Larran's chest deferred to a second pass. That buys
the identity and the loop for a fraction of the build, and the deferred half is self-contained.
Option D is the same build with this server's own rewards if a recreation is not wanted.

Two things to get right early, both learned the hard way in the week this was reviewed:

1. **Unlock bits.** Every tab of the rewards window writes one `%slayer_unlocks`. Three unlocks added
   on 7 October took bits the helmet recolours already owned, so an 80-point unlock handed over a
   1,000-point one. The battery compares the tables now; a new master's unlocks must take new bits.
2. **The battery rule.** A master may never be able to assign a task that nothing in the game counts.
   Krystilia's table should be written against that rule from the first commit rather than audited
   into shape later.
