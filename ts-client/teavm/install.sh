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
[ -f "$HERE/target/js/client.js" ] || { echo "no build - run setup.sh first" >&2; exit 1; }
mkdir -p "$ENGINE/public/teavm"
cp "$HERE/target/js/client.js" "$ENGINE/public/teavm/client.js"
cp "$HERE/index.html" "$ENGINE/public/teavm/index.html"
echo "installed $(stat -c%s "$ENGINE/public/teavm/client.js") bytes to $ENGINE/public/teavm/"
echo "play at http://<world>/teavm/"
