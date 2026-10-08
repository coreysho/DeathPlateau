# The Undertaker's shop: what to put on the shelves

Written 8 October 2026, after the Death token, the Undertaker and the veteran shipped with one
provisional row. Everything below is measured against the tree as it stands, not remembered.

---

## Four facts that decide the whole list

**1. What a player earns.** Measured by `tools/sim/deathtoken.ts` over 4,000 kills a side:
**0.17 tokens a kill at level 1, 0.49 past level 30.** A 150-kill task pays about **25 shallow or
73 deep**. At a realistic 200–300 kills an hour that is **35–50 tokens an hour shallow, 100–150
deep**. Every price below is quoted against that.

**2. The currency is untradeable, so the rewards should be too.** This is not fussiness. An
untradeable currency buying a tradeable item is a gold laundry with extra steps: the shop's price
becomes the trading-post price, and the token stops meaning anything. That reasoning is already
written into `death_token.obj` and it rules out most of the obvious ideas. It also means **no
buy-back** — `~can_sell_obj` refuses an untradeable item at every shop in this build — so a player
who spends 600 tokens on the wrong thing cannot undo it.

**3. One shop has one price multiplier, so an item's token price IS its gp cost.** `~calc_shop_value`
ends in `scale($mult, 1000, $cost)`, and the Undertaker runs at 1000 per mille, which is full price.
Two items can only be priced relative to each other by their gp costs. Three ways out, in order of
preference:

- **A custom reward gets `cost` = its token price.** This is already the house pattern — Grace's
  config says "sells at the item's own cost" for exactly this reason. It is why *the reward list
  wanting custom items is a feature and not a cost*.
- **A cache item whose gp value is meaningless just gets a `cost`.** The muddy key has no cost line
  at all (so, 1gp, so 1 token). Giving it `cost=20` costs nothing anywhere else — it is a junk key.
- **A cache item whose gp value matters gets its own shop.** `~openshop(inv, buy, sell, haggle,
  title)` takes the multiplier as an argument, so the Undertaker can open a second shelf from a
  dialogue option at a different rate. The rune pouch (cost 10,000) is the case that needs this.

**4. Stock is a tap, not a race.** `restock=yes` with one-at-a-time refill, `shop_delta,0` so a
price never drifts with how many he holds. A player saving for something finds it at the price it
was.

### Price bands that follow from the earn rate

| Band | Tokens | What it feels like |
|---|---|---|
| Pocket change | 5–25 | part of one task |
| Session kit | 50–150 | one to three tasks |
| Upgrade | 300–800 | a week of casual play, or 5–10 deep tasks |
| Capstone | 1,500–3,000 | a long-term goal you tell people about |

---

## A. The trip itself

**1. Looting bag — 10.** `cost=10` already, so it prices itself. It is *the* Wilderness item and
the slayer points shop sells it for 10 points; a parallel route in wilderness currency is not a new
power, it is the right shop finally selling it. **Build: one line.**

**2. Muddy key — 20.** Only chaos dwarfs drop it today. But **fix the chest first**: `lava_maze.rs2`
hands out a fixed list every single time — a mithril bar, two law runes, an anchovy pizza, a mithril
dagger, 50 coins, two death runes, two chaos runes and an uncut ruby. Selling keys to that is selling
a disappointment. Roll it instead. **Build: `cost=20` + a drop table.**

**3. Undertaker's casket — 60 / 180 / 500 (three tiers).** An untradeable box that rolls a
wilderness-flavoured table. **This is the best pure sink in the list**: you choose the cost, you
choose the table, and it keeps absorbing tokens for as long as the server runs without ever needing
a new mechanic. Tiers let the shelf have a floor and a ceiling with one idea.
**Build: one obj + icon + a drop table.**

**4. Pall-bearer's scroll — 25 for five uses.** A one-way teleport *into* the Wilderness, to the
level band your current task's monster lives at. It removes the walk, not the risk — you arrive
inside. **Build: obj + script.** (A teleport *out* is in the Don't list.)

**5. Hallowed oil — 40.** Ten charges; each one recolours your next gravestone… no. Cut. Listed only
so you know I considered and dropped the "soften death" shape.

**6. Skull of the fallen — 50, ten charges, each restoring 25 prayer.** Honest flag: prayer
restoration in the Wilderness is a **PvP balance decision**, not a shop decision. Attractive, and I
would want your call before building it.

Not worth it: salt, rock hammers, icy water, spray pumps, fungicide, broad arrows. They are gp items
in the slayer shop already and selling them twice teaches nothing.

---

## B. Crossover with the Slayer economy

**7. Scroll of imbuing — 100.** The current single row, and it earns its place: untradeable, slayer
flavoured, and already a drop, so the shop is a second route rather than a monopoly. **Keep.**

**8. Rune pouch — ~400.** 750 slayer points today. Needs the second-shop trick (gp cost 10,000).
A player who does wilderness slayer instead of normal slayer currently has no route to it.

**9. Herb sack — ~120.** Same argument, same mechanism (gp cost 1).

**10. Cancel this task — 40, as a dialogue option.** Costs 30 slayer points at a master. Priced a
little above so it is a convenience, not a discount. **Build: dialogue + the existing cancel proc.**

**11. Block this task — 150, dialogue.** 100 points at a master.

**12. Tokens into slayer points — 3 : 1, capped per task.** Deliberately a poor rate, so it drains
tokens without becoming the fast way to buy unlocks. **Build: dialogue + arithmetic.**

**13. "Bury Me Deeper" — 200.** A wilderness-flavoured task extension: green dragons, hellhounds and
greater demons run long when taken past the signs. The extension machinery is eleven rows of enum
already.

---

## C. Keys and chests

**14. Larran's key — ~75.** Agreed to land with Krystilia rather than before her, because the key
without the chest is a nothing. When it exists, this shop is the obvious second source.

**15. A chest of his own, inside the Wilderness.** If the Undertaker ever sells a key to something,
the something should be north of the signs. A chest on the Edgeville side would let a player bank
the risk and then collect at leisure, which is the whole loop backwards.

---

## D. Permanent unlocks, sold as items

Each is an item you buy and use once; it sets a bit and is consumed. The pattern already exists in
`%slayer_unlocks` — **but take new bits, not the next free-looking ones.** Three unlocks added on
7 October took bits the helmet recolours already owned and an 80-point unlock started handing over a
1,000-point one. `tools/slayer_battery.py` compares the tables now.

**16. Deeper Pockets — 400.** The drop rolls 1–5 instead of 1–3.

**17. Death's Handshake — 600.** +25% token rate, permanent. A sink that pays for itself in about
2,400 tokens of earning; that is the point — it gives the shop a *first* goal.

**18. Gravewatch — 1,200.** Tokens also drop from wilderness kills that are **not** on task, at a
reduced rate. This is the one that changes how the Wilderness feels, and it is priced to be late.

**19. Mourner's Licence — 500.** Your wilderness streak survives taking a Turael task. Only
meaningful once Krystilia exists.

---

## E. Cosmetics and prestige — where the big money should go

**20. A fourth slayer helmet recolour — 1,000. My strongest recommendation in the document.**
The whole pipeline is built: `genslayerhelm.py`, `tools/slayerhelmspec.json`, the Cosmetics tab, the
bit-collision check. A "Gravedigger" or "Undertaker" black-and-bone helm is a **spec file and a
row**, and it is the single most visible thing a player can buy. Cheapest high-value item here by a
distance.

**21. The Undertaker's outfit — 200 a piece, 800 the set.** Hat, coat, trousers, boots, cane.
**The models already exist** — `npc_undertaker_hat`, `_coat`, `_coat2`, `_legs`, `_cane`, `_boots`
were built for the npc and are `*_manwear`-shaped, so this is obj configs, wearpos lines and icon
cameras rather than art. Untradeable cosmetics are the perfect thing to sell for an untradeable
currency: no laundry, no power, pure status.

**22. The veteran's cape — 150.** `npc_veteran_cape` likewise already exists.

**23. Mourning cape — 300.** A custom black cape with the token's skull on it; reuses the coin's own
skull stamp.

**24. Tombstone, POH garden — 400.** Construction is built, garden and all.

**25. Death token display case, POH — 500.** The coin, mounted. A trophy for a currency is a joke
that lands.

**26. Pile of skulls, POH trophy — 750.** `slayer_heads.obj` already holds imported untradeable
trophy heads (abyssal, KQ), so the shape is proven.

**27. "Doff hat" / "Lay flowers" emote — 250.** Worth checking the cache for an existing anim before
costing it.

---

## F. Counting, which is cheap and keeps people coming back

**28. "How many have you brought me?"** — a dialogue line reporting lifetime tokens spent, with a
gift at 500, 2,500 and 10,000. One varp, three ifs.

**29. A Wilderness Slayer collection-log page.** The log is built. Listing every token reward makes
the shelf a checklist, which is most of why people grind a currency at all.

---

## G. One I'd mention and not build

**30. The Undertaker's wager** — 100 tokens for a roll that can return nothing or 1,000. It is
gambling-adjacent, and a token sink that pays out tokens is a loop rather than a sink. If you want
randomness, the casket (3) is the same thrill with a floor.

---

## H. What not to sell, and why it matters more here than usual

- **Anything tradeable.** The laundry argument above. This rules out food, potions, runes, gear, and
  every "quality of life" item that can be bought at a general store.
- **A teleport out of the Wilderness.** The token exists *because* the player stood somewhere
  dangerous. Selling the exit deletes the reason the currency has value.
- **Item protection, gravestones, body retrieval.** Same argument, louder. The most attractive-
  sounding idea in this whole space and the one that would do the most damage.
- **Combat bonuses that only apply in the Wilderness.** They make the PvP asymmetric in favour of
  whoever grinded longest, which is the opposite of what a slayer currency should buy.

---

## What I would actually ship, in order

**First pass — a shelf that works this week.** Everything here is data or already-built pipeline:

| Row | Tokens | Why |
|---|---|---|
| Looting bag | 10 | one line; the wilderness item in the wilderness shop |
| Muddy key | 20 | one line + the chest table it deserves |
| Undertaker's casket (small) | 60 | the sink that never runs out |
| Scroll of imbuing | 100 | already there, already right |
| Deeper Pockets | 400 | the first upgrade worth saving for |
| Gravedigger helmet | 1,000 | the thing people will actually chase |

Plus two dialogue services: **cancel a task for 40**, and **tokens into slayer points at 3:1**.

**Second pass.** The Undertaker's outfit (the models are sitting there), Death's Handshake, the POH
trophies, the collection-log page.

**Third pass, with Krystilia.** Larran's key and chest, Mourner's Licence, Gravewatch, Bury Me
Deeper.

---

## What I need from you

1. **Does the shop sell power, or only status?** My recommendation is **status plus token-economy
   upgrades, and no combat power at all** — it keeps the laundry rule simple and keeps PvP clean.
2. **The prayer flask (6)** — yes or no, since it is a PvP balance call rather than a shop one.
3. **Is the Undertaker also a services counter** (cancel, block, point exchange), or strictly a shop?
   Services are cheap to build and give him a reason to be talked to between purchases.
