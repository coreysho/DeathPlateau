# Patch notes — 27 October 2026

Discord markdown, split so each part is under 2000 characters. Post in order.

---

## Part 1

**NEW**

- **The imbued ancient cape.** The Undertaker now sells **ancient fabric**. Use it on an imbued god cape and the cape is remade in Old School's ancient colours — black, with Zaros's mark on the back in purple. It changes nothing but the look: same god, same bonuses, same God Wars protection, and Revert gives your cape and your fabric back. (This replaces the Zaros cape that went in last week — same shelf, same price, the real item's model this time.)
- **The imbued ancient max cape.** Combine an imbued ancient cape with a max cape and hood, as you would any other max cape variant. It keeps the god of the cape underneath it.
- **The granite hammer and the granite longsword**, from gargoyles. The hammer is a four-tick crush weapon — +57 crush, +56 strength — with Old School's **Hammer Blow** special: 60% of the bar, half again the accuracy, and five damage that lands *even if the attack misses*. The longsword is 56 stab / 65 slash / +62 strength at five ticks. Both need 50 Attack and 50 Strength.

---

## Part 2

**NEW**

- **Marim's five market stalls can be robbed.** Ape Atoll has had a food stall, a crafting stall, a general stall, a magic stall and a scimitar stall standing in the village since the island was built, all five offering **Steal from**, and the click did nothing at all. Food 5 Thieving / 16 xp / a banana; crafting 5 / 20 / a ring, necklace or amulet mould, a chisel or a gold bar; general 5 / 25 / a pot, hammer or tinderbox; **magic 65 / 90 / an air, earth, fire, nature or law rune**; **scimitar 65 / 210 / an iron, steel, mithril or adamant scimitar**. A robbed stall is picked over for a few seconds and then restocks, and **Padulah** will come over if he happens to see you at it.

**CHANGES**

- **The enchanted gem has a Check option.** It reads your task, your remaining kills, your Slayer points and your streak straight into the chat, without the four lines of dialogue.
- **Aleck's Hunter Emporium is on the minimap.** Yanille's Hunter shop finally has an icon — Old School's own, a kebbit.

---

## Notes for Corey, not for Discord

- The ancient cape's models are Jagex's. They are not in `caches/newest cache` (10 September) because the cape was released on 7 October, so OpenRS2 cache **2746** (20 October) was fetched and converted to `caches/osrs-2746`. Four models: 62044 the cape, 62047/62049 the worn pair, 62045 the fabric.
- There are **three** ancient cape records, one per god cape, where Old School has one. Old School's cape is Zarosian and gates nothing on it; here a god spell needs that god's cape, so a single record would silently take the spell and the God Wars protection away from anyone who made one. All three are named "Imbued ancient cape" and are told apart only by the examine.
- Not carried across from Old School: the +2% magic damage (this build has no magic damage percentage anywhere — 2006 had none) and the Zarosian God Wars alignment (there are no Zarosian npcs here).
- The granite weapons are **not** gargoyle drops in Old School — the hammer is the Grotesque Guardians' and the longsword the Wyvern Cave's, and neither source exists in a 377 cache. The rates are still Old School's own, 1/750 and 1/512, taken from the monster that really drops them.
- Hammer Blow has no Golembane bonus: this build has no golem category to test against.
- The minimap icon needed a **client release** — `Client.java` looped over a literal 71 when loading map icons, so slot 71 would never have been read.
- The Marim stalls needed one change to the generic stall path: every stall in the game is swapped for `market` - a 2x2 Varrock silver stall - while it restocks, which would have dropped a piece of Varrock onto a 1x1 monkey table. The 377 cache ships no emptied monkey stall, so each of the five names its own picked-over twin and the seven old stalls are untouched. Everything else in this push is Monkey Madness quest work and is deliberately not in the Discord part.
