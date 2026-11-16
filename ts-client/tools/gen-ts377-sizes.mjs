// Patch ts377's PACKET_SIZES with the engine's sizes for the packets it cannot know about.
//
// ts377 is the stock 377 client, so its table is right for every stock packet - but DeathPlateau
// adds nine of its own, and a stock client has 0 for all of them. 0 does not mean "empty", it
// means the client reads no length and no payload: the next payload byte is then read as an
// opcode and the stream is lost from there. That desync is what hung the client, and it looks
// nothing like its cause.
//
//   node gen-ts377-sizes.mjs <engine-dir> <ts377-dir> [--write]

import * as fs from 'fs';
import * as path from 'path';

const [engineDir, clientDir, ...rest] = process.argv.slice(2);
const WRITE = rest.includes('--write');
if (!engineDir || !clientDir) {
    console.error('usage: node gen-ts377-sizes.mjs <engine-dir> <ts377-dir> [--write]');
    process.exit(2);
}

const table = (file, cls) => {
    const re = new RegExp(`static readonly (\\w+) = new ${cls}\\((\\d+),\\s*(-?\\d+)\\)`, 'g');
    const m = new Map();
    for (const x of fs.readFileSync(file, 'utf8').matchAll(re)) m.set(x[1], { op: +x[2], size: +x[3] });
    return m;
};

const eng = new Map([
    ...table(path.join(engineDir, 'src/network/game/server/ServerGameProt.ts'), 'ServerGameProt'),
    ...table(path.join(engineDir, 'src/network/game/server/ServerGameZoneProt.ts'), 'ServerGameZoneProt'),
]);

const target = path.join(clientDir, 'osrs/util/PacketConstants.ts');
const src = fs.readFileSync(target, 'utf8');
const body = src.match(/PACKET_SIZES: number\[\] = \[([\s\S]*?)\];/);
const sizes = JSON.parse('[' + body[1].replace(/\s+/g, '') + ']');

const diff = [...eng].filter(([, v]) => sizes[v.op] !== v.size).map(([n, v]) => ({ n, op: v.op, was: sizes[v.op], now: v.size }));
console.log(`engine packets ${eng.size}, ts377 table ${sizes.length} entries`);
console.log(`differs on ${diff.length}:`);
for (const d of diff.sort((a, b) => a.op - b.op)) {
    console.log(`   ${String(d.op).padStart(3)}  ${d.n.padEnd(24)} ${String(d.was).padStart(3)} -> ${d.now}`);
    sizes[d.op] = d.now;
}

if (!WRITE) { console.log('\n(dry run - pass --write to apply)'); process.exit(0); }
const rendered = sizes.map((v, i) => `        ${v},${i === sizes.length - 1 ? '' : ''}`).join('\n');
fs.writeFileSync(target, src.replace(body[0], `PACKET_SIZES: number[] = [\n${rendered}\n    ];`));
console.log(`\nwritten -> ${target}`);
