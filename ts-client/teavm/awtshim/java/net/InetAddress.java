package java.net;
/** Browser shim: there is no host lookup in a page; the socket URL carries the host. */
public class InetAddress {
    private final String host;
    private InetAddress(String host) { this.host = host; }
    public static InetAddress getByName(String host) { return new InetAddress(host); }
    public static InetAddress getLocalHost() { return new InetAddress("localhost"); }
    public String getHostAddress() { return host; }
    public String getHostName() { return host; }
}
