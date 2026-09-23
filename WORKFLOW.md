# How this install is wired

Written down because three scripts that encoded it were deleted (see below) and
nothing else recorded it. `git remote -v` in each folder confirms all of it.

## Where things live

`C:\LostCityServer` is the orchestrator - this repo. The other three are nested
inside it, each its own git repo:

| folder | repo | branch |
|---|---|---|
| `C:\LostCityServer` | coreysho/LostCityServer | `main` |
| `C:\LostCityServer\content` | coreysho/Content | `377-wip` |
| `C:\LostCityServer\engine` | coreysho/Engine-TS | `377-wip` |
| `C:\LostCityServer\javaclient` | coreysho/Client-Java | `dev-logging` |

Each has two remotes: `origin` is the fork, `upstream` is LostCityRS, so
`git fetch upstream` still pulls the project's own updates.

`caches/` holds the source caches for asset imports (474, OSRS). It is
gitignored - tens of MB - so it exists only on the machine that downloaded it.
Anything that needs a cache has to run here, not in a cloud session.

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
- **The live server:** the LXC, `cd /opt/lostcity && ./deploy.sh`. That pulls
  `377-wip` for content and engine. It does not touch the java client, so a
  client change needs a rebuilt jar distributed separately.
- **Stale packs:** `rebuild-pack.bat` deletes `engine\data\pack`. The build
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
