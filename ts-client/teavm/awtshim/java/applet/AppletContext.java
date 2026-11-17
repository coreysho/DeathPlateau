package java.applet;
public interface AppletContext {
    void showDocument(java.net.URL url);
    void showDocument(java.net.URL url, String target);
    void showStatus(String s);
}
