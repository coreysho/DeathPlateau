import jagex2.config.*; import jagex2.dash3d.*; import jagex2.graphics.*; import jagex2.io.*;
import java.io.*; import java.nio.file.*; import java.util.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// Pose this build's default player body with a seq, using the client's own AnimFrame, Model and Pix3D.
// Written for the Lunar spellbook: its cast animations are 474's, and 474's player animations were
// rigged for 474's redrawn bodies - the Home Teleport ones pulled the head off this build's. This
// draws a strip of frames from each seq, so a broken one is a picture and not a surprise in game.
//
//   java -cp <client classes>;. PoseRender <config.jag> <textures.jag> <content dir> <out.png> <seq id>[:label] ...
//
// The anim sets are read straight out of <content>/models/*.anim, and the body parts are the first
// selectable male kit for each of the seven body parts (idk.dat), as a new character is dressed.
public class PoseRender {
    static final int W = 110, H = Integer.getInteger("pose.h", 170), PER = 6;

    public static void main(String[] a) throws Exception {
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(a[0])));
        Path content = Paths.get(a[2]);
        Pix3D.lowMem = false;
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(a[1]))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        IdkType.unpack(cfg);
        SeqType.unpack(cfg);
        Model.init(100000, null);

        Map<Integer, Path> models = new HashMap<>();
        Map<String, Path> byName = new HashMap<>();
        try (java.util.stream.Stream<Path> s = Files.walk(content.resolve("models"))) {
            s.filter(p -> p.toString().endsWith(".ob2")).forEach(p -> byName.put(p.getFileName().toString().replace(".ob2", ""), p));
        }
        for (String l : Files.readAllLines(content.resolve("pack/model.pack"))) {
            int eq = l.indexOf('=');
            if (eq > 0 && byName.containsKey(l.substring(eq + 1).trim())) models.put(Integer.parseInt(l.substring(0, eq)), byName.get(l.substring(eq + 1).trim()));
        }

        AnimFrame.init(65535);
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(content.resolve("models"), "*.anim")) {
            for (Path p : ds) AnimFrame.method262(Files.readAllBytes(p));
        }

        // a new male character: the first selectable kit of each body part 0..6
        List<IdkType> kit = new ArrayList<>();
        for (int part = 0; part < 7; part++) {
            for (IdkType t : IdkType.field1699) {
                if (t.field1700 == part && !t.field1705) { kit.add(t); break; }
            }
        }
        for (IdkType t : kit) for (int id : t.field1701) Model.method357(Files.readAllBytes(models.get(id)), id, (byte) 7);

        int seqs = a.length - 4;
        BufferedImage out = new BufferedImage(W * PER, H * seqs, BufferedImage.TYPE_INT_RGB);
        int[] px = new int[W * H];
        for (int s = 0; s < seqs; s++) {
            String[] spec = a[4 + s].split(":");
            SeqType seq = SeqType.field775[Integer.parseInt(spec[0])];
            for (int k = 0; k < PER; k++) {
                int f = seq.field776 <= 1 ? 0 : Math.min(seq.field776 - 1, k * (seq.field776 - 1) / (PER - 1));
                Model[] parts = new Model[kit.size()];
                for (int i = 0; i < parts.length; i++) parts[i] = kit.get(i).method578();
                Model body = new Model(parts.length, parts, (byte) -89);
                body.createLabelReferences();
                body.applyTransform(seq.field777[f]);
                body.calculateNormals(64, 850, -30, -50, -30, true);
                Arrays.fill(px, 0x3C5A78);
                Pix2D.bind(W, H, px);
                Pix3D.init3D(W, H);
                Pix3D.method545();
                // yaw 1536 is three-quarters on; lifted so the feet sit near the bottom of the frame
                body.method380(0, 1700, 0, 0, 0, Integer.getInteger("pose.y", 95), 520);
                for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) out.setRGB(k * W + x, s * H + y, px[y * W + x]);
            }
            System.out.printf("%-28s seq %s, %d frames%n", spec.length > 1 ? spec[1] : "", spec[0], seq.field776);
        }
        ImageIO.write(out, "png", new File(a[3]));
    }
}
