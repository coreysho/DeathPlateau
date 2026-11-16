# Project D - a browser client that is already JavaScript

The browser client today is our Java `client.jar` running under CheerpJ, a JVM compiled to
WebAssembly. It works, and on a phone it takes **over thirty minutes to reach a login screen**.
That is not a tuning problem: about twelve of those seconds, on a desktop processor, pass before a
single line of our code runs, and nothing in that design removes them.

This project replaces it with a client that is JavaScript to begin with.

## The evidence this rests on

Measured on a real iPhone, against the live Death Plateau server, 16 November 2026.

| | CheerpJ + client.jar | TypeScript client |
|---|---|---|
| runtime to download | 18.9 MB | none |
| app bundle | 1.34 MB jar | 1.6 MB |
| before our code runs | ~12s | ~0 |
| **first pixels** | **30+ minutes (phone)** | **1.6s (phone)** |
| title screen | - | 200-280 fps |

And every compatibility question answered, on that phone, against that server:

- **Our cache loads.** All eight archives from the routes `engine/src/web.ts` already serves the
  Java client - `/crc` then `/<name><crc>` - parsed in about two seconds, `config` and `interface`
  among them, which carry the most of our own content.
- **The protocol works.** Opcode-14 handshake accepted, revision 381 accepted, all nine CRCs
  matched, the RSA block decrypted with our key.
- **Authentication succeeds.** Response code 2, `loggedIn = true`. A non-admin account got 7,
  which is `World.ts` refusing an account below `NODE_MIN_STAFF_LEVEL` - a policy rule, correctly
  applied.
- **The on-demand stream carries data**: 99% of 1,446 animation files, pulled and decoded.

The whole of that took about 200 lines of changes to somebody else's client. `SPIKE.md` is the
record of how, and `setup.sh` rebuilds it from an upstream commit.

## What is NOT proven, and it is the important part

**Nobody has seen the game world render.** Everything above stops at the login screen. The title
screen's 200+ fps is sprite blitting; the world is a software 3D rasterizer, and no measurement
here says what a phone does with one. That single number could still sink this.

**This client has never been run against a live server past its title screen.** Six distinct bugs
turned up in its loader in one afternoon, all of the same shape - things the port dropped that only
bite once you are logged in:

1. `mouseCapturer` declared and never constructed; every successful login threw on it
2. `startUp` asks the update server for a music file and spins until it arrives
3. the on-demand wait loops have no escape when a request is never answered, only when it is refused
4. every animation in the game preloaded before the login screen will take a password
5. the login catch reports every possible failure as "Error connecting to server"
6. a reproducible block between fetching the `wordenc` and `sounds` archives - **open**

The repository was abandoned in August 2023. Adopting it means being the first to run it properly.

## Phases

**Phase 0 - make it run.** Clear the open freeze (6 above), get to the game world, read the fps.
Needs a debugger on the device: Safari's remote inspector from a Mac shows the blocked stack in
seconds. This is the gate - if the renderer cannot hold a playable rate on a phone, stop here and
the answer is that browser mobile does not work for this game.

**Phase 1 - playable.** On-demand models and maps during play rather than preloaded, input, the
game loop, enough interface to move and fight. Target: log in, walk to Lumbridge, kill a goblin.

Protocol work inside Phase 1, as measured on 2026-11-16 by actually doing the first piece:

    [done] opcode table            84 server + 86 client packets, generated from the engine
    [    ] Packet alt readers      6 methods: p1_alt1/2/3, p2_alt1/2/3 read back
    [    ] handler field reads     35 handlers read the right length, the wrong fields
    [    ] handlers to write       15 server packets Client-TS has no handler for
    [    ] payload layouts          2 LAST_LOGIN_INFO (10 -> 23), MIDI_JINGLE (4 -> 5)
    [    ] config opcodes          13 across 8 types, from the cache experiment

The byte order finding is the one that moved the estimate, and it is written up in COMPARISON.md
under "The byte order problem". It is also the one thing that could still change which client we
build on, so it should be settled before the rest of Phase 1 is attempted.

**Phase 2 - parity.** The plugin sidebar is **222 of our Java client's 384 classes** and has no
equivalent in any TypeScript client. This is the largest single piece of work in the project and
nothing in the spike touched it. Also: QoL settings, the Hunter stat slot, saved logins, the
trading post interfaces.

**Phase 3 - mobile.** Touch input, a layout that suits a phone, and the keyboard - which in a
JavaScript client is an `<input>` and nothing else. Three separate bugs went into making that work
through CheerpJ; none of them exist here.

**Phase 4 - ship.** Serve it from `rs2.cgi` beside the CheerpJ page, then instead of it.

## Decisions needed before Phase 1

- **Where the code lives.** The spike patches a third-party tree at a pinned commit. Real work
  needs it vendored into a repository of ours. That is a fork of an archived project, so the
  licensing wants checking first: its `package.json` says ISC and there is no LICENSE file.
- **This port, or Lost City's.** Compared in COMPARISON.md. The cache experiment that was meant
  to settle this passed - Client-TS reads our archives - but porting the opcode table turned up
  something the comparison had missed: **42 of the engine's 83 encoders write byte orders
  Client-TS has no reader for**, and 35 of them are packets it already thinks it handles. ts377
  reads them natively, being the actual 377 client. The recommendation is still Client-TS, on its
  mobile input, its cache routes and its live upstream - but it is now a closer call than the
  comparison made it look, and the honest version is in COMPARISON.md.
- **What happens to the CheerpJ client.** It works on desktop browsers and the recent fixes landed
  there. Keeping it as a fallback costs nothing.

## What exists now

    SPIKE.md            how the evidence above was obtained, and what it does not cover
    setup.sh            clone upstream at the pinned commit, apply the patch, build
    ts377-spike.patch   every change, against that commit
    entry.ts            the harness: flags, login form, timing readout
    rsshim.js           three Rust functions the port imported, in JavaScript
    build.mjs           esbuild, with resolvers for Parcel's glob and .rs imports
    serve.js            static files plus a proxy to the live cache routes
    dist/               built, and what the phone has been loading

    tools/gen-protocol.mjs    generates Client-TS's ServerProt.ts and ClientProt.ts from the
                              engine's three prot files. Idempotent; re-run it when they change
    clientts-protocol.patch   the result, against Client-TS at 7d6ca61

esbuild warns that `rsshim.js` uses BigInt literals against the `es2017` target it is built for.
That target was a hedge against an old Safari and bought nothing: the RSA those literals implement
is what encrypts the login block, and logins succeed on the phone, so BigInt is plainly supported.
Raise the target and the warning goes.

`dist/index.html` reports the build time and configuration as its first line, and loads the bundle
with a cache-busting timestamp. Both exist because a stale copy read as a failed fix three times.
