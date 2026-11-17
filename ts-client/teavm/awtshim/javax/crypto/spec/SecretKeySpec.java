package javax.crypto.spec;
public class SecretKeySpec implements java.security.Key {
    private final byte[] key;
    public SecretKeySpec(byte[] key, String algorithm) { this.key = key; }
    public String getAlgorithm() { return "AES"; }
    public String getFormat() { return "RAW"; }
    public byte[] getEncoded() { return key; }
}
