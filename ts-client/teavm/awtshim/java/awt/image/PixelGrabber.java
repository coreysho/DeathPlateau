package java.awt.image;
/** Browser shim: pixels come straight off the canvas, not through a grabber. */
public class PixelGrabber {
    public PixelGrabber(java.awt.Image img, int x, int y, int w, int h, int[] px, int off, int scan) { }
    public PixelGrabber(ImageProducer p, int x, int y, int w, int h, int[] px, int off, int scan) { }
    public boolean grabPixels() { return true; }
    public int getStatus() { return ImageObserver.ALLBITS; }
}
