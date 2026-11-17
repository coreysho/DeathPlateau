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
    public void addMouseListener(java.awt.event.MouseListener l) { }
    public void addMouseMotionListener(java.awt.event.MouseMotionListener l) { }
    public void addMouseWheelListener(java.awt.event.MouseWheelListener l) { }
    public void addKeyListener(java.awt.event.KeyListener l) { }
    public void addFocusListener(java.awt.event.FocusListener l) { }
    public void setBackground(Color c) { }
    public void repaint() { }
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
