package java.awt;
public class RenderingHints {
    public static class Key { }
    public static final Key KEY_INTERPOLATION = new Key();
    public static final Key KEY_ANTIALIASING = new Key();
    public static final Object VALUE_INTERPOLATION_NEAREST_NEIGHBOR = new Object();
    public static final Object VALUE_INTERPOLATION_BILINEAR = new Object();
    public static final Object VALUE_ANTIALIAS_ON = new Object();
}
