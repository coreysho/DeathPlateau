package java.awt;
public class Color {
    public static final Color black = new Color(0);
    public static final Color white = new Color(0xffffff);
    public final int rgb;
    public Color(int rgb) { this.rgb = rgb; }
    public Color(int r, int g, int b) { this.rgb = (r << 16) | (g << 8) | b; }
    public int getRGB() { return rgb; }
}
