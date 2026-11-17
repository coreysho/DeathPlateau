#!/usr/bin/env bash
# Build the browser shim jar that stands in for the JDK classes TeaVM has no implementation of.
#
# It must be compiled with JDK 8: javac 9+ refuses `package java.awt;` with "package exists in
# another module: java.desktop". JDK 8 has no module system and allows it. This matters only for
# building the shim - the client itself compiles with any modern JDK, because javac resolves AWT
# from the platform while TeaVM resolves it from its own classpath, which is where this jar goes.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
JDK8="${JDK8:?set JDK8 to a JDK 8 home}"
rm -rf "$HERE/out" && mkdir -p "$HERE/out"
"$JDK8/bin/javac" -nowarn -d "$HERE/out" $(find "$HERE" -name "*.java" -not -path "*/out/*")
(cd "$HERE/out" && "$JDK8/bin/jar" cf "$HERE/awtshim.jar" .)
echo "built: $HERE/awtshim.jar ($(find "$HERE/out" -name '*.class' | wc -l) classes)"
