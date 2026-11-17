package java.lang;
/** Browser shim: a page cannot start a process. */
public class ProcessBuilder {
    public ProcessBuilder(String... command) { }
    public ProcessBuilder(java.util.List<String> command) { }
    public ProcessBuilder directory(java.io.File dir) { return this; }
    public ProcessBuilder inheritIO() { return this; }
    public Process start() throws java.io.IOException { throw new java.io.IOException("no processes in a page"); }
}
