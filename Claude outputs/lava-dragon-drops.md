# The lava dragon's drop table: what Old School's is, what ours can be

Checked 9 October 2026 against the wiki's table and against what this build actually has.

> **BUILT, 9 October 2026.** All three questions at the bottom were answered: **lava scale out**,
> **the 2,960 coin line keeps Old School's 7/128**, and **no lava dragon head** - the draconic
> visage shipped the same day and fills that slot with the real thing. Lava dragon bones were
> built as proposed (`bone_exp,850`, dragon bones recoloured). The table is
> `scripts/drop_tables/scripts/lava_dragon.rs2`; the viewer's rows and the browser interface are
> regenerated from it. What follows is the reasoning, kept as the record of why.

---

## The good news: most of it already exists

Of Old School's table, these are all already items here — **lava battlestaff** and **lava runes**
included, which are the two that carry the flavour:

rune dart · rune knife · rune javelin · rune axe · rune kiteshield · rune med helm · rune full helm ·
rune longsword · adamant 2h sword · adamant platebody · adamantite bar · runite bolts · lava
battlestaff · lava rune · fire rune · blood rune · death rune · law rune · fire orb · fire talisman ·
chocolate cake · black dragonhide · looting bag

So the weapons, runes, coins and "other" sections port across essentially unchanged, and the gem and
rare tables map straight onto `~randomjewel` and `~ultrarare_getitem`.

## Four things do not exist, and each is a different decision

### 1. Lava dragon bones — build them

**This is the one that matters.** Lava dragon bones are *why* people kill lava dragons in Old
School; without them the monster has a table and no reason to exist.

Cheap, too. Bones in this build are six obj configs with `iop1=Bury`, `category=bones` and
`param=bone_exp`, and the xp is stored at ten times its face value (`bones` 45, `big_bones` 150,
`babydragon_bones` 300, `dragon_bones` 720). Old School gives lava dragon bones **85 xp**, so
**`param=bone_exp,850`** — a shade above dragon bones' 72, which is the point of them.

The icon is a recolour of the dragon bones model (`enakh_cutscene_bonepile_8`), which an obj config
does with a `recol` pair and no art at all.

### 2. Lava scale — I would leave it out

Old School's lava scale exists to be ground into lava scale shards, which go into Ancient brews and
the Hydra-era potions. **None of that Herblore content is in this build**, so a lava scale here is
an item whose only property is that you have some. A guaranteed drop with no use is worse than no
drop: it is inventory clutter that teaches the player the monster is not worth looting.

If you want it anyway, it should be a plain trade good with a sensible `cost` and nothing else, and
it should say so in its examine text rather than implying a use that isn't there.

### 3. Draconic visage — use this build's own precedent instead

There is no draconic visage here, and no dragonfire shield for one to make, so Old School's
1/10,000 line has nothing to point at.

But the build already solved this shape: **the King Black Dragon drops `kbd_head` at 1/128**, a
trophy from `slayer_heads.obj`. A **lava dragon head** on the same terms is consistent, costs one
obj config, and — worth noting — feeds the Undertaker idea from the shop document, where he stuffs
heads for tokens. Two trophy heads make that a feature rather than a one-off.

### 4. Onyx bolt tips, dragon javelin tips, ensouled dragon head — leave out

Post-2006 with no local hook. The javelin tips are gated on Monkey Madness II, which does not exist
here, and the ensouled head belongs to Arceuus magic, which also does not.

## And two are already deferred

**Larran's key** and **Slayer's enchantment** are Krystilia's wilderness-slayer tertiaries, and the
decision document already puts them with her rather than before her. Nothing to do here.

---

## The proposed table

One `random(128)` cascade, the way every other dragon in this build does it.

**Always:** Lava dragon bones ×1, Black dragonhide ×1

| band | /128 | drop |
|---|---|---|
| weapons | 6 | Rune dart ×12 |
| | 4 | Rune knife ×8 |
| | 3 | **Lava battlestaff** |
| | 2 each | Adamant 2h sword · Adamant platebody · Rune axe · Rune kiteshield · Rune longsword |
| | 1 each | Rune med helm · Rune full helm |
| runes | 10 | Rune javelin ×20 |
| | 7 | Fire rune ×75 |
| | 7 | Blood rune ×20 |
| | 6 | Runite bolts ×30 |
| | 5 | Death rune ×20 |
| | 5 | Law rune ×20 |
| | 4 | **Lava rune ×15** |
| | 4 | **Lava rune ×30** |
| coins | 15 | 66 |
| | 7 | 2,960 |
| | 1 | 690 |
| other | 5 | Fire orb (noted) ×15 |
| | 5 | Adamantite bar ×2 |
| | 3 | Chocolate cake ×3 |
| | 1 | Fire talisman |
| tables | 5 | `~randomherb` twice |
| | 5 | `~randomjewel` (the gem table) |
| | 3 | `~ultrarare_getitem` (the rare table) |
| | 5 | nothing |

**Tertiary, rolled separately:** Looting bag 1/3 · Hard clue at `^trail_hard_droprate` (Old School
gives an elite; this build's top tier is hard) · **Lava dragon head 1/128**

### One number worth a second look

**Coins 2,960 at 7/128.** In Old School that line only appears for accounts that have not finished
Monkey Madness II — which here is every account, so it is the real rate. It works out at about
**175 coins a kill** across all three coin lines, against roughly **92** for this build's black
dragon. Given the lava dragon is level 252 to the black dragon's 227 and lives at Wilderness 36-42,
I think twice the coins is right. Flagging it because it is the single biggest gp number in the
table and it is easy to halve if you disagree.

## How it gets built

Drop tables here are **RuneScript, not data**: an `[ai_queue3,lava_dragon]` death trigger in
`scripts/drop_tables/scripts/lava_dragon.rs2`, modelled on `black_dragon.rs2`. Then
`tools/gennpcdrops.py` re-reads the script and regenerates `npc_drops.dbrow` for the in-game drop
viewer, and `npcdrops_battery.py` checks it. Nothing is hand-maintained twice.

New items needed: **lava dragon bones** (one obj, one recolour, `bone_exp,850`) and **lava dragon
head** (one obj). Everything else is already in the game.

## What I need from you

1. **Lava scale — in or out?** My vote is out.
2. **The 2,960 coin line — keep Old School's rate, or halve it?** My vote is keep.
3. **Lava dragon head at 1/128 in place of the visage — yes?** It is the build's own precedent and
   it gives the Undertaker something to stuff.
