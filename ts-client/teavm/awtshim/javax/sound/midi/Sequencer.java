package javax.sound.midi;
/** Browser shim: music is Web Audio's job, not a JVM sequencer's. */
public interface Sequencer {
    void open();
    void close();
    boolean isOpen();
    void start();
    void stop();
    void setSequence(byte[] data);
    void setLoopCount(int count);
    Receiver getReceiver();
}
