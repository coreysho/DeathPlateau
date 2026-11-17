package javax.sound.midi;
public class ShortMessage {
    public static final int CONTROL_CHANGE = 176, NOTE_ON = 144, NOTE_OFF = 128;
    public ShortMessage() { }
    public void setMessage(int command, int channel, int data1, int data2) { }
    public int getChannel() { return 0; }
    public int getCommand() { return 0; }
    public int getData1() { return 0; }
    public int getData2() { return 0; }
}
