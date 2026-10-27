# Patch notes — 12 October 2026

Discord markdown, split so each part is under 2000 characters. Post in order.

---

## Part 1

**NEW**

- **The Zaros cape.** The Undertaker now sells a kit that repaints an imbued god cape in the colours of the empty lord. It changes nothing but the colour - same god, same bonuses, same God Wars protection - and Revert gives your cape back along with the kit.
- **Clue caskets stack.** One casket per tier instead of a hundred and three that would not merge, and they weigh nothing, so a bank slot now holds a trail's worth. Caskets you already have still open exactly as before.
- **Rum Deal pays out the barrelchest anchor.** A two-handed crush weapon - +92 crush, +100 strength - needing 60 Attack and 40 Strength. Its special attack is not built yet.
- **The Agility guide has a Courses page.** Open the Agility skill guide and it now has two tabs. *Courses* lists all twelve — the Gnome Stronghold and Draynor at level 1, through Al Kharid, Varrock, the Barbarian Outpost, Canifis, Falador, the Wilderness course, Seers', Pollnivneach and Rellekka, to Ardougne at 90 — with the Agility Arena's two trap tiers. *Shortcuts* keeps the obstacle list it always had.
- **A music toggle on the login screen.** "Music: on / Music: off" at the foot of the login box turns the title music off before you log in, and remembers your choice. It does not touch your in-game Music setting.

**CHANGES**

- **Manta rays and sea turtles have moved.** The Wilderness spot is now four spots on the water east and north-east of the **east** dragons - two at Wilderness 20-21 on the coast, two at 25 on the northern shore - instead of the one in the puddle by the west dragons. Same harpoon, same rates: 79 for turtles, 81 for mantas.
- **The Ghostspeak amulet has its own model at last.** It had been wearing the generic strung amulet — the same mesh as an amulet of strength, painted brown. It now has the bone pendant it is supposed to have, on your character as well as in your pack. The Crone's enchanted copy follows it and still glows green.

---

## Part 2

**CHANGES**

- **You can alch on the move.** High and Low Level Alchemy no longer freeze your feet: the cast rate is unchanged, but walk clicks during it are no longer thrown away, so a run across Varrock stays a run.
- **A blade in your pack cuts a web.** Slashing a web or a cactus no longer needs the knife or sword equipped — anything in your inventory that could cut it will, on the single left-click. Matches the Old School change.

**FIXES**

- **The Trading Post board** no longer rearranges itself as you move the camera. The notices were being sliced up by the board behind them from any angle but dead-on. The crest at the top now reads **DP**.
- **The Undertaker's boots** are black all the way round now. He was wearing the default brown boots underneath his own, and bits of them were showing through. The one-armed veteran was doing the same thing.
- **The Lumbridge graveyard fence** is named in the Agility guide now, so the level 29 shortcut behind the church is findable.

---

## Notes for Corey, not for Discord

- The client half (the music toggle) is pushed to `dev-logging` as `eb6bdb6`, so launchers will pull it. It had to be rebased over 111 commits first - the local checkout was that far behind - which is why it also carries a one-line fix to the roofs test's settings count.
- Everything else is on content `377-wip` and needs a deploy.
- **The cape line was pulled.** The hem-split fix shipped and tore holes in the capes with armour on, so it is reverted (`16ede59e9`) and is not in these notes. The boots-through-the-hem fault it was aimed at is back and still open.
- Still unposted from the previous round: the lava dragons and the red dragon swap, Ankou, the draconic visage and dragonfire shield with its Activate, the lava dragon drop table, the 3rd Age axe and pickaxe, and the dragonfire shield / dragon defender rig fix. Say the word and I will write those up too.
