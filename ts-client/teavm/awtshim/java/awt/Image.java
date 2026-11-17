package java.awt;
import java.awt.image.ColorModel;
import java.awt.image.ImageConsumer;
import java.awt.image.ImageProducer;

/**
 * Browser shim. In AWT this is an opaque handle fed by an ImageProducer; here it is simply the
 * pixels, because that is all PixMap ever puts in and all a canvas ever wants out.
 */
public class Image implements ImageConsumer {
    public int[] pixels;
    public int width, height;
    public ImageProducer producer;

    public Image() { }

    public Image(ImageProducer producer) {
        this.producer = producer;
        producer.addConsumer(this);
    }

    public int getWidth(java.awt.image.ImageObserver o) { return width; }
    public int getHeight(java.awt.image.ImageObserver o) { return height; }
    public Graphics getGraphics() { return new Graphics(); }
    public ImageProducer getSource() { return producer; }
    public void flush() { }

    // --- ImageConsumer: PixMap.setPixels() lands here ---

    @Override public void setDimensions(int w, int h) {
        this.width = w;
        this.height = h;
        if (pixels == null || pixels.length < w * h) {
            pixels = new int[w * h];
        }
    }
    @Override public void setProperties(java.util.Hashtable<?, ?> props) { }
    @Override public void setColorModel(ColorModel model) { }
    @Override public void setHints(int hints) { }
    @Override public void setPixels(int x, int y, int w, int h, ColorModel model, byte[] px, int off, int scan) { }
    @Override public void setPixels(int x, int y, int w, int h, ColorModel model, int[] px, int off, int scan) {
        if (pixels == null) {
            setDimensions(Math.max(w, width), Math.max(h, height));
        }
        for (int row = 0; row < h; row++) {
            int src = off + row * scan;
            int dst = (y + row) * width + x;
            if (dst < 0 || dst + w > pixels.length || src + w > px.length) {
                continue;
            }
            System.arraycopy(px, src, pixels, dst, w);
        }
    }
    @Override public void imageComplete(int status) { }
}
