declare const __BUILD_ID__: string;
import { Game } from "./osrs/Game";

// EVERY FLAG FIRST, BEFORE ANYTHING READS ONE. These were set half way down the file, below the
// line that prints them - so the readout said "preload: ON lowMemory: false" on a build where both
// were about to be set, which is exactly the kind of thing that costs a round to disbelieve.
(Game as any).lowMemory = true;
(globalThis as any).__SKIP_PRELOAD = !new URLSearchParams(location.search).has("preload");

const t0 = performance.now();
const at = () => ((performance.now() - t0) / 1000).toFixed(1) + "s";

const log = document.createElement("div");
log.id = "log";
document.body.appendChild(log);
const line = (text: string) => {
    const row = document.createElement("div");
    row.textContent = at() + "  " + text;
    log.appendChild(row);
    while (log.childElementCount > 40) log.removeChild(log.firstChild!);
};

const realLog = console.log.bind(console);
console.log = (...args: any[]) => {
    const text = args.map(a => String(a)).join(" ");
    if (/DP |archive|parse|init|stage|crc|SPIKE|response|throw/i.test(text)) line(text);
    realLog(...args);
};

// The game socket is this page's own origin: the engine carries login and update on '/'.
const wsScheme = location.protocol === "https:" ? "wss://" : "ws://";
(globalThis as any).__WS_URL = wsScheme + location.host + "/";
(globalThis as any).__NO_LOCAL_CACHE = true;
// ?nosocket=1 loads without connecting at all. If the page is healthy that way and locks up
// without it, the fault is the socket and the on-demand stream behind it, not the client's load.
const params = new URLSearchParams(location.search);
(globalThis as any).__NO_SOCKET = params.has("nosocket");
line("build " + (typeof __BUILD_ID__ !== "undefined" ? __BUILD_ID__ : "?")
    + "   preload: " + ((globalThis as any).__SKIP_PRELOAD ? "SKIPPED" : "ON")
    + "   lowMemory: " + String((Game as any).lowMemory));
line("socket " + (params.has("nosocket") ? "DISABLED (?nosocket=1)" : "enabled -> " + (globalThis as any).__WS_URL));

// A heartbeat, so a lock-up shows WHERE it stopped instead of just stopping. This is a timer, so
// it keeps ticking while the client works and goes silent the moment the main thread is blocked.
let beat = 0;
setInterval(() => { line("heartbeat " + (++beat)); }, 2000);

// (flags are set at the top of this file)
// LOW MEMORY, WHICH IS ALSO WHAT UNBLOCKS startUp. Its other job here is that the block it skips
// asks the update server for a music file and then spins until it arrives - and if the on-demand
// stream does not deliver, startUp never reaches the sprites, so minimapBackgroundImage stays null
// and the first thing the game draws after login throws on it. A phone wants low detail regardless.


const canvas = document.createElement("canvas");
canvas.id = "gameCanvas";
document.body.appendChild(canvas);

// A plain HTML login, which is the whole point: in a JavaScript client the phone's keyboard needs
// no bridge, no native and no handshake - it is just an input.
const form = document.createElement("div");
form.id = "form";
form.innerHTML =
    '<input id="u" placeholder="username" autocapitalize="none" autocorrect="off" spellcheck="false" />' +
    '<input id="p" placeholder="password" type="password" />' +
    '<button id="go" type="button">Log in</button>';
document.body.appendChild(form);
document.body.appendChild(log);   // move it below the form

line("page ready - starting client");
const game = new Game(canvas);
(window as any).__game = game;

let drawn = false;
const watch = setInterval(() => {
    if (drawn) return;
    try {
        const g = canvas.getContext("2d", { willReadFrequently: true });
        if (!g) return;
        const d = g.getImageData(0, 0, Math.min(canvas.width, 300), Math.min(canvas.height, 300)).data;
        let lit = 0;
        for (let k = 0; k < d.length; k += 16) if (d[k] + d[k + 1] + d[k + 2] > 60) lit++;
        if (lit > 500) { drawn = true; line("*** FIRST PIXELS DRAWN ***"); clearInterval(watch); }
    } catch (e) { /* not ready */ }
}, 250);

// frames per second, once there is something to count - the question the title screen cannot answer
let frames = 0;
const rafCount = () => { frames++; requestAnimationFrame(rafCount); };
requestAnimationFrame(rafCount);
setInterval(() => { if (drawn) { line("fps ~" + frames); frames = 0; } }, 5000);

document.getElementById("go")!.addEventListener("click", () => {
    const u = (document.getElementById("u") as HTMLInputElement).value;
    const p = (document.getElementById("p") as HTMLInputElement).value;
    line("logging in as " + u + " ...");
    const g = game as any;
    g.statusLineOne = "";
    g.statusLineTwo = "";
    Promise.resolve(g.login(u, p, false)).then(() => {
        // The client writes its outcome into the two status lines it would normally paint on its
        // own login screen. This harness drives login() straight from the form and never draws
        // that screen, so the message has to be read out of the client instead.
        const msg = ((g.statusLineOne || "") + " " + (g.statusLineTwo || "")).trim();
        line(msg ? "server says: " + msg : "logged in (no refusal message)");
        line("loggedIn flag = " + g.loggedIn);
    }).catch((e: any) => line("login threw: " + String(e && e.message ? e.message : e).slice(0, 120)));
});

game.initializeApplication(765, 503).catch((e: any) => line("client stopped: " + String(e).slice(0, 80)));
