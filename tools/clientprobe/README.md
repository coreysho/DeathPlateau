# clientprobe - render a model with the client's own code, from the client's own cache

`tools/models/ob2render.py` is a reimplementation: it ignores back-face culling, alpha and the
priority sort, and it cannot fail the way the client fails. This runs the REAL
`jagex2.graphics.Pix3D` and `jagex2.dash3d.Model`, headless, against the cache the client
downloaded - so what it draws is what the client draws.

It was written while chasing the Infernal cape, which rendered perfectly in `ob2render.py` and was
invisible in game (and took the wearer's helmet with it). The cause was one line in
`Pix3D.getTexels`: `texturePalette[id][textures[id].pixels[i]]`, where `pixels` is a `byte[]` of
palette indices, so a texture with more than 128 colours indexes with a negative number and throws
inside the scene raster - where `Model.method380` catches and discards. Read without the exception,
the pixel counts looked exactly like a culling bug, and a winding "fix" was shipped on them.

## Three rules, each of which cost a day

1. **`Model.method380` eats exceptions.** Any number that came through it may be a crash. Run
   `instrument.py` over the client's sources first and look at `BOOM` before believing anything.
   A priority whose `QUEUED` is far above its `DRAWN` is a model dying mid-draw.
2. **One model, one view, one JVM.** `Pix3D` and `Model` keep static state between draws: the same
   bytes measured twice in one process gave 5 px and 703 px. Every probe here draws once and exits.
3. **Look at the picture, in colour, on a background that is not black.** Pixel counts count
   `> 1`, so a nearly-black surface on a black background counts as nothing at all. The probes fill
   with a mid blue.

And for imported meshes specifically: the converter's winding is faithful - it reproduces 377's own
Fire cape face for face. **Do not reverse an imported mesh's winding** on a pixel count alone.

## Setting it up

1. Extract the archives and models from the client's file store (`C:\.file_store_32`) with
   `extract.py`. It writes `config.jag`, `textures.jag` and `models/<id>.ob2` next to itself:

       python3 extract.py "C:\.file_store_32" <model id> [<model id> ...]

   The archives are index 0 files 2 (config) and 6 (textures); on-demand models are index 1,
   gzip, one file per model id.

2. Compile the client's sources with the probes:

       javac -nowarn -d build $(find ../../javaclient/src/main/java -name "*.java") *.java
       java -Dprobe.dir=. -cp build Cape 9638 1024 out.png

   For the counters, patch a throwaway copy of the sources first:

       python3 instrument.py ../../javaclient dbgsrc
       javac -nowarn -d dbuild $(find dbgsrc -name "*.java") Dbg.java
       java -Dprobe.dir=. -cp dbuild Dbg 9638 1024

## The probes

- `Cape.java <model> <yaw> <out.png>` - one worn model, centred and whole in frame, one yaw.
- `Icon.java <obj> <model> <out.png>` - the inventory icon at the obj record's own angles and zoom,
  the way `ObjType` builds it, scaled up 6x to look at.
- `Dbg.java <model> <yaw>` - the same draw, no picture: culled / queued / drawn per priority, and
  what the catch swallowed. Needs `instrument.py`'s sources.
- `Composite.java` - several models merged the way `ClientPlayer` builds an appearance, four yaws
  in one image. Useful for placement, not for judging a surface: it draws repeatedly in one JVM
  (see rule 2) and the body parts crowd the frame.
- `Final.java` - the original one-model-at-a-time probe, kept for its icon-and-both-sides summary.
- `layers.py` - one .ob2 per priority group of an OSRS model, other groups collapsed to a point,
  so each layer can be drawn alone. This is the probe that broke the wrong diagnosis.

## Reading the numbers

Compare against a 377-era item of the same kind at the same yaws - the Fire cape (`9638` manwear,
`9631` inventory, obj `6570`) for anything worn on the back.

- **A count near zero from one side, with `BOOM=null`**, is genuine culling: that side's sheet is
  absent. Check whether the model has a second layer wound the other way before touching anything.
- **A count near zero with an exception in `BOOM`** is the client throwing, and the geometry is
  probably innocent.
- **High from both sides but well below the sum** is z-fighting: two layers at the same depth.
