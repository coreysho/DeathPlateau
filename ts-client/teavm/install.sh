#!/usr/bin/env bash
# Put a built browser client where a world will serve it.
#
# The engine serves public/ as static files at the site root, so the client needs no route of its
# own: it lands at /teavm/, beside the cache routes it fetches from and the WebSocket it plays
# over, all on one origin. Nothing in the server has to change.
#
#   ./install.sh [path-to-engine]          # default: ../../../deathplateau-engine
#
# Then open http://<world>/teavm/ - and see local-rsa.sh if the world is one you host yourself.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="${1:-$HERE/../../../deathplateau-engine}"
[ -d "$ENGINE/src" ] || { echo "no src/ under $ENGINE - is that the engine?" >&2; exit 1; }
# public/ is made by the server's own setup and may not be there in a fresh checkout.
mkdir -p "$ENGINE/public"
# A build if there is one, else the committed one in dist/ - which is what a server that has no
# Java toolchain on it uses: git pull, install, done.
if [ -f "$HERE/target/js/client.js" ]; then
    SRC="$HERE/target/js/client.js"
    echo "installing the local build"
elif [ -f "$HERE/dist/client.js" ]; then
    SRC="$HERE/dist/client.js"
    echo "installing dist/ (no local build here)"
else
    echo "nothing to install - run setup.sh, or pull a dist/" >&2
    exit 1
fi
mkdir -p "$ENGINE/public/teavm"
cp "$SRC" "$ENGINE/public/teavm/client.js"
cp "$HERE/index.html" "$ENGINE/public/teavm/index.html"
echo "installed $(stat -c%s "$ENGINE/public/teavm/client.js") bytes to $ENGINE/public/teavm/"
echo "play at http://<world>/teavm/"
