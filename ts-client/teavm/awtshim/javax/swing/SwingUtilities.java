package javax.swing;
public class SwingUtilities {
    public static void invokeLater(Runnable r) { r.run(); }
    public static void invokeAndWait(Runnable r) { r.run(); }
    public static boolean isEventDispatchThread() { return true; }
}
