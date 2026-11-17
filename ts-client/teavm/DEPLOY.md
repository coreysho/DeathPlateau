# Putting the browser client on a world

This is for the world other people play on. Nothing here needs Java, Maven or a build: `dist/`
holds a built client, and it is the one the live world's players would get.

## On the machine that runs the world

```
git pull
cd ts-client/teavm
./install.sh /path/to/deathplateau-engine
```

That copies two files into the engine's `public/teavm/`. The engine already serves `public/` as
static files at the site root, so there is no route to add and no server code to change. Static
files are read per request, so a later update is the same three lines again - no restart.

Players open **`/teavm/`** on the world's own address. On a phone that is the whole install.

## The two things that have to be true

**The world must take revision 384.** `ENGINE_REVISION=384` in the engine's `.env`. A world that
already serves the real Java client through CheerpJ is on 384 already, because that is the
revision the Java client logs in as - this is the same client.

**The login key must match.** The build in `dist/` carries the production `LOGIN_RSAN`, the same
one the desktop client and the launcher use, so it matches any world running the real key and
there is nothing to do. It is only a private test world with its own `npm run rsa` pair that needs
`local-rsa.sh` and a rebuild - see TEAVM.md.

Both mismatches are refused the same way, with login code 6, which the client shows as "RuneScape
has been updated! Please reload this page". It is not a cache and reloading cannot fix it.

## Music

Silent unless the world has a soundfont, and nothing for it is downloaded until then.

The client fetches its songs itself and hands each one over as a MIDI file; a desktop plays that
with the soundbank every JVM ships, and a browser has neither a synthesiser nor a bank. The
synthesiser comes with this client (spessasynth, Apache 2.0, ~1.3MB across two files, which
`install.sh` copies). The bank does not, because it is megabytes and the licence is a choice:

```
cd /path/to/public/teavm
curl -sSL -o music.sf3 https://unpkg.com/@librescore/sf3@0.8.0/TimGM6mb.sf3.wasm        # 3.9 MB, GPL-2
# or, better quality:
curl -sSL -o music.sf3 https://unpkg.com/@librescore/sf3@0.8.0/FluidR3Mono_GM.sf3.wasm  # 14.5 MB
```

Those are General MIDI banks packaged by LibreScore; the licence of each is in that package and
should be served or credited alongside. Name the file `music.sf3` and that is the whole install.

**What a player pays.** Nothing, until a song plays. The page asks for `music.sf3` when the first
one arrives: no file, one line in the console and the game is silent, with the synthesiser never
fetched. With a file, that player downloads the bank and the synthesiser once and the music plays
from then on - the title theme, then whatever the area sends.

Removing `music.sf3` turns music off again for everyone, with nothing else to change.

## Behind a proxy or a tunnel

The client opens its WebSocket back to whatever host served the page, so **serve `/teavm/` from
the same origin players already reach the world on**. A page on one hostname and the game on
another will load to the title screen and fail to log in.

That proxy has to pass WebSocket upgrades on `/`, which it already does if CheerpJ works there
today - it is the same socket.

Over HTTPS nothing extra is needed: the client reads the page's own scheme and switches to `wss`
and `https` cache fetches by itself.

## Refreshing dist/

After `setup.sh` and `mvn -B package`:

```
cp target/js/client.js dist/
sed -E "s|<script src=\"client\.js(\?v=[0-9-]+)?\">|<script src=\"client.js?v=$(date -u +%Y%m%d-%H%M)\">|" index.html > dist/index.html
```

(The script TAG only - the page says "client.js" in a couple of log lines too.)

The version on the script URL is what makes a browser fetch a new client instead of serving the
one it already has. The page is tiny and the script is not, so stamping the page is enough.

`install.sh` prefers a local build when there is one and falls back to `dist/`.
