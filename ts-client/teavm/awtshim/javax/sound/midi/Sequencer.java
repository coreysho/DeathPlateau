package javax.sound.midi;
/** Browser shim: music is Web Audio's job, not a JVM sequencer's. */
public interface Sequencer {
    void open();
    void close();
    boolean isOpen();
    boolean isRunning();
    void start();
    void stop();
    void setSequence(Sequence sequence);
    void setSequence(java.io.InputStream stream);
    void setLoopCount(int count);
    Receiver getReceiver();
    Transmitter getTransmitter();
}
