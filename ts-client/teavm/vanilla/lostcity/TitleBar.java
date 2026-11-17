package lostcity;

/**
 * Browser build stub.
 *
 * The real TitleBar is the launcher's custom window chrome, drawn with Swing. The browser has its
 * own chrome, so this exists only so ViewBox - which implements TitleBar.Actions - still compiles.
 */
public class TitleBar extends java.awt.Container {
    public interface Actions {
        void setSidebarVisible(boolean visible);
        boolean isSidebarVisible();
    }

    public TitleBar(Object window, String title, Actions actions) { }

    public static boolean isMaximised(Object window) { return false; }
    public static void limitMaximisedBounds(Object window) { }
    public void setMaximiseAllowed(boolean allowed) { }
    public void setSidebarAvailable(boolean available) { }
    public void sidebarChanged() { }
    public void sidebarChanged(boolean visible) { }
}
