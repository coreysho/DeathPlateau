package javax.sound.midi;
public class ShortMessage extends MidiMessage {
    public static final int CONTROL_CHANGE = 176, NOTE_ON = 144, NOTE_OFF = 128, PROGRAM_CHANGE = 192;
    private final byte[] data = new byte[3];
    public ShortMessage() { }
    public void setMessage(int status) { }
    public void setMessage(int command, int data1, int data2) { }
    public void setMessage(int command, int channel, int data1, int data2) { }
    public int getChannel() { return 0; }
    public int getCommand() { return 0; }
    @Override public int getStatus() { return 0; }
    @Override public byte[] getMessage() { return data; }
    @Override public int getLength() { return data.length; }
    public int getData1() { return 0; }
    public int getData2() { return 0; }
}
