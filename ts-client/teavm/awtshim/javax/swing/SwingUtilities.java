package javax.swing;
public class SwingUtilities {
    public static void invokeLater(Runnable r) { r.run(); }
    public static void invokeAndWait(Runnable r) { r.run(); }
    public static boolean isEventDispatchThread() { return true; }
    public static java.awt.Point convertPoint(java.awt.Component from, java.awt.Point p, java.awt.Component to) {
        return p == null ? new java.awt.Point() : new java.awt.Point(p.x, p.y);
    }
    public static java.awt.Point convertPoint(java.awt.Component from, int x, int y, java.awt.Component to) {
        return new java.awt.Point(x, y);
    }
}
