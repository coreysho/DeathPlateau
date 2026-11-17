package browser;

import awtbridge.Events;
import org.teavm.jso.JSBody;
import org.teavm.jso.JSFunctor;
import org.teavm.jso.JSObject;
import org.teavm.jso.dom.html.HTMLCanvasElement;

/**
 * A FINGER, WHERE THE CLIENT EXPECTS A MOUSE (2026-11-17).
 *
 * This client is played with two buttons and a hover, and a phone has none of the three. What a
 * touch screen gives is a point, a duration and a distance, so that is what this turns into the
 * events GameShell already handles:
 *
 *   a tap               -> move, press, release, left button
 *   a press held still  -> move, press, release, RIGHT button: the menu opens under the finger
 *   a press and a drag  -> press at where it started, drags as it moves, release at the end
 *
 * The decision is made from movement, not from timing alone: a finger that has moved more than a
 * few pixels is a drag and can never become a long press, and one that has not moved by the time
 * the timer fires is a long press and never becomes a tap. That ordering matters - a scroll bar
 * dragged slowly would otherwise open a menu in the middle of the drag.
 *
 * jagex2/client/BrowserInput.java is the same problem solved for CheerpJ, and it is worth reading
 * for why it is harder there: that runtime ignores synthetic events, so the page has to hand its
 * keys and taps across as field writes and the client polls for them. Nothing of the sort is
 * needed here. The AWT these events arrive at is this build's own shim, so a press made up in
 * JavaScript is as real as any other, and the client cannot tell the difference.
 *
 * THE STATE MACHINE LIVES IN JAVASCRIPT because the timer does. Java gets one call per event with
 * the kind already decided, which keeps the Java side a switch.
 */
public final class BrowserTouch {

    /** How long a finger must stay still before it counts as a right-click, in milliseconds. */
    private static final int LONG_PRESS_MS = 450;

    /** How far it may wander first, in canvas pixels, before it is a drag instead. */
    private static final int SLOP_PX = 12;

    private static final int MOVE = 1, PRESS = 2, RELEASE = 3, PRESS_RIGHT = 4, RELEASE_RIGHT = 5,
            DRAG = 6, CAMERA = 7;

    private BrowserTouch() { }

    @JSFunctor
    public interface Sink extends JSObject {
        void on(int kind, int x, int y);
    }

    public static void install(HTMLCanvasElement canvas, final java.awt.Component component) {
        wire(canvas, new Sink() {
            @Override public void on(int kind, int x, int y) {
                switch (kind) {
                    case MOVE: Events.mouseMoved(component, x, y); break;
                    case PRESS: Events.mousePressed(component, x, y, 1); break;
                    case RELEASE: Events.mouseReleased(component, x, y, 1); break;
                    case PRESS_RIGHT: Events.mousePressed(component, x, y, 3); break;
                    case RELEASE_RIGHT: Events.mouseReleased(component, x, y, 3); break;
                    case DRAG: Events.mouseDragged(component, x, y, 1); break;
                    // Two fingers turn the camera. GameShell takes this as a running total and
                    // folds the difference into the same deltas a middle-button drag produces -
                    // see BrowserInput, which was written for a page that had no middle button
                    // either.
                    case CAMERA:
                        jagex2.client.BrowserInput.cameraDragX += x;
                        jagex2.client.BrowserInput.cameraDragY += y;
                        break;
                    default: break;
                }
            }
        }, LONG_PRESS_MS, SLOP_PX);
    }

    /**
     * Coordinates come back in the canvas's own pixels. A phone draws the client scaled to fit the
     * screen, so clientX has to be divided by that stretch - the same correction the mouse path
     * makes, and the same bug if it is left out: every touch lands short of where it was aimed,
     * worse the further from the top left.
     */
    @JSBody(params = { "c", "sink", "longMs", "slop" }, script =
        "var active = false, sx = 0, sy = 0, lx = 0, ly = 0;\n" +
        "var moved = false, dragging = false, longFired = false, timer = null;\n" +
        "var two = false, mx = 0, my = 0;\n" +
        "function mid(ts) {\n" +
        "  var a = at(ts[0]), b = at(ts[1]);\n" +
        "  return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];\n" +
        "}\n" +
        "function at(t) {\n" +
        "  var r = c.getBoundingClientRect();\n" +
        "  return [Math.round((t.clientX - r.left) * (c.width / r.width)),\n" +
        "          Math.round((t.clientY - r.top) * (c.height / r.height))];\n" +
        "}\n" +
        "c.addEventListener('touchstart', function (e) {\n" +
        // A second finger ends whatever the first was doing: no tap, no menu, no drag - the
        // gesture is now a camera turn, and the single-finger state machine stays out of it.
        "  if (e.touches.length === 2) {\n" +
        "    if (timer) { clearTimeout(timer); timer = null; }\n" +
        "    if (dragging) { sink(3, lx, ly); }\n" +
        "    active = false; dragging = false; two = true;\n" +
        "    var m = mid(e.touches); mx = m[0]; my = m[1];\n" +
        "    e.preventDefault(); return;\n" +
        "  }\n" +
        "  if (e.touches.length !== 1 || two) { return; }\n" +
        "  var p = at(e.touches[0]);\n" +
        "  sx = lx = p[0]; sy = ly = p[1];\n" +
        "  active = true; moved = false; dragging = false; longFired = false;\n" +
        "  sink(1, sx, sy);\n" +
        "  if (timer) { clearTimeout(timer); }\n" +
        "  timer = setTimeout(function () {\n" +
        "    if (active && !moved) { longFired = true; sink(4, sx, sy); sink(5, sx, sy); }\n" +
        "  }, longMs);\n" +
        "  e.preventDefault();\n" +
        "}, { passive: false });\n" +
        "c.addEventListener('touchmove', function (e) {\n" +
        "  if (two && e.touches.length === 2) {\n" +
        "    var m = mid(e.touches);\n" +
        "    sink(7, m[0] - mx, m[1] - my);\n" +
        "    mx = m[0]; my = m[1];\n" +
        "    e.preventDefault(); return;\n" +
        "  }\n" +
        "  if (!active || e.touches.length !== 1) { return; }\n" +
        "  var p = at(e.touches[0]); lx = p[0]; ly = p[1];\n" +
        "  if (!moved && (Math.abs(lx - sx) > slop || Math.abs(ly - sy) > slop)) {\n" +
        "    moved = true;\n" +
        "    if (timer) { clearTimeout(timer); timer = null; }\n" +
        "    if (!longFired) { dragging = true; sink(2, sx, sy); }\n" +
        "  }\n" +
        "  sink(dragging ? 6 : 1, lx, ly);\n" +
        "  e.preventDefault();\n" +
        "}, { passive: false });\n" +
        "function end(e) {\n" +
        "  if (two) {\n" +
        // Both fingers have to leave before a tap can start again, or lifting one of them is read
        // as the start of a press that was never made.
        "    if (e.touches.length === 0) { two = false; }\n" +
        "    if (e.cancelable) { e.preventDefault(); }\n" +
        "    return;\n" +
        "  }\n" +
        "  if (!active) { return; }\n" +
        "  active = false;\n" +
        "  if (timer) { clearTimeout(timer); timer = null; }\n" +
        "  if (dragging) { sink(3, lx, ly); }\n" +
        "  else if (!longFired) { sink(2, sx, sy); sink(3, sx, sy); }\n" +
        "  if (e.cancelable) { e.preventDefault(); }\n" +
        "}\n" +
        "c.addEventListener('touchend', end, { passive: false });\n" +
        "c.addEventListener('touchcancel', end, { passive: false });")
    private static native void wire(HTMLCanvasElement c, Sink sink, int longMs, int slop);
}
