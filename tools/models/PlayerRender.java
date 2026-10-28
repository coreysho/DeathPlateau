package jagex2.client;
import jagex2.config.*;
import jagex2.dash3d.*;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.util.*; import java.io.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// Offline render of a DRESSED, POSED player with the real client code: the same
// Model(int, Model[], byte) merge, createLabelReferences, calculateNormals, applyTransform and
// method381 that ClientPlayer.method573 runs when a player walks past you.
//
// Written 2026-10-28 for the staff of light bar. A worn model is authored and reviewed ALONE, and
// ob2render.py draws it alone; the fault was in what the merge does to two of them TOGETHER, which
// no still of either one can show. The merge welds vertices that share a position and keeps the
// FIRST part's vertex label, so a weapon vertex that happens to sit where a cape vertex sits gets
// skinned to the cape - invisible in the base pose, a stretched triangle the moment anything moves.
// That is a thing you have to pose to see.
//
// dir must hold config.jag and textures.jag (archives 2 and 6 of a client cache, as SceneRender's
// does) and anims/ - the .anim files from content/models, which carry their own skeletons.
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.PlayerRender <dir> <out.png> \
//        --part <a.ob2> --part <b.ob2> [--frame N] [--yan N] [--dist N] [--cols N]
//
// --part is given ONCE PER WORN MODEL, IN WEAR-SLOT ORDER (hat, cape, amulet, weapon, torso,
// shield, arms, legs, head, hands, feet, beard), because the merge order is what decides which
// part's label a welded vertex keeps. --frame may be repeated for a strip of poses; 0 means the
// base pose, unposed, and --frames-file reads a list of frame ids one per line.
//
// --dump writes "<frame> <face> <x> <y> <z>" per posed face instead of drawing, as a way to sweep
// thousands of frames for the ones a change actually moves. It is per FACE because a change to the
// merge alters the vertex count, and face order survives that where vertex indexes do not.
public class PlayerRender {
    public static void main(String[] a) throws Exception {
        String dir = a[0], out = a[1];
        List<String> parts = new ArrayList<>();
        List<Integer> frames = new ArrayList<>();
        int yan = 0, dist = 250, cols = 0, size = 320;
        String dump = null;
        for (int i = 2; i < a.length; i++) {
            switch (a[i]) {
                case "--part":  parts.add(a[++i]); break;
                case "--frame": frames.add(Integer.parseInt(a[++i])); break;
                case "--yan":   yan = Integer.parseInt(a[++i]); break;
                case "--dist":  dist = Integer.parseInt(a[++i]); break;
                case "--cols":  cols = Integer.parseInt(a[++i]); break;
                case "--size":  size = Integer.parseInt(a[++i]); break;
                case "--frames-file":
                    for (String l : Files.readAllLines(Paths.get(a[++i]))) {
                        if (!l.trim().isEmpty()) frames.add(Integer.parseInt(l.trim()));
                    }
                    break;
                case "--dump":  dump = a[++i]; break;
                default: throw new IllegalArgumentException("no such option: " + a[i]);
            }
        }
        if (frames.isEmpty()) frames.add(0);

        World.lowMem = false; World3D.lowMem = false; Pix3D.lowMem = false; LocType.lowMem = false;
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(dir, "config.jag")));
        ObjType.unpack(cfg); LocType.unpack(cfg); FloType.unpack(cfg); SeqType.unpack(cfg); VarbitType.unpack(cfg);
        Model.init(parts.size() + 16, null);
        for (int i = 0; i < parts.size(); i++) {
            Model.method357(Files.readAllBytes(Paths.get(parts.get(i))), i, (byte) 7);
        }
        // Frame ids are global and sparse, so the table is sized past the largest id in the set.
        AnimFrame.init(70000);
        Path anims = Paths.get(dir, "anims");
        if (Files.isDirectory(anims)) {
            try (DirectoryStream<Path> ds = Files.newDirectoryStream(anims, "*.anim")) {
                for (Path p : ds) {
                    try { AnimFrame.method262(Files.readAllBytes(p)); }
                    catch (Exception | Error e) { System.out.println("skipped " + p.getFileName() + ": " + e); }
                }
            }
        }

        int W = size, H = (int) (size * 1.4);
        int[] px = new int[W * H];
        Pix2D.bind(W, H, px);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(H, W);

        int nc = dump != null ? 1 : (cols > 0 ? Math.min(cols, frames.size()) : frames.size());
        int nr = dump != null ? 1 : (frames.size() + nc - 1) / nc;
        BufferedImage sheet = new BufferedImage(nc * W, nr * H, BufferedImage.TYPE_INT_RGB);
        PrintWriter dumper = dump == null ? null : new PrintWriter(new BufferedWriter(new FileWriter(dump)));

        for (int f = 0; f < frames.size(); f++) {
            int frame = frames.get(f);
            Arrays.fill(px, 0x141414);

            Model[] kit = new Model[parts.size()];
            for (int i = 0; i < parts.size(); i++) kit[i] = Model.tryGet(i);
            Model body = new Model(kit.length, kit, (byte) -89);
            body.createLabelReferences();
            body.calculateNormals(64, 850, -30, -50, -30, true);

            Model draw = body;
            if (frame > 0 && !AnimFrame.isNull(frame)) {
                draw = Model.field1190;
                draw.method361(false, body);
                draw.applyTransform(frame);
                draw.method363();
                draw.field1226 = null;
                draw.field1225 = null;
            }
            // pitch 0 looks level, so the only offsets needed are the vertical centring and the
            // camera distance; arg0 spins the model on the spot.
            draw.method381(yan, 0, 65536, 0, 65536, 0, 85, dist, 0);
            if (dumper != null) {
                for (int i = 0; i < draw.field1199; i++) {
                    int x = (draw.field1196[draw.field1200[i]] + draw.field1196[draw.field1201[i]] + draw.field1196[draw.field1202[i]]) / 3;
                    int y = (draw.field1197[draw.field1200[i]] + draw.field1197[draw.field1201[i]] + draw.field1197[draw.field1202[i]]) / 3;
                    int z = (draw.field1198[draw.field1200[i]] + draw.field1198[draw.field1201[i]] + draw.field1198[draw.field1202[i]]) / 3;
                    dumper.println(frame + " " + i + " " + x + " " + y + " " + z);
                }
            }

            if (dumper == null) {
                BufferedImage one = new BufferedImage(W, H, BufferedImage.TYPE_INT_RGB);
                one.setRGB(0, 0, W, H, px, 0, W);
                sheet.createGraphics().drawImage(one, (f % nc) * W, (f / nc) * H, null);
                System.out.println("frame " + frame + ": " + draw.field1195 + " vertices, " + draw.field1199 + " faces");
            }
        }
        if (dumper != null) {
            dumper.close();
            System.out.println("wrote " + dump + " (" + frames.size() + " frames)");
            return;
        }
        ImageIO.write(sheet, "png", new File(out));
        System.out.println("wrote " + out);
    }
}
