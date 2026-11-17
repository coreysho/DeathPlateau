package javax.imageio;
import java.awt.image.BufferedImage;
/** Browser shim: image decoding is the browser's, not ImageIO's. */
public class ImageIO {
    public static BufferedImage read(java.io.InputStream in) { return null; }
    public static BufferedImage read(java.io.File f) { return null; }
    public static boolean write(java.awt.image.RenderedImage img, String fmt, java.io.File f) { return false; }
}
