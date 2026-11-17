package browser;

import org.teavm.jso.JSBody;

/**
 * The browser half of WsSocket.
 *
 * On CheerpJ these four were natives the page implemented; here they are the same four calls in
 * JavaScript, kept byte-for-byte compatible - bytes still cross as base64, because that is what
 * the client's WsSocket already encodes and decodes and the protocol is not worth re-cutting for
 * this. Reads are non-blocking and return null when nothing has arrived, exactly as before.
 */
public final class BrowserSocket {

    private BrowserSocket() { }

    @JSBody(params = "url", script =
        "if (!window.__ws) { window.__ws = { next: 1, socks: {} }; }\n" +
        "var id = window.__ws.next++;\n" +
        "var s = { ws: new WebSocket(url), buf: [], out: [], open: false, closed: false };\n" +
        "s.ws.binaryType = 'arraybuffer';\n" +
        // A WebSocket is not open for a round trip after new WebSocket(), but the client writes its
        // first byte (the stream-type byte, 14 or 15) the instant openSocket returns. Dropping it
        // leaves the server waiting for a type and the client waiting for the reply: a hang at
        // "Connecting to update server". So writes before onopen are queued and flushed here.
        "s.ws.onopen = function () { s.open = true;\n" +
        "  for (var i = 0; i < s.out.length; i++) { try { s.ws.send(s.out[i]); } catch (e) { } }\n" +
        "  s.out = []; };\n" +
        "s.ws.onclose = function () { s.closed = true; };\n" +
        "s.ws.onerror = function () { s.closed = true; };\n" +
        "s.ws.onmessage = function (e) {\n" +
        "  var a = new Uint8Array(e.data);\n" +
        "  for (var i = 0; i < a.length; i++) { s.buf.push(a[i]); }\n" +
        "};\n" +
        "window.__ws.socks[id] = s;\n" +
        "return id;")
    public static native int open(String url);

    /**
     * Up to max bytes as base64. Empty string means "nothing yet" and null means the socket is
     * gone - the distinction matters: WsSocket.fill treats null as a lost connection and throws.
     */
    @JSBody(params = { "handle", "max" }, script =
        "var s = window.__ws && window.__ws.socks[handle];\n" +
        "if (!s || s.closed) { return null; }\n" +
        "if (s.buf.length === 0) { return ''; }\n" +
        "var n = Math.min(max, s.buf.length);\n" +
        "var out = '';\n" +
        "for (var i = 0; i < n; i++) { out += String.fromCharCode(s.buf[i]); }\n" +
        "s.buf.splice(0, n);\n" +
        "return btoa(out);")
    public static native String read(int handle, int max);

    @JSBody(params = { "handle", "base64" }, script =
        "var s = window.__ws && window.__ws.socks[handle];\n" +
        "if (!s || s.closed) { return; }\n" +
        "var bin = atob(base64);\n" +
        "var a = new Uint8Array(bin.length);\n" +
        "for (var i = 0; i < bin.length; i++) { a[i] = bin.charCodeAt(i); }\n" +
        "if (!s.open) { s.out.push(a); return; }\n" +
        "s.ws.send(a);")
    public static native void write(int handle, String base64);

    @JSBody(params = "handle", script =
        "var s = window.__ws && window.__ws.socks[handle];\n" +
        "if (s) { try { s.ws.close(); } catch (e) { } delete window.__ws.socks[handle]; }")
    public static native void close(int handle);

    @JSBody(params = "handle", script =
        "var s = window.__ws && window.__ws.socks[handle];\n" +
        "return s ? (s.closed ? -1 : (s.open ? 1 : 0)) : -1;")
    public static native int state(int handle);
}
