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
| Scroll of imbuing | 100 | already stocked — see the named exception below |
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

## The one named exception: the Scroll of imbuing stays

**Corey's call, 12 October: *"i still want the imbue scroll in the shop"*.** I had it coming off for
failing rule 1, and it is staying. Writing down why it is defensible, so the rule survives the
exception rather than being quietly abandoned:

* **It is not new power.** The scroll is already a drop — from on-task kills and, far more often,
  from superiors. The shop is a *second route* to a thing that exists, not a source of something
  that otherwise would not.
* **It is untradeable, and so is everything it makes.** No laundry: an imbued ring cannot be sold,
  so the shop's price never becomes anybody else's price.
* **It is slayer content being bought with a slayer currency**, which is the one place a combat
  item has a claim to being on these shelves at all.

> **The exception has to stay narrow or it eats the rule.** "Already a drop, untradeable, slayer's
> own" is the test it passes. Anything that fails any one of those three is still out — which is why
> *imbue at the counter* stays off the list below, even though it is the same effect: that one has no
> drop behind it, so it would be a new route to power rather than a second one.

## What comes OFF the shelf

Ruled out, from the two idea documents:

| Idea | Which rule |
|---|---|
| Muddy key, clue scrolls, scroll boxes | 3 — they pay out tradeable loot |
| The casket, as originally conceived | 3 — same, unless its table is cosmetics only |
| Barrows repair for tokens | 1 — cheaper combat sustain |
| Imbue at the counter | 1 — the scroll's effect with no drop behind it; see the exception above |
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

---

## Killing a player who is wearing it — what they drop, and what I would change

**Corey asked: what is the reward for killing someone wearing the cosmetic set in the Wilderness?**
Measured rather than guessed, and the answer today is **nothing at all.** The engine decides it, in
`Engine-TS/src/engine/script/handlers/InvOps.ts`, `BOTH_DROPSLOT`:

```
if (!objType.tradeable) {
    // untradeables still drop to the primary player
    World.addObj(dropObj, fromPlayer.hash64, duration);
} else {
    World.addObj(dropObj, toPlayer.hash64, duration);
}
```

On a PvP death this build drops **everything** — there is no untradeable-is-destroyed rule here, only
four items in the whole obj table carry `param=destroy_death`, and the god capes are special-cased by
hand. Tradeables drop assigned to the **killer**; untradeables drop assigned to the **victim**. So an
Undertaker's hat lands at the dead player's feet, flagged to them, and they walk back and collect it.
The killer gets a message, a kill on their counter, and not one token.

**That is a hole, and it is the hole that matters**, because with no Wilderness Slayer master this
shop is the entire wilderness identity. A cosmetic that cannot be lost is a taunt with no stake
behind it.

### The fix: the Undertaker pays a finder's fee

A param on each token-bought cosmetic — call it `pvp_token_bounty` — and two lines in
`pvp_death_lose_items`:

* if the victim dies **in the Wilderness** wearing it, the piece is **destroyed** rather than
  dropped, and
* the **killer is paid that many Death tokens**, with a line telling them the Undertaker will take
  the deceased's effects off their hands.

**A quarter of the shop price** is my suggestion: a 200-token hat pays 50, the full five-piece set
pays 250. The victim re-buys at full price, so every kill **burns 150 tokens net** — the mechanism
is a sink with a faucet attached, not a money printer.

Why this is the right shape:

* **It is the only other way to get a token.** Slay for them, or take them off somebody who did.
  That is a whole second economy for one param and two lines.
* **It stays inside the rule.** The reward is cosmetic currency. Nothing bought with it can be
  pointed at a player, and the bounty itself changes no combat number.
* **It is opt-in risk, which is exactly what we kept when we turned down the master.** Nobody is
  ever *sent* into the Wilderness; a player wearing 1,000 tokens of black suit up there has chosen
  to be worth hunting. That is the risk loop Krystilia was supposed to create, arrived at from the
  other end.
* **It gives PKers a reason to care about slayers**, which is the ecology the Wilderness has never
  had here.

**Scope it to the Wilderness explicitly.** The duel arena is already safe — `death.rs2` branches to
`@player_death_duel` before the PvP item path — but the bounty should test
`~wilderness_level(coord)` rather than rely on that, because `findhero` is true for any PvP kill
anywhere and the next PvP zone somebody adds will not come with a warning.

**Open question for Corey:** does the piece being **destroyed** sit right, or should it drop to the
victim as it does today with the killer still paid? Destroyed is the version that makes the set a
statement and the economy a sink; dropped is gentler and makes the bounty pure profit with no loss
behind it.

## What I would build first

1. **The Undertaker's outfit, five pieces.** The models exist; this is obj configs, wearpos lines
   and icon cameras. It fills the shelf, it is pure status, and it makes the npc and the reward the
   same idea.
2. **The bounty**, in the same commit as the outfit — a cosmetic that cannot be lost is a taunt, and
   the outfit is the first thing worth losing.
3. **Head-stuffing**, because the heads are sitting there asking for it.
4. **The Gravedigger helmet recolour**, which is the thing people will actually chase.

The Scroll of imbuing stays on the shelf throughout.

Then the kits, the cape, the max cape variant, the log page and the deep-stock shelf.
