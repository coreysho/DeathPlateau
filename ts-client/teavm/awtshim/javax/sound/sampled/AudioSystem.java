package javax.sound.sampled;
/** Browser shim: Web Audio replaces this entirely. */
public class AudioSystem {
    public static SourceDataLine getSourceDataLine(AudioFormat f) { return null; }
    public static Object getLine(Object info) { return null; }
    public static AudioInputStream getAudioInputStream(java.io.InputStream in) { return null; }
}
