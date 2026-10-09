# The Undertaker's shop, second pass: fifty more, sorted by what they reuse

Written 9 October 2026, after the first list. That one was sorted by *what the reward is*. This one
is sorted by **which already-built mechanism it rides on**, because in this codebase that is the
same thing as sorting by cost — and it turned up a dozen veins the first pass never touched.

Nothing here repeats the first document. Read them together.

---

## The machinery that already exists, and what it will carry

| Mechanism | Where it lives | What it can sell |
|---|---|---|
| Ornament kits | `ornament_kit.param`, `ornament_results.obj` | cosmetic overlays on existing gear, with Dismantle |
| Max cape variants | `genmaxvariants.py`, `max_cape_variants.enum` | a capstone cape |
| Slayer helmet recolours | `genslayerhelm.py`, `slayerhelmspec.json`, Cosmetics tab | the most visible cosmetic in the game |
| Collection log rewards | `collection_log_reward` rows, `gencollectionlog.py` | threshold payouts, a checklist |
| Skilling outfit set bonuses | `outfit_effects.rs2`, `outfits.param` | a cosmetic set that is also an economy perk |
| Skillcape worn passives | the `skillcape_worn(` hooks | "while worn" effects, 20-odd precedents |
| Degradation and repair | `degrade_repair_rate` and friends | a repair counter that scales with play |
| Recharge-with-loyalty | `crystal_recharge.rs2` | a price that falls the more you use him |
| Imbue pairing | `imbue_into` / `imbue_from` | an imbue service with no scroll |
| Trophy heads | `slayer_heads.obj` (abyssal, KQ, untradeable) | stuffing, which is literally his trade |
| POH costume room / garden | `poh_costume.inv` (perm, 72), `poh_garden.inv` | storage and decoration |
| Music | `music.dbrow` + varp | a track, at zero balance risk |
| Clue trails | three tiers, scroll boxes, clue hunter outfit | a sink that pays into another economy |
| Extra shelves | `~openshop(inv, buy, sell, haggle, title)` | more price bands, rotating stock, gated stock |

---

## 1. Ornament kits — the richest vein in the tree

The pairing lives on the items as params, there is a `Dismantle` op, and `poh_battery.py` already
fails a kit that only points one way. A kit is **two params and an obj**. There are sixteen of them
shipped, so this is a worn path.

1. **Gravedigger kit (slayer helmet) — 800.** Black and bone, matched to the token.
2. **Mourning kit (black mask) — 600.** The mask is the slayer item people actually look at.
3. **Undertaker kit (rune scimitar) — 450.** Note the base item already carries three kit slots for
   the three gods, so a fourth slot is a known, already-solved cost.
4. **Bone-inlay kit (dragon dagger) — 500.**
5. **Bone-inlay kit (dragon boots) — 550.** `dragon_boots_g` is the proven shape.
6. **Pallbearer kit (any cape) — 300.**
7. **Coffin-nail kit (rune platebody) — 700.**
8. **A kit that fits the *Fremennik helm*** the veteran wears — 350. Ties the two npcs together.

> The whole vein shares one virtue: **a kit sells status and cannot sell power**, because the
> ornamented result copies the base item's stats. That is the laundry rule and the power question
> answered by the mechanism itself rather than by discipline.

## 2. The capstone: a Max cape variant

9. **Undertaker's cape + Max cape = Undertaker max cape — 1,500 for the cape.**
   `genmaxvariants.py` already generates cape → variant, variant → hood and variant → source, and
   `skillcape_perks.rs2` reads "is this a variant" straight off the third table. A new row is a spec
   edit and a regenerate. This is the single best **capstone** available: it is visible, it is
   expensive, it requires a maxed account *and* a wilderness grind, and the pipeline is built.

## 3. Collection log, which turns a shop into a checklist

10. **A "Wilderness Slayer" log page.** Every token reward on one grid. People grind currencies for
    the list far more than for the items.
11. **Threshold rewards on that page** — `collection_log_reward` pays an item at a count you choose.
    Half the page pays a cosmetic; the full page pays the cape at 9.
12. **A whole-log token payout** — rows can key off the entire log, not just a page, so "every
    distinct item in the log" could pay a one-off pile of tokens.
13. **Message-only milestones**, which the table supports with no reward at all. Cheap, and they
    make the page feel authored.

## 4. The slayer helmet, three colours instead of one

14. **Gravedigger — 1,000.** (Carried from the first list; still my top single recommendation.)
15. **Greenscale — 1,000.** Green dragons are the wilderness task.
16. **Hellfire — 1,000.** Hellhounds are the other one.
    Three colours make the Cosmetics tab read as a *wilderness sub-theme* rather than one orphan.
    **Take new unlock bits** — the 7 October collision is in the notes for a reason.

## 5. The outfit, as a set bonus rather than just clothes

17. **The Undertaker's outfit — 200 a piece, and the full set gives +10% token rate.**
    `outfit_effects.rs2` and `outfits.param` already do set detection and set bonuses for the
    skilling outfits. This is the answer to "status or power?": **the set bonus is paid in the
    shop's own currency**, so it is status that buys more status and touches no combat number.
18. **A partial bonus per piece** (2.5% each) if you want the pieces to matter on their own.
19. **Costume room storage for the set** — `poh_costume.inv` is `scope=perm`, size 72. Adding the
    five pieces to the costume item list is data.

## 6. Worn passives, the skillcape way

Twenty-odd precedents for "while worn, this happens", each hooked where the skill does its work.

20. **Undertaker's hat: +10% token rate while worn.** Better design than a permanent unlock — you
    pay for it by wearing a hat instead of a helmet in the Wilderness, which is a real cost in the
    one place it matters.
21. **Veteran's cape: your task counter shows wilderness kills separately.** Pure information.
22. **Mourning gloves: bones you walk over are buried.** The 2006-safe bonecrusher — prayer xp, no
    item, no combat.
23. **Gravedigger boots: a quarter less run-energy drain north of the signs.** Flagging it:
    mobility in a PvP zone is a **PvP balance call**, not a shop call.

## 7. Repair and recharge — sinks that scale with how much someone plays

24. **He repairs Barrows gear for tokens.** `degrade_repair_rate` is per slot (helm 60, body 90,
    legs 80, weapon 100 gold per point, 1000 points a piece) so the arithmetic exists; price it in
    tokens at a discount to the gp rate and it becomes the reason a Barrows user comes north.
25. **A loyalty curve on that price**, exactly like `crystal_recharge_price` — his rate drops each
    time, bottoming out on the fifth. The shape is written and tested.
26. **Grave-wax — 40.** One hour of half degradation.
27. **He recharges jewellery and charged items for tokens**, wherever the build has them.

## 8. Imbues without a scroll

28. **Imbue at the counter — 150 tokens.** `imbue_into` means the service is one proc reading a
    param; it costs nothing per item and automatically covers every imbueable thing including the
    fourteen recoloured helmets. The scroll stays on the shelf at 100 for people who want to carry
    it.

## 9. Stuffing heads, which is his actual job

29. **Bring a head, he mounts it — 200.** `slayer_heads.obj` already holds imported untradeable
    trophy heads whose desc is literally *"I should get it stuffed!"*. Nothing in the build stuffs
    them. This is the most *in-character* idea in either document and the item already exists.
30. **A KBD head** — the wilderness boss, mounted at 1,500.
31. **Mounted Death token, POH** — 500.
32. **Pile of skulls, POH — 750.**
33. **A gravestone in the POH garden — 400**, engraved with your highest wilderness level reached.

## 10. Music, at zero risk

34. **A dirge — 200.** `music.dbrow` plus a varp bit. No balance surface at all, and a track people
    associate with the shop is cheap identity.

## 11. Clues, which pay into somebody else's economy

35. **A hard clue scroll — 150.** The trail system has three tiers; selling a clue converts tokens
    into *other* content rather than into items, which is the healthiest kind of sink.
36. **A scroll box — 80.** `scroll_box.obj` exists.
37. **Clue hunter outfit pieces for tokens**, as an alternate route to a cosmetic set that already
    exists.

## 12. More shelves, because `~openshop` takes its multiplier as an argument

38. **A sundries shelf** at a different rate, for cache items whose gp cost is awkward (the rune
    pouch at 10,000).
39. **A rotating shelf** — "what came in this week" — a varp picking one of several invs. The
    cheapest retention mechanic in the document.
40. **A deep-stock shelf that only opens once you have earned N tokens past level 30.** This is the
    one structural idea I would fight for: it ties the best rewards to *risk*, not to *hours*, and
    it is the difference between a wilderness shop and a shop that happens to be near the
    Wilderness.
41. **One-per-player rows**, held by a varp bit rather than stock, for things that should not be
    farmed.
42. **A shelf that only opens while you are on a wilderness-completable task.**

## 13. Structure, not items

43. **Shelves that unlock by lifetime tokens *spent*.** The shop grows as you use it; one varp.
44. **A weekly cap on the deepest sink**, so it drips.
45. **A loyalty discount across the whole shop**, the crystal-recharge curve applied to the counter.
46. **"Count my dead"** — a line reporting lifetime tokens earned, spent, and deepest level reached.
47. **A funeral for a lost item.** Tell him what you lost; he says something appropriate. Costs one
    token, builds nothing, and is the kind of thing players screenshot.

## 14. Two I'd price carefully

48. **A tip-off: a temporary drop-rate boost on your current task.** The droprate machinery exists
    (`^droprate_boost_*`, in ten-millionths). It is a **power purchase** and it would be the first
    one. My instinct is no — but it is the strongest "I want to buy something that helps" answer if
    you decide status alone is too thin.
49. **Bury bones at his yard for bonus Prayer xp, paying tokens per bone.** A sink that burns tokens
    *and* a tradeable item without creating one — the direction that is safe. Watch that it does not
    become the best prayer training in the game.

## 15. One non-starter, named so it stops coming up

50. **Bank space cannot be sold.** `^bank_total_slots` is a single constant and `bank.inv` takes
    `size=` at pack time, so bank size is the same number for every account. Per-player bank size is
    engine work, not a config change. Same for item packs of *tradeable* contents — the pack
    mechanism is lovely (`item_pack_contents`, `item_pack_amount`, Open already wired) and the
    laundry rule rules out almost everything you would put in one. Packs of untradeable consumables
    are the exception.

---

## Revised recommendation, both documents together

**The spine.** Three things, each riding a built pipeline, each at a different horizon:

| | tokens | pipeline it reuses |
|---|---|---|
| Gravedigger slayer helmet | 1,000 | `genslayerhelm.py` + Cosmetics tab |
| Gravedigger ornament kit (helmet) | 800 | `ornament_kit.param` + Dismantle |
| Undertaker max cape | 1,500 | `genmaxvariants.py` |

**The counter.** Four services, all dialogue, no new items: **stuff a head (200)**, **repair Barrows
(by the existing per-point rate)**, **imbue without a scroll (150)**, **cancel a task (40)**.
Stuffing is the one I would build first — the heads exist, their examine text asks for it, and
nothing in the game does it.

**The structure.** A **deep-stock shelf gated on tokens earned past level 30**, and a **collection
log page**. Together they turn a shop into a reason to go further in, which is the only thing the
Death token was ever for.

**Still open, and still yours:** does the shop sell any power at all (48 and 23 are where that
question actually bites), and is the Undertaker a counter as well as a shelf.
