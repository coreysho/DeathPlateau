# The Undertaker's shop: decided

**12 October 2026.** Corey's two decisions, in his words: *"shop should sell status - not power.
nothing that can be used against other players or anything"* and *"i dont think we need a wildy
slayer master."*

This supersedes the recommendations in `death-token-shop-ideas.md` and
`death-token-shop-ideas-2.md`. Those stay as the catalogue; this is the list.

---

## The rule, written so it can be applied without me

A row may go on the shelf only if **all** of these are true:

1. It changes **no combat number** — not the player's, not a monster's.
2. It cannot be **used against another player**, directly or by making you harder to kill, faster to
   escape or better at catching someone.
3. It is **untradeable**, and it does not **pay out** anything tradeable. (The laundry rule, already
   in `death_token.obj`: an untradeable currency buying tradeable goods makes the shop's price the
   trading-post price and the token stops meaning anything.)
4. It is not **gated behind** a combat advantage either — no "buy the thing that buys the thing".

**The happy part: one whole mechanism satisfies the rule by construction.** An ornament kit's result
copies the base item's stats, so a kit *cannot* sell power even if someone later wires it carelessly.
Where there is a choice, prefer a kit.

---

## The shelf

Everything here rides a pipeline that is already built and tested. Prices are against the measured
rate — **0.17 tokens a kill at level 1, 0.49 past 30**, so 35–50 an hour shallow and 100–150 deep.

| Row | Tokens | Rides |
|---|---|---|
| A dirge (music track) | 200 | `music.dbrow` + a varp |
| Undertaker's hat | 200 | the npc's own `npc_undertaker_hat` model |
| Undertaker's coat | 200 | `npc_undertaker_coat`, `_coat2` |
| Undertaker's trousers | 200 | `npc_undertaker_legs` |
| Undertaker's boots | 200 | `npc_undertaker_boots` |
| Undertaker's cane | 200 | `npc_undertaker_cane` |
| Gravestone, POH garden | 400 | `poh_garden.inv` |
| Undertaker's cape | 400 | `npc_veteran_cape`, retinted |
| Mounted Death token, POH | 500 | POH furniture |
| Mourning kit (black mask) | 600 | `ornament_kit.param` + Dismantle |
| Pile of skulls, POH trophy | 750 | `slayer_heads.obj` precedent |
| Gravedigger kit (slayer helmet) | 800 | `ornament_kit.param` + Dismantle |
| Gravedigger helmet recolour | 1,000 | `genslayerhelm.py` + the Cosmetics tab |
| Undertaker's cape → **Undertaker max cape** | 1,500 | `genmaxvariants.py` |

**Services at the counter, dialogue rather than rows:**

* **Stuff a head — 200.** Bring one, he mounts it. `slayer_heads.obj` already holds untradeable
  trophy heads whose examine text reads *"I should get it stuffed!"* and **nothing in the build
  stuffs them.** The most in-character row in either document and the items already exist.
* **Count my dead — free.** Lifetime tokens earned, spent, and deepest Wilderness level reached.
* **A funeral for a lost item — 1 token.** Tell him what you lost; he says something appropriate.
  Builds nothing, costs nothing, and is the kind of thing people screenshot.

**And the two structural pieces, which matter more now than they did:**

* **A Wilderness Slayer collection log page.** With no master, this list *is* the skill's wilderness
  content — the page is what makes it a thing to finish rather than a shelf to browse.
* **A deep-stock shelf, gated on tokens earned past level 30.** `~openshop` takes its multiplier as
  an argument, so a second shelf is cheap. This ties the best cosmetics to **risk** rather than to
  **hours**, which with no master is the only mechanism left that does.

---

## What comes OFF the shelf

**The Scroll of imbuing — the single row on the shelf today — fails rule 1.** Imbued rings and an
imbued black mask are combat upgrades, and three of the four rings are worn in PvP. It has to go.

> **It should not go until something replaces it.** `death_token_shop.inv` ships one row precisely
> because an empty window with a Trade option is worse than no option — Grace's config says the same
> thing about hers. So: the first status rows land, and the scroll comes off in the same commit. It
> loses nothing; the scroll is already a drop from on-task kills and from superiors.

Also ruled out by the rule, from the two idea documents:

| Idea | Which rule |
|---|---|
| Muddy key, clue scrolls, scroll boxes | 3 — they pay out tradeable loot |
| The casket, as originally conceived | 3 — same, unless its table is cosmetics only |
| Barrows repair for tokens | 1 — cheaper combat sustain |
| Imbue at the counter | 1 — the scroll's problem without the scroll |
| Prayer flask | 1 and 2 |
| Reduced run-energy drain while skulled | 2 — mobility in a PvP zone |
| Purchasable drop-rate boost | 1 |
| Rune pouch, herb sack, looting bag | see the judgement call below |
| Bury bones for Prayer xp | 1 — xp is a combat number by another road |

---

## Two judgement calls, with my reading

**1. Economy perks — the outfit's set bonus, Deeper Pockets, Death's Handshake.**
These change how fast you earn *tokens* and nothing else. They cannot be pointed at another player.
**My reading: they pass**, and the outfit set bonus in particular is the thing that makes a 1,000-
token cosmetic set worth buying — status that buys more status. **But they are power in the loose
sense**, so if the rule is meant strictly, drop all three and the shelf above still stands on its
own. Say the word either way.

**2. Storage — looting bag, herb sack, rune pouch.**
None of them touches a combat number or can be used against anyone; they are inventory convenience.
The looting bag only matters *because* of PvP, which is the uncomfortable part. **My reading: the
looting bag passes and I would still leave it off**, because it is already 10 slayer points and a
second route adds nothing but a row. The other two are 750 points each and genuinely have no
wilderness flavour. **Recommend: none of the three.**

---

## What I would build first

1. **The Undertaker's outfit, five pieces.** The models exist; this is obj configs, wearpos lines
   and icon cameras. It fills the shelf, it is pure status, and it makes the npc and the reward the
   same idea.
2. **The scroll comes off in that same commit.**
3. **Head-stuffing**, because the heads are sitting there asking for it.
4. **The Gravedigger helmet recolour**, which is the thing people will actually chase.

Then the kits, the cape, the max cape variant, the log page and the deep-stock shelf.
