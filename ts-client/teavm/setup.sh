#!/usr/bin/env bash
# Compile the DeathPlateau Java client to JavaScript with TeaVM.
#
# Needs JDK 17+ (TeaVM 0.16 will not load its own maven plugin on 11 - the mojo fails with
# "Type org.teavm.maven.TeaVMCompileMojo not present", which looks like a missing artifact and
# is not one).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CLIENT="${1:-$HERE/../../../deathplateau-client}"

echo "==> copying client sources from $CLIENT"
rm -rf "$HERE/src/main/java/jagex2" "$HERE/src/main/java/deob" "$HERE/src/main/java/sign" "$HERE/src/main/java/lostcity"
cp -r "$CLIENT/src/main/java/jagex2" "$CLIENT/src/main/java/deob" "$CLIENT/src/main/java/sign" "$HERE/src/main/java/"
cp -r "$CLIENT/launcher/src/lostcity" "$HERE/src/main/java/"   # build.gradle has launcher/src as a source root

echo "==> building"
cd "$HERE" && mvn -B package

echo
echo "built: $HERE/target/js/client.js"
echo "run:   node -e \"require('$HERE/target/js/client.js').main([], ()=>{})\""
