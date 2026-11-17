package javax.sound.sampled;
public class FloatControl {
    public static class Type {
        public static final Type MASTER_GAIN = new Type();
    }
    public void setValue(float v) { }
    public float getValue() { return 0f; }
    public float getMinimum() { return 0f; }
    public float getMaximum() { return 0f; }
}
