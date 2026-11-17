package dp;

import browser.BrowserShell;
import org.teavm.jso.browser.Window;

/**
 * Browser entry point.
 *
 * Installs the canvas and the pixel path, points the client at the page's own origin, then starts
 * it exactly as the desktop does - new Client(), initApplication() - and binds DOM events to the
 * component it registered its listeners on. The client is unchanged and unaware.
 *
 * The host has to be set BEFORE Client is first touched: WEB_URL and WS_URL are `static final`,
 * read from system properties when the class initialises, so a property set afterwards is too
 * late. Same shape as the flags bug in the ts377 readout, and the same fix - do it first.
 */
public class Main {
    private static final int WIDTH = 765;
    private static final int HEIGHT = 503;

    public static void main(String[] args) {
        String host = origin();
        System.setProperty("lostcity.weburl", "http://" + host);
        System.setProperty("lostcity.ws", "ws://" + host + "/");
        System.out.println("browser shell " + WIDTH + "x" + HEIGHT + ", server " + host);

        BrowserShell.install(WIDTH, HEIGHT);
        start();
    }

    /** Separate so Client is not resolved until the properties above are set. */
    private static void start() {
        jagex2.client.Client app = new jagex2.client.Client();
        app.initApplication(HEIGHT, WIDTH);
        BrowserShell.bind(app.getBaseComponent());
        System.out.println("client started");
    }

    @org.teavm.jso.JSBody(params = {}, script = "return location.host;")
    private static native String origin();
}
