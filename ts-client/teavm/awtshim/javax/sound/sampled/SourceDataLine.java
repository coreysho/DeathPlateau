package javax.sound.sampled;
public interface SourceDataLine extends Line {
    void open(AudioFormat format, int bufferSize);
    void open(AudioFormat format);
    void start();
    void stop();
    void flush();
    void drain();
    int write(byte[] b, int off, int len);
    int available();
    boolean isActive();
    Control getControl(Control.Type type);
    boolean isControlSupported(Control.Type type);
}
