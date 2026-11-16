import { Game } from "./osrs/Game";

const t0 = performance.now();
const at = () => ((performance.now() - t0) / 1000).toFixed(1) + "s";

const log = document.createElement("div");
log.id = "log";
const line = (text: string) => {
    const row = document.createElement("div");
    row.textContent = at() + "  " + text;
    log.appendChild(row);
    while (log.childElementCount > 40) log.removeChild(log.firstChild!);
};

const realLog = console.log.bind(console);
console.log = (...args: any[]) => {
    const text = args.map(a => String(a)).join(" ");
    if (/DP |archive|parse|init|Starting|crc|SPIKE|response/i.test(text)) line(text);
    realLog(...args);
};

// The game socket is this page's own origin: the engine carries login and update on '/'.
const wsScheme = location.protocol === "https:" ? "wss://" : "ws://";
(globalThis as any).__WS_URL = wsScheme + location.host + "/";
(globalThis as any).__NO_LOCAL_CACHE = true;

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
document.body.appendChild(log);

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
    }).catch((e: any) => line("login threw: " + String(e).slice(0, 80)));
});

game.initializeApplication(765, 503).catch((e: any) => line("client stopped: " + String(e).slice(0, 80)));
