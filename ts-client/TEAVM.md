# Compiling our own client to JavaScript

The question behind this spike was Corey's: *"are you not using our actual client?"* The answer was
no - all the work before it went into ts377, a machine translation of a **stock** 377 client, into
which I had been hand-copying DeathPlateau's features one at a time, reading each one out of
`deathplateau-client` first. Eight or nine times. That is the wrong direction, and the right
question is whether our own client can be compiled to the browser directly.

## JSweet is not available

ts377 was produced with JSweet (its output style is unmistakable - the `/* equals */` wrappers, the
`charCodeAt` guards). Using the same tool on our client is not possible:

- `repository.jsweet.org` resolves but serves a TLS certificate for a different hostname
- `www.jsweet.org` fails TLS outright
- both the 2.x and 3.x maven plugins hard-depend on `org.jsweet.ext:typescript.java-ts.core`,
  which is on that host only - not Maven Central, not Sonatype, not JitPack

This is not our network policy: this environment has unrestricted egress. The project's
infrastructure is simply broken.

## TeaVM compiles it

TeaVM 0.16.0 is on Maven Central and maintained. `teavm/` holds the spike; `setup.sh` copies the
client's sources and builds.

**It needs JDK 17+.** On JDK 11 its own maven plugin fails to load with *"Type
org.teavm.maven.TeaVMCompileMojo not present"*, which reads like a missing artifact and is not one.
That cost a round; JDK 21 works as-is.

### The protocol core runs, and is correct

Compiling `jagex2/io`, `jagex2/wordenc`, `jagex2/datastruct`, `jagex2/jstring` and exercising them
from a `main`: 55 classes, 681 methods, 53 KB of JavaScript, and in node:

    wrote 8 bytes
    g1=42 g2=1337 g4=123456789 g1_alt1=7
    format=[Hello WORLD 123] packed=15 unpack=[Hello WORLD 123]
    CORE OK

That is **our** `Packet`, alt encodings included, and **our** `ChatText` - the revision-381 chat
codec whose absence from ts377 silently corrupted every chat line in both directions and took a
byte-level trace to find. Here it is simply correct, because it is the same code the engine was
written against.

### The whole client is nine errors away

Pointing TeaVM at `jagex2.client.Client` over all 179 source files produces exactly nine errors:

    GameShell extends java.applet.Applet          - missing in the classpath
    GameShell implements MouseListener            -   "
    GameShell implements MouseMotionListener      -   "
    GameShell implements MouseWheelListener       -   "
    GameShell implements KeyListener              -   "
    GameShell implements FocusListener            -   "
    GameShell implements WindowListener           -   "
    java.net.InetAddress was not found            - x2

Everything else is accepted: `Client.java` entire, the `dash3d` renderer, the config decoders, the
protocol, the plugin code. The AWT problem is not spread through the client - it is the shell class
and nothing else.

Of the 21 files that import AWT at all, **ten are the plugin desktop UI** (`plugin/ui/*` - Swing
panels for the plugin hub and sidebar) and one is `worldmap/MapWindow`. A browser build does not
need any of them. The rest use `Graphics`/`Color`/`Dimension` for drawing, which is what a canvas
surface replaces.

## What this changes

Every bug fixed by hand in ts377 over the last two days - the chat codec in both directions,
VARP_BATCH, MESSAGE_CLAN, UPDATE_CLANCHANNEL, the clan tab, the '~' the chatbox dropped so every
developer command died silently - exists and is correct in our client already. On this route they
are not work at all.

What remains is one piece of real work, done once: a browser shell to stand in for `GameShell`'s
AWT base (canvas for the drawing surface, DOM events for the six listener interfaces), a stub for
`InetAddress`, and the desktop plugin UI left out of the build. That is the same shim ts377's
author wrote - but against our code, so nothing has to be ported into it afterwards.

## The AWT shim

`teavm/awtshim/` is 31 classes, 12 KB compiled, and it clears the entire AWT blocker list. With it
on TeaVM's classpath, `GameShell extends java.applet.Applet` and all six listener interfaces link.

It has to be built with **JDK 8**: javac 9+ refuses `package java.awt;` with "package exists in
another module: java.desktop", while JDK 8 has no module system and allows it. This only affects
building the shim. The client compiles with any modern JDK, because javac resolves AWT from the
platform while TeaVM resolves it from its own classpath - which is where the jar goes.

## What still blocks a full link

Three places, and all three are platform, not game:

    jagex2/client/ViewBox.java     extends javax.swing.JFrame - the desktop window
    jagex2/graphics/PixMap.java    java.awt.image producer/consumer - the drawing surface
    sign/MidiPlayer.java           javax.sound.midi - the music sequencer

Each needs a browser equivalent rather than a stub: a canvas-backed window, a canvas-backed pixel
surface, and Web Audio. That is the shell shim, and it is the real remaining work on this route.

## The size is still unknown, and it is the number that decides this

Three attempts, none of them trustworthy:

| what was built | classes | methods | bytes |
|---|---|---|---|
| protocol core, exercised from a main | 55 | 681 | 53 KB |
| renderer + config referenced by class literal | 83 | 871 | 57 KB |
| the same, with `classesToPreserve` over 60 game classes | 109 | 980 | 74 KB |

All three understate it. TeaVM's dead-code elimination is **method-level and reachability-driven**:
a `Class` literal keeps a class from being removed but compiles none of its methods, and
`classesToPreserve` does the same. Only code actually called from `main` is compiled - and `main`
here is a probe, not the client.

Building from the real entry point emits nothing at all: TeaVM reports "Output file built with
errors" and writes no file, and `stopOnErrors=false` does not change that - it controls whether the
*maven build* fails, not whether output is written.

**So there is no honest full-client size yet, and there will not be one until the three classes
above have browser equivalents and the client links cleanly.** Everything else about this route
looks right; this is the measurement that decides whether it beats CheerpJ, and it is still
outstanding.

## Also not yet known

- Rendering performance. No drawing code has been compiled or run.
- Whether the sound path can simply be left out of a first build.
