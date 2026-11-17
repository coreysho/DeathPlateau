package java.awt.event;
public class KeyEvent {
    public static final int VK_LEFT=37, VK_UP=38, VK_RIGHT=39, VK_DOWN=40, VK_ENTER=10,
        VK_BACK_SPACE=8, VK_ESCAPE=27, VK_TAB=9, VK_SHIFT=16, VK_CONTROL=17, VK_ALT=18,
        VK_F1=112, VK_HOME=36, VK_END=35, VK_PAGE_UP=33, VK_PAGE_DOWN=34, VK_DELETE=127,
        CHAR_UNDEFINED=0;
    public int keyCode; public char keyChar;
    public int getKeyCode() { return keyCode; }
    public char getKeyChar() { return keyChar; }
    public boolean isControlDown() { return false; }
    public boolean isShiftDown() { return false; }
    public boolean isAltDown() { return false; }
    public void consume() { }
}
