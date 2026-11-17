package java.awt.image;
public interface ImageObserver {
    int WIDTH = 1, HEIGHT = 2, ALLBITS = 32, ABORT = 128;
    boolean imageUpdate(java.awt.Image img, int flags, int x, int y, int w, int h);
}
