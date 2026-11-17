package java.awt;
/** Browser shim: every call lands on the canvas surface instead. */
public class Graphics {
    public void setColor(Color c) { }
    public void fillRect(int x, int y, int w, int h) { }
    public void drawRect(int x, int y, int w, int h) { }
    public void drawString(String s, int x, int y) { }
    public void setFont(Font f) { }
    public FontMetrics getFontMetrics() { return new FontMetrics(); }
    public FontMetrics getFontMetrics(Font f) { return new FontMetrics(); }
    /**
     * Where the client's pixels leave Java.
     *
     * PixMap hands over an int[] of ARGB, which is exactly a canvas ImageData, so the browser
     * shell sets a Blitter and every draw lands on the canvas. Kept as a hook rather than calling
     * JSO here so this jar stays plain Java and can be compiled by JDK 8 on its own.
     */
    public interface Blitter {
        void blit(int[] pixels, int width, int height, int x, int y);
    }

    public static Blitter blitter;

    public boolean drawImage(Image img, int x, int y, java.awt.image.ImageObserver o) {
        if (blitter != null && img != null && img.pixels != null) {
            blitter.blit(img.pixels, img.width, img.height, x, y);
        }
        return true;
    }
    public boolean drawImage(Image img, int x, int y, int w, int h, java.awt.image.ImageObserver o) {
        return drawImage(img, x, y, o);
    }
    public void translate(int x, int y) { }
    public Graphics create() { return this; }
    public void dispose() { }
}
