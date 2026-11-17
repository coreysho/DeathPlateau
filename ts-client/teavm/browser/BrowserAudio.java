package browser;

import awtbridge.Audio;
import org.teavm.jso.JSBody;
import org.teavm.jso.typedarrays.Int8Array;

/**
 * SOUND, THROUGH WEB AUDIO (2026-11-17).
 *
 * The client does all of its own mixing - envelopes, filters, every voice summed into signed
 * 16-bit mono samples a fortieth of a second at a time (jagex2/sound/AreaSounds.mix) - and then
 * asks javax.sound.sampled for somewhere to put them. So nothing of the sound engine has to be
 * ported: this is the speaker at the end of it, and it is small.
 *
 * SCHEDULED, NOT PLAYED. Each chunk becomes an AudioBuffer started at an exact time on the
 * context's own clock, each one beginning where the last ends. Playing them as they arrive would
 * leave a gap wherever a frame ran long, and a gap in 8kHz mono is a click.
 *
 * AND A PAGE MAY NOT MAKE A SOUND UNTIL IT IS TOUCHED. Every browser refuses audio until the
 * person has interacted with the page, so the context is created suspended and resumed on the
 * first click, key or touch - which on this client is someone typing their name.
 */
public final class BrowserAudio implements Audio {

    public static void install() {
        Audio.set(new BrowserAudio());
    }

    @Override public void open(int sampleRate) { jsOpen(sampleRate); }

    @Override public void write(byte[] pcm, int off, int len) {
        // TeaVM byte[] is a JS Int8Array underneath, so this hands over the same memory rather
        // than copying it sample by sample across the boundary.
        jsWrite(Int8Array.copyFromJavaArray(pcm), off, len);
    }

    @Override public double queuedSeconds() { return jsQueued(); }

    @Override public void close() { jsClose(); }

    @JSBody(params = "rate", script =
        "var A = window.AudioContext || window.webkitAudioContext;\n" +
        "if (!A) { return; }\n" +
        "if (!window.__audio) {\n" +
        "  var ctx = new A({ sampleRate: rate });\n" +
        "  window.__audio = { ctx: ctx, next: 0, rate: rate };\n" +
        // Autoplay policy: a context made before the first interaction starts suspended, and
        // anything scheduled on it is silently dropped. These wake it on the first one.
        "  var wake = function () {\n" +
        "    if (window.__audio.ctx.state !== 'running') { window.__audio.ctx.resume(); }\n" +
        "  };\n" +
        "  ['pointerdown', 'touchstart', 'keydown', 'click'].forEach(function (e) {\n" +
        "    document.addEventListener(e, wake, { passive: true });\n" +
        "  });\n" +
        "}")
    private static native void jsOpen(int rate);

    @JSBody(params = { "bytes", "off", "len" }, script =
        "var a = window.__audio;\n" +
        "if (!a || a.ctx.state === 'closed') { return; }\n" +
        "var n = len >> 1;\n" +
        "var buf = a.ctx.createBuffer(1, n, a.rate);\n" +
        "var out = buf.getChannelData(0);\n" +
        "for (var i = 0; i < n; i++) {\n" +
        "  var lo = bytes[off + i * 2] & 0xff;\n" +
        "  var hi = bytes[off + i * 2 + 1];\n" +          // signed: this is the high byte
        "  out[i] = ((hi << 8) | lo) / 32768;\n" +
        "}\n" +
        "var src = a.ctx.createBufferSource();\n" +
        "src.buffer = buf;\n" +
        "src.connect(a.ctx.destination);\n" +
        "var now = a.ctx.currentTime;\n" +
        // A chunk that arrived late starts now rather than in the past, which would drop it.
        "if (a.next < now) { a.next = now + 0.02; }\n" +
        "src.start(a.next);\n" +
        "a.next += buf.duration;")
    private static native void jsWrite(Int8Array bytes, int off, int len);

    @JSBody(params = {}, script =
        "var a = window.__audio;\n" +
        "if (!a) { return 0; }\n" +
        "var left = a.next - a.ctx.currentTime;\n" +
        "return left > 0 ? left : 0;")
    private static native double jsQueued();

    @JSBody(params = {}, script =
        "var a = window.__audio;\n" +
        "if (a) { a.next = 0; }")
    private static native void jsClose();
}
