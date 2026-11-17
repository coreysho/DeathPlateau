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
cp target/js/client.js index.html dist/
```

`install.sh` prefers a local build when there is one and falls back to `dist/`.
