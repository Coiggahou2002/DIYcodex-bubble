// Anonymous intake. GitHub credentials stay in Worker secrets, never in the site.
const LIMIT=2*1024*1024;
export async function validateSubmission(request){
 const length=Number(request.headers.get('content-length')||0);if(length>LIMIT*1.5)throw Error('Submission exceeds 2 MB');
 const form=await request.formData();const nickname=String(form.get('nickname')||'').trim(),name=String(form.get('name')||'').trim();
 if(!nickname||nickname.length>40||!name||name.length>60||/[\x00-\x1f]/.test(nickname+name))throw Error('Enter a nickname and bubble name');
 if(form.get('consent')!=='yes')throw Error('Please confirm image rights and non-commercial sharing');
 if(form.get('website'))throw Error('Invalid submission');
 const file=form.get('png');if(!file||typeof file.arrayBuffer!=='function'||file.size>LIMIT)throw Error('Choose a PNG smaller than 2 MB');
 const bytes=new Uint8Array(await file.arrayBuffer());if(bytes.length<33||bytes.slice(0,8).join(',')!=='137,80,78,71,13,10,26,10'||String.fromCharCode(...bytes.slice(12,16))!=='IHDR')throw Error('Invalid PNG');
 const view=new DataView(bytes.buffer);const width=view.getUint32(16),height=view.getUint32(20);if(width<2||height<2||width>4096||height>4096)throw Error('PNG dimensions must be 2–4096 pixels');
 const sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
 return {bytes,metadata:{nickname,name,width,height,sha256,consent:'Non-commercial gallery display and downloads; submitter confirms rights',createdAt:new Date().toISOString(),status:'pending'}};
}
function base64(bytes){let s='';for(let i=0;i<bytes.length;i+=8192)s+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(s);}
export async function storeSubmission(data,env,fetcher=fetch){
 const repo=env.QUEUE_REPO;if(!/^[\w.-]+\/[\w.-]+$/.test(repo||'')||!env.GITHUB_TOKEN)throw Error('Submission service is not configured');
 const api=async(path,body)=>{const r=await fetcher('https://api.github.com/repos/'+repo+path,{method:body?'POST':'GET',headers:{Authorization:'Bearer '+env.GITHUB_TOKEN,Accept:'application/vnd.github+json','Content-Type':'application/json','User-Agent':'DIY-Codex-Bubble'},...(body?{body:JSON.stringify(body)}:{})});if(!r.ok)throw Error('Private queue unavailable');return r.json();};
 // Refuse a mistakenly public queue before transmitting the PNG.
 const repository=await api('');if(!repository.private)throw Error('Review queue must be private');
 const id=crypto.randomUUID();data.metadata.id=id;
 const png=await api('/git/blobs',{content:base64(data.bytes),encoding:'base64'});
 const metadata=await api('/git/blobs',{content:JSON.stringify(data.metadata,null,2),encoding:'utf-8'});
 for(let attempt=0;attempt<3;attempt++){
  const branch=repository.default_branch||'main';const ref=await api('/git/ref/heads/'+branch);const parent=ref.object.sha;const previous=await api('/git/commits/'+parent);
  const tree=await api('/git/trees',{base_tree:previous.tree.sha,tree:[{path:'pending/'+id+'/bubble.png',mode:'100644',type:'blob',sha:png.sha},{path:'pending/'+id+'/submission.json',mode:'100644',type:'blob',sha:metadata.sha}]});
  const commit=await api('/git/commits',{message:'Receive bubble submission '+id,tree:tree.sha,parents:[parent]});
  const r=await fetcher('https://api.github.com/repos/'+repo+'/git/refs/heads/'+branch,{method:'PATCH',headers:{Authorization:'Bearer '+env.GITHUB_TOKEN,Accept:'application/vnd.github+json','Content-Type':'application/json','User-Agent':'DIY-Codex-Bubble'},body:JSON.stringify({sha:commit.sha,force:false})});
  if(r.ok)return {id,status:'pending'};if(![409,422].includes(r.status))break;
 }
 throw Error('Queue busy. Please try again');
}
export default {async fetch(request,env){
 const origin=request.headers.get('Origin');const allowed=env.ALLOWED_ORIGIN||'https://kaitongg-bit.github.io';const headers={'Content-Type':'application/json','Cache-Control':'no-store','Vary':'Origin'};
 if(origin===allowed)Object.assign(headers,{'Access-Control-Allow-Origin':allowed,'Access-Control-Allow-Methods':'POST,OPTIONS','Access-Control-Allow-Headers':'Content-Type'});
 const reply=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
 if(origin!==allowed)return reply({error:'Origin not allowed'},403);
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
 if(new URL(request.url).pathname!=='/api/submissions'||request.method!=='POST')return reply({error:'Not found'},404);
 if(!env.GITHUB_TOKEN||!env.TURNSTILE_SECRET)return reply({error:'Submission service is not configured'},503);
 try{
  if(Number(request.headers.get('content-length')||0)>LIMIT*1.5)return reply({error:'Submission exceeds 2 MB'},413);
  const reader=request.body.getReader();const chunks=[];let total=0;while(true){const part=await reader.read();if(part.done)break;total+=part.value.byteLength;if(total>LIMIT*1.5){await reader.cancel();return reply({error:'Submission exceeds 2 MB'},413);}chunks.push(part.value);}
  const bounded=new Uint8Array(total);let offset=0;for(const chunk of chunks){bounded.set(chunk,offset);offset+=chunk.byteLength;}
  const safeRequest=new Request(request.url,{method:'POST',headers:request.headers,body:bounded});
  const copy=safeRequest.clone();const form=await copy.formData();const token=form.get('cf-turnstile-response');
  const verify=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',body:new URLSearchParams({secret:env.TURNSTILE_SECRET,response:String(token||'')})});const result=await verify.json();
  if(!result.success||result.hostname!==new URL(allowed).hostname||result.action!=='bubble-submit')return reply({error:'Please complete verification'},403);
  const data=await validateSubmission(safeRequest);return reply(await storeSubmission(data,env),201);
 }catch(e){return reply({error:e.message},400);}
}};
