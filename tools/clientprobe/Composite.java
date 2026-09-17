import jagex2.io.*; import jagex2.config.*; import jagex2.dash3d.*; import jagex2.graphics.*;
import java.io.*; import java.nio.file.*; import javax.imageio.ImageIO; import java.awt.image.BufferedImage;
/** A cape merged with body parts, the way ClientPlayer builds an appearance. */
public class Composite {
    static String DIR = System.getProperty("probe.dir", ".");
    static byte[] file(String p) throws IOException { return Files.readAllBytes(Paths.get(p)); }
    public static void main(String[] a) throws Exception {
        Pix3D.lowMem = false;
        Pix3D.unpackTextures(new Jagfile(file(DIR + "/textures.jag")));
        Pix3D.initColourTable(0.8D); Pix3D.initPool(20);
        Model.init(100000, new OnDemandProvider());
        int[] body = { 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 63, 81, 120 };
        for (int id : body) Model.method357(file(DIR + "/models/" + id + ".ob2"), id, (byte) 7);
        int[] capes = { -1, 9638, 16482, 99601 };   // none, fire, infernal as imported, infernal flipped
        for (int id : capes) if (id > 0) Model.method357(file(DIR + "/models/" + id + ".ob2"), id, (byte) 7);
        int W = 140;
        int[] yaws = { 0, 512, 1024, 1536 };
        BufferedImage out = new BufferedImage(W * yaws.length, W * capes.length, BufferedImage.TYPE_INT_RGB);
        int[] px = new int[W * W];
        for (int ci = 0; ci < capes.length; ci++) {
            for (int yi = 0; yi < yaws.length; yi++) {
                java.util.List<Model> parts = new java.util.ArrayList<>();
                for (int id : body) { Model m = Model.tryGet(id); if (m != null) parts.add(m); }
                if (capes[ci] > 0) parts.add(Model.tryGet(capes[ci]));
                Model merged = new Model(parts.size(), parts.toArray(new Model[0]), (byte) -89);
                merged.calculateNormals(64, 850, -30, -50, -30, true);
                Pix2D.bind(W, W, px); Pix2D.fillRect(W, 0, 0, W, 0);
                Pix3D.init3D(W, W); Pix3D.method545();
                merged.method380(0, yaws[yi], 0, 0, 0, 0, 500);
                int lit = 0;
                for (int y = 0; y < W; y++) for (int x = 0; x < W; x++) {
                    int c = px[y * W + x]; if (c > 1) lit++;
                    out.setRGB(yi * W + x, ci * W + y, c);
                }
                System.out.printf("%-22s yaw %4d : %5d px%n",
                    capes[ci] == -1 ? "no cape" : capes[ci] == 9638 ? "fire cape"
                    : capes[ci] == 16482 ? "infernal as imported" : "infernal flipped", yaws[yi], lit);
            }
        }
        ImageIO.write(out, "png", new File(DIR + "/composite.png"));
    }
}
