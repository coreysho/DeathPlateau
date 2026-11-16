#!/usr/bin/env bash
# Build the TypeScript client from a clean checkout. Everything here is reproducible from an
# upstream commit plus this directory - nothing depends on a machine anybody has set up by hand.
set -euo pipefail

UPSTREAM=https://github.com/89wc/runescape-web-client-37789
COMMIT=7582d035a67bf6be22ebb7565e5c9f8cc6abaf4d
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$HERE/work}"

if [ ! -d "$WORK/.git" ]; then
    echo "==> cloning upstream into $WORK"
    git clone -q "$UPSTREAM" "$WORK"
    git -C "$WORK" checkout -q "$COMMIT"
    echo "==> applying ts377-spike.patch"
    git -C "$WORK" apply "$HERE/ts377-spike.patch"
else
    echo "==> $WORK exists, leaving it alone"
fi

cp "$HERE"/{rsshim.js,build.mjs,entry.ts,serve.js} "$WORK/"
mkdir -p "$WORK/public"
cp "$HERE/dist/index.html" "$WORK/public/index.html"

cd "$WORK"
if [ ! -d node_modules ]; then
    echo "==> installing dependencies"
    npm install --silent esbuild jpeg-js long pako big-integer isaac-crypto @stardazed/zlib cyclic-32
fi

echo "==> building"
node build.mjs
echo
echo "built: $WORK/public/game.js"
echo "serve: node $WORK/serve.js   ->  http://localhost:9998/ts/"
echo "       (proxies anything it does not have to play.deathplateau.com)"
