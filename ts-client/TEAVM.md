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

## It runs in a browser, and it draws

The client starts in a page and renders its own loading screen - the backdrop, the progress bar,
"Connecting to update server" - from the same Java that runs on the desktop. `teavm-loading.png`
is the screenshot of that moment. It no longer stops there: the client loads, logs in, and plays.
`teavm-ingame.png` is the game world - the tutorial room, the guide, the minimap, the sidebar.

`browser/` is the shell that makes that possible, and it is small:

**`BrowserShell`** creates the canvas, installs the pixel path and routes DOM events into the AWT
listener interfaces GameShell already implements. Mouse coordinates are scaled into canvas space,
because the page sizes the canvas with CSS and `offsetX` is in CSS pixels - the same off-by-the-
stretch-ratio bug that cost a round in the ts377 client.

**`BrowserSocket`** is WsSocket's four CheerpJ natives rewritten as `@JSBody`. Bytes still cross as
base64, because that is what the client already encodes and the protocol was not worth re-cutting.

**`awtbridge`** is the piece that makes the whole arrangement work, and it exists because of an
asymmetry worth writing down: **javac resolves `java.awt.*` from the platform, TeaVM resolves it
from the shim jar.** So the browser shell, compiled by javac, sees the REAL AWT and cannot touch
anything the shim adds - while the shim, compiled by JDK 8 against itself, can. A package outside
`java.*` is visible to both, so every call between them goes through `awtbridge.Events`.

## It plays

A browser logs in to a world, walks, opens the sidebar tabs and raises a right-click menu, and the
server sees every one of those as it would from the desktop client:

```
[SESSION] logged in as "teavm5"
[ACTION] Accept    | player=(3094,3106,0) | action=352
[ACTION] Walk here | player=(3094,3106,0) | action=14  paramB=258 paramC=165
[ACTION] Walk here | player=(3095,3103,0) | action=14  paramB=400 paramC=260
```

Rendering is not the bottleneck anyone feared: the canvas takes **~97 `putImageData` calls a
second** with a full scene, a player, an NPC and the minimap on screen - the client's own 50Hz
loop, drawing more than once a frame, never waiting on the browser.

## Four bugs stood between the loading screen and the game

Each one looked like something else, which is why they are written down.

**`java.net.Socket` had no `protected Socket(SocketImpl)`.** `WsSocket` calls `super((SocketImpl)
null)` - the documented way to build a Socket with no implementation underneath. javac resolves
that constructor from the platform and is happy; TeaVM resolves it from the shim jar, where it did
not exist, and quietly compiled a method that throws. The on-demand thread died on its first call
with no message anywhere. The fix is three lines: `SocketImpl` as an empty name, and the
constructor beside the others.

**A WebSocket is not open when `new WebSocket()` returns.** The client writes its stream-type byte
(15 for the update stream, 14 for login) the instant `openSocket` returns, and `BrowserSocket.write`
dropped anything sent before `onopen`. The server then waited for a type byte that never came and
the client waited for a reply it would never get. Writes are now queued and flushed on open.

**TeaVM has no working `ConcurrentLinkedQueue`.** The name links; `poll()` is not there. It shows
up as `TypeError: var$5.$wanted.$poll is not a function` on the first frame that draws the world
map, repeating until the shell gives up. A page runs the client's threads cooperatively, so
`LinkedList` is safe and is what the browser build uses.

**The page moved the canvas under its own clicks.** `index.html` logs the client's console output
into a div above the canvas, and that div grew as lines arrived - so the canvas slid down the page
and every click landed a little higher in the client than where it was aimed. Fixed height.

## A phone can play it

The reason this client exists is that CheerpJ takes half an hour to start on a
phone. So the browser shell has the three things a phone needs and a desktop does not:

**Touch** (`BrowserTouch`). A tap is a left click, a press held still is a RIGHT click so the
menu opens under the finger, a press and drag is a drag, and two fingers turn the camera. The
decision comes from movement before timing: a finger that has wandered more than a few pixels is a
drag and can never become a menu, so a slowly dragged scroll bar does not open one halfway down.

**A keyboard** (`BrowserKeyboard`). A real `<input>` kept out of sight, because that is the only
thing that raises a phone's keyboard. Characters are read from the `input` event rather than from
`keydown`, since most Android keyboards report every key as 229 and put the character only in the
event that follows; Backspace and Enter do arrive properly and are taken from `keydown`.

**A screen that is not 765x503.** The canvas keeps those pixels and CSS stretches it to whatever
screen this is, letterboxed. Every coordinate coming in is divided by that stretch.

`jagex2/client/BrowserInput.java` is the same problem solved for CheerpJ, and it is worth reading
for why it is harder there: that runtime ignores synthetic events, so the page has to write static
fields and the client polls them. The AWT here is this build's own shim, so an event made up in
JavaScript is as real as any other. The camera is the exception - it still goes through
BrowserInput's running totals, because GameShell already folds those into its middle-drag.

## Sound

The client mixes all of its own audio and then asks `javax.sound.sampled` for somewhere to put it,
so nothing of the sound engine needed porting - only the speaker at the end of it. `BrowserAudio`
schedules each chunk as an AudioBuffer at an exact time on the context's clock, each starting
where the last ended.

The part that matters is not handing bytes over too fast. On a desktop the mixer thread is paced
by the line blocking when the card's buffer is full; nothing in a page blocks, and the mixer is a
`while (true)` with no clock of its own. Left alone it mixes hours of audio a second and starves
every other thread. So the line asks how much is still unplayed and sleeps until under a quarter
of a second remains. In game the schedule sits 0.25s ahead of the clock and tracks it.

Music is still silent: MIDI needs a synthesiser and a soundbank, which is its own piece of work.

## Running it

```
JDK8=/path/to/jdk8 ./setup.sh          # build (JDK 8 for the shim, 17+ for TeaVM)
./install.sh [path-to-engine]          # copy the two files into the world's public/teavm/
```

The engine serves `public/` statically, so the client needs no route of its own: it lands beside
the cache routes it fetches and the WebSocket it plays over, all on one origin. Open `/teavm/`.

Against a world you host, two things have to agree or the server answers login code **6**, which
the client shows as "RuneScape has been updated! Please reload this page" - a message that sends
you looking at caches and cannot be fixed by reloading:

- **The revision.** This client logs in as 384, so the engine needs `ENGINE_REVISION=384`.
- **The login key.** The login block is RSA-encrypted with a modulus compiled into the client, and
  an engine you run yourself has its own pair from `npm run rsa`. `./local-rsa.sh <modulus>` points
  a local build at it; the committed source keeps the production key.

The engine tells those apart even though the client cannot: revision, cache CRC, and an RSA block
that will not decrypt are three separate refusals in `World.onClientData`.

## The numbers

| | this | CheerpJ |
| --- | --- | --- |
| download | 1.3 MB, **0.35 MB gzipped** | 18.9 MB runtime + the jar |
| title screen | **7.4s** | ~30 minutes on a phone |
| title screen, processor throttled 4x | **32s** | - |
| drawing, a full scene | ~98 blits a second | - |
| drawing, processor throttled 4x | 64 blits a second | - |

Throttling the processor to a quarter speed is Chromium's stand-in for a mid-range phone, and it
is the row that matters: half a minute to the title screen where CheerpJ took half an hour, and
the game still drawing fast enough to play.

Four and a half minutes of walking the world from a phone profile: 41 actions, **0 errors**, heap
flat at 228 MB, still drawing at 98 blits a second at the end, with new map squares streaming in
over an update socket that is dropped and reopened as the client goes.

## What is still unknown

- Music. Sound effects and ambience play; MIDI does not.
- Nobody has played this on a real phone yet - every touch, keystroke and gesture here was
  measured in Chromium's phone emulation, which is not the same as a thumb on glass.
- Load time on a phone's processor. 7.4s is a desktop unpacking the cache.
