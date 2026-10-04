#!/usr/bin/env python3
"""Cross-platform launcher used by the Windows .bat files: start the studio if needed, optionally relaunch apps, open the browser."""
from pathlib import Path
import json,os,subprocess,sys,time,urllib.request,webbrowser
ROOT=Path(__file__).resolve().parent.parent
BASE='http://127.0.0.1:19329'
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')  # Windows pipes/consoles default to a legacy code page
DETACHED_FLAGS=0x00000008|0x00000200|0x08000000  # DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP|CREATE_NO_WINDOW
def alive():
 try:
  with urllib.request.urlopen(BASE+'/api/library',timeout=1):return True
 except OSError:return False
def start_studio():
 if alive():return
 (ROOT/'.local').mkdir(exist_ok=True)
 log=(ROOT/'.local'/'studio.log').open('a')
 kwargs={'creationflags':DETACHED_FLAGS} if sys.platform=='win32' else {'start_new_session':True}
 subprocess.Popen([sys.executable,str(ROOT/'app'/'server.py')],cwd=ROOT,stdout=log,stderr=log,stdin=subprocess.DEVNULL,env={**os.environ,'PYTHONIOENCODING':'utf-8'},**kwargs)
 for _ in range(30):
  if alive():return
  time.sleep(0.2)
def launch_active():
 request=urllib.request.Request(BASE+'/api/launch-active',data=b'{}',headers={'Origin':BASE,'X-Bubble-Studio':'1','Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=30) as response:data=json.load(response)
 except urllib.error.HTTPError as error:data=json.load(error)
 except OSError:data={}
 print(data.get('message') or data.get('error') or '未能启动已选气泡。请查看工坊中的连接状态。')
def main():
 start_studio()
 if '--apps' in sys.argv:launch_active()
 webbrowser.open(BASE)
if __name__=='__main__':main()
