import jagex2.io.*; import jagex2.config.*; import jagex2.dash3d.*; import jagex2.graphics.*;
import java.io.*; import java.nio.file.*;
/** ONE model, ONE view, one JVM, against sources instrument.py has patched: what was culled, what
 *  was queued, what was actually drawn, and what the client's own catch swallowed. */
public class Dbg {
    static String DIR = System.getProperty("probe.dir", ".");
    static byte[] file(String p) throws IOException { return Files.readAllBytes(Paths.get(p)); }
    public static void main(String[] a) throws Exception {
        int id = Integer.parseInt(a[0]), yaw = Integer.parseInt(a[1]);
        Pix3D.lowMem = false;
        Pix3D.unpackTextures(new Jagfile(file(DIR + "/textures.jag")));
        Pix3D.initColourTable(0.8D); Pix3D.initPool(20);
        Model.init(100000, new OnDemandProvider());
        Model.method357(file(DIR + "/models/" + id + ".ob2"), id, (byte) 7);
        Model m = Model.tryGet(id);
        int W = 160; int[] px = new int[W * W];
        m.calculateNormals(64, 850, -30, -50, -30, true);
        Pix2D.bind(W, W, px); Pix2D.fillRect(W, 0, 0x2b4a6b, W, 0);   // NOT black: see the README
        Pix3D.init3D(W, W); Pix3D.method545();
        m.method380(0, yaw, 0, 0, 0, 96, 600);
        StringBuilder sb = new StringBuilder();
        for (int p = 0; p < 13; p++) if (Model.QUEUED[p] + Model.CULLED[p] + Model.DRAWN[p] > 0)
            sb.append(" pri" + p + ": culled " + Model.CULLED[p] + " queued " + Model.QUEUED[p]
                      + " drawn " + Model.DRAWN[p] + ";");
        System.out.println(id + " yaw " + yaw + " |" + sb + "  BOOM=" + Model.BOOM);
    }
}
