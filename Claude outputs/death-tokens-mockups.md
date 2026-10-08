# Death tokens: look, shop npc, and rewards — options

Settled already: a random drop from kills made **while on a slayer task, in the Wilderness**;
**untradeable**; **coexists** with Slayer points; the shop npc stands in **Edgeville**; the name is
**Death token**, because it is this server's own.

Everything below is costed against what the build already has. `param=shop_currency` has worked
since the TzHaar needed Tokkul and Grace needed Marks of Grace, so a token shop needs no new
machinery — one obj, one shop inv, one npc.

---

## 1. What the token looks like — 16 options

See `token_candidates.png` for the sheet. Every one of these is art already in the build, so the
work is a recolour and a new obj, not an import.

| # | Base | The idea | Why it reads |
|---|---|---|---|
| 1 | **Death rune** | charcoal stone, bone-white skull glyph (or glyph in blood red) | Already a grey disc with a skull on it. The closest thing in the cache to a "Death token" and the one I would start from |
| 2 | **Blood rune** | deep red on black | Reads as "blood money" — the PvP-currency idiom players know from other servers |
| 3 | **Soul rune** | pale blue glyph on slate | Spectral rather than gory; pairs with a ghost shopkeeper |
| 4 | **Mark of Grace** | minted disc, gold → black iron with a red glyph | A *struck coin* silhouette: unmistakably currency, and it matches the build's other earned currency |
| 5 | **Tokkul chips** | obsidian → bone white | Primitive, scattered; good at small stack sizes |
| 6 | **Tokkul (25 pile)** | the bigger pile, same recolour | If you want stack art: 1 / 5 / 25 / 100 variants, which the shop UI already handles |
| 7 | **Warrior guild token** | tarnished iron | Tiny and humble — a token that looks *cheap*, which makes a big pile feel earned |
| 8 | **Ectotoken** | parchment chit, stained red | Reads as a voucher rather than money: "turn this in" |
| 9 | **Coins** | gold → black/silver | Strongest "this is money" read, weakest identity — and risks being misread as coins at a glance |
| 10 | **Skull** | as-is, or bleached | Brutal and unmistakable. Better as a 1-of trophy than as something you hold 400 of |
| 11 | **Mark of Hazeel** | cult medallion | "Issued by someone" — fits a named broker npc |
| 12 | **Crystal key** | key shape, recoloured | A currency that looks like it opens something — ties to Larran's and the muddy chest |
| 13 | **Casket** | small chest | Better as a *bundle*: a "Death casket" that opens into a handful of tokens |
| 14 | **Amulet of power** | pendant on a cord | A token you could believe is worn on a belt; unusual silhouette in a pack |
| 15 | **Import** | OSRS's own blood money / ancient emblem art | A model job (`importosrs.py`), for when nothing in the cache reads right |
| 16 | **New art** | a drawn 32×32 through the icon pipeline | Most work, most distinct — the only option nobody else's server has |

**My pick:** #1 for the token itself and #4 if you want it to read as money at a glance. Both are
a recolour of art that already renders correctly at inventory size, which is where most custom
items fall over.

---

## 2. What the shopkeeper looks like — 14 options

Reusing a cache npc is minutes of work: a new npc block pointing at existing models, the three shop
params, a spawn and some dialogue. An import is a model job on top.

| # | Who | The look | Cost |
|---|---|---|---|
| 1 | **Mage of Zamorak** | black robes, hood — already the wilderness's own face | reuse |
| 2 | **Dark warrior** | Khazard helm and platemail; a deserter running a stall | reuse |
| 3 | **Elder Chaos druid** | deep-wilderness cult, level 129 presence | reuse |
| 4 | **Chaos druid** | the milder version — a hedge-witch broker | reuse |
| 5 | **Necromancer / Invrigar** | robed, staff; buys in bones and sells in favours | reuse |
| 6 | **Witch** | OSRS's own answer for Krystilia — "a witch who likes chaos" | reuse |
| 7 | **Dark wizard (bearded)** | the cheapest instantly-readable "shady" npc in the game | reuse |
| 8 | **Zamorak monk** | monastery robes; Edgeville already has the monastery next door | reuse |
| 9 | **Noterazzo** | the existing Bandit Camp shopkeeper — players already read him as "the wilderness shop" | reuse (but he is taken) |
| 10 | **Black Heather / Speedy Keith** | Rogues' Den characters: a fence, not a merchant | reuse |
| 11 | **Ghost** | a spectral broker — the literal reading of a death token | reuse |
| 12 | **Skeleton** | a skeletal trader; strong theme, slightly comic | reuse |
| 13 | **Zombie** | same idea, grubbier | reuse |
| 14 | **Import Krystilia** | the OSRS silhouette, if you want people to recognise her | `importosrsnpc.py` |

**Placement in Edgeville:** three spots worth considering — inside the **jail** northeast of the
bank (OSRS's own answer, and the lore fits a broker who deals with the condemned); beside the
**bank** (shortest loop, least atmosphere); or at the **Wilderness line** itself (there is no ditch in a 2006 game - it was dug in late 2007; the boundary here is a row of warning signs), which puts the
shop where the decision is made and gives the walk back a purpose.

**My pick:** #1 or #6, standing in the jail. Both read as "this person deals with the wilderness"
without needing a single line of dialogue to explain it.

---

## 3. What the tokens buy — 16 options

Two rules I would hold the list to, because they decide whether the currency stays healthy:

* **Mostly untradeable or consumable.** An untradeable currency that buys tradeable goods is a gold
  laundry with extra steps: the price of everything in the shop becomes the price of the item on the
  trading post, and the token stops meaning anything.
* **Don't duplicate the Slayer points shop.** Points buy task control (blocks, extends, unlocks).
  Tokens should buy *being in the wilderness* — getting there, staying there, showing you were.

| # | Reward | Shape | Notes |
|---|---|---|---|
| 1 | **Larran's key** | consumable | The anchor: tokens buy the key, the key opens the chest, the chest pays from a wilderness-only table. Keeps the whole loop inside the Wilderness |
| 2 | **Muddy key** | consumable | Already works, already 2006 — a cheap low-tier sink from day one |
| 3 | **Blighted supplies** | consumable, wilderness-only | OSRS's best idea in this space: food, brews and runes that only work in the Wilderness. Value cannot leak out, so you can price them generously |
| 4 | **A restock crate** | consumable | One click, a fixed kit of food and potions. Removes the bank trip, which is the real friction of a wilderness task |
| 5 | **Looting bag** | item (untradeable) | Wilderness staple; already in the build's Slayer Buy tab, so pick one home for it |
| 6 | **Rune pouch** | item (untradeable) | As above |
| 7 | **Amulet of glory recharges** | consumable | The standard teleport sink; cheap, constant demand |
| 8 | **Ammo in bulk** | consumable | Broad arrows and bolts by the hundred; a steady low-tier sink that never distorts prices |
| 9 | **A slayer-helmet colour** | cosmetic | The helm generator already takes a source block — a wilderness colour priced in tokens instead of points is a few lines and a model |
| 10 | **A server cape or hood** | cosmetic | Death Plateau's own, token-only. No economy risk at all and the strongest "I did this" signal |
| 11 | **A trophy for the house** | cosmetic | A mounted skull or banner in the POH, which the build already supports |
| 12 | **Scroll of imbuing** | item | Gives the top end of the token curve something worth saving for — it is already a drop, so this is a second route, not a new power |
| 13 | **A pet** | cosmetic, rare | Token-priced at a number that means hundreds of wilderness kills |
| 14 | **Teleport scrolls to the edge of the Wilderness** | consumable | Convenience that *increases* time at risk rather than reducing it |
| 15 | **A bigger chest key** | consumable | This server's own chest in the deep Wilderness, keyed and priced above Larran's |
| 16 | **Token → coins at a fence** | sink | Simple, and I would not: it prices the token in gold and everything above it stops mattering |

**A shape for the list, if you want one:** three or four cheap consumables (3, 4, 7, 8) so tokens are
always worth something; one mid-tier item (1 or 5); one or two cosmetics (9, 10) as the long goal;
and nothing tradeable anywhere on it.

---

## What I would build first

The currency, the npc and a four-row shop — cheap consumables plus one cosmetic — before Larran's
key exists. That gets the loop running and lets you watch the drop rate against real play, which is
the number nobody can guess right first time. Larran's key then slots in as the anchor when the
wilderness slayer master lands.
