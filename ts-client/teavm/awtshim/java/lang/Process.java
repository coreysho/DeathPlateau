package java.lang;
public abstract class Process {
    public abstract int waitFor() throws InterruptedException;
    public abstract int exitValue();
    public abstract void destroy();
}
