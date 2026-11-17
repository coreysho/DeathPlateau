package java.awt;
public class Desktop {
    public static class Action { public static final Action BROWSE = new Action(); }
    public static Desktop getDesktop() { return new Desktop(); }
    public static boolean isDesktopSupported() { return false; }
    public boolean isSupported(Action a) { return false; }
    public void browse(java.net.URI uri) { }
}
