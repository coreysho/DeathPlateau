# Does a TypeScript client fit this server?

A spike, run 16 November 2026, to put a number on one question: CheerpJ spends about
twelve seconds booting a WebAssembly JVM before `client.jar` executes a single line, and
nothing in that architecture removes it. Would a client that is *already* JavaScript load
in a time a player would wait?

Everything here is the change set, not the client. The client is somebody else's:

    https://github.com/89wc/runescape-web-client-37789
    commit 7582d035a67bf6be22ebb7565e5c9f8cc6abaf4d (2023-02-23)

a fork of reinismu/runescape-web-client-377, archived by its owner in August 2025. Clone
it, apply `ts377-spike.patch`, drop the four files beside it in, and it runs.

## What it answered

| | CheerpJ + client.jar | this |
|---|---|---|
| runtime to download | 18.9 MB | none |
| app bundle | 1.34 MB jar | 1.6 MB |
| before our code runs | **~12s** | ~0 |
| first thing drawn | ~24s | **0.6s** |
| our eight cache archives parsed | - | **~2s** |

Measured on one machine, Chromium with an iPhone 13 profile, against live's cache both
ways - the CheerpJ figures through a local proxy so neither side paid for the network.

**It loads OUR cache.** `/crc0` for the table, then `/<name><crc>` for each archive - the
same routes `engine/src/web.ts` already serves the Java client. All eight parse, config
and interface included, which are the two carrying the most of our own content. No errors.

## What it does NOT answer

- **Login.** Never attempted. World 2 is unreachable from the sandbox this ran in (43594,
  43595 and 8889 all refused; only play.deathplateau.com:443 was open), and an automated
  login against live was refused by the sandbox as an unwanted action - correctly. The
  handshake needs running from a machine that can reach World 2.
- **On-demand** - models, maps, animations over the game socket. The client asks for it
  and is refused here, so nothing past the title screen has ever rendered.
- **Touch, and the plugin sidebar.** This client has neither. The sidebar is 222 of our
  Java client's 384 classes and has no upstream equivalent in any TypeScript client; it is
  the single largest piece of work in a real port and nothing here touched it.

## The protocol, read off the engine rather than tested

`World.ts` accepts revision `ENGINE_REVISION` (384) or `LOGIN_LEGACY_REVISION` (381) and
answers anything else with a 6. The patch announces 381, which also avoids the saved-login
fields, since those are gated on `LOGIN_TOKEN_REVISION`. The RSA modulus is ours, taken
from `Client.java`'s `LOGIN_RSAN`. Transport is one `wss://` endpoint rather than two TCP
ports, because our engine multiplexes login and update on `/` and splits them by the first
byte.

**The gate that will fail first is the CRCs.** The engine checks all nine against its own
cache and closes the socket on a mismatch. A client fed this cache should pass it; one fed
a vanilla 377 cache cannot. That is why the cache layer had to come before the login test,
and it is the next thing to try.

## The load test, to run on a real phone

`dist/` is this built and ready to serve. The engine already serves `public/` statically, and
`public/` is gitignored, so it goes there the same way `client.jar` does:

    mkdir -p /opt/deathplateau/dev/engine/public/ts
    cd /opt/deathplateau/dev/engine/public/ts
    curl -L -O https://raw.githubusercontent.com/coreysho/DeathPlateau/claude/clever-cori-bee392/spikes/ts-client/dist/index.html
    curl -L -O https://raw.githubusercontent.com/coreysho/DeathPlateau/claude/clever-cori-bee392/spikes/ts-client/dist/game.js

Then open `http://<world2>:8889/ts/` on the phone. The page prints its own timings, so there is
nothing to measure by hand - photograph the green text.

Here, on a desktop processor with a phone-sized viewport, it reads:

    0.0s  page ready - starting client
    0.4s  DP crc table
    0.6s  DP archive title = 51547 bytes
     ...  all eight, 1.6 MB in total
    1.9s  DP parse: versionlist
    2.0s  *** FIRST PIXELS DRAWN ***

**Treat that number with suspicion until a phone has produced one.** The same method said CheerpJ
took 24 seconds; a real phone took over thirty minutes. An emulated viewport on desktop silicon is
not a phone, and the whole point of this build is to stop guessing about that.

It draws the title screen and stops: `__NO_SOCKET` and `__NO_LOCAL_CACHE` in `entry.ts` turn off
the game socket and the 18 MB disk cache, because neither is needed to time a load and the retry
loop for a socket that cannot connect pins the main thread - which on a phone means the timings
never become readable. Delete both flags to go further.

## Running it from source

    git clone https://github.com/89wc/runescape-web-client-37789 ts377
    cd ts377 && git checkout 7582d035a67bf6be22ebb7565e5c9f8cc6abaf4d
    git apply /path/to/ts377-spike.patch
    cp /path/to/{rsshim.js,build.mjs,entry.ts,serve.js} .
    npm install esbuild jpeg-js long pako big-integer isaac-crypto @stardazed/zlib cyclic-32
    node build.mjs && node serve.js      # http://localhost:9998

`serve.js` proxies anything it does not have locally to play.deathplateau.com, so the cache
routes are same-origin. Point it at World 2 instead to try the login.

## The four files beside the patch

- `rsshim.js` - the client imports three functions from a Rust crate that Parcel compiled
  to WebAssembly: a string hash, an RSA modpow and a noise function. All three are a few
  lines of JavaScript, and `BigInt` does the modpow. This is why the Rust toolchain and
  Parcel's `.rs` imports can both be dropped.
- `build.mjs` - esbuild, with resolvers for Parcel's glob imports (`client_cache/*.dat`)
  and the `.rs` import. The archived 2020 Parcel setup is not needed to build this.
- `entry.ts` - `new Game(canvas)` and nothing else. The React page it ships with is not
  load-bearing.
- `serve.js` - static files plus the proxy described above.

## What the patch is

Five files, 128 lines, and that is the whole of it:

- `Game.ts` - `loadDpCache()`, and `requestArchive()` returning from it. That method's own
  comment already said *"In rs it does web requests, hash checks and updates"*; it now does.
- `Configuration.ts` - our RSA modulus.
- `util/SignLink.ts` - revision 381.
- `net/Socket.ts` - one `wss://` endpoint.
- `cache/media/ImageRGB.ts` - `useTArray` for jpeg-js, which otherwise wants Node's Buffer.
