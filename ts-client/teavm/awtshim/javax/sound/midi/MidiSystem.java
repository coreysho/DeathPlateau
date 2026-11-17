package javax.sound.midi;
import java.io.File;
import java.io.InputStream;
/** Browser shim: the JVM sequencer does not exist in a page; music goes through Web Audio. */
public class MidiSystem {
    public static Sequencer getSequencer() { return null; }
    public static Sequencer getSequencer(boolean connected) { return null; }
    public static Synthesizer getSynthesizer() { return null; }
    public static Receiver getReceiver() { return null; }
    public static Sequence getSequence(File file) { return null; }
    public static Sequence getSequence(InputStream in) { return null; }
    public static Soundbank getSoundbank(File file) { return null; }
    public static Soundbank getSoundbank(InputStream in) { return null; }
}
