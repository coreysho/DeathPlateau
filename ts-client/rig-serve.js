// Serves the built bundle at /ts/ and forwards everything else - cache routes and the game
// WebSocket - to a world. Target may be a local engine (plain http) or the live one (tls).
//   node serve.js <dist-dir> <host[:port]>
const http = require('http'), fs = require('fs'), path = require('path');
const https = require('https'), tls = require('tls'), net = require('net');
const DIST = process.argv[2] || '/tmp/claude-0/work2/public';
const RAW = process.argv[3] || 'play.deathplateau.com';
const [HOST, PORTSTR] = RAW.split(':');
const LOCAL = HOST === '127.0.0.1' || HOST === 'localhost';
const PORT = PORTSTR ? Number(PORTSTR) : (LOCAL ? 8888 : 443);
const types = { '.html': 'text/html', '.js': 'application/javascript' };

const server = http.createServer((req, res) => {
    let u = req.url.split('?')[0];
    if (u === '/' || u === '/ts' || u === '/ts/') u = '/ts/index.html';
    if (u.startsWith('/ts/')) {
        const f = path.join(DIST, u.slice(4));
        if (fs.existsSync(f) && fs.statSync(f).isFile()) {
            const b = fs.readFileSync(f);
            res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream', 'content-length': b.length });
            return res.end(b);
        }
    }
    const mod = LOCAL ? http : https;
    mod.get({ host: HOST, port: PORT, path: req.url, headers: { host: `${HOST}:${PORT}` } }, up => {
        res.writeHead(up.statusCode, up.headers); up.pipe(res);
    }).on('error', e => { res.writeHead(502); res.end(String(e)); });
});

let n = 0;
server.on('upgrade', (req, socket, head) => {
    const id = ++n;
    console.log(`[ws ${id}] ${req.url} -> ${LOCAL ? 'ws' : 'wss'}://${HOST}:${PORT}`);
    const onReady = () => {
        const headers = { ...req.headers, host: `${HOST}:${PORT}` };
        if (!LOCAL) headers.origin = `https://${HOST}`;
        let raw = `GET ${req.url} HTTP/1.1\r\n`;
        for (const [k, v] of Object.entries(headers)) raw += `${k}: ${v}\r\n`;
        up.write(raw + '\r\n');
        if (head && head.length) up.write(head);
        up.pipe(socket); socket.pipe(up);
    };
    const up = LOCAL ? net.connect({ host: HOST, port: PORT }, onReady)
                     : tls.connect({ host: HOST, port: PORT, servername: HOST }, onReady);
    up.on('error', e => { console.log(`[ws ${id}] upstream: ${e.message}`); socket.destroy(); });
    socket.on('error', () => up.destroy());
    socket.on('close', () => console.log(`[ws ${id}] closed`));
});
server.listen(9998, () => console.log(`rig on 9998  dist=${DIST}  target=${LOCAL?'http':'https'}://${HOST}:${PORT}`));
