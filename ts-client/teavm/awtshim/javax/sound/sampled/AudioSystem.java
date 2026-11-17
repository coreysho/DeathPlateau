package javax.sound.sampled;

/**
 * Browser shim. A page has Web Audio and no mixer, which is all this client needs: it sums its
 * own voices and asks for one line of signed 16-bit mono samples (AreaSounds.mix).
 *
 * With no sink installed this returns null, exactly as it did before sound existed here - the
 * caller's try/catch turns that into "no sound" and the game runs on.
 */
public class AudioSystem {

    public static SourceDataLine getSourceDataLine(AudioFormat f) {
        return awtbridge.Audio.get() == null ? null : new BrowserLine(f);
    }

    public static Line getLine(Line.Info info) { return null; }

    public static AudioInputStream getAudioInputStream(java.io.InputStream in) { return null; }
}

/**
 * The line itself. Everything it does is handing bytes to the page - except the one thing that
 * matters, which is NOT handing them over too fast.
 *
 * On a desktop the mixer thread is paced by this write blocking when the sound card's buffer is
 * full. Nothing in a browser blocks, and the mixer is a `while (true)` with no clock, so left to
 * itself it would mix as fast as the processor allows: hours of audio a second, every other thread
 * starved, the game frozen with the music playing. So the write waits until the page has less than
 * a quarter of a second left to play before it adds more.
 */
class BrowserLine implements SourceDataLine {

    /** How far ahead of the speaker to stay. Lower is tighter timing, higher survives a slow frame. */
    private static final double AHEAD_SECONDS = 0.25D;

    private final AudioFormat format;
    private boolean open;

    BrowserLine(AudioFormat format) { this.format = format; }

    @Override public void open(AudioFormat f, int bufferSize) { open(f); }

    @Override public void open(AudioFormat f) {
        awtbridge.Audio a = awtbridge.Audio.get();
        if (a != null && !this.open) {
            a.open((int) f.getSampleRate());
            this.open = true;
        }
    }

    @Override public void open() { open(this.format); }

    @Override public int write(byte[] b, int off, int len) {
        awtbridge.Audio a = awtbridge.Audio.get();
        if (a == null) {
            return len;
        }
        while (a.queuedSeconds() > AHEAD_SECONDS) {
            try {
                Thread.sleep(5L);
            } catch (InterruptedException ignore) {
                break;
            }
        }
        a.write(b, off, len);
        return len;
    }

    @Override public void start() { }
    @Override public void stop() { }
    @Override public void flush() { }

    @Override public void drain() {
        awtbridge.Audio a = awtbridge.Audio.get();
        if (a == null) {
            return;
        }
        while (a.queuedSeconds() > 0.0D) {
            try {
                Thread.sleep(10L);
            } catch (InterruptedException ignore) {
                break;
            }
        }
    }

    @Override public void close() {
        awtbridge.Audio a = awtbridge.Audio.get();
        if (a != null) {
            a.close();
        }
        this.open = false;
    }

    @Override public int available() { return Integer.MAX_VALUE; }
    @Override public boolean isActive() { return this.open; }
    @Override public boolean isOpen() { return this.open; }
    @Override public Control getControl(Control.Type type) { return null; }
    @Override public boolean isControlSupported(Control.Type type) { return false; }
}
