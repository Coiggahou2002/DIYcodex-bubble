#!/usr/bin/env python3
"""Owner-only moderation CLI. No public approval endpoint or embedded credentials."""
import argparse,base64,hashlib,json,re,subprocess,tempfile,shutil,os,sys
from pathlib import Path
QUEUE='kaitongg-bit/DIYcodex-bubble-submissions'
def gh(*args,body=None):
 command=['gh',*args]
 if body is not None:command+=['--input','-']
 result=subprocess.run(command,input=json.dumps(body) if body is not None else None,text=True,capture_output=True,check=True)
 return json.loads(result.stdout) if result.stdout.strip() else None
def content(path):return gh('api',f'repos/{QUEUE}/contents/{path}')
def read(path):return base64.b64decode(content(path)['content'])
def record(sid):
 if not re.fullmatch(r'[a-f0-9-]{36}',sid):raise ValueError('Invalid submission ID')
 return json.loads(read(f'pending/{sid}/submission.json'))

ROOT=Path(__file__).resolve().parents[1]
def publish_work(sid,row):
 """Copy an approved queue item into the public gallery and deploy Pages."""
 approved=ROOT/'community'/'approved';approved.mkdir(parents=True,exist_ok=True)
 manifest_path=approved/'manifest.json'
 manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'version':1,'items':[]}
 filename=f'{sid}.png';(approved/filename).write_bytes(read(f'pending/{sid}/bubble.png'))
 config=row.get('config') or {'width':row['width'],'height':row['height'],'left':round(row['width']*.35),'right':round(row['width']*.73),'top':round(row['height']*.45),'bottom':round(row['height']*.55),'scale':.6,'padding':[29,37,36,48],'color':'#44362f','radius':0,'borderWidth':0,'borderColor':'#d0d0d0'}
 (approved/f'{sid}.bubble.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
 item={'id':sid,'community':True,'name':row.get('name') or 'Untitled bubble','nameEn':row.get('name') or 'Untitled bubble','filename':filename,'author':row.get('nickname') or 'Anonymous','license':'Non-commercial only','config':config,'description':{'zh':'经人工审核收录的社区作品。','en':'A community bubble accepted after manual review.'}}
 manifest['items']=[x for x in manifest.get('items',[]) if x.get('id')!=sid]+[item]
 manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 subprocess.run(['git','add','community/approved'],cwd=ROOT,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode==0:
  pass
 else:
  subprocess.run(['git','commit','-m',f'Publish community bubble {sid}'],cwd=ROOT,check=True)
  subprocess.run(['git','push','origin','main'],cwd=ROOT,check=True)
 pages=os.environ.get('PAGES_WORKTREE')
 if not pages:
  worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True)
  blocks=worktrees.split('\n\n')
  for block in blocks:
   if '\nbranch refs/heads/gh-pages' in block:
    pages=block.splitlines()[1].removeprefix('worktree ');break
 if not pages:
  candidate=ROOT.parent.parent/'work'/'community-site'
  if candidate.is_dir() and (candidate/'.git').exists():pages=str(candidate)
 if not pages or not Path(pages).is_dir():raise RuntimeError('找不到 gh-pages 工作树，请设置 PAGES_WORKTREE')
 subprocess.run([sys.executable,str(ROOT/'scripts/export-gallery.py'),pages],cwd=ROOT,check=True,capture_output=True,text=True)
 subprocess.run(['git','add','-A'],cwd=pages,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=pages).returncode==0:
  return {'status':'published','pages':'unchanged'}
 subprocess.run(['git','commit','-m',f'Publish community bubble {sid}'],cwd=pages,check=True,capture_output=True,text=True)
 subprocess.run(['git','push','origin','gh-pages'],cwd=pages,check=True,capture_output=True,text=True)
 return {'status':'published','pages':'deployed'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['list','inspect','approve','reject']);parser.add_argument('id',nargs='?');parser.add_argument('--output',type=Path);parser.add_argument('--reason',default='');args=parser.parse_args()
 if args.action=='list':
  try:entries=content('pending')
  except subprocess.CalledProcessError as error:
   if "404" not in (error.stderr or ""):raise
   entries=[]
  pending=[]
  for entry in entries:
   if entry['type']=='dir':
    row=record(entry['name'])
    if row['status']=='pending':pending.append(row)
  print(json.dumps({'pendingCount':len(pending),'submissions':pending},ensure_ascii=False,indent=2));return
 row=record(args.id)
 if args.action=='inspect':
  png=read(f'pending/{args.id}/bubble.png')
  if hashlib.sha256(png).hexdigest()!=row['sha256']:raise ValueError('Image integrity check failed')
  if args.output:args.output.mkdir(parents=True,exist_ok=True);(args.output/'bubble.png').write_bytes(png);(args.output/'submission.json').write_text(json.dumps(row,ensure_ascii=False,indent=2))
  print(json.dumps(row,ensure_ascii=False,indent=2));return
 if row['status']!='pending':raise ValueError('Submission already reviewed')
 row['status']='approved' if args.action=='approve' else 'rejected';row['reviewReason']=args.reason
 path=f'pending/{args.id}/submission.json';old=content(path)
 gh('api','--method','PUT',f'repos/{QUEUE}/contents/{path}',body={'message':f'Review submission {args.id}: {row["status"]}','sha':old['sha'],'content':base64.b64encode(json.dumps(row,ensure_ascii=False,indent=2).encode()).decode()})
 result={'id':args.id,'status':row['status']}
 if args.action=='approve':
  result.update(publish_work(args.id,row))
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
