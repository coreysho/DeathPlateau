#!/usr/bin/env bash
# Compile the DeathPlateau Java client to JavaScript with TeaVM - vanilla only, no plugins.
#
#   JDK8=/path/to/jdk8 ./setup.sh [path-to-deathplateau-client]
#
# JDK 17+ runs the build (TeaVM 0.16's maven plugin will not load on 11 - it fails with "Type
# org.teavm.maven.TeaVMCompileMojo not present", which looks like a missing artifact and is not
# one). JDK 8 is needed only to build the shim jar, because javac 9+ refuses `package java.awt;`.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CLIENT="${1:-$HERE/../../../deathplateau-client}"
: "${JDK8:?set JDK8 to a JDK 8 home (only used for the shim jar)}"

echo "==> building the browser shim"
"$HERE/awtshim/build.sh"

echo "==> copying client sources"
SRC="$HERE/src/main/java"
rm -rf "$SRC/jagex2" "$SRC/deob" "$SRC/sign" "$SRC/lostcity"
cp -r "$CLIENT/src/main/java/jagex2" "$CLIENT/src/main/java/deob" "$CLIENT/src/main/java/sign" "$SRC/"
cp -r "$CLIENT/launcher/src/lostcity" "$SRC/"            # build.gradle lists launcher/src as a source root

echo "==> dropping the desktop and plugin tree"
# Swing, a second window, jar class loading and a plugin hub: none of it exists in a page, and
# vanilla does not need any of it. vanilla/ holds the stubs the client still names.
rm -rf "$SRC/jagex2/client/plugin" "$SRC/jagex2/client/worldmap/MapWindow.java"
rm -f "$SRC/lostcity/TitleBar.java" "$SRC/lostcity/Launcher.java" \
      "$SRC/lostcity/LauncherWindow.java" "$SRC/lostcity/Splash.java" "$SRC/lostcity/DiscordSignIn.java"
cp -r "$HERE/vanilla/"* "$SRC/"
mkdir -p "$SRC/browser" && cp "$HERE/browser/"*.java "$SRC/browser/"

echo "==> applying the browser patch"
# The parts a shim cannot reach: TeaVM ships its own java.awt.Color, System, File and
# ConcurrentHashMap, and its versions lack what the desktop client uses. See TEAVM.md.
(cd "$SRC" && patch -p1 --no-backup-if-mismatch < "$HERE/vanilla-client.patch")

echo "==> building"
cd "$HERE" && mvn -B package
echo
cp "$HERE/index.html" "$HERE/target/js/index.html"
echo "built: $HERE/target/js/client.js"
echo "serve: that directory, with /crc* and the game WebSocket proxied to the engine"
