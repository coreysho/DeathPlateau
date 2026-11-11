# The staff zone - ::sz

Built 11 November 2026. One map square nobody can walk to, reached by `::sz`
(moderator, staffModLevel 2 and up) and left by `::home` like anywhere else.

## Where the work is

| repo | branch | what |
|---|---|---|
| DeathPlateau-Engine | `claude/custom-staff-zone-j1ibx8` | **pushed.** The `::sz` command, the rank, the shared free-teleport rule, and `tools/sim/staffzone.ts` |
| DeathPlateau-Content | `claude/custom-staff-zone-j1ibx8` | **not pushed** - this session was not given push access to the content repo. The commit is `0001-staff-zone-content.patch` beside this file: `git am 0001-staff-zone-content.patch` on `377-wip` |

The patch is here rather than only in the cloud session because a cloud
container is reclaimed after a while and an unpushed commit goes with it.

## The square

`m22_56`, world x 1408..1471, z 3584..3647. `::sz` lands on `0_22_56_32_32`
(1440, 3616).

The same row as Burthorpe and the real Death Plateau, five squares west of
anything that exists: all eight neighbouring squares are empty, so no edge of a
real map square is ever in view. Outside both wilderness rectangles, far inside
the 14-bit coord packing, and in `maps/ignore.csv` so it is not on the world
map.

Terrain is the real plateau's own - underlay 94 under overlay 83, which is what
Death Plateau and Trollheim are made of. Indoor floors are the Edgeville bank's,
the sparring ring is the Duel Arena's.

## The four districts

- **The camp** (middle, where you land) - altar, signpost, a table and chairs.
- **The office** (north-west) - brick room, lectern, bookcases, and two 3x3
  **holding cells** of prison bars with a door apiece.
- **The vault** (north-east) - four bank booths, two bankers, and the general
  store's keeper and assistant, for reading stock and prices off the live
  economy.
- **The range** (south) - five attackable dummies, archery targets, a bare stone
  pad to `::npcadd` a boss onto, and a railed sparring ring, open at the corners.

Nothing new was imported and nothing new was wired: every loc and npc on the
square is already in the packs and already has its handler somewhere else. The
only new content script is the teleport itself, plus the login guard.

## Staff only, in two halves

- `::sz` is in the engine's moderator block, so nobody below rank 2 can type it.
- `~staffzone_login` (hooked into `login.rs2` beside `~poh_login`) puts anybody
  below rank 2 who logs in inside the zone back in Edgeville and tells them why.
  `::teleother` can put a player on those tiles, and a rank can be taken away
  from an account logged out on them; neither goes through the command.
- A moderator is held to `::home`'s rule - no `::sz` out of combat, out of the
  Wilderness, or out of an instance with its own way out. An administrator is not.

## Running it

```
cd Engine-TS && npm run build                       # packs the new square
BUILD_SRC_DIR=../content npx tsx tools/sim/staffzone.ts    # 40 checks, all green
python tools/genstaffzone.py --preview               # in content: the plan below
```

No new client jar: map data is cache the server serves, so a client picks the
square up on its next connect.

## The plan, as the generator prints it

`#` wall, bars or fence   `o` something standing on the tile   `@` where `::sz` lands
`C` camp (and the two cells)   `O` office   `V` vault   `P` boss pad   `R` ring   `.` open plateau

```
63                                                                 
62                                                                 
61                                                                 
60                                                                 
59                                                                 
58                                                                 
57      o  o  o  o  o  o  o  o  o  o  o  o  o  o  o  o  o  o       
56      o                                                   o      
55         ................................................        
54         ................................................        
53      o  ................................................ o      
52         ....#############...............................        
51         ....#OOOOOOOOOOO#...............................        
50      o  ....#OOOOoOOOOOO#.............#############..... o      
49         ....#OOOOOOOOOOO#.............#VVVVVVVVVVV#.....        
48         ....#OOOOOOOOOOO#.............#VooooVVVVVV#.....        
47      o  ....#OOOOOOO###O#.............#VVVVVVVVVVV#..... o      
46         ....#OOOOOOO#C#O#.............#VVVVVVVVVVV#.....        
45         ....#OoooOOO###O#.............#VVVVVVVVVVV#.....        
44      o  ....#OOOOOOOOOOO#.............#VVVVVVVoVVV#..... o      
43         ....#OOOOOOOOOOO#.............#VVVVVVVVVVV#.....        
42         ....#OOOOOOO###O#.............#VVVVVVVVVVV#.....        
41      o  ....#OOOOOOO#C#O#.............#VVVVVVVVVVV#..... o      
40         ....#OOOOOOO###O#.............#VVVVVVVVVVV#.....        
39         ....#OOOOOOOOOOO#.............#VVVVVVVVVVV#.....        
38      o  ....#############.............#############..... o      
37         ...................CCCCCCCCCCC..................        
36         ...................CCCCCCoCCCC..................        
35      o  ...................CooCCoooCCC.................. o      
34         ...................CCCCCCCCCCC..................        
33         ...................CCCCCCCCCCC..................        
32      o  ...................CCCCC@CoCCC.................. o      
31         ...................CCCCCCCCCCC..................        
30         ...................CCCCCCCCCCC..................        
29      o  ...................CCCCCCCCCCC.................. o      
28         ...................CCCCCCCCCCC..................        
27         ...................CCCCCCCCCCC..................        
26      o  ................................................ o      
25         ................................................        
24         ................................................        
23      o  ......o.o....................................... o      
22         ................................................        
21         ................................................        
20      o  ......o.o.o.o.o...................R#######R..... o      
19         ....................PPPPPPPP......#RRRRRRR#.....        
18         ....................PPPPPPPP......#RRRRRRR#.....        
17      o  ....................PPPPPPPP......#RRRRRRR#..... o      
16         ....................PPPPPPPP......#RRRRRRR#.....        
15         ....................PPPPPPPP......#RRRRRRR#.....        
14      o  ....................PPPPPPPP......#RRRRRRR#..... o      
13         ....................PPPPPPPP......#RRRRRRR#.....        
12         ....................PPPPPPPP......R#######R.....        
11      o  ................................................ o      
10         ................................................        
 9         ................................................        
 8      o  ................................................ o      
 7                                                                 
 6                                                                 
```
