package java.awt.image;
public class BufferedImage extends java.awt.Image implements RenderedImage {
    public static final int TYPE_INT_RGB = 1, TYPE_INT_ARGB = 2;
    public BufferedImage(int w, int h, int type) { setDimensions(w, h); }
    public int getRGB(int x, int y) { return pixels == null ? 0 : pixels[y * width + x]; }
    public void setRGB(int x, int y, int rgb) { if (pixels != null) pixels[y * width + x] = rgb; }
    public int getWidth() { return width; }
    public int getHeight() { return height; }
    public int[] getRGB(int x, int y, int w, int h, int[] out, int off, int scan) {
        if (out == null) { out = new int[w * h]; }
        for (int row = 0; row < h; row++) {
            for (int col = 0; col < w; col++) {
                out[off + row * scan + col] = getRGB(x + col, y + row);
            }
        }
        return out;
    }
    public void setRGB(int x, int y, int w, int h, int[] in, int off, int scan) {
        for (int row = 0; row < h; row++) {
            for (int col = 0; col < w; col++) {
                setRGB(x + col, y + row, in[off + row * scan + col]);
            }
        }
    }
    public java.awt.Graphics2D createGraphics() { return new java.awt.Graphics2D(); }
}
