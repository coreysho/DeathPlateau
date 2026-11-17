package javax.sound.sampled;
public interface SourceDataLine {
    void open(AudioFormat format, int bufferSize);
    void open(AudioFormat format);
    void start();
    void stop();
    void close();
    void flush();
    int write(byte[] b, int off, int len);
    int available();
    boolean isActive();
    Object getControl(FloatControl.Type type);
}
