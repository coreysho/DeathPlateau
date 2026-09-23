package jagex2.client;

import jagex2.config.*; import jagex2.graphics.*; import jagex2.io.*;
import java.io.*; import java.nio.file.*; import java.util.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// Draw a side-tab interface with the client's own Component and Client.drawInterface, on the stone
// the client puts behind every tab (media "invback"), with the interface's client scripts run against
// a player you describe - so an icon is lit exactly when the client would light it.
//
//   java -cp <client classes>;. jagex2.client.IfRender <data/pack/client> <content> <out.png> <interface> [options]
//     magic=<level>          every skill at 99 except Magic (default 99)
//     runes=<obj>:<n>,...    the pack (default: nothing)
//     hover=<layer>          show this hidden layer, as the client does while the mouse is over its button
//
// Written for the Lunar spellbook (LostCityServer tools/models/genlunar474.py).
public class IfRender {
    public static void main(String[] a) throws Exception {
        Path data = Paths.get(a[0]), content = Paths.get(a[1]);
        String out = a[2], iface = a[3];
        int magic = 99;
        String runes = "", hover = null;
        for (int i = 4; i < a.length; i++) {
            if (a[i].startsWith("magic=")) magic = Integer.parseInt(a[i].substring(6));
            if (a[i].startsWith("runes=")) runes = a[i].substring(6);
            if (a[i].startsWith("hover=")) hover = a[i].substring(6);
        }
        Jagfile title = new Jagfile(Files.readAllBytes(data.resolve("title")));
        Jagfile media = new Jagfile(Files.readAllBytes(data.resolve("media")));
        Jagfile config = new Jagfile(Files.readAllBytes(data.resolve("config")));
        ObjType.unpack(config);
        PixFont[] fonts = { new PixFont(false, title, "p11_full"), new PixFont(false, title, "p12_full"),
                            new PixFont(false, title, "b12_full"), new PixFont(true, title, "q8_full") };
        Component.unpack(fonts, new Jagfile(Files.readAllBytes(data.resolve("interface"))), media);

        Map<String, Integer> ids = new HashMap<>(), objs = new HashMap<>();
        for (String l : Files.readAllLines(content.resolve("pack/interface.pack"))) {
            int eq = l.indexOf('=');
            if (eq > 0) ids.put(l.substring(eq + 1).trim(), Integer.parseInt(l.substring(0, eq)));
        }
        for (String l : Files.readAllLines(content.resolve("pack/obj.pack"))) {
            int eq = l.indexOf('=');
            if (eq > 0) objs.put(l.substring(eq + 1).trim(), Integer.parseInt(l.substring(0, eq)));
        }

        sun.misc.Unsafe u; java.lang.reflect.Field f = sun.misc.Unsafe.class.getDeclaredField("theUnsafe"); f.setAccessible(true); u = (sun.misc.Unsafe) f.get(null);
        Client c = (Client) u.allocateInstance(Client.class);
        c.skillLevel = new int[50]; c.skillBaseLevel = new int[50]; c.skillExperience = new int[50]; c.varps = new int[5000];
        Arrays.fill(c.skillLevel, 99); Arrays.fill(c.skillBaseLevel, 99);
        c.skillLevel[6] = magic; c.skillBaseLevel[6] = magic;
        Client.membersWorld = true;
        Component inv = Component.get(ids.get("inventory:inv"));
        int slot = 0;
        if (!runes.isEmpty()) for (String r : runes.split(",")) {
            String[] p = r.split(":");
            inv.invSlotObjId[slot] = objs.get(p[0]) + 1;
            inv.invSlotObjCount[slot] = Integer.parseInt(p[1]);
            slot++;
        }
        if (hover != null) c.sidebarHoveredInterfaceIndex = ids.get(iface + ":" + hover);

        int W = 190, H = 261;
        int[] px = new int[W * H];
        Pix2D.bind(W, H, px);
        new Pix8(media, "invback", 0).plotSprite(0, 0);
        c.drawInterface(0, 0, Component.get(ids.get(iface)), 0);
        BufferedImage img = new BufferedImage(W, H, BufferedImage.TYPE_INT_RGB);
        for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) img.setRGB(x, y, px[y * W + x]);
        ImageIO.write(img, "png", new File(out));
        System.out.println("drew " + iface + (hover != null ? " hovering " + hover : "") + " -> " + out);
    }
}
