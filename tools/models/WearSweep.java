package jagex2.client;
import jagex2.config.*;
import jagex2.dash3d.*;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.util.*; import java.io.*;

// EVERY WORN MODEL, CHECKED FOR PAINTING ITSELF ONTO THE PLAYER UNDER IT.
//
// tools/models/wearpoke.py does this for one pair and costs a JVM start and 1,500 animation files
// per render, which is fine for one cape and hopeless for two thousand models. This is the same
// measurement with the loading done once: the client is set up, the reference kit is loaded, and
// then each model is merged with it, drawn twice - with and without itself - and the pixels that
// differ INSIDE the reference kit's own silhouette are counted. A model beside the player is not
// counted; a model on top of it is.
//
// WHAT A NON-ZERO NUMBER MEANS. Model.method382 paints the merged player a priority group at a
// time, 0 through 9, and a face's group is fixed in the model, so a face in a later group is
// painted over the body however far behind it is. Groups 10 and 11 are the exception - those are
// interleaved by real depth. So a count here is the model asking to be drawn in front of a body
// it is behind, which is what the max capes were doing on 29 October.
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.WearSweep <dir> <objdir> <list> \
//        [--under a,b] [--frame N] [--yan N] [--dist N] [--size N]
//
// <list> is one model name per line, optionally "name slot" - a torso is measured against the legs
// alone and legs against the torso alone, so a model is never measured against its own slot.
public class WearSweep {
    static int W, H;
    static int[] px;

    public static void main(String[] a) throws Exception {
        String dir = a[0], objdir = a[1], list = a[2];
        String under = "obj_saradomin_platebody_manwear,obj_saradomin_plateskirt_manwear";
        int frame = 2422, yan = 0, dist = 150, size = 700;
        for (int i = 3; i < a.length; i++) {
            switch (a[i]) {
                case "--under": under = a[++i]; break;
                case "--frame": frame = Integer.parseInt(a[++i]); break;
                case "--yan":   yan = Integer.parseInt(a[++i]); break;
                case "--dist":  dist = Integer.parseInt(a[++i]); break;
                case "--size":  size = Integer.parseInt(a[++i]); break;
                default: throw new IllegalArgumentException("no such option: " + a[i]);
            }
        }

        World.lowMem = false; World3D.lowMem = false; Pix3D.lowMem = false; LocType.lowMem = false;
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(dir, "config.jag")));
        ObjType.unpack(cfg); LocType.unpack(cfg); FloType.unpack(cfg); SeqType.unpack(cfg); VarbitType.unpack(cfg);
        Model.init(8, null);
        AnimFrame.init(70000);
        Path anims = Paths.get(dir, "anims");
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(anims, "*.anim")) {
            for (Path p : ds) {
                try { AnimFrame.method262(Files.readAllBytes(p)); } catch (Exception | Error e) { }
            }
        }
        W = size; H = (int) (size * 1.4);
        px = new int[W * H];
        Pix2D.bind(W, H, px);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(H, W);

        String[] underNames = under.split(",");
        // slot 0 is the model being measured; 1.. are the reference kit
        for (int i = 0; i < underNames.length; i++) {
            Model.method357(Files.readAllBytes(Paths.get(objdir, underNames[i] + ".ob2")), i + 1, (byte) 7);
        }

        int[] bare = new int[W * H];
        int[] asis = new int[W * H];
        for (String line : Files.readAllLines(Paths.get(list))) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = line.split("\\s+");
            String name = f[0], slot = f.length > 1 ? f[1] : "";
            Path file = Paths.get(objdir, name + ".ob2");
            if (!Files.exists(file)) { System.out.println(name + " MISSING"); continue; }
            // never measure a model against its own slot - it would be replacing it, not clipping it
            List<Integer> kit = new ArrayList<>();
            for (int i = 0; i < underNames.length; i++) {
                if (slot.equals("torso") && underNames[i].contains("platebody")) continue;
                if ((slot.equals("legs")) && (underNames[i].contains("plateskirt") || underNames[i].contains("platelegs"))) continue;
                kit.add(i + 1);
            }
            if (kit.isEmpty()) { System.out.println(name + " 0 no-reference"); continue; }
            try {
                Model.method357(Files.readAllBytes(file), 0, (byte) 7);
                draw(kit, -1, frame, yan, dist, false);                // the kit alone
                System.arraycopy(px, 0, bare, 0, px.length);
                draw(kit, 0, frame, yan, dist, false);                 // as the model asks to be drawn
                System.arraycopy(px, 0, asis, 0, px.length);
                draw(kit, 0, frame, yan, dist, true);                  // and as depth says it should be
                // THE MEASUREMENT. Not "does it cover the body" - a pauldron covers the body and is
                // meant to. It is "where does the model's own priority group disagree with its real
                // depth", which is the only thing that can put a model in front of a body it is
                // behind. Counted inside the body's own silhouette, so the model's outline against
                // the floor is not counted.
                int over = 0, body = 0;
                for (int i = 0; i < px.length; i++) {
                    if (bare[i] != 0x141414) {
                        body++;
                        if (asis[i] != px[i]) over++;
                    }
                }
                System.out.println(name + " " + over + " " + body);
            } catch (Exception | Error e) {
                System.out.println(name + " THREW " + e);
            }
        }
    }

    /** Draw the reference kit, with model id `with` merged in when it is not -1. */
    static void draw(List<Integer> kit, int with, int frame, int yan, int dist, boolean depthSorted) {
        Arrays.fill(px, 0x141414);
        Model[] parts = new Model[kit.size() + 1];
        int n = 0;
        if (with >= 0) parts[n++] = Model.tryGet(with);               // the cape slot comes first
        for (int id : kit) parts[n++] = Model.tryGet(id);
        Model body = new Model(n, parts, (byte) -89);
        if (depthSorted && with >= 0) {
            // the merge keeps face order, so the model under test is faces 0.. of the result
            int faces = parts[0].field1199;
            if (body.field1207 == null) {
                body.field1207 = new int[body.field1199];
                Arrays.fill(body.field1207, body.field1210 < 0 ? 0 : body.field1210);
            }
            Arrays.fill(body.field1207, 0, faces, 10);
        }
        body.createLabelReferences();
        body.calculateNormals(64, 850, -30, -50, -30, true);
        Model out = body;
        if (frame > 0 && !AnimFrame.isNull(frame)) {
            out = Model.field1190;
            out.method361(false, body);
            out.applyTransform(frame);
            out.method363();
            out.field1226 = null;
            out.field1225 = null;
        }
        out.method381(yan, 0, 65536, 0, 65536, 0, 85, dist, 0);
    }
}
