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
    public boolean drawImage(Image img, int x, int y, java.awt.image.ImageObserver o) { return true; }
    public void dispose() { }
}
