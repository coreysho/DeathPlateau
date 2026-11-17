package javax.swing;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Insets;
import java.awt.event.WindowListener;
/**
 * Browser shim. The page is the window: there is nothing to decorate, move or maximise, so these
 * are accepted and ignored. ViewBox still runs; it simply has no frame to manage.
 */
public class JFrame extends java.awt.Container {
    public static final int NORMAL = 0, MAXIMIZED_BOTH = 6, EXIT_ON_CLOSE = 3;
    public JFrame() { }
    public JFrame(String title) { }
    public void setTitle(String t) { }
    public void setResizable(boolean b) { }
    public void setUndecorated(boolean b) { }
    public void setLocationRelativeTo(Component c) { }
    public void setDefaultCloseOperation(int op) { }
    public void setExtendedState(int state) { }
    public int getExtendedState() { return NORMAL; }
    public void setIconImages(java.util.List<? extends java.awt.Image> icons) { }
    public void setIconImage(java.awt.Image icon) { }
    public java.awt.Container getContentPane() { return new java.awt.Container(); }
    public void addWindowListener(WindowListener l) { }
    public void pack() { }
    public void toFront() { }
    public void paint(java.awt.Graphics g) { }
    public Insets getInsets() { return new Insets(0, 0, 0, 0); }
    public Dimension getMinimumSize() { return new Dimension(0, 0); }
}
