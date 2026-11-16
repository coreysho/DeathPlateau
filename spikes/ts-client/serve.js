const http=require('http'),fs=require('fs'),path=require('path');
const types={'.html':'text/html','.js':'application/javascript','.dat':'application/octet-stream'};
http.createServer((req,res)=>{
  let u=req.url.split('?')[0]; if(u==='/')u='/index.html';
  const f=path.join(__dirname,'public',u);
  if(!fs.existsSync(f)){
    // anything we do not have locally: Death Plateau's own cache routes, same-origin via this proxy
    const https=require('https');
    return https.get({host:'play.deathplateau.com',path:u,headers:{host:'play.deathplateau.com'}},up=>{
      res.writeHead(up.statusCode,up.headers); up.pipe(res);
    }).on('error',e=>{res.writeHead(502);res.end(String(e));});
  }
  const b=fs.readFileSync(f);
  res.writeHead(200,{'content-type':types[path.extname(f)]||'application/octet-stream','content-length':b.length});
  res.end(b);
}).listen(9998,()=>console.log('spike on 9998'));
