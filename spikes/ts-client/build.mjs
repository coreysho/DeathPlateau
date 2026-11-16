import * as esbuild from 'esbuild';
const globShim = {
  name: 'glob-shim',
  setup(b) {
    b.onResolve({ filter: /wasm\/src\/lib\.rs$/ }, () => ({ path: process.cwd() + '/rsshim.js' }));
    b.onResolve({ filter: /^(fs|@babel\/types|image-pixels)$/ }, a => ({ path: a.path, namespace: 'stub' }));
    b.onLoad({ filter: /.*/, namespace: 'stub' }, () => ({ contents: 'export default {}; export const parse = null;', loader: 'js' }));
    b.onResolve({ filter: /client_cache\/\*\.(dat|idx\*)$/ }, a => ({ path: a.path, namespace: 'glob' }));
    b.onLoad({ filter: /.*/, namespace: 'glob' }, a => {
      const contents = a.path.includes('.dat')
        ? 'export default { main_file_cache: "/client_cache/main_file_cache.dat" };'
        : 'export default { main_file_cache: ["/client_cache/main_file_cache.idx0","/client_cache/main_file_cache.idx1","/client_cache/main_file_cache.idx2","/client_cache/main_file_cache.idx3","/client_cache/main_file_cache.idx4"] };';
      return { contents, loader: 'js' };
    });
  }
};
const r = await esbuild.build({
  entryPoints: ['entry.ts'], bundle: true, outfile: 'public/game.js',
  format: 'iife', target: 'es2020', logLevel: 'warning', plugins: [globShim],
  loader: { '.png': 'dataurl' }, logLimit: 15
});
console.log('build ok');
