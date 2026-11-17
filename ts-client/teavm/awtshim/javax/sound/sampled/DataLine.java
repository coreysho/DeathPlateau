package javax.sound.sampled;
public interface DataLine {
    class Info {
        public Info(Class<?> lineClass, AudioFormat format) { }
        public Info(Class<?> lineClass, AudioFormat format, int bufferSize) { }
    }
}
