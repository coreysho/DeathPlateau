package javax.sound.midi;
/** Browser shim: Web Audio is the synthesiser; nothing here produces sound. */
public interface Synthesizer {
    void open();
    void close();
    boolean isOpen();
    Receiver getReceiver();
    boolean loadAllInstruments(Soundbank sb);
    void unloadAllInstruments(Soundbank sb);
    Soundbank getDefaultSoundbank();
}
