package java.awt.event;
public class MouseEvent {
    public static final int BUTTON1 = 1, BUTTON2 = 2, BUTTON3 = 3;
    public int x, y, button, clickCount, modifiers;
    public int getX() { return x; }
    public int getY() { return y; }
    public int getButton() { return button; }
    public int getClickCount() { return clickCount; }
    public int getModifiers() { return modifiers; }
    public boolean isMetaDown() { return button == BUTTON3; }
    public boolean isAltDown() { return false; }
    public java.awt.Component getComponent() { return null; }
    public java.awt.Point getPoint() { return new java.awt.Point(x, y); }
    public java.awt.Point getLocationOnScreen() { return new java.awt.Point(x, y); }
    public int getXOnScreen() { return x; }
    public int getYOnScreen() { return y; }
    public void consume() { }
}
