package java.awt;
public class Rectangle {
    public int x, y, width, height;
    public Rectangle() { }
    public Rectangle(int x, int y, int w, int h) { this.x=x; this.y=y; this.width=w; this.height=h; }
    public Rectangle(Rectangle r) { this(r.x, r.y, r.width, r.height); }
    public boolean contains(int px, int py) {
        return px >= x && py >= y && px < x + width && py < y + height;
    }
}
