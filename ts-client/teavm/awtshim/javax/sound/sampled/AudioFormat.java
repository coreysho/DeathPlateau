package javax.sound.sampled;
/** Browser shim: enough of the shape for the one format this client asks for. */
public class AudioFormat {
    private final float sampleRate;
    private final int sampleSizeInBits;
    private final int channels;
    private final boolean signed;
    private final boolean bigEndian;

    public AudioFormat(float sampleRate, int sampleSizeInBits, int channels, boolean signed, boolean bigEndian) {
        this.sampleRate = sampleRate;
        this.sampleSizeInBits = sampleSizeInBits;
        this.channels = channels;
        this.signed = signed;
        this.bigEndian = bigEndian;
    }

    public float getSampleRate() { return this.sampleRate; }
    public int getSampleSizeInBits() { return this.sampleSizeInBits; }
    public int getChannels() { return this.channels; }
    public boolean isBigEndian() { return this.bigEndian; }
    public boolean isSigned() { return this.signed; }
}
