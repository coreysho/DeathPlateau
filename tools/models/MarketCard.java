package jagex2.client;
import jagex2.config.*;
import jagex2.dash3d.*;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.util.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// A trading post listing, drawn as a card for Discord - out of the GAME'S OWN PIXELS.
//
// Every other server's market feed is a web mock-up of a game interface: a picture drawn to look
// like the thing. This draws the thing. The item is ObjType.method230, the same call that fills an
// inventory slot, with the real models and the real textures; the type is PixFont reading the real
// p11/p12/b12 out of the cache's title archive. Nothing here is a lookalike, which is the whole
// idea - the card is made of the client, so it cannot drift from what the client shows.
//
// AND IT SAYS SOMETHING A WANTED AD CANNOT. This market is not a board of buy orders: a seller
// lists an item and anybody may buy it outright OR offer coins, items, or both
// (engine/market/TradingPost.ts). The bartering line is on the card because it is the part of this
// market that has no equivalent elsewhere, and a card that left it out would be advertising a
// different game's feature.
//
// dir must hold what ObjIconRender's does - config.jag, textures.jag, models.txt, objs.txt - plus
// title.jag, which is where the fonts live.
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.MarketCard <dir> <out.png> \
//        --obj <name-or-id> [--count N] [--seller NAME] [--buyout N] [--id N] [--scale N]
//
// --buyout 0, or leaving it out, is a listing with no buy-it-now price: offers only.
// --scale defaults to 2, nearest-neighbour, because the game's font is 11px and Discord shows an
// attachment at around 400 across. Drawn at 1x and enlarged, so the pixels stay square.
public class MarketCard {
    // THE SERVER'S OWN PALETTE, copied from DeathPlateauWeb src/app/globals.css rather than picked
    // to taste - the card is a piece of the site that happens to live in Discord, and two sets of
    // nearly-the-same greys would read as a mistake. The variable each one is called there is in
    // the comment, so a change on the site can be followed here.
    static final int BG = 0x1A1A1A;      // --ground
    static final int SLOT = 0x141414;    // --ink
    static final int EDGE = 0x3A3A3A;    // --line
    static final int RULE = 0x5A2420;    // --edge-red
    static final int ACCENT = 0xB83228;  // --blood
    static final int TEXT = 0xD0D0D0;    // --text
    static final int DIM = 0x8A8A8A;     // --text-dim
    static final int STEEL = 0xDDDDDD;   // --knob, the brightest thing on the card

    static int W = 540, H = 172;
    static int[] px;

    static void rect(int x, int y, int w, int h, int colour) {
        for (int j = Math.max(0, y); j < Math.min(H, y + h); j++) {
            for (int i = Math.max(0, x); i < Math.min(W, x + w); i++) {
                px[j * W + i] = colour;
            }
        }
    }

    static void frame(int x, int y, int w, int h, int colour) {
        rect(x, y, w, 1, colour); rect(x, y + h - 1, w, 1, colour);
        rect(x, y, 1, h, colour); rect(x + w - 1, y, 1, h, colour);
    }

    /** 30000 -> "30,000". The game writes coin counts this way and so should a card about coins. */
    static String commas(long n) {
        String s = Long.toString(n);
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if (i > 0 && (s.length() - i) % 3 == 0) out.append(',');
            out.append(s.charAt(i));
        }
        return out.toString();
    }

    public static void main(String[] a) throws Exception {
        String dir = a[0], out = a[1];
        String objArg = null, seller = "somebody";
        int count = 1, buyout = 0, listing = 0, scale = 2;
        for (int i = 2; i < a.length; i++) {
            switch (a[i]) {
                case "--obj":    objArg = a[++i]; break;
                case "--count":  count = Integer.parseInt(a[++i]); break;
                case "--seller": seller = a[++i]; break;
                case "--buyout": buyout = Integer.parseInt(a[++i]); break;
                case "--id":     listing = Integer.parseInt(a[++i]); break;
                case "--scale":  scale = Integer.parseInt(a[++i]); break;
                default: throw new IllegalArgumentException("no such option: " + a[i]);
            }
        }
        if (objArg == null) throw new IllegalArgumentException("--obj is required");

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
        Integer objId = byName.get(objArg);
        if (objId == null) objId = Integer.parseInt(objArg);

        // The icon FIRST, because method230 binds a raster of its own and would otherwise take the
        // card's out from under it.
        int IW = 765, IH = 503;
        Pix2D.bind(IW, IH, new int[IW * IH]);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(IH, IW);
        // mode 0 and the real stack count: a stackable draws its own number sprite, so a listing of
        // 100 essence shows as the player would see it in the slot.
        Pix32 icon = ObjType.method230(0, count, objId);
        int[] iconPx = new int[32 * 32];
        if (icon != null) System.arraycopy(icon.pixels, 0, iconPx, 0, 32 * 32);
        ObjType type = ObjType.get(objId);
        // field811 is the obj's name (ObjType's decoder fills it for opcode 2, and the
        // members-world stub overwrites it with "Members Object").
        String name = type.field811 == null ? objArg : type.field811;

        Jagfile title = new Jagfile(Files.readAllBytes(Paths.get(dir, "title.jag")));
        // "_full", not "p11": this build packs the complete 256-character fonts under those names
        // (tools/pack/sprite/title.ts), and asking for "p11" hands back a null and an NPE four
        // frames deep in Packet.
        PixFont p11 = new PixFont(false, title, "p11_full");
        PixFont p12 = new PixFont(false, title, "p12_full");
        PixFont b12 = new PixFont(false, title, "b12_full");

        px = new int[W * H];
        Pix2D.bind(W, H, px);

        rect(0, 0, W, H, BG);
        frame(0, 0, W, H, EDGE);
        // A red spine down the left edge: the one piece of colour, and the same gesture Discord
        // itself makes with an embed's stripe, so the card sits with the client rather than against
        // it. Everything else is grey, which is what the site is.
        rect(0, 0, 3, H, ACCENT);
        rect(3, 28, W - 4, 1, RULE);
        b12.drawString(18, ACCENT, 21, "DEATH PLATEAU");
        p11.drawString(18 + b12.stringWid("DEATH PLATEAU") + 10, DIM, 21, "trading post");
        if (listing > 0) {
            String tag = "#" + listing;
            p11.drawString(W - 16 - p11.stringWid(tag), DIM, 21, tag);
        }

        // The item, in something the size and colour of a real inventory slot.
        int sx = 20, sy = 46, cell = 64;
        rect(sx, sy, cell, cell, SLOT);
        frame(sx, sy, cell, cell, EDGE);
        for (int y = 0; y < 32; y++) {
            for (int x = 0; x < 32; x++) {
                int p = iconPx[y * 32 + x];
                if (p == 0) continue;
                rect(sx + x * 2, sy + y * 2, 2, 2, p);
            }
        }

        int tx = sx + cell + 20;
        String heading = count > 1 ? commas(count) + " x " + name : name;
        b12.drawString(tx, STEEL, 62, heading);
        p12.drawString(tx, TEXT, 84, "Listed by " + seller);

        if (buyout > 0) {
            p12.drawString(tx, DIM, 110, "Buy it now");
            p12.drawString(tx + p12.stringWid("Buy it now "), STEEL, 110, commas(buyout) + " gp");
        } else {
            p12.drawString(tx, TEXT, 110, "No buyout price");
        }
        // THE LINE THAT MAKES THIS CARD THIS SERVER'S. A wanted ad has no equivalent.
        p11.drawString(tx, DIM, 130, "or offer for it - coins, items, or both");

        rect(3, H - 24, W - 4, 1, EDGE);
        // ONE TRADING POST, AND IT IS IN EDGEVILLE. loc 15396 is placed once in the whole build,
        // at 3084,3492 (maps/m48_54.jm2) - so "any trading post" was wrong, and ::market was a
        // command this server does not have: it was carried over from the card this was asked to
        // not resemble. Naming the place is also the point. Edgeville is meant to be where people
        // end up, and a line that sends them there is worth more than one that saves them the walk.
        p11.drawString(18, DIM, H - 8, "At the trading post in Edgeville");

        BufferedImage img = new BufferedImage(W * scale, H * scale, BufferedImage.TYPE_INT_RGB);
        for (int y = 0; y < H * scale; y++) {
            for (int x = 0; x < W * scale; x++) {
                img.setRGB(x, y, px[(y / scale) * W + (x / scale)]);
            }
        }
        ImageIO.write(img, "png", new java.io.File(out));
        System.out.println("wrote " + out + "  (" + name + (count > 1 ? " x" + count : "") + ")");
    }
}
