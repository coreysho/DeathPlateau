package jagex2.client.plugin.event;

/** Vanilla-only stub: the types Client names when it asks plugins for extra menu rows. */
public class SettingsMenuOpening {

    public static final class Target {
        public final String kind;
        public final String name;
        public final String verb;
        public Target(String kind, String name, String verb) {
            this.kind = kind; this.name = name; this.verb = verb;
        }
    }

    public static final class Row {
        public final String label;
        public final Runnable action;
        public Row(String label, Runnable action) { this.label = label; this.action = action; }
    }
}
