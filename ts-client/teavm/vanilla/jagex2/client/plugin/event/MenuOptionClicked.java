package jagex2.client.plugin.event;

/**
 * Vanilla-only stub. Client resolves every menu click into one of these so plugins can inspect it;
 * with no plugins the value is still built and still read by the client's own code, so Target is
 * real here rather than empty.
 */
public class MenuOptionClicked {

    public static final class Target {
        public static final String NONE = "none";
        public static final String NPC = "npc";
        public static final String LOC = "loc";
        public static final String OBJ = "obj";
        public static final String WORN = "worn";
        public static final String PLAYER = "player";

        public final String kind;
        public final int id;
        public final int op;
        public final int sceneTileX;
        public final int sceneTileZ;

        public Target(String kind, int id, int op, int sceneTileX, int sceneTileZ) {
            this.kind = kind;
            this.id = id;
            this.op = op;
            this.sceneTileX = sceneTileX;
            this.sceneTileZ = sceneTileZ;
        }

        public boolean is(String kind) { return this.kind != null && this.kind.equals(kind); }

        public static Target none() { return new Target(NONE, -1, -1, -1, -1); }
    }
}
