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
//        <name-or-id> [<name-or-id> ...] [--scale N]
public class ObjIconRender {
    public static void main(String[] a) throws Exception {
        String dir = a[0], out = a[1];
        int scale = 6;
        List<String> want = new ArrayList<>();
        for (int i = 2; i < a.length; i++) {
            if (a[i].equals("--scale")) { scale = Integer.parseInt(a[++i]); continue; }
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
        for (String l : Files.readAllLines(Paths.get(dir, "objs.txt"))) {
            int sp = l.indexOf(' ');
            if (sp > 0) byName.put(l.substring(sp + 1).trim(), Integer.parseInt(l.substring(0, sp)));
        }

        // The icon raster needs the same 3D setup the client gives it, and the TEXTURES - which is
        // the entire reason this exists.
        int W = 765, H = 503;
        Pix2D.bind(W, H, new int[W * H]);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(H, W);

        int cell = 32 * scale, pad = 6;
        BufferedImage sheet = new BufferedImage(want.size() * (cell + pad) + pad, cell + pad * 2,
                BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics2D g = sheet.createGraphics();
        g.setColor(new java.awt.Color(0x14, 0x14, 0x14));
        g.fillRect(0, 0, sheet.getWidth(), sheet.getHeight());

        for (int i = 0; i < want.size(); i++) {
            String s = want.get(i);
            Integer id = byName.get(s);
            if (id == null) id = Integer.parseInt(s);
            // arg1 -1 is the "no cache, 1.5x zoom" path the client uses for a cert's base icon;
            // arg2 10 is the stack count, which only matters for a stackable's number sprite.
            Pix32 icon = ObjType.method230(-1, 10, id);
            if (icon == null) { System.out.println("no icon for " + s); continue; }
            BufferedImage one = new BufferedImage(32, 32, BufferedImage.TYPE_INT_RGB);
            // pixel 0 is the icon's own transparent, and 1 is the outline it draws around itself
            for (int y = 0; y < 32; y++) for (int x = 0; x < 32; x++) {
                int p = icon.pixels[y * 32 + x];
                one.setRGB(x, y, p == 0 ? 0x141414 : p);
            }
            java.awt.Image big = one.getScaledInstance(cell, cell, java.awt.Image.SCALE_REPLICATE);
            g.drawImage(big, pad + i * (cell + pad), pad, null);
            System.out.println("drew " + s + " (obj " + id + ")");
        }
        g.dispose();
        ImageIO.write(sheet, "png", new File(out));
        System.out.println("wrote " + out);
    }
}
