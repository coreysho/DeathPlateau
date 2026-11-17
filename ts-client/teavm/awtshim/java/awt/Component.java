package java.awt;
/** Browser shim: the AWT component GameShell draws into. Geometry and focus only. */
public class Component {
    public int width, height;
    public void setSize(int w, int h) { width = w; height = h; }
    public void setPreferredSize(Dimension d) { width = d.width; height = d.height; }
    public Dimension getPreferredSize() { return getSize(); }
    public void setMinimumSize(Dimension d) { }
    public void setMaximumSize(Dimension d) { }
    public void setLayout(LayoutManager l) { }
    public void setLayout(Object l) { }
    public void setVisible(boolean b) { visible = b; }
    public boolean isVisible() { return visible; }
    public boolean isResizable() { return true; }
    private boolean visible = true;
    public Dimension getSize() { return new Dimension(width, height); }
    public int getWidth() { return width; }
    public int getHeight() { return height; }
    public Dimension size() { return getSize(); }
    public Graphics getGraphics() { return new Graphics(); }
    public void requestFocus() { }
    public void setFocusTraversalKeysEnabled(boolean b) { }
    // The listeners are KEPT, not dropped: the browser shell has no other way to reach the
    // client's own handlers. GameShell registers itself here during run(), exactly as it does on
    // the desktop, and the shell then feeds DOM events straight into these.
    public final java.util.List<java.awt.event.MouseListener> mouseListeners =
        new java.util.ArrayList<java.awt.event.MouseListener>();
    public final java.util.List<java.awt.event.MouseMotionListener> mouseMotionListeners =
        new java.util.ArrayList<java.awt.event.MouseMotionListener>();
    public final java.util.List<java.awt.event.MouseWheelListener> mouseWheelListeners =
        new java.util.ArrayList<java.awt.event.MouseWheelListener>();
    public final java.util.List<java.awt.event.KeyListener> keyListeners =
        new java.util.ArrayList<java.awt.event.KeyListener>();
    public final java.util.List<java.awt.event.FocusListener> focusListeners =
        new java.util.ArrayList<java.awt.event.FocusListener>();

    public void addMouseListener(java.awt.event.MouseListener l) { if (l != null) mouseListeners.add(l); }
    public void addMouseMotionListener(java.awt.event.MouseMotionListener l) { if (l != null) mouseMotionListeners.add(l); }
    public void addMouseWheelListener(java.awt.event.MouseWheelListener l) { if (l != null) mouseWheelListeners.add(l); }
    public void addKeyListener(java.awt.event.KeyListener l) { if (l != null) keyListeners.add(l); }
    public void addFocusListener(java.awt.event.FocusListener l) { if (l != null) focusListeners.add(l); }
    public void setBackground(Color c) { }
    public void repaint() { }
    public void setCursor(Cursor c) { }
    public Image createImage(int w, int h) {
        Image img = new Image();
        img.setDimensions(w, h);
        return img;
    }

    /** PixMap passes itself in as the producer; the Image registers as its consumer. */
    public Image createImage(java.awt.image.ImageProducer producer) { return new Image(producer); }

    public boolean prepareImage(Image img, java.awt.image.ImageObserver o) { return true; }

    public FontMetrics getFontMetrics(Font f) { return new FontMetrics(); }
    public java.awt.Toolkit getToolkit() { return new Toolkit(); }
}
