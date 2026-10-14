#!/usr/bin/env bash
# Fetch the source caches for asset imports (rev 474, OSRS) from the OpenRS2 archive.
#
# caches/ is gitignored, so a fresh clone - and every cloud session's container - starts without
# it and every importosrs.py / import474.py / animconvosrs.py run fails until this has run. See
# WORKFLOW.md for which cache is which and why the OSRS one needs converting.
#
# Point the cloud environment's Setup script at this and a new session starts ready to import:
#
#     bash tools/fetch-caches.sh
#
# IDEMPOTENT, and that is the point rather than a nicety: a setup script runs unattended, and the
# Windows box already has these. Each of the three steps checks for its own output first, so
# running this on a machine that has the caches costs three stat calls and no download.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p caches

# 474 (OpenRS2 runescape #237) is a disk store and is read as one - no conversion step.
# keys-237.json is the XTEA keys import474map.py needs; OpenRS2 serves them beside the cache.
if [ -f caches/474/main_file_cache.dat2 ] && [ -f caches/474/keys-237.json ]; then
    echo "caches/474: present, skipping"
else
    echo "caches/474: fetching rev 474 (OpenRS2 runescape #237)"
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    curl -fsS --retry 3 --retry-delay 2 -o "$tmp/474.zip" \
        https://archive.openrs2.org/caches/runescape/237/disk.zip
    mkdir -p caches/474
    unzip -q -o -j "$tmp/474.zip" -d caches/474
    curl -fsS --retry 3 --retry-delay 2 -o caches/474/keys-237.json \
        https://archive.openrs2.org/caches/runescape/237/keys.json
    rm -rf "$tmp"
    trap - EXIT
fi

# OSRS (OpenRS2 runescape #2710). OpenRS2 serves a disk store; the OSRS import tools read the
# .flatcache text layout, hence disk2flat.py. caches/osrs-disk is the intermediate and is kept
# only so the conversion can be re-run without re-downloading 182 MB.
if [ -f caches/osrs/2.flatcache ]; then
    echo "caches/osrs: present, skipping"
else
    if [ -f caches/osrs-disk/main_file_cache.dat2 ]; then
        echo "caches/osrs-disk: present, skipping download"
    else
        echo "caches/osrs-disk: fetching OSRS (OpenRS2 runescape #2710)"
        tmp=$(mktemp -d)
        trap 'rm -rf "$tmp"' EXIT
        curl -fsS --retry 3 --retry-delay 2 -o "$tmp/osrs.zip" \
            https://archive.openrs2.org/caches/runescape/2710/disk.zip
        mkdir -p caches/osrs-disk
        unzip -q -o -j "$tmp/osrs.zip" -d caches/osrs-disk
        rm -rf "$tmp"
        trap - EXIT
    fi
    echo "caches/osrs: converting disk store to flatcache"
    python3 tools/models/disk2flat.py caches/osrs-disk caches/osrs
fi

echo "caches ready: $(du -sh caches | cut -f1)"
