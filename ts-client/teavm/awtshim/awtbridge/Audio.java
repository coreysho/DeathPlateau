package awtbridge;

/**
 * The one door between the sound shim and the page, for the same reason awtbridge.Blit exists:
 * the shim is compiled against itself with JDK 8 and has never heard of TeaVM, so it cannot call
 * a @JSBody. It calls this instead, and the browser shell puts the implementation in.
 *
 * The client mixes every voice itself into signed 16-bit mono samples and pushes them at one
 * line - see jagex2/sound/AreaSounds.mix - so this is the whole of its audio output. A desktop
 * client hands those same bytes to javax.sound.sampled and never comes near here.
 */
public interface Audio {

    /** Opened once, with the sample rate the client mixes at. */
    void open(int sampleRate);

    /** Signed 16-bit little-endian mono samples, as the mixer produced them. */
    void write(byte[] pcm, int off, int len);

    /**
     * How much has been handed over but not yet played, in seconds. The mixer thread is a loop
     * with no clock of its own: on a desktop the line blocks when its buffer is full and that is
     * what paces it. Nothing here blocks, so the mixer asks instead and sleeps - without it the
     * loop would run flat out, mixing hours of audio a second and starving every other thread.
     */
    double queuedSeconds();

    void close();

    /** Set by the browser shell at startup; null on a desktop, where nothing calls any of this. */
    Audio[] HOLDER = new Audio[1];

    static void set(Audio a) { HOLDER[0] = a; }

    static Audio get() { return HOLDER[0]; }
}
