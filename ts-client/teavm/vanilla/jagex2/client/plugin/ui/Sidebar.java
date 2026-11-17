package jagex2.client.plugin.ui;

/**
 * Vanilla-only stub. The real Sidebar is the Swing plugin hub docked beside the game; a page has
 * neither Swing nor a second pane to dock, and vanilla does not need one. ViewBox still asks
 * whether a sidebar is present, so the type has to exist.
 */
public class Sidebar extends java.awt.Container {
    public Sidebar() { }
    public Sidebar(Object... ignored) { }
    public void setResizeListener(Runnable r) { }
}
