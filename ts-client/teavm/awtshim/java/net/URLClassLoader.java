package java.net;
/** Browser shim: a page cannot load a jar into the JVM. */
public class URLClassLoader extends ClassLoader {
    public URLClassLoader(URL[] urls) { }
    public URLClassLoader(URL[] urls, ClassLoader parent) { }
    public Class<?> loadClass(String name) throws ClassNotFoundException { throw new ClassNotFoundException(name); }
    public void close() { }
}
