# How this install is wired

Written down because three scripts that encoded it were deleted (see below) and
nothing else recorded it. `git remote -v` in each folder confirms all of it.

## Where things live

On the Windows box, `C:\LostCityServer` is the orchestrator - this repo. The
other three are nested inside it, each its own git repo. **The live server is
laid out differently; its table is the next section.**

| folder | repo | branch |
|---|---|---|
| `C:\LostCityServer` | coreysho/DeathPlateau | `main` |
| `C:\LostCityServer\content` | coreysho/DeathPlateau-Content | `377-wip` |
| `C:\LostCityServer\Engine-TS` | coreysho/DeathPlateau-Engine | `377-wip` |
| `C:\LostCityServer\javaclient` | coreysho/DeathPlateau-Client | `dev-logging` |

Each has two remotes: `origin` is the fork, `upstream` is LostCityRS, so
`git fetch upstream` still pulls the project's own updates.

## THE LIVE SERVER IS NOT THAT LAYOUT

The table above is the Windows box. The live server is an LXC container on
Proxmox and its folders are named differently, which matters because a path
copied out of this file fails there - `cd: /opt/deathplateau/Engine-TS: No such
file or directory`, 15 November 2026, from following this very document.

| folder | repo | branch |
|---|---|---|
| `/opt/deathplateau` | holds `deploy.sh` and the `players-backup-<date>` snapshots | |
| `/opt/deathplateau/engine` | coreysho/DeathPlateau-Engine | `377-wip` |
| `/opt/deathplateau/content` | coreysho/DeathPlateau-Content | `377-wip` |
| `/opt/deathplateau/web` | coreysho/DeathPlateau-Web | `main` |

`engine`, not `Engine-TS`. **There is no java client on the box at all** -
`deploy.sh` does not touch it, so a client change needs a jar built and
distributed separately. `start.bat`, `start-safe.bat` and `start.js` are the
Windows box's and have no part in the live server: `deploy.sh` is the whole of
it. PowerShell does not run here either - `Get-ChildItem Env:` and
`$env:USERPROFILE` belong to the other table.

The box also answers to `/opt/lostcity`; it was named before the server was,
and `deploy.sh` resolves whichever of the two it finds.

Two systemd units: `deathplateau.service` is the world, `deathplateau-web.service`
is the website. `deploy.sh` restarts both and then tails the game log, and says
so: Ctrl-C stops the tail, not the server.

### The commands that only exist on the box

From `/opt/deathplateau/engine` unless stated otherwise:

- `bash tools/server/backup-offsite.sh` - snapshots the four sqlite databases
  (accounts, tradingpost, clans, vote) and the player saves, writes
  `/var/backups/dp-offsite/dp-<stamp>.tar.gz` and sends it to
  `root@10.8.0.1:/var/backups/deathplateau`, keeping 14 archives at each end.
  **`bash`, not `sh`**: it uses `set -o pipefail`, which dash refuses with
  "Illegal option -o pipefail". `./tools/server/backup-offsite.sh` is fine too -
  the shebang is right, and only `sh <file>` overrides it. The archive includes
  the login key, which it tells you, so treat it as a secret.
- `npx tsx tools/server/wipe.ts --profile main --confirm` - the wipe. Keeps
  staff, moves characters to `data/players/main/wiped-<stamp>` rather than
  deleting them, credits vote tickets back, clears the trading post and the
  non-staff clan channels, and backs up every database it touches first. World
  down before it, up after. `tools/server/rehearse-wipe.sh` runs it against a
  copy with the world still up.
- `npx tsx tools/server/account.ts <command>` - ranks, items, stats, passwords.
  Its own file header is the full list. It refuses to write while that account
  is logged in, and proves the new bytes load before replacing a save.
- `cd ../web && node scripts/discord-panels.mjs <panel>` posts a Discord panel
  and prints its message id; `--edit <id>` rewrites that message instead of
  posting a second copy of it.

Two things about git and sqlite there, both learned the hard way:

- As root, git inside `/opt/deathplateau/web` needs
  `git -c safe.directory=/opt/deathplateau/web` - git refuses a repository whose
  owner is not the user running it ("dubious ownership").
- `sqlite3` is installed, so `engine/db.sqlite` can be edited directly, and
  sometimes has to be. Prefer `account.ts`: it is the path that checks a save
  still loads. Either way copy the file first - that is what the
  `db.sqlite.pre-*` copies sitting in that folder are.

`caches/` holds the source caches for asset imports (474, OSRS). It is
gitignored, so it exists only on the machine that downloaded it. Measured, not
"tens of MB": `caches/474` is 44 MB, `caches/osrs` 257 MB as flatcache, plus
219 MB for the `caches/osrs-disk` intermediate, which can be deleted once
`disk2flat.py` has run.

Both come from the OpenRS2 archive (archive.openrs2.org). **A cloud session can
do this, and the commands below are all of it** - confirmed 12 October 2026:
archive.openrs2.org is already reachable from the cloud environment with no
allowlist change, the two downloads are 31 MB and 182 MB and took well under a
minute each, and `importosrs.py` then imported an item (Skills necklace, obj
11113, 3 models round-trip verified) out of the result. So an import round does
not have to happen on the Windows box.

What a cloud session does NOT get is persistence: the container is reclaimed
after a while and `caches/` is gitignored, so the fetch runs once per session.
To avoid that, put `bash tools/fetch-caches.sh` in the environment's **Setup
script** (the cloud environment menu in the session's title bar, then Edit) and
every new session starts with the caches already in place.

| folder | OpenRS2 cache | what |
|---|---|---|
| `caches/474` | runescape #237 | rev 474, Oct 2007: `disk.zip`, plus `keys.json` saved as `keys-237.json` (the XTEA keys `import474map.py` needs) |
| `caches/osrs` | runescape #2710 | OSRS, 16 Sep 2026: `disk.zip`, converted with `tools/models/disk2flat.py` |

`tools/fetch-caches.sh` is those four commands, made idempotent and committed, so the
cloud environment's **Setup script** can be one line:

```
bash tools/fetch-caches.sh
```

Measured both ways, 12 October: **33 seconds** from an empty `caches/` to ready
(both downloads, the unzips and the 24-index conversion), and **13 milliseconds**
when the caches are already there - which is the case that matters, because a
setup script runs unattended and the Windows box already has them. Each of the
three steps checks for its own output, so nothing re-downloads. Verified by
importing out of the result afterwards, not just by the script exiting 0.

The commands it runs, if you would rather do it by hand:

```
curl -o 474.zip  https://archive.openrs2.org/caches/runescape/237/disk.zip
curl -o osrs.zip https://archive.openrs2.org/caches/runescape/2710/disk.zip
unzip -j 474.zip  -d caches/474  && curl -o caches/474/keys-237.json https://archive.openrs2.org/caches/runescape/237/keys.json
unzip -j osrs.zip -d caches/osrs-disk && python3 tools/models/disk2flat.py caches/osrs-disk caches/osrs
```

The OSRS tools (`importosrs*.py`, `animconvosrs.py`) read the `.flatcache` text
layout; OpenRS2 serves disk stores, hence `disk2flat.py`. The OSRS caches on
OpenRS2 carry no XTEA keys, so OSRS *map* imports still need keys from
elsewhere; 474 has them, which is why Feldip came from 474.

## THE JAVA CLIENT IS ON dev-logging, NOT 377

`377` and `dev-logging` have NO COMMON ANCESTOR - `dev-logging` was started
fresh on 2026-09-01 rather than branched, so `git merge-base --all` between them
returns nothing. There is nothing to merge and nothing to reconcile:

- `dev-logging` holds all 89 of `377`'s files plus 17 more, and zero files are
  unique to `377`
- the QoL batch of 2026-09-01 (tab-to-reply, space-to-continue, Escape-to-close,
  middle-mouse drag, scroll zoom, shift-click drop) is present in both
- `377` stopped on 2026-09-03; `dev-logging` is where the work is

Building from `377` gets you a client missing everything since, including the
Hunter stat slot. `377` is left on the remote as history, not as a branch to
build.

## Running and deploying

- **Locally, on Windows:** `start.bat` (or `start-safe.bat`, which skips
  `npm install` and pauses so the window survives a crash). Both run `start.js`,
  the upstream orchestrator: a menu with Start Server, Update Source, Run Java
  Client. "Update Source" is `git pull` in all four folders.
- **The live server:** the LXC, `cd /opt/deathplateau && ./deploy.sh` (the box
  was named before the server was, and still answers to `/opt/lostcity` too -
  `deploy.sh` resolves whichever of the two it finds). That pulls `377-wip` for
  content and engine, snapshots the saves, builds, migrates the database and
  restarts the world. `--countdown=300` warns players first, and starts the
  timer only once the build has succeeded, so a failed build leaves them
  playing. `--dev` does all of it to World 2 instead, which is staff-only with
  its own saves, database and service. It does not touch the java client, so a
  client change needs a rebuilt jar distributed separately.
- **Launch day, and the wipe:** `content/tools/launch-day.sh`, on the box. It
  prints the sequence - off-site backup, deploy, world down, wipe, world up,
  website, veteran rank - with the reason each step is where it is, and reports
  what the box says about each one. It acts on nothing: the only thing it runs
  is the wipe's own dry run. The wipe is `tools/server/wipe.ts` in the engine
  checkout - `engine/` on the box, `Engine-TS\` on Windows - which
  refuses while anybody is logged in, moves saves rather than deleting them, and
  can be rehearsed against a copy of the live data with the world still up:
  `tools/server/rehearse-wipe.sh`.
- **Only one engine checkout.** It is `Engine-TS`. There was a second one at
  `engine\` for a long time - same repo, cloned and then abandoned: 761 commits
  behind, no `data\pack` because it had never been built, and 420 lines of
  September work that had already landed upstream by another route. Deleted on
  31 October 2026; that work is kept as a patch in
  `Claude outputs\engine-clone-rescue\` and its `.env` was NOT copied over, so
  `Engine-TS` still runs on `.env.example` defaults. `start.js` still clones
  into `engine\`, so running the start script would make a fresh one.
- **Stale packs:** `rebuild-pack.bat` deletes `Engine-TS\data\pack`. The build
  regenerates the server-only packs on its own when their sources move, so this
  is a shortcut for when it does not, not a required step.

## Scripts that used to be here

- `pull-from-github.bat` - per-repo `git pull` with branch merges. `start.js`'s
  "Update Source" does the same thing and is maintained upstream. Deleted mainly
  because it merged `origin/377` into the java client, which is the dead line
  above; a hardcoded branch name in a local script is exactly what goes stale.
- `push-to-github.bat` - FIRST-TIME fork setup: `git remote add origin`,
  `git merge --allow-unrelated-histories`, initial push. That happened once. Run
  today it would try to merge unrelated histories into four repos. The remote
  layout it set up is the table above.
- `apply-construction-engine.sh` - a one-off from the Construction round
  (2026-09-10) carrying an embedded base64 patch and a dated player backup. The
  patch is committed; the script is spent.
