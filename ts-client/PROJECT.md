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
- **This port, or Lost City's.** Compared in COMPARISON.md, and the answer is not the one this
  spike assumed. Client-TS's revision gap is a renumbering table - 54 of 56 shared packets have
  identical payloads, and our own `ServerGameProt.ts` has the numbers - while ts377's cost is
  living in 3,769 machine-translated identifiers with no upstream. **The recommendation is
  Client-TS**, subject to one experiment: point it at our cache and see whether it parses our eight
  archives. A day, and it settles the question.
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

esbuild warns that `rsshim.js` uses BigInt literals against the `es2017` target it is built for.
That target was a hedge against an old Safari and bought nothing: the RSA those literals implement
is what encrypts the login block, and logins succeed on the phone, so BigInt is plainly supported.
Raise the target and the warning goes.

`dist/index.html` reports the build time and configuration as its first line, and loads the bundle
with a cache-busting timestamp. Both exist because a stale copy read as a failed fix three times.
