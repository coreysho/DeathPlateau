package awtbridge;

import java.awt.Component;
import java.awt.event.FocusListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.event.MouseWheelEvent;
import java.awt.event.MouseWheelListener;

/**
 * The one door between the browser shell and the AWT shim.
 *
 * It exists because of an asymmetry that is easy to trip over: javac resolves `java.awt.*` from
 * the platform, so code outside this jar sees the REAL AWT API and cannot touch anything the shim
 * adds - while TeaVM resolves the same names from this jar and sees only the shim. A class outside
 * `java.*` is visible to both: compiled here against the shim, resolved there from the jar.
 */
public final class Events {

    private Events() { }

    public static void mousePressed(Component c, int x, int y, int button) {
        MouseEvent e = event(x, y, button);
        for (MouseListener l : c.mouseListeners) {
            l.mousePressed(e);
        }
    }

    public static void mouseReleased(Component c, int x, int y, int button) {
        MouseEvent e = event(x, y, button);
        for (MouseListener l : c.mouseListeners) {
            l.mouseReleased(e);
        }
    }

    public static void mouseMoved(Component c, int x, int y) {
        MouseEvent e = event(x, y, MouseEvent.BUTTON1);
        for (MouseMotionListener l : c.mouseMotionListeners) {
            l.mouseMoved(e);
        }
    }

    public static void mouseDragged(Component c, int x, int y, int button) {
        MouseEvent e = event(x, y, button);
        for (MouseMotionListener l : c.mouseMotionListeners) {
            l.mouseDragged(e);
        }
    }

    public static void mouseExited(Component c) {
        MouseEvent e = event(-1, -1, MouseEvent.BUTTON1);
        for (MouseListener l : c.mouseListeners) {
            l.mouseExited(e);
        }
    }

    public static void mouseWheel(Component c, int x, int y, int rotation) {
        MouseWheelEvent e = new MouseWheelEvent();
        e.x = x;
        e.y = y;
        e.wheelRotation = rotation;
        for (MouseWheelListener l : c.mouseWheelListeners) {
            l.mouseWheelMoved(e);
        }
    }

    public static void keyPressed(Component c, int keyCode, char keyChar) {
        KeyEvent e = key(keyCode, keyChar);
        for (KeyListener l : c.keyListeners) {
            l.keyPressed(e);
        }
    }

    public static void keyReleased(Component c, int keyCode, char keyChar) {
        KeyEvent e = key(keyCode, keyChar);
        for (KeyListener l : c.keyListeners) {
            l.keyReleased(e);
        }
    }

    public static void keyTyped(Component c, char keyChar) {
        KeyEvent e = key(0, keyChar);
        for (KeyListener l : c.keyListeners) {
            l.keyTyped(e);
        }
    }

    public static void focus(Component c, boolean gained) {
        java.awt.event.FocusEvent e = new java.awt.event.FocusEvent();
        for (FocusListener l : c.focusListeners) {
            if (gained) {
                l.focusGained(e);
            } else {
                l.focusLost(e);
            }
        }
    }

    /** Point the shim's pixel path at the browser's canvas. */
    public static void setBlitter(final Blit target) {
        java.awt.Graphics.blitter = new java.awt.Graphics.Blitter() {
            public void blit(int[] pixels, int width, int height, int x, int y) {
                target.blit(pixels, width, height, x, y);
            }
        };
    }

    private static MouseEvent event(int x, int y, int button) {
        MouseEvent e = new MouseEvent();
        e.x = x;
        e.y = y;
        e.button = button;
        e.clickCount = 1;
        return e;
    }

    private static KeyEvent key(int keyCode, char keyChar) {
        KeyEvent e = new KeyEvent();
        e.keyCode = keyCode;
        e.keyChar = keyChar;
        return e;
    }
}
