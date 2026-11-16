# A local world to test clients against

The live server is not a test rig. Logging a client into it means creating accounts on a
production database and putting characters in the world other people are playing in. This sets up
a complete world in a container instead, which costs about five minutes and then costs nothing.

Everything below was run on 2026-11-16 and the world came up: `World ready`, 12,669 static NPCs,
and the ts377 client authenticating against it with login response 2.

## Setup

    git clone --depth 1 -b 377-wip https://github.com/coreysho/deathplateau-content ../content
    cd <engine>
    npm install
    npx tsx tools/server/rsa.ts        # prints the modulus - keep it, the client needs it
    npm run sqlite:migrate
    npm run build                      # packs the cache from ../content, ~25s
    npx tsx src/app.ts

`.env` needs only this:

    DB_BACKEND=sqlite
    WEB_PORT=8888
    NODE_PORT=43594
    NODE_PROFILE=main
    LOGIN_SERVER=false

The engine finds content at `../content` (`BUILD_SRC_DIR`), so the clone has to be a sibling of
the engine directory.

**Unknown usernames are registered on first login** (`LoginThread.ts`), so no account setup is
needed - any name works, and the accounts only exist in the container's sqlite file.

## Pointing a client at it

Two things differ from the live server, and both bit before they were understood.

**The login keypair.** `tools/server/rsa.ts` generates a fresh one, so a client with the live
server's modulus baked in gets its login block rejected - and the engine answers that with
response **6**, "RuneScape has been updated! Please reload this page", because it sends "out of
date" on an RSA failure deliberately. A revision error looks exactly the same from the client, so
the message is worth distrusting: `World.ts` sends 6 from three different places.

`ts377-rsa-override.patch` makes the client read `__RSA_MODULUS` off the page instead, and
`entry.ts` takes it from `?rsa=<modulus>`. It has to be a getter, not a field: a static field
initialises when its module is imported, which happens before `entry.ts` runs, so a field reads
the override before anything has set it.

**The revision.** The engine takes `ENGINE_REVISION` (384) or `LOGIN_LEGACY_REVISION` (381). The
ts377 client announces 381, so it passes as-is. `ENGINE_REVISION=377` in `.env` is the documented
escape hatch if a client needs it.

## The rig

`rig/serve.js` serves the built bundle at `/ts/` and forwards everything else to a world - the
cache routes over HTTP and, importantly, the game WebSocket through an upgrade proxy, because the
client builds its socket URL from the page's own origin.

    node serve.js <dist-dir> 127.0.0.1:8888      # the local world
    node serve.js <dist-dir> play.deathplateau.com

## Where this got to

The ts377 client authenticates and the server puts the character in the world:

    [Login]: rigbase1 asked for no saved login
    login  rigbase1 at 0,3094,3106
    logout rigbase1 at 0,3094,3106 - no response for 60s (socket already gone)

That last line is the open bug, and it is a race the Java original could not have:

`Game.ts` sets `loggedIn = true` the instant the server replies 2, but the buffers the game screen
draws into are built by `method122()`, several `await`s later. In Java the login handler ran to
completion inside the client thread and no frame could be drawn in between. Here each `await`
yields, `mainLoop` paints a frame, `drawGame` -> `redrawTabs` dereferences a buffer that is still
null, and **the throw escapes the async `mainLoop` and kills it permanently**. The client never
reads or writes another packet, so `loadingStage` stays at 1, `localPlayer` stays null, and the
server times the character out after 60 seconds.

Two fixes were tried and neither worked, both reverted:

- Falling back to the login screen while the buffers are missing. Drawing the login screen calls
  `prepareTitle()`, which restarts the title flames - and `method141()`, inside the very setup
  being waited on, is waiting for those flames to stop. They chase each other forever.
- Bounding that flame wait. Login then ends with `loggedIn` false and the title sequence restarted
  from "10% Connecting to fileserver", so something further along resets the client.

The fix wants the whole login-to-game handover read as a state machine rather than another guess
at one symptom. It is the next piece of work, and the rig above makes it a fast loop.
