#!/usr/bin/env python3
"""Local PNG library + nine-slice editor + Codex appearance bridge. No cloud calls."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json,struct,hashlib,base64,subprocess,shutil,os,threading,time,argparse,uuid,sys
ROOT=Path(__file__).resolve().parent.parent
DATA=Path(os.environ.get('BUBBLE_STUDIO_DATA',str(ROOT/'.local')))
DATA.mkdir(parents=True,exist_ok=True)
STATE=DATA/'state.json'
LOCK=threading.RLock()
STOP=threading.Event()
DEFAULT={'folders':[],'presets':{},'favorites':[],'active':None,'debugPort':19327,'trash':[]}
STATUS={'connected':False,'matched':0}
PORT=19329
NAMES={'cat-big-paw-scruffy':'毛茸茸猫咪 · 大爪子','cat-big-paw-doodle':'涂鸦猫咪 · 大爪子','chef-cat-wok-doodle':'猫咪主厨','onigiri-cat-doodle':'饭团猫咪','guangdong-stool':'广东小板凳','rippled-glass-nine-slice':'水波玻璃','mondrian-painting':'蒙德里安画框','mondrian':'蒙德里安','colorful-happy-doodle':'彩色快乐涂鸦','happy-stickman':'快乐小人','love-square-charcoal':'LOVE 方形炭笔','love-charcoal':'LOVE 炭笔'}
def state():
 try:return {**DEFAULT,**json.loads(STATE.read_text())}
 except (OSError,ValueError):return json.loads(json.dumps(DEFAULT))
def save(s):
 with LOCK:
  tmp=DATA/'state.tmp';tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2));tmp.replace(STATE)
def clean_trash(s):
 remaining=[entry for entry in s.get('trash',[]) if Path(entry['stored']).is_file()]
 if remaining!=s.get('trash',[]):s['trash']=remaining;save(s)
 return s
def choose_folder(language="zh"):
 if sys.platform!='darwin':raise ValueError('目前仅支持 macOS 文件夹选择')
 prompt='Choose your bubble asset folder' if language.startswith('en') else '选择气泡素材文件夹'
 script='try\nreturn POSIX path of (choose folder with prompt "'+prompt+'")\non error number -128\nreturn ""\nend try'
 result=subprocess.run(['/usr/bin/osascript','-e',script],capture_output=True,text=True)
 if result.returncode:raise ValueError('无法打开文件夹选择窗口，请重试')
 return result.stdout.strip()
def png_info(path):
 b=path.read_bytes()
 if len(b)<33 or b[:8]!=b'\x89PNG\r\n\x1a\n' or b[12:16]!=b'IHDR':raise ValueError('不是有效的 PNG')
 w,h=struct.unpack('>II',b[16:24])
 if not(2<=w<=4096 and 2<=h<=4096):raise ValueError('图片尺寸需在 2–4096 像素内')
 return w,h,len(b)
def asset_id(path):return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:20]
def library(s=None):
 s=s or state();items=[];seen=set()
 for folder in s['folders']+[str(DATA/'imports')]:
  p=Path(folder)
  if not p.is_dir():continue
  for f in sorted(p.glob('*.png')):
   if str(f.resolve()) in seen:continue
   try:w,h,size=png_info(f)
   except (ValueError,OSError):continue
   seen.add(str(f.resolve()));key=asset_id(f);name=f.stem.removeprefix('douyin-bubble-').replace('-198x162','')
   for term,label in NAMES.items():
    if name.startswith(term):name=name.replace(term,label);break
   config={**defaults(w,h),**s['presets'].get(key,{})}
   items.append({'id':key,'name':name,'filename':f.name,'width':w,'height':h,'bytes':size,'douyinSize':w<=198 and h<=162 and size<=2*1024*1024,'favorite':key in s['favorites'],'config':config,'url':'/asset/'+key,'path':str(f.resolve())})
 return items
def defaults(w,h):return {'left':round(w*.35),'right':round(w*.73),'top':round(h*.45),'bottom':round(h*.55),'scale':round(max(.01,min(.6,240/w,98/h)),4),'radius':0,'borderWidth':0,'borderColor':'#d0d0d0','color':'#44362f','padding':[29,37,36,48],'width':w,'height':h}
def validate(c,w,h):
 import re
 c={**defaults(w,h),**c,'width':w,'height':h}
 for k in ('left','right','top','bottom'):c[k]=int(c[k])
 if not(0<c['left']<c['right']<w and 0<c['top']<c['bottom']<h):raise ValueError('拉伸线不能交叉或超出图片')
 c['scale']=float(c['scale'])
 if not .01<=c['scale']<=2:raise ValueError('比例需在 1%–200% 之间')
 c['radius']=float(c['radius'])
 if not 0<=c['radius']<=200:raise ValueError('圆角需在 0–200 像素之间')
 c['borderWidth']=float(c['borderWidth'])
 if not 0<=c['borderWidth']<=20:raise ValueError('边框需在 0–20 像素之间')
 if not re.fullmatch(r'#[0-9a-fA-F]{6}',c['borderColor']):raise ValueError('边框颜色需为六位十六进制颜色')
 if not re.fullmatch(r'#[0-9a-fA-F]{6}',c['color']):raise ValueError('文字颜色需为六位十六进制颜色')
 if len(c['padding'])!=4 or any(not 0<=float(v)<=200 for v in c['padding']):raise ValueError('文字边距需在 0–200 之间')
 c['padding']=[float(v) for v in c['padding']];return c
def node_path():
 n=os.environ.get('BUBBLE_STUDIO_NODE') or shutil.which('node')
 if n:return n
 fallback=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
 if fallback.exists():return str(fallback)
 raise ValueError('请安装 Node.js 22 或以上版本')
def bridge(action):
 try:
  result=subprocess.run([node_path(),str(ROOT/'app/bridge.mjs'),str(STATE),action],capture_output=True,text=True,timeout=12)
  return json.loads(result.stdout) if result.returncode==0 else {'connected':False,'matched':0,'message':'应用连接失败'}
 except Exception:return {'connected':False,'matched':0,'message':'应用连接暂不可用'}
def watch():
 global STATUS
 while not STOP.wait(3):
  s=state();STATUS=bridge('apply' if s['active'] else 'status')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,data,code=200,kind='application/json'):
  body=json.dumps(data,ensure_ascii=False).encode() if kind=='application/json' else data
  self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self):
  path=self.path.split('?')[0]
  if path=='/api/library':
   with LOCK:s=clean_trash(state());items=library(s)
   for item in items:item.pop('path')
   return self.send({'items':items,'folders':s['folders'],'activeId':s['active']['id'] if s['active'] else None,'preferredId':s.get('preferredId'),'trashCount':len(s.get('trash',[])),'latestTrashId':s['trash'][-1]['token'] if s.get('trash') else None,'status':STATUS})
  if path=='/api/status':return self.send({**STATUS,'activeId':state()['active']['id'] if state()['active'] else None})
  if path.startswith('/asset/'):
   item=next((x for x in library() if x['id']==path[7:]),None)
   if not item:return self.send({'error':'素材不存在'},404)
   return self.send(Path(item['path']).read_bytes(),kind='image/png')
  if path=='/api/design-prompt':return self.send({'prompt':'使用 $douyin-chat-bubble skill 设计一款原创抖音聊天气泡。先确定四边直线锚区和点九拉伸线，保证镜像可读与文字空间；导出到我的素材库，完成尺寸、边距、四边锚点与长短消息预检，再在气泡工坊里选择并应用。'})
  if path=='/api/export':
   s=state();return self.send({'version':1,'active':None if not s['active'] else {'filename':Path(s['active']['path']).name,'config':s['active']['config']}})
  files={'/':'index.html','/index.html':'index.html','/app.css':'app.css','/app.js':'app.js','/nine-slice.mjs':'nine-slice.mjs','/i18n.mjs':'i18n.mjs'}
  if path not in files:return self.send({'error':'不存在'},404)
  f=ROOT/'app/static'/files[path];kind={'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','mjs':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[f.suffix[1:]];return self.send(f.read_bytes(),kind=kind)
 def do_POST(self):
  global STATUS
  if self.headers.get('Origin')!=f'http://127.0.0.1:{PORT}' or self.headers.get('X-Bubble-Studio')!='1':return self.send({'error':'只允许本机工作台操作'},403)
  try:
   length=int(self.headers.get('Content-Length','0'))
   if length>4*1024*1024:raise ValueError('请求过大')
   body=json.loads(self.rfile.read(length))
   if self.path=='/api/choose-folder':
    selected=choose_folder(self.headers.get('Accept-Language','zh'))
    if not selected:return self.send({'ok':True,'cancelled':True})
    body={'path':selected}
   with LOCK:
    s=state()
    if self.path in ('/api/folder','/api/choose-folder'):
     p=Path(body['path']).expanduser().resolve()
     if not p.is_dir():raise ValueError('文件夹不存在')
     if str(p) not in s['folders']:s['folders'].append(str(p))
     save(s);return self.send({'ok':True})
    if self.path=='/api/open-trash':
     if sys.platform!='darwin':raise ValueError('目前仅支持 macOS')
     trash=DATA/'trash';trash.mkdir(exist_ok=True)
     subprocess.run(['/usr/bin/open',str(trash.resolve())],check=True,capture_output=True)
     return self.send({'ok':True})
    if self.path=='/api/import':
     data=base64.b64decode(body['data'],validate=True)
     if len(data)>2*1024*1024:raise ValueError('PNG 不得超过 2 MB')
     folder=DATA/'imports';folder.mkdir(exist_ok=True);name=Path(body['name']).name
     if not name.lower().endswith('.png'):raise ValueError('请选择 PNG')
     p=folder/(uuid.uuid4().hex[:8]+'-'+name);p.write_bytes(data)
     try:png_info(p)
     except Exception:p.unlink();raise
     return self.send({'ok':True,'id':asset_id(p)})
    if self.path=='/api/delete':
     item=next((x for x in library(s) if x['id']==body['id']),None)
     if not item:raise ValueError('素材不存在')
     source=Path(item['path']);token=uuid.uuid4().hex
     trash=DATA/'trash';trash.mkdir(exist_ok=True);destination=trash/(token[:8]+'-'+source.name)
     shutil.move(str(source),str(destination))
     entry={'token':token,'id':item['id'],'original':str(source),'stored':str(destination)}
     s.setdefault('trash',[]).append(entry)
     removed_active=bool(s['active'] and s['active']['id']==item['id'])
     if removed_active:s['active']=None
     try:save(s)
     except Exception:shutil.move(str(destination),str(source));raise
     if removed_active:STATUS=bridge('restore')
     return self.send({'ok':True,'token':token,'activeRemoved':removed_active})
    if self.path=='/api/undo-delete':
     entry=next((x for x in s.get('trash',[]) if x['token']==body['token']),None)
     if not entry:raise ValueError('未找到可恢复的素材')
     original=Path(entry['original']);stored=Path(entry['stored'])
     if original.exists() or original.is_symlink():raise ValueError('原位置已有同名文件，恢复未覆盖任何文件')
     original.parent.mkdir(parents=True,exist_ok=True)
     shutil.move(str(stored),str(original));s['trash']=[x for x in s['trash'] if x['token']!=entry['token']]
     try:save(s)
     except Exception:shutil.move(str(original),str(stored));raise
     return self.send({'ok':True,'id':entry['id']})
    if self.path=='/api/favorite':
     key=body['id'];s['favorites']=[x for x in s['favorites'] if x!=key] if key in s['favorites'] else s['favorites']+[key];save(s);return self.send({'ok':True})
    if self.path in ('/api/save','/api/apply'):
     item=next((x for x in library(s) if x['id']==body['id']),None)
     if not item:raise ValueError('素材不存在')
     c=validate(body['config'],item['width'],item['height']);s['presets'][item['id']]=c;s['preferredId']=item['id']
     if self.path=='/api/apply':
      s['active']={'id':item['id'],'path':item['path'],'config':c,'version':uuid.uuid4().hex}
      # Hand off from the old one-bubble monitor before taking ownership.
      old=ROOT.parent/'codex-cat-bubble'
      if old.is_dir():(old/'stop-watch').write_text('studio owns appearance')
     save(s)
    elif self.path=='/api/restore':s['active']=None;save(s)
    elif self.path=='/api/launch':
     if sys.platform!='darwin':raise ValueError('目前仅支持 macOS')
     app=next((p for p in [Path('/Applications/ChatGPT.app/Contents/MacOS/ChatGPT'),Path('/Applications/Codex.app/Contents/MacOS/Codex')] if p.exists()),None)
     if not app:raise ValueError('未找到 ChatGPT 或 Codex 应用')
     running=subprocess.run(['/usr/bin/pgrep','-f','^'+str(app)],capture_output=True)
     if running.returncode==0:raise ValueError('请先保存输入并用 ⌘Q 完全退出 ChatGPT/Codex，再点击启动。')
     log=(DATA/'app-start.log').open('a');subprocess.Popen([str(app),'--remote-debugging-address=127.0.0.1',f'--remote-debugging-port={s["debugPort"]}'],stdout=log,stderr=log,start_new_session=True);return self.send({'ok':True,'message':'正在启动应用，连接后会自动应用已选气泡。'})
    else:raise ValueError('未知操作')
   if self.path in ('/api/apply','/api/restore'):STATUS=bridge('restore' if self.path=='/api/restore' else 'apply')
   return self.send({'ok':True,'status':STATUS})
  except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as e:self.send({'error':str(e)},400)
def main():
 global PORT
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=19329);args=parser.parse_args();PORT=args.port
 if not STATE.exists():save(DEFAULT)
 threading.Thread(target=watch,daemon=True).start();print(f'气泡工坊 http://127.0.0.1:{PORT}',flush=True)
 try:ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
 finally:STOP.set()
if __name__=='__main__':main()
