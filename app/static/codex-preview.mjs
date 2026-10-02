import {renderNineSlice} from './nine-slice.mjs';
import {t} from './i18n.mjs';

// A self-contained simulation. No app connection, account, or chat data.
export class CodexPreview {
 constructor(container,{dark=false}={}){
  this.container=container;this.dark=dark;this.messages=[];this.sequence=0;this.image=null;this.config=null;
  this.observer=new ResizeObserver(()=>this.paint());this.build();
 }
 element(tag,className,text){const el=document.createElement(tag);el.className=className;if(text!==undefined)el.textContent=text;return el;}
 build(){
  this.observer.disconnect();const h=(tag,cls,text)=>this.element(tag,cls,text);
  const frame=h('div','codex-sim'+(this.dark?' sim-dark':''));this.frame=frame;
  const sidebar=h('aside','sim-sidebar');const chrome=h('div','sim-window-controls');for(const color of ['red','yellow','green'])chrome.append(h('i',color));chrome.append(h('span','sim-window-icon','▤'));sidebar.append(chrome,h('strong','sim-brand','Codex'));
  for(const [icon,key] of [['↗','新对话'],['⌘','拉取请求'],['◷','定时任务'],['✧','插件']]){const row=h('div','sim-nav');row.append(h('span','sim-icon',icon),h('span','',t(key)));sidebar.append(row);}
  sidebar.append(h('small','sim-section',t('项目')));const project=h('div','sim-project','▱  DIY Codex Bubble');sidebar.append(project);
  for(const key of ['给聊天一点自己的风格','整理今天的灵感','做一个小工具'])sidebar.append(h('div','sim-thread',t(key)));
  sidebar.append(h('small','sim-section',t('最近对话')),h('div','sim-thread',t('试试新的聊天气泡')));
  const account=h('div','sim-account');account.append(h('span','sim-avatar','k'),h('span','','kaitongg'),h('span','sim-settings','⚙'));sidebar.append(account);
  const main=h('section','sim-main');const bar=h('div','sim-toolbar');bar.append(h('span','sim-crumb',t('给聊天一点自己的风格')));const badge=h('span','sim-badge',t('模拟预览'));const toggle=h('button','sim-theme',this.dark?'☼':'☾');toggle.type='button';toggle.title=t('切换预览外观');toggle.onclick=()=>{this.dark=!this.dark;frame.classList.toggle('sim-dark',this.dark);toggle.textContent=this.dark?'☼':'☾';};bar.append(badge,toggle);main.append(bar);
  const conversation=h('div','sim-conversation');this.conversation=conversation;
  this.addUser(conversation,t('把我喜欢的图片，变成聊天气泡。'));
  const reply=h('div','sim-reply');reply.append(h('p','',t('可以。我们给日常的对话，加一点自己的风格。')),h('p','',t('选择一张 PNG，调整拉伸线和文字位置，再看看短句与长消息。')));const points=h('ul','sim-points');for(const key of ['角色和装饰留在固定边角','文字区域跟着消息自然伸展','只改变你发送的消息气泡'])points.append(h('li','',t(key)));reply.append(points);conversation.append(reply);
  this.addUser(conversation,t('这条消息稍微长一点。我想看看在真正的聊天布局里，换行以后有没有足够的文字空间，也希望小猫、尾巴和边框都能保持原来的样子。'));
  const second=h('div','sim-reply');second.append(h('p','',t('好，短句和长消息都会展示在这里。')),h('div','sim-code','bubble.png  →  preview  →  apply'),h('div','sim-reply-actions','⧉   ↻   ⋯'));conversation.append(second);
  for(const message of this.messages)this.addUser(conversation,message);
  main.append(conversation);
  const composerWrap=h('div','sim-composer-wrap');const composer=h('form','sim-composer');const input=h('textarea','sim-input');input.placeholder=t('输入一句话，试试气泡效果');input.rows=2;input.setAttribute('aria-label',t('模拟消息输入'));const tools=h('div','sim-composer-tools');tools.append(h('span','sim-composer-left','＋  ⌘'),h('span','sim-model','Codex  ·  Local'));const send=h('button','sim-send','↑');send.type='submit';send.setAttribute('aria-label',t('发送模拟消息'));tools.append(send);composer.append(input,tools);
  const submit=e=>{e.preventDefault();const text=input.value.trim();if(!text)return;this.messages.push(text);this.addUser(conversation,text);input.value='';this.paint();conversation.scrollTop=conversation.scrollHeight;};composer.onsubmit=submit;input.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing)submit(e);};composerWrap.append(composer,h('div','sim-environment','▱ DIY Codex Bubble   ·   main    ⌘'));main.append(composerWrap);frame.append(sidebar,main);this.container.replaceChildren(frame);this.paint();
 }
 addUser(parent,text){const row=this.element('div','sim-user-row');const bubble=this.element('div','sim-user-bubble',text);row.append(bubble);const time=this.element('div','sim-message-tools','12:34   ⧉   ✎');const wrap=this.element('div','sim-user-turn');wrap.append(row,time);parent.append(wrap);this.observer.observe(bubble);return bubble;}
 async setAsset(url,config){if(this.image&&this.assetUrl===url){this.config=structuredClone(config);this.paint();return;}const sequence=++this.sequence;const image=new Image();image.src=url;await image.decode();if(sequence!==this.sequence)return;this.image=image;this.assetUrl=url;this.config=structuredClone(config);this.paint();}
 paint(){if(!this.image||!this.config)return;const c=this.config;for(const el of this.container.querySelectorAll('.sim-user-bubble')){el.style.padding=c.padding.map(v=>v+'px').join(' ');el.style.color=c.color;el.style.minHeight=(Math.round(c.top*c.scale)+Math.round((c.height-c.bottom)*c.scale)+1)+'px';el.style.minWidth=`min(${Math.ceil(c.width*c.scale)}px,100%)`;el.style.setProperty('--sim-radius',c.radius+'px');el.style.setProperty('--sim-border-width',c.borderWidth+'px');el.style.setProperty('--sim-border-color',c.borderColor);el.style.setProperty('--sim-art',`url("${renderNineSlice(this.image,c,el.offsetWidth,el.offsetHeight,window.devicePixelRatio||1)}")`);}}
 refreshLanguage(){this.build();}
 destroy(){this.observer.disconnect();this.sequence++;}
}
