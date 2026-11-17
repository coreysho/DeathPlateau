package browser;

import org.teavm.jso.JSBody;
import org.teavm.jso.typedarrays.Int8Array;

/**
 * MUSIC (2026-11-17).
 *
 * The client fetches its songs over the update stream and hands each one to the platform as a MIDI
 * file - Client.saveMidi, 60KB for the title theme, around 20KB for an area. On a desktop that
 * goes to javax.sound.midi, which plays it with the soundbank every JVM ships. A browser has
 * neither a MIDI synthesiser nor a soundbank, so both have to be supplied: spessasynth (Apache
 * 2.0) is the synthesiser, and the soundfont is a file the server operator puts next to the
 * client.
 *
 * NOTHING IS FETCHED UNTIL A SONG PLAYS, AND NOTHING AT ALL WITHOUT A SOUNDFONT. The synthesiser
 * is about 900KB and a General MIDI bank is megabytes - against a client that is 0.35MB gzipped,
 * so it cannot be part of the download. The page asks for music.sf3 when the first song arrives:
 * if the server has one, the synthesiser is loaded and the music plays from then on; if it 404s,
 * this says so once and the game is as silent as it was before. See DEPLOY.md.
 */
public final class BrowserMusic {

    private BrowserMusic() { }

    /** A song, as the MIDI bytes the client just received. fade is the client's crossfade flag. */
    public static void play(byte[] midi, boolean fade) {
        if (midi != null && midi.length > 0) {
            jsPlay(Int8Array.copyFromJavaArray(midi), fade);
        }
    }

    public static void stop() { jsStop(); }

    /** The client's own music volume, 0-127 (signlink.midivol, 96 by default). */
    public static void volume(int midiVol) { jsVolume(midiVol); }

    @JSBody(params = { "bytes", "fade" }, script =
        "var M = window.__music;\n" +
        "if (!M) {\n" +
        "  M = window.__music = { ready: false, failed: false, pending: null, vol: 96 };\n" +
        "  M.start = function (buf) {\n" +
        "    try {\n" +
        "      M.seq.loadNewSongList([{ binary: buf }]);\n" +
        // The client sends one song and expects it to keep playing until it sends another.
        "      M.seq.loopCount = Infinity;\n" +
        "      M.seq.play();\n" +
        "    } catch (e) { console.log('music: ' + e); }\n" +
        "  };\n" +
        "  (async function () {\n" +
        "    try {\n" +
        "      var res = await fetch('music.sf3');\n" +
        "      if (!res.ok) {\n" +
        "        M.failed = true;\n" +
        "        console.log('music: no music.sf3 beside the client, so the game stays silent');\n" +
        "        return;\n" +
        "      }\n" +
        "      var sf = await res.arrayBuffer();\n" +
        // Taken now: loading the bank hands the buffer to the worklet thread, which detaches it,
        // and a detached ArrayBuffer reads as zero bytes.
        "      var sfKB = Math.round(sf.byteLength / 1024);\n" +
        "      var A = window.AudioContext || window.webkitAudioContext;\n" +
        "      var ctx = new A();\n" +
        "      await ctx.audioWorklet.addModule('spessasynth_processor.min.js');\n" +
        "      var lib = await import('./spessasynth_lib.js');\n" +
        "      var synth = new lib.WorkletSynthesizer(ctx);\n" +
        // Through a gain node of our own, because the client has a music volume in its settings
        // and the synthesiser's own is not what that slider means.
        "      var gain = ctx.createGain();\n" +
        "      gain.gain.value = M.vol / 127;\n" +
        "      synth.connect(gain);\n" +
        "      gain.connect(ctx.destination);\n" +
        "      await synth.isReady;\n" +
        "      await synth.soundBankManager.addSoundBank(sf, 'main');\n" +
        "      M.ctx = ctx; M.synth = synth; M.gain = gain;\n" +
        "      M.seq = new lib.Sequencer(synth);\n" +
        "      M.ready = true;\n" +
        "      console.log('music: ready, ' + sfKB + 'KB soundfont');\n" +
        "      if (M.pending) { var p = M.pending; M.pending = null; M.start(p); }\n" +
        "    } catch (e) { M.failed = true; console.log('music: ' + e); }\n" +
        "  })();\n" +
        // Autoplay policy: a context made before the page has been touched starts suspended.
        "  var wake = function () { if (M.ctx && M.ctx.state !== 'running') { M.ctx.resume(); } };\n" +
        "  ['pointerdown', 'touchstart', 'keydown', 'click'].forEach(function (ev) {\n" +
        "    document.addEventListener(ev, wake, { passive: true });\n" +
        "  });\n" +
        "}\n" +
        "if (M.failed) { return; }\n" +
        // Copied out of the Java heap: that array is the client's and it reuses it.
        "var buf = new Uint8Array(bytes).buffer;\n" +
        "if (!M.ready) { M.pending = buf; return; }\n" +
        "M.start(buf);")
    private static native void jsPlay(Int8Array bytes, boolean fade);

    @JSBody(params = {}, script =
        "var M = window.__music;\n" +
        "if (M && M.ready) { try { M.seq.pause(); } catch (e) { } }\n" +
        "if (M) { M.pending = null; }")
    private static native void jsStop();

    @JSBody(params = "vol", script =
        "var M = window.__music;\n" +
        "if (!M) { return; }\n" +
        "M.vol = vol;\n" +
        "if (M.gain) { M.gain.gain.value = vol / 127; }")
    private static native void jsVolume(int vol);
}
