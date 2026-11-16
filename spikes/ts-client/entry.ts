import { Game } from "./osrs/Game";
const canvas = document.createElement("canvas");
canvas.id = "gameCanvas";
document.body.appendChild(canvas);
(window as any).__t0 = performance.now();
const game = new Game(canvas);
(window as any).__game = game;
game.initializeApplication(765, 503)
  .then(() => console.log("GAME STOPPED"))
  .catch((e: any) => console.log("GAME ERROR " + e));
