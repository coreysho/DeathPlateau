import jagex2.config.*; import jagex2.dash3d.*; import jagex2.graphics.*; import jagex2.io.*;
import java.io.*; import java.nio.file.*; import java.util.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// Pose an NPC with its own combat animations, using the client's own NpcType, AnimFrame and Pix3D.
//
// content/tools/bossanims.py answers "can this animation move this mesh at all" by comparing the
// sequence's vertex label groups against the ones the mesh carries - which is the test that matters,
// because Model.method369 discards a transform for a group the mesh lacks and says nothing. What it
// cannot answer is the next question: the groups line up, so SOMETHING moves - is it the right
// something? A dive where an attack belongs passes every static test there is.
//
// So this draws the creature, and measures it. For each sequence it reports how far the mesh
// actually travels from its base pose, in model units, frame by frame; a sequence that moves the
// mesh nowhere is a number and not a judgement call. The strip of pictures beside it is for the
// cases a number cannot settle.
//
//   java -cp <client classes>;. NpcPose <config.jag> <textures.jag> <content dir> <out.png|-> \
//        <npcId>:<label>:<seqId>[,<seqId>...] ...
//
// The archives are the ones the build writes: Engine-TS/data/pack/client/config and .../textures.
// Models and animation sets are read straight out of <content>/models, as the client reads them
// from the file store - only the models this npc names are loaded, so the probe stays quick.
//
// GEOMETRY, NOT PIXELS. clientprobe/README.md's second rule is that Pix3D and Model keep static
// state between draws and the same bytes measured twice in one process gave 5 px and 703 px. The
// vertex arrays do not have that problem: method475 copies the cached base mesh into the scratch
// model before every transform, so each frame starts from the same numbers. Everything reported
// here is read out of field1196/1197/1198 - the vertex x, y and z - and the picture is for looking
// at, never for counting.
public class NpcPose {
    static final int PER = Integer.getInteger("pose.frames", 6);
    static final int W = Integer.getInteger("pose.w", 140), H = Integer.getInteger("pose.h", 150);

    public static void main(String[] a) throws Exception {
        if (a.length < 5) {
            System.err.println("usage: NpcPose <config.jag> <textures.jag> <content> <out.png|-> "
                + "<npcId>:<label>:<seqId>[,<seqId>...] ...");
            System.exit(2);
        }
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(a[0])));
        Path content = Paths.get(a[2]);
        boolean draw = !a[3].equals("-");

        Pix3D.lowMem = false;
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(a[1]))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        NpcType.unpack(cfg);
        SeqType.unpack(cfg);
        Model.init(100000, null);

        // model id -> .ob2, the same join pack/model.pack makes
        Map<String, Path> byName = new HashMap<>();
        try (java.util.stream.Stream<Path> s = Files.walk(content.resolve("models"))) {
            s.filter(p -> p.toString().endsWith(".ob2"))
             .forEach(p -> byName.put(p.getFileName().toString().replace(".ob2", ""), p));
        }
        Map<Integer, Path> models = new HashMap<>();
        for (String l : Files.readAllLines(content.resolve("pack/model.pack"))) {
            int eq = l.indexOf('=');
            if (eq > 0) {
                Path p = byName.get(l.substring(eq + 1).trim());
                if (p != null) models.put(Integer.parseInt(l.substring(0, eq)), p);
            }
        }

        AnimFrame.init(65535);
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(content.resolve("models"), "*.anim")) {
            for (Path p : ds) AnimFrame.method262(Files.readAllBytes(p));
        }

        // ------------------------------------------------------------------ the plan
        // SPECS FROM A FILE WHEN THERE ARE TOO MANY FOR A COMMAND LINE. Three hundred bosses is
        // past what Windows will accept in one, and this runs on Java 8, where @argfiles are a
        // javac feature and `java @file` is read as a class name with the slashes turned to dots.
        List<String> raw = new ArrayList<>();
        for (int i = 4; i < a.length; i++) {
            if (a[i].startsWith("@")) raw.addAll(Files.readAllLines(Paths.get(a[i].substring(1))));
            else raw.add(a[i]);
        }
        List<String[]> specs = new ArrayList<>();
        int rows = 0;
        for (String line : raw) {
            if (line.trim().isEmpty()) continue;
            String[] spec = line.trim().split(":", 3);
            specs.add(spec);
            rows += spec[2].split(",").length;
        }
        BufferedImage out = draw ? new BufferedImage(W * PER, H * rows, BufferedImage.TYPE_INT_RGB) : null;
        int[] px = new int[W * H];
        int row = 0;

        for (String[] spec : specs) {
            int npcId = Integer.parseInt(spec[0]);
            String label = spec[1];
            NpcType type = NpcType.get(npcId);

            // A MULTINPC PARENT HAS NO MESH OF ITS OWN. method476 resolves the child through
            // Client.varps, which a probe with no world does not have, so it would be a null
            // pointer three frames in rather than a message. Say so and move on.
            if (type.field1425 != null) {
                System.out.printf("%-34s npc %d SKIPPED: a multinpc parent, its mesh is whichever "
                    + "child the varp selects%n", label, npcId);
                for (String ignored : spec[2].split(",")) row++;
                continue;
            }
            if (type.field1429 == null) {
                System.out.printf("%-34s npc %d SKIPPED: no model at all%n", label, npcId);
                for (String ignored : spec[2].split(",")) row++;
                continue;
            }
            for (int id : type.field1429) {
                Path p = models.get(id);
                if (p == null) {
                    System.out.printf("%-34s npc %d SKIPPED: model %d is in no .ob2%n", label, npcId, id);
                    break;
                }
                Model.method357(Files.readAllBytes(p), id, (byte) 7);
            }

            // the base pose: method475 applies no transform for frame -1
            Model base = type.method475(-1, -1, null);
            if (base == null) {
                System.out.printf("%-34s npc %d SKIPPED: the client would not build its model%n", label, npcId);
                for (String ignored : spec[2].split(",")) row++;
                continue;
            }
            int vc = base.field1195;
            int[] bx = Arrays.copyOf(base.field1196, vc);
            int[] by = Arrays.copyOf(base.field1197, vc);
            int[] bz = Arrays.copyOf(base.field1198, vc);
            // one camera for the whole creature, from its own size, so a duck and Zulrah both fit
            long far = 0;
            for (int v = 0; v < vc; v++) {
                long d = (long) bx[v] * bx[v] + (long) by[v] * by[v] + (long) bz[v] * bz[v];
                if (d > far) far = d;
            }
            int lift = Integer.getInteger("pose.lift", 0);
            int tilt = Integer.getInteger("pose.tilt", 180);   // a gentle look down, out of 2048

            // MEASURE EVERY SEQUENCE FIRST, THEN JUDGE. Zero movement turned out to be the wrong
            // test on its own: a duck's human_unarmedpunch moves 4 units, not 0, because the low
            // label groups it shares with a human do get transformed - the duck twitches instead
            // of punching. And plenty of stand animations legitimately move nothing at all
            // (leechready is two identical frames). So the only honest yardstick is the creature's
            // OWN largest animation, which cannot be read until all of them have been measured.
            String[] parts = spec[2].split(",");
            int[] seqIds = new int[parts.length];
            String[] params = new String[parts.length];
            String[] seqNames = new String[parts.length];
            int[] frameCount = new int[parts.length];
            long[] worstOf = new long[parts.length];
            int[] worstFrameOf = new int[parts.length];
            long[] meanOf = new long[parts.length];
            int[] movedOf = new int[parts.length];
            long biggest = 0;
            String biggestName = "";
            for (int i = 0; i < parts.length; i++) {
                String[] bits = parts[i].split("=", 3);
                params[i] = bits[0];
                seqIds[i] = Integer.parseInt(bits[1].trim());
                seqNames[i] = bits.length > 2 ? bits[2] : "";
                SeqType seq = seqIds[i] >= 0 && seqIds[i] < SeqType.field775.length
                    ? SeqType.field775[seqIds[i]] : null;
                if (seq == null || seq.field777 == null || seq.field776 <= 0) {
                    frameCount[i] = -1;
                    continue;
                }
                int frames = frameCount[i] = seq.field776;
                long worst = 0, total = 0;
                for (int f = 0; f < frames; f++) {
                    Model m = type.method475(seq.field777[f], -1, null);
                    if (m == null) continue;
                    long sum = 0;
                    int n = Math.min(vc, m.field1195);
                    for (int v = 0; v < n; v++) {
                        long dx = m.field1196[v] - bx[v], dy = m.field1197[v] - by[v], dz = m.field1198[v] - bz[v];
                        sum += (long) Math.sqrt((double) (dx * dx + dy * dy + dz * dz));
                    }
                    long mean = n > 0 ? sum / n : 0;
                    total += mean;
                    if (mean > worst) { worst = mean; worstFrameOf[i] = f; }
                    if (mean > 0) movedOf[i]++;
                    // the camera is sized from the POSED extents, not the base pose: a lunge
                    // carries the mesh well outside the standing silhouette, and framing on the
                    // stand alone cropped half of Barrelchest's anchor swing off the picture
                    for (int v = 0; v < n; v++) {
                        long d = (long) m.field1196[v] * m.field1196[v]
                               + (long) m.field1197[v] * m.field1197[v]
                               + (long) m.field1198[v] * m.field1198[v];
                        if (d > far) far = d;
                    }
                }
                worstOf[i] = worst;
                meanOf[i] = frames > 0 ? total / frames : 0;
                if (worst > biggest) { biggest = worst; biggestName = params[i]; }
            }

            System.out.printf("%s  (npc %d)%n", label, npcId);
            for (int i = 0; i < parts.length; i++) {
                if (frameCount[i] < 0) {
                    System.out.printf("    %-12s %-34s seq %-6d NOT IN THE CACHE%n",
                        params[i], seqNames[i], seqIds[i]);
                    continue;
                }
                int pct = biggest > 0 ? (int) (worstOf[i] * 100 / biggest) : 0;
                // ONE VERDICT ONLY, AND IT IS THE UNAMBIGUOUS ONE. A first version also flagged
                // anything under 15% of the creature's own biggest animation, and immediately
                // called a vampire leech's block and death broken - because a block is SUPPOSED
                // to be a flinch next to a lunge, and a percentage cannot tell a small animation
                // from a failed one. bossanims.py already learned that lesson three times over.
                // A combat animation that moves the mesh zero units is the only thing a number
                // can settle on its own; the percentage is printed for a person to read, and the
                // picture is there for everything else.
                boolean combat = params[i].endsWith("_anim") && !params[i].equals("readyanim");
                String flag = combat && worstOf[i] == 0 ? "   <-- MOVES NOTHING AT ALL" : "";
                System.out.printf("    %-12s %-34s %3d frames  peak %4d at frame %-3d "
                        + "mean %4d  %3d%% of its own biggest  %d/%d move%s%n",
                    params[i], seqNames[i], frameCount[i], worstOf[i], worstFrameOf[i], meanOf[i],
                    pct, movedOf[i], frameCount[i], flag);
            }

            int radius = (int) Math.sqrt((double) far);
            int zoom = Integer.getInteger("pose.zoom", 0) > 0
                ? Integer.getInteger("pose.zoom") : Math.max(420, radius * 4);

            // the drawing pass owns the row counter: one image row per sequence, in spec order,
            // so a skipped sequence still leaves its band blank rather than shifting the rest up
            for (int i = 0; i < parts.length; i++) {
                int seqId = seqIds[i];
                SeqType seq = frameCount[i] < 0 ? null : SeqType.field775[seqId];
                if (seq == null) { row++; continue; }
                int frames = frameCount[i];
                if (draw) {
                    for (int k = 0; k < PER; k++) {
                        int f = frames <= 1 ? 0 : Math.min(frames - 1, k * (frames - 1) / (PER - 1));
                        Model m = type.method475(seq.field777[f], -1, null);
                        Arrays.fill(px, 0x3C5A78);
                        if (m != null) {
                            // NO calculateNormals HERE. method475 lights the cached base mesh with
                            // the npc's own ambient and contrast before caching it, then nulls the
                            // scratch copy's label arrays - so a second call walks into them and
                            // throws inside method378. The client never calls it twice either.
                            Pix2D.bind(W, H, px);
                            Pix3D.init3D(W, H);
                            Pix3D.method545();
                            // THE CLIENT'S OWN ORBIT CAMERA, as TitleScreen and ObjType set it up:
                            // the tilt is an angle, not a y offset, and the model is centred on
                            // half its own height. Pitching straight ahead with a hand-guessed
                            // lift drew the ground-dwelling creatures edge-on - a vampire leech
                            // came out as a green sliver four pixels tall.
                            int sin = Pix3D.sinTable[tilt] * zoom >> 16;
                            int cos = Pix3D.cosTable[tilt] * zoom >> 16;
                            m.method380(0, Integer.getInteger("pose.yaw", 1700), 0, tilt, 0,
                                m.field1709 / 2 + sin + lift, cos);
                        }
                        for (int y = 0; y < H; y++)
                            for (int x = 0; x < W; x++) out.setRGB(k * W + x, row * H + y, px[y * W + x]);
                    }
                }
                row++;
            }
        }
        if (draw) ImageIO.write(out, "png", new File(a[3]));
    }
}
