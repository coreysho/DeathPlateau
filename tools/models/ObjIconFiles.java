package jagex2.client;
import jagex2.config.*;
import jagex2.dash3d.*;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.util.*; import java.io.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// Every inventory icon as its own transparent PNG, drawn by the real client code - ObjType.method230,
// the same call that draws a pack slot.
//
// WHY NOT ObjIconRender. That one is a survey: it lays items out on a dark contact sheet with
// padding so a person can squint at a hundred at once and spot the wrong one. The sheet is opaque
// (TYPE_INT_RGB on 0x141414) and the padding is baked in, neither of which a web page can use - an
// icon has to sit on whatever colour the table row happens to be. Same renderer, different output.
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.ObjIconFiles <dir> <outdir> [--ids a,b,c]
//
// dir holds what tools/models/objicondir.py writes: config.jag, textures.jag, models.txt, objs.txt.
// Without --ids every obj in objs.txt is rendered. Files are named by obj ID, not by debug name,
// because the id is what the game records in a trade and a drop table.
//
// WRITTEN AT 32x32, the size the client draws, and not scaled up. The art is pixel art: a browser
// told to show it larger with image-rendering: pixelated gets exactly what a doubled PNG would
// give, without shipping four times the bytes.
public class ObjIconFiles {
    public static void main(String[] a) throws Exception {
        String dir = a[0], outDir = a[1];
        List<String> only = null;
        for (int i = 2; i < a.length; i++) {
            if (a[i].equals("--ids")) { only = Arrays.asList(a[++i].split(",")); continue; }
            throw new IllegalArgumentException("no such flag: " + a[i]);
        }

        World.lowMem = false; World3D.lowMem = false; Pix3D.lowMem = false; LocType.lowMem = false;
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(dir, "config.jag")));
        ObjType.unpack(cfg); LocType.unpack(cfg); FloType.unpack(cfg); SeqType.unpack(cfg); VarbitType.unpack(cfg);
        Model.init(70000, null);
        for (String l : Files.readAllLines(Paths.get(dir, "models.txt"))) {
            String[] p = l.split(" ", 2);
            Model.method357(Files.readAllBytes(Paths.get(p[1])), Integer.parseInt(p[0]), (byte) 7);
        }

        List<Integer> ids = new ArrayList<>();
        for (String l : Files.readAllLines(Paths.get(dir, "objs.txt"))) {
            int sp = l.indexOf(' ');
            if (sp > 0) ids.add(Integer.parseInt(l.substring(0, sp)));
        }
        if (only != null) {
            Set<Integer> want = new HashSet<>();
            for (String s : only) want.add(Integer.parseInt(s.trim()));
            ids.removeIf(id -> !want.contains(id));
        }

        int W = 765, H = 503;
        Pix2D.bind(W, H, new int[W * H]);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(H, W);

        Files.createDirectories(Paths.get(outDir));
        int wrote = 0, none = 0, threw = 0, blank = 0;
        for (int id : ids) {
            // ONE BAD OBJ MUST NOT END THE RUN, for the reason ObjIconRender gives: an obj whose
            // certlink points at -1 throws out of ObjType.get, and nine thousand icons should not
            // be lost to one of them.
            ObjType.field828.clear();
            ObjType.field819.clear();
            Pix32 icon = null;
            try { icon = ObjType.method230(0, 10, id); }
            catch (Exception | Error e) { threw++; continue; }
            if (icon == null) { none++; continue; }

            BufferedImage one = new BufferedImage(32, 32, BufferedImage.TYPE_INT_ARGB);
            boolean any = false;
            for (int y = 0; y < 32; y++) for (int x = 0; x < 32; x++) {
                int p = icon.pixels[y * 32 + x];
                // 0 is the icon's own transparent. Everything else is opaque colour - the client
                // has no partial alpha here, so this is a straight two-way split.
                if (p == 0) {
                    one.setRGB(x, y, 0);
                } else {
                    one.setRGB(x, y, 0xFF000000 | p);
                    any = true;
                }
            }
            // An obj that draws nothing at all is a placeholder, a template half, or a mesh that
            // did not load. Writing a 32x32 of pure transparency would look like a working icon
            // that happens to be invisible, which is worse than having no file.
            if (!any) { blank++; continue; }

            ImageIO.write(one, "png", new File(outDir, id + ".png"));
            wrote++;
        }
        System.out.println("wrote " + wrote + " icons to " + outDir);
        System.out.println("  " + none + " had no icon, " + blank + " drew nothing, " + threw + " threw");
    }
}
