package java.awt.image;
public interface ImageConsumer {
    int SINGLEFRAME = 2, STATICIMAGEDONE = 3;
    void setDimensions(int w, int h);
    void setProperties(java.util.Hashtable<?, ?> props);
    void setColorModel(ColorModel model);
    void setHints(int hints);
    void setPixels(int x, int y, int w, int h, ColorModel model, byte[] pixels, int off, int scan);
    void setPixels(int x, int y, int w, int h, ColorModel model, int[] pixels, int off, int scan);
    void imageComplete(int status);
}
