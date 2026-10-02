import {language} from './i18n.mjs';
const text=(zh,en)=>language==='en'?en:zh;
export function initSubmission(){
 const dialog=document.createElement('dialog');dialog.className='submission-dialog';dialog.id='contribute';document.body.append(dialog);
 let configuration;
 async function show(){
  dialog.innerHTML=`<form id="submissionForm"><div class="detail-top"><h2>${text('贡献一款气泡','Contribute a bubble')}</h2><button type="button" id="closeSubmission" aria-label="Close">×</button></div><p>${text('无需注册。投稿先进入私有待审库，通过审核后才会公开。','No account needed. Your PNG stays in a private review queue until approved.')}</p><label>${text('你的昵称','Nickname')}<input name="nickname" maxlength="40" required autocomplete="nickname"></label><label>${text('气泡名称','Bubble name')}<input name="name" maxlength="60" required></label><label>${text('气泡 PNG · 最大 2 MB','Bubble PNG · up to 2 MB')}<input name="png" type="file" accept="image/png" required></label><img id="submissionArt" alt="PNG preview" hidden><label class="submission-consent"><input name="consent" type="checkbox" value="yes" required>${text('我有权分享此图片，同意审核后展示并提供非商业下载。','I have the right to share this image and allow gallery display and non-commercial downloads after review.')}</label><input name="website" tabindex="-1" autocomplete="off" class="honeypot" aria-hidden="true"><div id="submissionVerification"></div><p id="submissionStatus" role="status"></p><button id="sendSubmission" class="download-button" type="submit" disabled>${text('提交审核','Submit for review')}</button></form>`;
  dialog.querySelector('#closeSubmission').onclick=()=>dialog.close();dialog.showModal();
  const status=dialog.querySelector('#submissionStatus'),button=dialog.querySelector('#sendSubmission');
  try{configuration=await (await fetch('./submission-config.json')).json();if(!configuration.endpoint)throw Error(text('投稿服务正在接入，请稍后再来。你仍然可以预览自己的 PNG。','Submissions are being set up. You can still preview your PNG.'));
   if(configuration.siteKey){if(!window.turnstile){await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';script.onload=resolve;script.onerror=reject;document.head.append(script);});}window.turnstile.render(dialog.querySelector('#submissionVerification'),{sitekey:configuration.siteKey,action:'bubble-submit',callback:()=>{button.disabled=false;},'expired-callback':()=>{button.disabled=true;}});}else if(location.hostname==='127.0.0.1')button.disabled=false;else throw Error('Verification unavailable');
  }catch(e){status.textContent=e.message;}
  let artUrl;dialog.querySelector('[name=png]').onchange=async e=>{const file=e.target.files[0];if(!file)return;if(artUrl)URL.revokeObjectURL(artUrl);artUrl=URL.createObjectURL(file);const art=dialog.querySelector('#submissionArt');art.src=artUrl;art.hidden=false;};
  dialog.querySelector('form').onsubmit=async e=>{e.preventDefault();button.disabled=true;status.textContent=text('正在提交…','Submitting…');try{const form=new FormData(e.target);if(form.get('png').size>2*1024*1024)throw Error(text('PNG 不得超过 2 MB','PNG must be smaller than 2 MB'));const response=await fetch(configuration.endpoint,{method:'POST',body:form});const data=await response.json();if(!response.ok)throw Error(data.error||'Submission failed');status.textContent=text('已进入待审库，投稿编号：','Received for review. Submission ID: ')+data.id;e.target.querySelectorAll('input').forEach(input=>input.disabled=true);button.textContent=text('已提交','Submitted');}catch(e){status.textContent=e.message;button.disabled=false;}};
 }
 document.querySelector('.gallery-submission').innerHTML='<button id="contributeBubble" class="secondary-button">'+text('贡献气泡 ↗','Contribute a bubble ↗')+'</button>';
 document.querySelector('#contributeBubble').onclick=show;
 if(location.hash==='#contribute')show();
 return ()=>{document.querySelector('#contributeBubble').textContent=text('贡献气泡 ↗','Contribute a bubble ↗');};
}
