package dp;

import jagex2.io.Packet;
import jagex2.wordenc.ChatText;

/**
 * Exercises the parts of the real client this spike compiles, so the output has something to run
 * rather than only something to typecheck: write a packet the way the engine's protocol does, read
 * it back, and round-trip a chat line through ChatText.
 */
public class Main {
    public static void main(String[] args) {
        Packet buf = new Packet(new byte[64]);
        buf.p1(42);
        buf.p2(1337);
        buf.p4(123456789);
        buf.p1_alt1(7);
        int written = buf.pos;

        buf.pos = 0;
        int a = buf.g1();
        int b = buf.g2();
        int c = buf.g4();
        int d = buf.g1_alt1();

        String line = ChatText.format("  hello   WORLD 123  ");
        Packet chat = new Packet(new byte[96]);
        ChatText.pack(line, chat);
        int packed = chat.pos;
        chat.pos = 0;
        String back = ChatText.unpack(chat, packed);

        System.out.println("wrote " + written + " bytes");
        System.out.println("g1=" + a + " g2=" + b + " g4=" + c + " g1_alt1=" + d);
        System.out.println("format=[" + line + "] packed=" + packed + " unpack=[" + back + "]");
        System.out.println(a == 42 && b == 1337 && c == 123456789 && d == 7 && back.equals(line)
            ? "CORE OK" : "CORE MISMATCH");
    }
}
