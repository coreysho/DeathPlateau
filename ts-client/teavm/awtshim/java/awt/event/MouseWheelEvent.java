package java.awt.event;
public class MouseWheelEvent extends MouseEvent {
    public int wheelRotation;
    public int getWheelRotation() { return wheelRotation; }
    public int getUnitsToScroll() { return wheelRotation; }
}
