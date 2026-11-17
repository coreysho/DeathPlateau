package java.security;
public class MessageDigest {
    public static MessageDigest getInstance(String algorithm) { return new MessageDigest(); }
    public void update(byte[] b) { }
    public byte[] digest() { return new byte[0]; }
    public byte[] digest(byte[] b) { return new byte[0]; }
}
