import jagex2.io.*; import jagex2.config.*; import jagex2.dash3d.*; import jagex2.graphics.*;
import java.io.*; import java.nio.file.*; import javax.imageio.ImageIO; import java.awt.image.BufferedImage;
public class Final {
    static String DIR = System.getProperty("probe.dir", ".");
    static byte[] file(String p) throws IOException { return Files.readAllBytes(Paths.get(p)); }
    public static void main(String[] a) throws Exception {
        Pix3D.lowMem = false;
        Pix3D.unpackTextures(new Jagfile(file(DIR + "/textures.jag")));
        Pix3D.initColourTable(0.8D); Pix3D.initPool(20);
        ObjType.unpack(new Jagfile(file(DIR + "/config.jag")));
        Model.init(100000, new OnDemandProvider());
        for (int id : new int[] { 9638, 16482, 99400, 16481, 99401 })
            Model.method357(file(DIR + "/models/" + id + ".ob2"), id, (byte) 7);
        int W = 120;
        int[][] jobs = { {9638,0},{9638,1024},{16482,0},{16482,1024},{99400,0},{99400,1024} };
        BufferedImage out = new BufferedImage(W * jobs.length, W, BufferedImage.TYPE_INT_RGB);
        int[] px = new int[W * W];
        for (int j = 0; j < jobs.length; j++) {
            Model m = Model.tryGet(jobs[j][0]);
            m.calculateNormals(64, 768, -50, -10, -50, true);
            Pix2D.bind(W, W, px); Pix2D.fillRect(W, 0, 0, W, 0);
            Pix3D.init3D(W, W); Pix3D.method545();
            m.method380(0, jobs[j][1], 0, 0, 0, 0, 420);
            int lit = 0;
            for (int y = 0; y < W; y++) for (int x = 0; x < W; x++) {
                int c = px[y * W + x]; if (c > 1) lit++;
                out.setRGB(j * W + x, y, c);
            }
            System.out.printf("worn %5d yaw %4d : %5d px%n", jobs[j][0], jobs[j][1], lit);
        }
        ImageIO.write(out, "png", new File(DIR + "/final.png"));
        ObjType t = ObjType.get(8377);
        BufferedImage icons = new BufferedImage(32 * 3 * 4, 32 * 4, BufferedImage.TYPE_INT_RGB);
        int[] which = { 9631, 16481, 99401 }; int k = 0;
        for (int mid : which) {
            Model m = Model.tryGet(mid);
            if (m == null) { k++; continue; }
            m.calculateNormals(t.ambient + 64, t.contrast + 768, -50, -10, -50, true);
            int[] ip = new int[32 * 32];
            Pix2D.bind(32, 32, ip); Pix2D.fillRect(32, 0, 0, 32, 0);
            Pix3D.init3D(32, 32); Pix3D.method545();
            int dx = Pix3D.sinTable[t.field841] * t.field851 >> 16;
            int dz = Pix3D.cosTable[t.field841] * t.field851 >> 16;
            m.method380(0, t.field838, t.field821, t.field841, t.field809, m.field1709 / 2 + dx + t.field822, t.field822 + dz);
            int lit = 0; for (int p : ip) if (p > 1) lit++;
            System.out.printf("icon %5d : %4d of 1024 px%n", mid, lit);
            for (int y = 0; y < 32; y++) for (int x = 0; x < 32; x++)
                for (int sy = 0; sy < 4; sy++) for (int sx = 0; sx < 4; sx++)
                    icons.setRGB(k * 128 + x * 4 + sx, y * 4 + sy, ip[y * 32 + x]);
            k++;
        }
        ImageIO.write(icons, "png", new File(DIR + "/final_icons.png"));
    }
}
