package java.util.concurrent;
import java.util.ArrayDeque;
import java.util.Collection;
import java.util.Iterator;
/** Browser shim: a page is single threaded, so a plain deque is already concurrent enough. */
public class ConcurrentLinkedQueue<E> implements Iterable<E> {
    private final ArrayDeque<E> q = new ArrayDeque<E>();
    public boolean add(E e) { return q.add(e); }
    public boolean offer(E e) { return q.offer(e); }
    public E poll() { return q.poll(); }
    public E peek() { return q.peek(); }
    public boolean isEmpty() { return q.isEmpty(); }
    public int size() { return q.size(); }
    public void clear() { q.clear(); }
    public boolean remove(Object o) { return q.remove(o); }
    public boolean addAll(Collection<? extends E> c) { return q.addAll(c); }
    @Override public Iterator<E> iterator() { return q.iterator(); }
}
