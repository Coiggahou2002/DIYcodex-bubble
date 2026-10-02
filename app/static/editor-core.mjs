import {renderNineSlice} from './nine-slice.mjs';

export function bubbleDefaults(item){
 const w=item.width,h=item.height;
 return {width:w,height:h,left:Math.max(1,Math.min(w-2,Math.round(w*.35))),right:Math.max(2,Math.min(w-1,Math.round(w*.73))),top:Math.max(1,Math.min(h-2,Math.round(h*.45))),bottom:Math.max(2,Math.min(h-1,Math.round(h*.55))),scale:Math.max(.01,Math.min(.6,240/w,98/h)),padding:[29,37,36,48],color:'#44362f',radius:0,borderWidth:0,borderColor:'#d0d0d0'};
}
export function bubbleValid(item,c){
 return !!(item&&c&&Number.isInteger(c.left)&&Number.isInteger(c.right)&&Number.isInteger(c.top)&&Number.isInteger(c.bottom)&&0<c.left&&c.left<c.right&&c.right<item.width&&0<c.top&&c.top<c.bottom&&c.bottom<item.height&&Number.isFinite(c.scale)&&c.scale>=.01&&c.scale<=2&&Array.isArray(c.padding)&&c.padding.length===4&&c.padding.every(v=>Number.isFinite(v)&&v>=0&&v<=200)&&Number.isFinite(c.radius)&&c.radius>=0&&c.radius<=200&&Number.isFinite(c.borderWidth)&&c.borderWidth>=0&&c.borderWidth<=20);
}
export function textRect(item,c){
 const s=c.scale;return {left:c.padding[3]/s,top:c.padding[0]/s,right:item.width-c.padding[1]/s,bottom:item.height-c.padding[2]/s};
}
export function drawCanvas(art,textBox,band,item,c,{maxHeight=300}={}){
 const size=Math.min(2,Math.max(80,art.parentElement.clientWidth-56)/item.width,maxHeight/item.height);
 art.style.width=item.width*size+'px';art.style.height=item.height*size+'px';
 const sx=art.clientWidth/item.width,sy=art.clientHeight/item.height;
 for(const key of ['left','right','top','bottom']){
  const line=art.querySelector('[data-key='+key+']');line.style[key==='left'||key==='right'?'left':'top']=c[key]*(key==='left'||key==='right'?sx:sy)+'px';
 }
 band.style.cssText=`left:${c.left*sx}px;top:${c.top*sy}px;width:${(c.right-c.left)*sx}px;height:${(c.bottom-c.top)*sy}px`;
 const box=textRect(item,c);
 textBox.style.cssText=`left:${box.left*sx}px;top:${box.top*sy}px;width:${Math.max(8,box.right-box.left)*sx}px;height:${Math.max(8,box.bottom-box.top)*sy}px`;
}
export function styleBubble(el,item,c,width){
 el.style.padding=c.padding.map(v=>v+'px').join(' ');
 el.style.minWidth=`min(${Math.ceil(item.width*c.scale)}px,100%)`;
 el.style.minHeight=(Math.round(c.top*c.scale)+Math.round((item.height-c.bottom)*c.scale)+1)+'px';
 el.style.width=width+'px';
 for(const [key,value] of Object.entries({'--textColor':c.color,'--text-color':c.color,'--radius':c.radius+'px','--border-width':c.borderWidth+'px','--border-color':c.borderColor}))el.style.setProperty(key,value);
}
export function paintBubble(el,image,c){
 if(!image?.naturalWidth||!el.offsetWidth||!el.offsetHeight)return;
 el.style.setProperty('--paint',`url("${renderNineSlice(image,c,el.offsetWidth,el.offsetHeight,window.devicePixelRatio||1)}")`);
}
export function bindCanvas(art,textBox,{getItem,getConfig,onChange}){
 for(const line of art.querySelectorAll('.guide')){
  const handle=line.querySelector('b'),key=line.dataset.key;let pointer=null;
  handle.onpointerdown=e=>{if(!getItem())return;pointer=e.pointerId;handle.setPointerCapture(pointer);e.preventDefault();};
  handle.onpointermove=e=>{if(pointer!==e.pointerId||!handle.hasPointerCapture(pointer))return;const item=getItem(),c=getConfig(),r=art.getBoundingClientRect(),axis=key==='left'||key==='right',value=Math.round((axis?e.clientX-r.left:e.clientY-r.top)/(axis?r.width/item.width:r.height/item.height)),bounds={left:[1,c.right-1],right:[c.left+1,item.width-1],top:[1,c.bottom-1],bottom:[c.top+1,item.height-1]};c[key]=Math.max(bounds[key][0],Math.min(bounds[key][1],value));onChange();};
  handle.onpointerup=handle.onpointercancel=()=>{pointer=null;};
 }
 let drag=null;
 textBox.onpointerdown=e=>{const item=getItem();if(!item)return;e.preventDefault();e.stopPropagation();drag={x:e.clientX,y:e.clientY,rect:textRect(item,getConfig()),corner:e.target.dataset.corner};textBox.setPointerCapture(e.pointerId);};
 textBox.onpointermove=e=>{if(!drag||!textBox.hasPointerCapture(e.pointerId))return;const item=getItem(),c=getConfig(),r=art.getBoundingClientRect(),dx=(e.clientX-drag.x)/(r.width/item.width),dy=(e.clientY-drag.y)/(r.height/item.height),a=drag.rect;let left=a.left,top=a.top,right=a.right,bottom=a.bottom;if(!drag.corner){const mx=Math.max(-left,Math.min(item.width-right,dx)),my=Math.max(-top,Math.min(item.height-bottom,dy));left+=mx;right+=mx;top+=my;bottom+=my;}else{if(drag.corner.includes('w'))left=Math.max(0,Math.min(right-8,left+dx));if(drag.corner.includes('e'))right=Math.min(item.width,Math.max(left+8,right+dx));if(drag.corner.includes('n'))top=Math.max(0,Math.min(bottom-8,top+dy));if(drag.corner.includes('s'))bottom=Math.min(item.height,Math.max(top+8,bottom+dy));}const s=c.scale;c.padding=[top*s,(item.width-right)*s,(item.height-bottom)*s,left*s].map(v=>Math.round(v*10)/10);onChange();};
 textBox.onpointerup=textBox.onpointercancel=()=>{drag=null;};
}
