package jagex2.client.worldmap;

/**
 * Browser build stub.
 *
 * The real MapWindow is a javax.swing.JFrame - a second desktop window holding the world map. A
 * page has no second window, so the browser build leaves it out; the WorldMap itself (the tiles,
 * the marks, the loading) is untouched and still compiles.
 */
public final class MapWindow {
    public MapWindow(WorldMap map) { }
    public void setMark(int x, int z, int level, String label) { }
    public void setPlayer(int x, int z, int level) { }
    public void centreOn(int x, int z) { }
    public boolean isVisible() { return false; }
    public void setVisible(boolean visible) { }
    public void toFront() { }
    public void dispose() { }
}
