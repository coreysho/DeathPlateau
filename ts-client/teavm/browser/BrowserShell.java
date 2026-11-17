package browser;

import awtbridge.Blit;
import awtbridge.Events;
import org.teavm.jso.JSBody;
import org.teavm.jso.browser.Window;
import org.teavm.jso.canvas.CanvasRenderingContext2D;
import org.teavm.jso.canvas.ImageData;
import org.teavm.jso.dom.events.Event;
import org.teavm.jso.dom.events.EventListener;
import org.teavm.jso.dom.events.KeyboardEvent;
import org.teavm.jso.dom.events.MouseEvent;
import org.teavm.jso.dom.html.HTMLCanvasElement;
import org.teavm.jso.dom.html.HTMLDocument;
import org.teavm.jso.typedarrays.Uint8ClampedArray;

/**
 * The browser half of the client's shell.
 *
 * On the desktop GameShell is an Applet: AWT gives it a drawing surface and feeds it mouse and key
 * events. A page has neither, so this supplies both - a canvas for the pixels, DOM events routed
 * into the listener interfaces GameShell already implements. The client is unchanged and unaware;
 * everything crosses through awtbridge, which both javac and TeaVM can see.
 */
public final class BrowserShell {

    private static HTMLCanvasElement canvas;
    private static CanvasRenderingContext2D ctx;
    private static ImageData scratch;
    private static int scratchW, scratchH;

    /**
     * HOW BIG EACH GAME PIXEL IS IN THE CANVAS (2026-11-17).
     *
     * The client draws 765x503 and cannot be asked for more. A page then has to stretch that to
     * the window, and stretching by a fraction is what makes it look grainy: at 1.49 some game
     * pixels land on two screen pixels and their neighbours land on one, so straight edges come
     * out with a tooth in them. Reported from a desktop.
     *
     * So on a monitor the frame is pixel-doubled into a canvas twice the size - whole numbers,
     * every pixel the same - and the browser scales THAT to the window. Shrinking a doubled
     * image is smooth work; blowing up the original is not. The game stays as big as it was and
     * stops shimmering.
     *
     * A phone keeps 1, because it pays for this twice: the extra copy every frame, and a screen
     * dense enough that the stretch was never visible on it anyway.
     */
    private static int scale = 1;

    /** Where the client's own pixels are drawn before the doubling. Null when scale is 1. */
    private static HTMLCanvasElement buffer;
    private static CanvasRenderingContext2D bufferCtx;

    /** Canvas pixels per game pixel, for everything that has to turn a click back into one. */
    public static int scale() { return scale; }

    private BrowserShell() { }

    public static HTMLCanvasElement canvas() { return canvas; }

    public static void install(int width, int height) {
        HTMLDocument doc = Window.current().getDocument();
        canvas = (HTMLCanvasElement) doc.getElementById("gameCanvas");
        if (canvas == null) {
            canvas = (HTMLCanvasElement) doc.createElement("canvas");
            canvas.setAttribute("id", "gameCanvas");
            doc.getBody().appendChild(canvas);
        }
        scale = wantsDoubling() ? 2 : 1;
        canvas.setWidth(width * scale);
        canvas.setHeight(height * scale);
        canvas.setAttribute("tabindex", "0");
        ctx = (CanvasRenderingContext2D) canvas.getContext("2d");
        if (scale != 1) {
            // Off, so the doubling stays square-edged. The smoothing that makes this look right
            // is the browser's, when it fits this canvas to the window.
            noSmoothing(ctx);
            buffer = (HTMLCanvasElement) doc.createElement("canvas");
            buffer.setWidth(width);
            buffer.setHeight(height);
            bufferCtx = (CanvasRenderingContext2D) buffer.getContext("2d");
        }

        // Where PixMap's pixels end up. The client hands over ARGB ints; a canvas wants RGBA
        // bytes, so the only work per frame is the channel shuffle.
        Events.setBlitter(new Blit() {
            @Override public void blit(int[] pixels, int w, int h, int x, int y) {
                if (pixels == null || w <= 0 || h <= 0) {
                    return;
                }
                if (scratch == null || scratchW != w || scratchH != h) {
                    scratch = ctx.createImageData(w, h);
                    scratchW = w;
                    scratchH = h;
                }
                Uint8ClampedArray out = scratch.getData();
                int n = w * h;
                for (int i = 0; i < n; i++) {
                    int argb = pixels[i];
                    int o = i << 2;
                    out.set(o, (argb >> 16) & 0xff);
                    out.set(o + 1, (argb >> 8) & 0xff);
                    out.set(o + 2, argb & 0xff);
                    out.set(o + 3, 255);
                }
                if (scale == 1) {
                    ctx.putImageData(scratch, x, y);
                } else {
                    // Only the rectangle that changed is doubled, not the whole frame: the client
                    // blits the viewport and the sidebar separately and most frames touch one.
                    bufferCtx.putImageData(scratch, x, y);
                    blowUp(ctx, buffer, x, y, w, h, scale);
                }
            }
        });
    }

    /**
     * Route DOM events into the component's AWT listeners.
     *
     * Coordinates are scaled into canvas space. The page sizes the canvas with CSS so it fits the
     * window - on a phone it must - and offsetX is in CSS pixels, so without the scale every click
     * lands off by the stretch ratio, worse the nearer the edge. That exact bug cost a round in
     * the ts377 client; it is not a hypothetical.
     */
    public static void bind(final java.awt.Component component) {
        canvas.addEventListener("mousedown", new EventListener<MouseEvent>() {
            @Override public void handleEvent(MouseEvent e) {
                Events.mousePressed(component, x(e), y(e), button(e));
                canvas.focus();
            }
        });
        canvas.addEventListener("mouseup", new EventListener<MouseEvent>() {
            @Override public void handleEvent(MouseEvent e) {
                Events.mouseReleased(component, x(e), y(e), button(e));
            }
        });
        canvas.addEventListener("mousemove", new EventListener<MouseEvent>() {
            @Override public void handleEvent(MouseEvent e) {
                if (buttonsDown(e) != 0) {
                    Events.mouseDragged(component, x(e), y(e), button(e));
                } else {
                    Events.mouseMoved(component, x(e), y(e));
                }
            }
        });
        canvas.addEventListener("mouseout", new EventListener<MouseEvent>() {
            @Override public void handleEvent(MouseEvent e) { Events.mouseExited(component); }
        });
        canvas.addEventListener("wheel", new EventListener<Event>() {
            @Override public void handleEvent(Event e) {
                Events.mouseWheel(component, 0, 0, wheelDelta(e) > 0 ? 1 : -1);
                e.preventDefault();
            }
        });
        canvas.addEventListener("keydown", new EventListener<KeyboardEvent>() {
            @Override public void handleEvent(KeyboardEvent e) {
                char ch = charOf(e);
                Events.keyPressed(component, code(e), ch);
                if (ch != 0) {
                    Events.keyTyped(component, ch);
                }
                // Swallowed, so the page does not scroll and Tab does not walk the focus ring -
                // except for the browser's own: a player who cannot press Ctrl+R or F5 is stuck.
                if (!e.isCtrlKey() && !e.isMetaKey() && !isBrowserKey(e)) {
                    e.preventDefault();
                }
            }
        });
        canvas.addEventListener("keyup", new EventListener<KeyboardEvent>() {
            @Override public void handleEvent(KeyboardEvent e) {
                Events.keyReleased(component, code(e), charOf(e));
            }
        });
        canvas.addEventListener("contextmenu", new EventListener<Event>() {
            @Override public void handleEvent(Event e) { e.preventDefault(); }
        });
        canvas.addEventListener("focus", new EventListener<Event>() {
            @Override public void handleEvent(Event e) { Events.focus(component, true); }
        });
        canvas.addEventListener("blur", new EventListener<Event>() {
            @Override public void handleEvent(Event e) { Events.focus(component, false); }
        });
        canvas.focus();
    }

    /**
     * THE BROWSER'S KEY CODES ARE NOT AWT'S (2026-11-17).
     *
     * GameShell.keyPressed switches on AWT constants, and a DOM keydown carries DOM ones. They
     * agree about letters, digits, Backspace, Tab, Escape, the modifiers, the arrows, Home/End,
     * the page keys and F1-F12 - which is most of the keyboard, and is exactly why this went
     * unnoticed: typing worked.
     *
     * They disagree about two. ENTER is 10 in AWT and 13 in the DOM, and DELETE is 127 against
     * 46. So Enter fell through every branch, its character was dropped by the `ch < 30` guard
     * above them, and nothing happened: no login, no chat line sent, on a keyboard that was
     * otherwise working perfectly. Reported from a desktop, 2026-11-17.
     *
     * Read from the key's NAME rather than its code, because that is the part of a keydown with
     * one meaning: keyCode is deprecated, and numpad Enter and the main one differ in `code` but
     * not in `key`.
     */
    private static int code(KeyboardEvent e) {
        String key = e.getKey();
        if (key != null) {
            if ("Enter".equals(key)) {
                return 10;
            }
            if ("Delete".equals(key)) {
                return 127;
            }
            if ("Backspace".equals(key)) {
                return 8;
            }
            if ("Tab".equals(key)) {
                return 9;
            }
            if ("Escape".equals(key)) {
                return 27;
            }
            if ("Shift".equals(key)) {
                return 16;
            }
            if ("Control".equals(key)) {
                return 17;
            }
            if ("Alt".equals(key)) {
                return 18;
            }
            if ("ArrowLeft".equals(key)) {
                return 37;
            }
            if ("ArrowUp".equals(key)) {
                return 38;
            }
            if ("ArrowRight".equals(key)) {
                return 39;
            }
            if ("ArrowDown".equals(key)) {
                return 40;
            }
            if ("Home".equals(key)) {
                return 36;
            }
            if ("End".equals(key)) {
                return 35;
            }
            if ("PageUp".equals(key)) {
                return 33;
            }
            if ("PageDown".equals(key)) {
                return 34;
            }
            if (key.length() > 1 && key.charAt(0) == 'F') {
                int n = number(key.substring(1));
                if (n >= 1 && n <= 12) {
                    return 111 + n;
                }
            }
        }
        return e.getKeyCode();
    }

    /** F5 reloads, F11 goes full screen, F12 opens the tools: the page does not get to keep those. */
    private static boolean isBrowserKey(KeyboardEvent e) {
        String key = e.getKey();
        return "F5".equals(key) || "F11".equals(key) || "F12".equals(key);
    }

    private static int number(String s) {
        int n = 0;
        if (s.length() == 0) {
            return -1;
        }
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') {
                return -1;
            }
            n = n * 10 + (c - '0');
        }
        return n;
    }

    private static char charOf(KeyboardEvent e) {
        String key = e.getKey();
        if (key != null && key.length() == 1) {
            return key.charAt(0);
        }
        if ("Enter".equals(key)) {
            return 10;
        }
        if ("Backspace".equals(key)) {
            return 8;
        }
        return 0;
    }

    // Into the client's own pixels: out of CSS pixels by the stretch, then out of canvas pixels
    // by the doubling. Miss the second step and every click lands at twice its distance from the
    // top left corner.
    private static int x(MouseEvent e) {
        return (int) Math.round(offsetX(e) * (canvas.getWidth() / (double) clientWidth(canvas)) / scale);
    }

    private static int y(MouseEvent e) {
        return (int) Math.round(offsetY(e) * (canvas.getHeight() / (double) clientHeight(canvas)) / scale);
    }

    /** AWT button numbering: 1 left, 2 middle, 3 right. */
    private static int button(MouseEvent e) {
        int b = e.getButton();
        return b == 2 ? 3 : b == 1 ? 2 : 1;
    }

    /** A mouse means a monitor, where there is processor to spare and the stretch shows. */
    @JSBody(params = {}, script =
        "return !!(window.matchMedia && window.matchMedia('(pointer: fine)').matches);")
    private static native boolean wantsDoubling();

    @JSBody(params = "c", script = "c.imageSmoothingEnabled = false;")
    private static native void noSmoothing(CanvasRenderingContext2D c);

    @JSBody(params = { "c", "src", "x", "y", "w", "h", "s" },
        script = "c.drawImage(src, x, y, w, h, x * s, y * s, w * s, h * s);")
    private static native void blowUp(CanvasRenderingContext2D c, HTMLCanvasElement src,
            int x, int y, int w, int h, int s);

    @JSBody(params = "e", script = "return e.offsetX;")
    private static native double offsetX(MouseEvent e);

    @JSBody(params = "e", script = "return e.offsetY;")
    private static native double offsetY(MouseEvent e);

    @JSBody(params = "e", script = "return e.buttons || 0;")
    private static native int buttonsDown(MouseEvent e);

    @JSBody(params = "e", script = "return e.deltaY || 0;")
    private static native double wheelDelta(Event e);

    @JSBody(params = "c", script = "return c.clientWidth || c.width;")
    private static native int clientWidth(HTMLCanvasElement c);

    @JSBody(params = "c", script = "return c.clientHeight || c.height;")
    private static native int clientHeight(HTMLCanvasElement c);
}
