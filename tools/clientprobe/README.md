# clientprobe - render a model with the client's own code, from the client's own cache

Written while chasing the Infernal cape, which was invisible in game and hid the helmet while
rendering perfectly in `tools/models/ob2render.py`. The difference is that ob2render is a
reimplementation: it ignores back-face culling, alpha and the priority sort. This runs the REAL
`jagex2.graphics.Pix3D` and `jagex2.dash3d.Model`, headless, against the cache the client
downloaded - so what it draws is what the client draws.

It found, in order: that the texture was loading fine (51 slots, palette 205); that the icon painted
6 pixels of 1024 where the Fire cape painted 362; that the worn model was solid from one side and
5 pixels from the other; and that reversing the winding fixed both, because the 377 client culls
back faces and modern OSRS cloth is a single sheet.

## Setting it up

1. Extract the archives and models from the client's file store (`C:\.file_store_32`) with
   `extract.py`. It writes `config.jag`, `textures.jag` and `models/<id>.ob2` next to itself:

       python3 extract.py "C:\.file_store_32" <model id> [<model id> ...]

   The archives are index 0 files 2 (config) and 6 (textures); on-demand models are index 1,
   gzip, one file per model id.

2. Compile the client's sources together with one of the probes:

       javac -nowarn -d build $(find javaclient/src/main/java -name "*.java") clientprobe/Final.java
       java -cp build Final

## The probes

- `Final.java` - one model at a time: the inventory icon at the obj record's own angles, and the
  worn model from the front and the back, with pixel counts and a PNG.
- `Composite.java` - several models merged the way `ClientPlayer` builds an appearance, drawn at
  four yaws. This is the one that shows whether a cape is where a cape should be.

Both take model ids by editing the array at the top; both write PNGs beside themselves.

## What to watch for

- **A pixel count near zero from one side** is a culling problem: the sheet is single-layered and
  wound the wrong way. Reverse b and c.
- **A count that is high from both sides but lower than the sum** is z-fighting: two layers at the
  same depth. Give the second layer thickness instead of duplicating in place.
- **An exception swallowed by `Model.method380`** (it catches and discards) truncates a model
  silently. Put a print in that catch in a throwaway build if a model is partly drawn.
