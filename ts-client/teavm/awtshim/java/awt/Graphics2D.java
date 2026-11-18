package java.awt;
public class Graphics2D extends Graphics {
    public void setRenderingHint(RenderingHints.Key key, Object value) { }
    public Object getRenderingHint(RenderingHints.Key key) { return null; }
    public void setStroke(Object s) { }
    public void fill(Object shape) { }
    public void draw(Object shape) { }

    /**
     * The desktop's stretched window scales its drawing through this. A page never gets here -
     * the client always draws 765x503 and the CANVAS is what gets stretched, by CSS and by the
     * pixel doubling in BrowserShell - but the call has to link.
     */
    public void scale(double sx, double sy) { }
}
