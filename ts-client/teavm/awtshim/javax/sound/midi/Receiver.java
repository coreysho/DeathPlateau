package javax.sound.midi;
public interface Receiver {
    void send(ShortMessage message, long timeStamp);
    void close();
}
