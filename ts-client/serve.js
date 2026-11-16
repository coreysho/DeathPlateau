const http=require('http'),fs=require('fs'),path=require('path'),https=require('https');
const types={'.html':'text/html','.js':'application/javascript'};
http.createServer((req,res)=>{
  let u=req.url.split('?')[0];
  if(u==='/ts/'||u==='/ts'||u==='/')u='/ts/index.html';
  if(u.startsWith('/ts/')){
    const f=path.join(__dirname,'public',u.slice(4));
    if(fs.existsSync(f)){const b=fs.readFileSync(f);
      res.writeHead(200,{'content-type':types[path.extname(f)]||'application/octet-stream','content-length':b.length});
      return res.end(b);}
  }
  https.get({host:'play.deathplateau.com',path:u,headers:{host:'play.deathplateau.com'}},up=>{
    res.writeHead(up.statusCode,up.headers); up.pipe(res);
  }).on('error',e=>{res.writeHead(502);res.end(String(e));});
}).listen(9998,()=>console.log('ready'));
