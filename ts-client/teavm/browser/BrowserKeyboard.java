package browser;

import awtbridge.Events;
import org.teavm.jso.JSBody;
import org.teavm.jso.JSFunctor;
import org.teavm.jso.JSObject;

/**
 * A PHONE HAS NO KEYS (2026-11-17).
 *
 * The game is a canvas, and a phone raises its keyboard for a focused HTML input and for nothing
 * else - so on a touch device there is no way to type the username, which is the one thing that
 * has to happen before anything else can. The page keeps a real input out of sight, the phone puts
 * its keyboard up against that, and what is typed is forwarded here as key events.
 *
 * WHAT A SOFT KEYBOARD ACTUALLY SENDS. Most Android keyboards report every keydown as keyCode 229
 * ("composing") and give the character only in the input event that follows; iOS is better but not
 * reliable either. So characters are read from the input event's data, where they are always
 * right, and only the two keys that do arrive as proper keydowns everywhere - Backspace and Enter
 * - are taken from keydown. The field is emptied after each one, so it never grows and the phone
 * never offers to autocomplete it.
 *
 * The input is also what the client's own password masking expects to NOT exist: the characters go
 * to the client, which draws its own asterisks. Nothing is ever shown in the field.
 */
public final class BrowserKeyboard {

    private BrowserKeyboard() { }

    @JSFunctor
    public interface Keys extends JSObject {
        void key(int code, int ch);
    }

    public static void install(final java.awt.Component component) {
        wire(new Keys() {
            @Override public void key(int code, int ch) {
                Events.keyPressed(component, code, (char) ch);
                if (ch != 0) {
                    Events.keyTyped(component, (char) ch);
                }
                Events.keyReleased(component, code, (char) ch);
            }
        });
    }

    @JSBody(params = "keys", script =
        "var input = document.getElementById('kbin');\n" +
        "if (!input) { return; }\n" +
        "var btn = document.getElementById('kb');\n" +
        "if (btn) {\n" +
        // focus() only raises a phone's keyboard inside a real gesture, so it happens in the
        // handler itself and not after any await or timeout.
        "  btn.addEventListener('click', function (e) {\n" +
        "    if (document.activeElement === input) { input.blur(); btn.classList.remove('on'); }\n" +
        "    else { input.focus(); btn.classList.add('on'); }\n" +
        "    e.preventDefault();\n" +
        "  });\n" +
        "  input.addEventListener('blur', function () { btn.classList.remove('on'); });\n" +
        "}\n" +
        "input.addEventListener('keydown', function (e) {\n" +
        "  if (e.key === 'Backspace') { keys(8, 8); e.preventDefault(); }\n" +
        "  else if (e.key === 'Enter') { keys(10, 10); e.preventDefault(); }\n" +
        "  else if (e.key === 'ArrowUp') { keys(38, 0); e.preventDefault(); }\n" +
        "  else if (e.key === 'ArrowDown') { keys(40, 0); e.preventDefault(); }\n" +
        "  else if (e.key === 'ArrowLeft') { keys(37, 0); e.preventDefault(); }\n" +
        "  else if (e.key === 'ArrowRight') { keys(39, 0); e.preventDefault(); }\n" +
        "});\n" +
        "input.addEventListener('input', function (e) {\n" +
        "  var text = e.data != null ? e.data : input.value;\n" +
        "  if (text) {\n" +
        "    for (var i = 0; i < text.length; i++) {\n" +
        "      var ch = text.charCodeAt(i);\n" +
        "      var up = String.fromCharCode(ch).toUpperCase().charCodeAt(0);\n" +
        "      keys(up, ch);\n" +
        "    }\n" +
        "  }\n" +
        "  input.value = '';\n" +
        "});")
    private static native void wire(Keys keys);
}
