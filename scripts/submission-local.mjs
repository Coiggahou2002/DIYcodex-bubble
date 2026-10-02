// Loopback-only development adapter: credentials never leave the server.
import http from 'node:http';
import {execFileSync} from 'node:child_process';
import {readFile} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
import {validateSubmission,storeSubmission} from '../community/worker.mjs';
const root=resolve(process.argv[2]||'/tmp/bubble-submission-preview'),port=Number(process.argv[3]||19334);
const token=execFileSync('gh',['auth','token'],{encoding:'utf8'}).trim();
const types={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png'};
http.createServer(async(req,res)=>{try{
 const url=new URL(req.url,'http://127.0.0.1:'+port);
 if(url.pathname==='/api/submissions'&&req.method==='POST'){
  if(req.headers.origin!=='http://127.0.0.1:'+port)throw Error('Origin not allowed');
  let size=0;const chunks=[];for await(const chunk of req){size+=chunk.length;if(size>3*1024*1024)throw Error('Too large');chunks.push(chunk);}
  const request=new Request(url,{method:'POST',headers:req.headers,body:Buffer.concat(chunks)});const data=await validateSubmission(request);const receipt=await storeSubmission(data,{QUEUE_REPO:'kaitongg-bit/DIYcodex-bubble-submissions',GITHUB_TOKEN:token});res.writeHead(201,{'Content-Type':'application/json'});res.end(JSON.stringify(receipt));return;
 }
 if(url.pathname==='/submission-config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify({endpoint:'/api/submissions',siteKey:''}));return;}
 const path=resolve(root,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));if(!path.startsWith(root+'/'))throw Error('Invalid path');const bytes=await readFile(path);res.setHeader('Content-Type',types[extname(path)]||'application/octet-stream');res.end(bytes);
 }catch(e){res.writeHead(400,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}
}).listen(port,'127.0.0.1',()=>console.log('Submission test: http://127.0.0.1:'+port));
