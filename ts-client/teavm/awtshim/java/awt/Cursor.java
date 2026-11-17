package java.awt;
public class Cursor {
    public static final int DEFAULT_CURSOR = 0, HAND_CURSOR = 12, CROSSHAIR_CURSOR = 1,
        N_RESIZE_CURSOR = 8, S_RESIZE_CURSOR = 9, E_RESIZE_CURSOR = 11, W_RESIZE_CURSOR = 10,
        NE_RESIZE_CURSOR = 7, NW_RESIZE_CURSOR = 6, SE_RESIZE_CURSOR = 5, SW_RESIZE_CURSOR = 4,
        MOVE_CURSOR = 13, TEXT_CURSOR = 2, WAIT_CURSOR = 3;
    public Cursor(int type) { }
    public static Cursor getPredefinedCursor(int type) { return new Cursor(type); }
    public static Cursor getDefaultCursor() { return new Cursor(DEFAULT_CURSOR); }
    public int getType() { return 0; }
}
