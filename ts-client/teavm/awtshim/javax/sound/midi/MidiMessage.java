package javax.sound.midi;
public abstract class MidiMessage {
    public abstract byte[] getMessage();
    public abstract int getStatus();
    public abstract int getLength();
}
