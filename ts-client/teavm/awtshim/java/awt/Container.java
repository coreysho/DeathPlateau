package java.awt;
/** Matches real AWT: add(Component) returns the component, add(Component, Object) returns void. */
public class Container extends Component {
    public Component add(Component c) { return c; }
    public void add(Component c, Object constraints) { }
    public void remove(Component c) { }
    public void removeAll() { }
    public Component[] getComponents() { return new Component[0]; }
    public Insets getInsets() { return new Insets(0, 0, 0, 0); }
}
