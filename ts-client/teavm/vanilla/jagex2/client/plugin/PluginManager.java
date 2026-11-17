package jagex2.client.plugin;

import jagex2.client.Client;
import jagex2.client.plugin.event.SettingsMenuOpening;
import jagex2.graphics.PixFont;

import java.util.ArrayList;
import java.util.List;

/**
 * Vanilla-only stub for the browser build.
 *
 * The real PluginManager loads plugin jars with a URLClassLoader, posts events on a bus and draws
 * a Swing hub - none of which a page can do, and none of which the vanilla client needs. Every
 * hook here answers "nothing is running", which is exactly what the real one does when no plugin
 * is loaded, so the client takes its own path in every case.
 *
 * Plugins come back once vanilla runs in the browser; they will need a different mechanism than a
 * jar and a class loader.
 */
public class PluginManager {

    /** A row in the plugin panel. Nothing builds one here, but Client names the type. */
    public static final class PanelRow {
        public static final int KIND_PLUGIN = 0, KIND_CONFIG = 1, KIND_ACTION = 2, KIND_TEXT = 3;

        public final int kind;
        public final String label;
        public final String hint;
        public final boolean checked;
        public final boolean showCheckbox;

        public PanelRow(int kind, String label, String hint, boolean checked, boolean showCheckbox) {
            this.kind = kind;
            this.label = label;
            this.hint = hint;
            this.checked = checked;
            this.showCheckbox = showCheckbox;
        }

        public boolean isClickable() { return false; }
    }

    public PluginManager(Client client, PixFont small, PixFont normal, PixFont bold) { }

    public List<PanelRow> buildPanelRows() { return new ArrayList<PanelRow>(); }
    public void clickRow(PanelRow row) { }
    public boolean dragWantsClick(int x, int y) { return false; }
    public boolean wantsHoverTile() { return false; }
    public boolean isClickable(Object o) { return false; }

    public void onClientTick(int cycle) { }
    public void onGameTick() { }
    public void onChatMessage(String sender, String message, int type) { }
    public void onStatChanged(int skill, int level, int experience, int gained) { }
    public void onMenuBuilt(int size) { }
    public boolean onMenuOptionClicked(String option, int action, int paramA, int paramB, int paramC,
        jagex2.client.plugin.event.MenuOptionClicked.Target target) { return false; }
    public boolean onViewportClick(int x, int y) { return false; }
    public boolean onViewportScroll(int x, int y, int delta) { return false; }
    public boolean onKeyPressed(int key) { return false; }
    public void onOverlayDrag(int x, int y, int button, boolean alt, int width, int height) { }
    public void renderOverlays(int width, int height, int layer) { }

    public List<SettingsMenuOpening.Row> onSettingsMenuOpening(
        List<SettingsMenuOpening.Target> targets, boolean worldMenu, int room) {
        return new ArrayList<SettingsMenuOpening.Row>();
    }

    public void reload() { }
    public void shutdown() { }
}
