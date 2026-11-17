package javax.crypto;
/** Browser shim: saved-login encryption is a desktop feature. */
public class Cipher {
    public static final int ENCRYPT_MODE = 1, DECRYPT_MODE = 2;
    public static Cipher getInstance(String t) { return new Cipher(); }
    public void init(int mode, java.security.Key key) { }
    public void init(int mode, java.security.Key key, java.security.spec.AlgorithmParameterSpec spec) { }
    public byte[] doFinal(byte[] in) { return new byte[0]; }
    public byte[] getIV() { return new byte[0]; }
}
