import { Game } from "./osrs/Game";

// A load test that reports itself, so judging it on a phone needs nothing but eyes.
(globalThis as any).__NO_SOCKET = true;
(globalThis as any).__NO_LOCAL_CACHE = true;
const t0 = performance.now();
const at = () => ((performance.now() - t0) / 1000).toFixed(1) + "s";

const log = document.createElement("div");
log.id = "log";
document.body.appendChild(log);
const line = (text: string) => {
    const row = document.createElement("div");
    row.textContent = at() + "  " + text;
    log.appendChild(row);
};

const realLog = console.log.bind(console);
console.log = (...args: any[]) => {
    const text = args.map(a => String(a)).join(" ");
    if (/DP |archive|parse|init|Starting|crc/i.test(text)) line(text);
    realLog(...args);
};

const canvas = document.createElement("canvas");
canvas.id = "gameCanvas";
document.body.insertBefore(canvas, log);

line("page ready - starting client");
const game = new Game(canvas);
(window as any).__game = game;

// the moment anything of the game is actually on screen
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

game.initializeApplication(765, 503).catch((e: any) => line("client stopped: " + String(e).slice(0, 80)));
