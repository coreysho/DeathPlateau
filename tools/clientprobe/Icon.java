import jagex2.io.*; import jagex2.config.*; import jagex2.dash3d.*; import jagex2.graphics.*;
import java.io.*; import java.nio.file.*; import javax.imageio.ImageIO; import java.awt.image.BufferedImage;
/** ONE inventory icon, one JVM: the obj record's own angles and zoom, the way ObjType does it. */
public class Icon {
    static String DIR = System.getProperty("probe.dir", ".");
    static byte[] file(String p) throws IOException { return Files.readAllBytes(Paths.get(p)); }
    public static void main(String[] a) throws Exception {
        int obj = Integer.parseInt(a[0]), mid = Integer.parseInt(a[1]);
        Pix3D.lowMem = false;
        Pix3D.unpackTextures(new Jagfile(file(DIR + "/textures.jag")));
        Pix3D.initColourTable(0.8D); Pix3D.initPool(20);
        ObjType.unpack(new Jagfile(file(DIR + "/config.jag")));
        Model.init(100000, new OnDemandProvider());
        Model.method357(file(DIR + "/models/" + mid + ".ob2"), mid, (byte) 7);
        Model m = Model.tryGet(mid);
        ObjType t = ObjType.get(obj);
        m.calculateNormals(t.ambient + 64, t.contrast + 768, -50, -10, -50, true);
        int[] px = new int[32 * 32];
        Pix2D.bind(32, 32, px); Pix2D.fillRect(32, 0, 0x2b4a6b, 32, 0);
        Pix3D.init3D(32, 32); Pix3D.method545();
        int dx = Pix3D.sinTable[t.field841] * t.field851 >> 16;
        int dz = Pix3D.cosTable[t.field841] * t.field851 >> 16;
        m.method380(0, t.field838, t.field821, t.field841, t.field809,
                    m.field1709 / 2 + dx + t.field822, t.field822 + dz);
        int lit = 0; for (int p : px) if (p != 0x2b4a6b) lit++;
        int Z = 6; BufferedImage img = new BufferedImage(32 * Z, 32 * Z, BufferedImage.TYPE_INT_RGB);
        for (int y = 0; y < 32 * Z; y++) for (int x = 0; x < 32 * Z; x++)
            img.setRGB(x, y, px[(y / Z) * 32 + x / Z]);
        ImageIO.write(img, "png", new File(a[2]));
        System.out.println("obj " + obj + " model " + mid + ": " + lit + " of 1024 px");
    }
}
