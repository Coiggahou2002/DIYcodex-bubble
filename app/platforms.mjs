// Explicit platform selection controls the port and selector. Never guess from rounded elements.
export const platforms={
 codex:{debugPort:19327,userSelector:'',name:'Codex'},
 doubao:{debugPort:19326,userSelector:'[class~="bg-g-send-msg-bubble-bg"]',name:'豆包'}
};
export function profileFor(state,key){
 if(!Object.hasOwn(platforms,key))throw Error('Unsupported platform');
 const saved=state.platforms?.[key];
 return {...platforms[key],...(saved||{}),active:saved?saved.active||null:key==='codex'?state.active||null:null,
  debugPort:saved?.debugPort||(key==='codex'?state.debugPort:null)||platforms[key].debugPort,
  userSelector:saved?.userSelector||platforms[key].userSelector};
}
export function acceptsTarget(target,key){
 if(target.type!=='page'||!target.webSocketDebuggerUrl)return false;
 try{const url=new URL(target.url);
  if(key==='codex')return url.protocol==='app:'&&url.hostname==='-';
  return key==='doubao'&&((url.protocol==='doubao:'&&url.hostname==='doubao-chat')||
   (url.protocol==='https:'&&(url.hostname==='doubao.com'||url.hostname.endsWith('.doubao.com')))||
   (url.protocol==='app:'&&(url.hostname==='-'||url.hostname==='doubao'))||
   (url.protocol==='file:'&&decodeURIComponent(url.pathname).includes('/Doubao.app/')));
 }catch{return false;}
}
