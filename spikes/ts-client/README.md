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

**On a real phone, 16 November: 1.5 seconds to first pixels.** All eight archives down by 0.9s.
The same device took over thirty minutes to reach a login screen through CheerpJ. For once the
desktop estimate was the pessimistic one - it said 2.0s.

On a desktop processor with a phone-sized viewport it reads:

    0.0s  page ready - starting client
    0.4s  DP crc table
    0.6s  DP archive title = 51547 bytes
     ...  all eight, 1.6 MB in total
    1.9s  DP parse: versionlist
    2.0s  *** FIRST PIXELS DRAWN ***

**Treat that number with suspicion until a phone has produced one.** The same method said CheerpJ
took 24 seconds; a real phone took over thirty minutes. An emulated viewport on desktop silicon is
not a phone, and the whole point of this build is to stop guessing about that.

`__NO_LOCAL_CACHE` turns off the 18 MB disk cache, which is not used when the archives come from
the server.

## Then: login, and the question the title screen cannot answer

The current `dist/` connects. The page is served by the engine, so the game socket is the page's
own origin - the engine carries login and update on `/` and splits them by the first byte, which is
why this client's two "ports" are one endpoint.

It has an **HTML login form**, and that is worth noticing on its own: in a JavaScript client the
phone's keyboard needs no bridge, no native method, no acknowledgement protocol and no handshake.
It is an `<input>`. Three separate bugs went into making that work through CheerpJ.

The readout prints a rough **fps** every five seconds once anything is drawn. That is the real
question here. A title screen is 2D sprite blitting; the game world is a software 3D rasterizer,
and nothing measured so far says a phone can run one at a playable rate.

The CRC gate should now pass, because the nine hashes the login block carries are read from the
same archives this client just loaded from the server - which is why the cache layer had to come
first.

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
