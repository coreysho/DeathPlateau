package java.applet;
/** Browser shim: GameShell extends this. The page is the applet context. */
public class Applet extends java.awt.Component {
    public void init() { }
    public void start() { }
    public void stop() { }
    public void destroy() { }
    public String getParameter(String name) { return null; }
    public java.net.URL getDocumentBase() { return null; }
    public java.net.URL getCodeBase() { return null; }
    public AppletContext getAppletContext() { return null; }
}
