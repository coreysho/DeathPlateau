package jagex2.client;
import jagex2.config.*;
import jagex2.dash3d.*;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.util.*; import java.io.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// Offline render of an INVENTORY ICON with the real client code: ObjType.method230, which is the
// same call Client makes to draw a pack slot, so what comes out is what a player sees.
//
// Written 2026-10-03 after the magic shortbow (i) shipped wrong TWICE. ob2render.py cannot draw a
// textured face and says so - it skips them - so a bow whose whole visible difference is a
// textured sparkle looked fine in a contact sheet and looked like nothing in game. A renderer that
// cannot draw what the thing is made of cannot be used to check it.
//
// dir must hold what SceneRender's does, plus objs.txt ("<obj id> <debugname>" per line, from
// content/pack/obj.pack):
//   config.jag, textures.jag, models.txt, objs.txt
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.ObjIconRender <dir> <out.png> \
//        <name-or-id> [<name-or-id> ...] [--scale N] [--cols N] [--mode N]
//
// AN ENTRY MAY CARRY A CAMERA, as name@xan=448,zoom=1150,yan=0,zan=0,xof=0,yof=0 - any subset of
// those, plus model=<id> to borrow an item's config for a DIFFERENT mesh. The overrides are written
// onto the ObjType just before the render, so one sheet can hold a dozen cameras over one item, or
// one camera over a dozen shapes of it. Tuning an icon by rebuilding the cache once per candidate
// is how you end up shipping the first guess.
//
// --mode is method230's first argument and DEFAULTS TO 0, the path a pack slot takes. -1 is the
// path a cert's base icon takes and it multiplies the zoom by 1.5, so a sheet rendered at -1 comes
// out half again larger than the inventory - which is no way to judge a zoom. The icon cache is
// cleared per entry, so mode 0 still renders every camera candidate separately.
public class ObjIconRender {
    public static void main(String[] a) throws Exception {
        String dir = a[0], out = a[1];
        int scale = 6, cols = 0, mode = 0;   // cols 0 = one row
        boolean all = false;
        List<String> want = new ArrayList<>();
        for (int i = 2; i < a.length; i++) {
            if (a[i].equals("--scale")) { scale = Integer.parseInt(a[++i]); continue; }
            if (a[i].equals("--cols")) { cols = Integer.parseInt(a[++i]); continue; }
            if (a[i].equals("--mode")) { mode = Integer.parseInt(a[++i]); continue; }
            if (a[i].equals("--all")) { all = true; continue; }
            want.add(a[i]);
        }

        World.lowMem = false; World3D.lowMem = false; Pix3D.lowMem = false; LocType.lowMem = false;
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(dir, "config.jag")));
        ObjType.unpack(cfg); LocType.unpack(cfg); FloType.unpack(cfg); SeqType.unpack(cfg); VarbitType.unpack(cfg);
        Model.init(70000, null);
        for (String l : Files.readAllLines(Paths.get(dir, "models.txt"))) {
            String[] p = l.split(" ", 2);
            Model.method357(Files.readAllBytes(Paths.get(p[1])), Integer.parseInt(p[0]), (byte) 7);
        }

        Map<String, Integer> byName = new HashMap<>();
        List<String> byNameOrder = new ArrayList<>();
        for (String l : Files.readAllLines(Paths.get(dir, "objs.txt"))) {
            int sp = l.indexOf(' ');
            if (sp > 0) { byName.put(l.substring(sp + 1).trim(), Integer.parseInt(l.substring(0, sp)));
                          byNameOrder.add(l.substring(sp + 1).trim()); }
        }

        if (all) want.addAll(byNameOrder);

        // The icon raster needs the same 3D setup the client gives it, and the TEXTURES - which is
        // the entire reason this exists.
        int W = 765, H = 503;
        Pix2D.bind(W, H, new int[W * H]);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(H, W);

        int cell = 32 * scale, pad = 6;
        int nc = cols > 0 ? Math.min(cols, want.size()) : want.size();
        int nr = (want.size() + nc - 1) / nc;
        BufferedImage sheet = new BufferedImage(nc * (cell + pad) + pad, nr * (cell + pad) + pad,
                BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics2D g = sheet.createGraphics();
        g.setColor(new java.awt.Color(0x14, 0x14, 0x14));
        g.fillRect(0, 0, sheet.getWidth(), sheet.getHeight());

        for (int i = 0; i < want.size(); i++) {
            String s = want.get(i);
            String cam = null;
            int at = s.indexOf('@');
            if (at >= 0) { cam = s.substring(at + 1); s = s.substring(0, at); }
            Integer id = byName.get(s);
            if (id == null) id = Integer.parseInt(s);
            // Both caches are keyed by obj id ALONE, so without this two cameras on one item would
            // hand back the same picture - and the same lit model - twice. get()'s own ten-slot
            // cache is what makes the override stick: method230 asks get() for the type again and
            // is given back the very instance we edited.
            ObjType.field828.clear();
            ObjType.field819.clear();
            if (cam != null) {
                ObjType t = ObjType.get(id);
                for (String kv : cam.split(",")) {
                    String[] p = kv.split("=", 2);
                    int v = Integer.parseInt(p[1].trim());
                    switch (p[0].trim()) {
                        case "xan":  t.field841 = v; break;   // 2dxan - the camera's pitch down from level
                        case "yan":  t.field838 = v; break;   // 2dyan - spins the model on the spot
                        case "zan":  t.field821 = v; break;   // 2dzan - rolls it in the frame
                        case "zoom": t.field851 = v; break;   // 2dzoom - bigger number, smaller item
                        case "xof":  t.field809 = v; break;   // 2dxof
                        case "yof":  t.field822 = v; break;   // 2dyof
                        case "model": t.field842 = v; break;  // the mesh itself, by model.pack id
                        default: throw new IllegalArgumentException("no such camera field: " + p[0]);
                    }
                }
            }
            // arg2 10 is the stack count, which only matters for a stackable's number sprite.
            // ONE BAD OBJ MUST NOT END THE RUN. method230 resolves certlink/templates through
            // method224, and an obj whose link points at -1 throws out of ObjType.get - which killed
            // a whole 2,290-item sheet on its first bad entry. Rendering a contact sheet is a survey:
            // the useful answer is "these 2,288 drew and these two did not", not a stack trace.
            Pix32 icon = null;
            try { icon = ObjType.method230(mode, 10, id); }
            catch (Exception | Error e) { System.out.println("threw for " + s + ": " + e); }
            if (icon == null) { System.out.println("no icon for " + s); continue; }
            BufferedImage one = new BufferedImage(32, 32, BufferedImage.TYPE_INT_RGB);
            // pixel 0 is the icon's own transparent, and 1 is the outline it draws around itself
            for (int y = 0; y < 32; y++) for (int x = 0; x < 32; x++) {
                int p = icon.pixels[y * 32 + x];
                one.setRGB(x, y, p == 0 ? 0x141414 : p);
            }
            java.awt.Image big = one.getScaledInstance(cell, cell, java.awt.Image.SCALE_REPLICATE);
            g.drawImage(big, pad + (i % nc) * (cell + pad), pad + (i / nc) * (cell + pad), null);
        }
        g.dispose();
        ImageIO.write(sheet, "png", new File(out));
        System.out.println("wrote " + out);
    }
}
