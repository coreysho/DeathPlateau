package java.awt;
public class FontMetrics {
    public int stringWidth(String s) { return s == null ? 0 : s.length() * 7; }
    public int getHeight() { return 12; }
    public int charWidth(char c) { return 7; }
}
