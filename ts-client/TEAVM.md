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

`teavm/awtshim/` is 72 source files, 76 classes compiled. It must be built with **JDK 8**: javac 9+
refuses `package java.awt;` with "package exists in another module: java.desktop". That affects
only the shim - the client compiles against the platform AWT, while TeaVM links against this jar.

The interesting part is `PixMap`. In AWT it pushes pixels through an `ImageProducer`/`ImageConsumer`
handshake into an opaque `Image`; in a browser that whole dance is unnecessary, because the `int[]`
it holds *is* canvas `ImageData`. The shim implements the handshake so **`PixMap` needs no changes
at all**: `Image` is itself the consumer, keeps the pixels, and `Graphics.drawImage` hands them to
a `Blitter` the browser shell sets. One hook, and every pixel the client draws has somewhere to go.

## Three classes TeaVM owns, which a shim cannot reach

TeaVM ships its own `java.awt.Color`, `Dimension` and `Point` (`TColor`, `TDimension`, `TPoint` in
`teavm-classlib`), and they win over anything on the classpath. `TColor` has `BLACK` but not
`black`, and no `getRGB()`. Same story for `System.exit`, `File.setReadable` and
`ConcurrentHashMap.newKeySet`.

So a browser build is **not purely additive**: it needs a small patch to our source as well as the
shim. Measured, that patch is 16 `Color.black`/`white`/`yellow` constants, 3 `System.exit` calls,
2 `setReadable` calls, 2 `newKeySet` calls and one `getRGB`. All of it in loading-screen drawing,
window teardown and the desktop launcher - none in the game.

## It links, and here is the number

**The vanilla client compiles to JavaScript: 731 classes, 6,530 methods.**

    unminified   4.93 MB raw    0.60 MB gzipped
    minified     1.22 MB raw    0.34 MB gzipped

CheerpJ's runtime, the thing this replaces, is **18.9 MB** - and that is before the client itself.
What a browser downloads goes from 18.9 MB to **0.34 MB**, about fifty-five times less.

That was the measurement the whole route hung on, and it is decisive. It does not say the client
*runs* - nothing has been executed yet - but it settles whether the approach is worth running.

## What "vanilla only" meant

Corey's call, and it cut the work in half: no plugin panel and no plugins until the vanilla client
is up. The whole `jagex2/client/plugin` tree goes, along with `MapWindow` (a second desktop
window) and the launcher's Swing chrome. `vanilla/` holds small stubs for the types the client
still names - `PluginManager` answers "nothing is running" to every hook, which is exactly what
the real one does with no plugin loaded, so the client takes its own path in every case.

That also removed most of the awkward dependencies at a stroke: `URLClassLoader`, `ProcessBuilder`
and the plugin hub's file moves were all plugin machinery.

## The three pieces

    awtshim/            91 classes. java.awt, applet, swing, sound, crypto, imageio and the odd
                        java.net/java.util.concurrent gap. Built with JDK 8 - javac 9+ refuses
                        `package java.awt;`
    vanilla/            the stubs that replace the plugin and desktop tree
    vanilla-client.patch  what a shim cannot reach: TeaVM ships its own java.awt.Color, System,
                        File and ConcurrentHashMap, and its versions lack `Color.black`,
                        `System.exit`, `File.setWritable` and `newKeySet`. Also the four WsSocket
                        and three BrowserInput natives, which are CheerpJ's bridge and become
                        @JSBody in a TeaVM build

`setup.sh` does all of it from a clean checkout.

The `PixMap` trick is the part worth keeping: in AWT it pushes pixels through an
`ImageProducer`/`ImageConsumer` handshake, and in a browser that `int[]` *is* canvas `ImageData`.
The shim implements the handshake, so **`PixMap` itself needs no changes** - `Image` is the
consumer, keeps the pixels, and `Graphics.drawImage` hands them to a `Blitter` the browser shell
sets.

## What is still unknown

- **It has not been run.** Linking is not working. The next step is a browser shell: a canvas, the
  `Blitter`, DOM events into `GameShell`'s six listener interfaces, and `@JSBody` WebSocket methods
  for `WsSocket`.
- Rendering performance. The 10-13 ms per frame measured on ts377 says what a software rasteriser
  costs in JavaScript, but TeaVM's output is a different compiler's and the number will differ.
- Sound is stubbed, not implemented.
