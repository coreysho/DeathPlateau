package java.net;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
/**
 * Browser shim. A page cannot open a TCP socket, so the real implementation is the client's own
 * WsSocket over a WebSocket; this type exists so the classes that still name java.net.Socket link.
 */
public class Socket {
    public Socket() { }
    public Socket(InetAddress address, int port) throws IOException { }
    public Socket(String host, int port) throws IOException { }
    public InputStream getInputStream() throws IOException { throw new IOException("no TCP in a browser"); }
    public OutputStream getOutputStream() throws IOException { throw new IOException("no TCP in a browser"); }
    public void setSoTimeout(int ms) throws IOException { }
    public void setTcpNoDelay(boolean on) throws IOException { }
    public void close() throws IOException { }
    public boolean isClosed() { return true; }
    public InetAddress getInetAddress() { return null; }
}
