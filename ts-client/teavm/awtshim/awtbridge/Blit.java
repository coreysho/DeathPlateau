package awtbridge;

/**
 * The blitter interface, outside java.* so the browser shell can implement it.
 *
 * java.awt.Graphics.Blitter lives in the shim and is invisible to anything javac compiles against
 * the platform AWT; this is the same contract in a package both sides can name.
 */
public interface Blit {
    void blit(int[] pixels, int width, int height, int x, int y);
}
