package javax.sound.sampled;
public interface Line {
    class Info {
        public Info(Class<?> lineClass) { }
    }
    void open();
    void close();
    boolean isOpen();
}
