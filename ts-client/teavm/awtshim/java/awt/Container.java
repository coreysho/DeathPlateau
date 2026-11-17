package java.awt;
public class Container extends Component {
    public Component add(Component c) { return c; }
    public Component add(Component c, Object constraints) { return c; }
    public void remove(Component c) { }
    public void removeAll() { }
    public Component[] getComponents() { return new Component[0]; }
}
