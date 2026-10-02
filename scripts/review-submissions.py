#!/usr/bin/env python3
"""Owner-only moderation CLI. No public approval endpoint or embedded credentials."""
import argparse,base64,hashlib,json,re,subprocess,tempfile
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
 # Approval records a decision, not publication. Publication still requires image/config review.
 row['status']='approved' if args.action=='approve' else 'rejected';row['reviewReason']=args.reason
 path=f'pending/{args.id}/submission.json';old=content(path)
 gh('api','--method','PUT',f'repos/{QUEUE}/contents/{path}',body={'message':f'Review submission {args.id}: {row["status"]}','sha':old['sha'],'content':base64.b64encode(json.dumps(row,ensure_ascii=False,indent=2).encode()).decode()})
 print(json.dumps({'id':args.id,'status':row['status']},ensure_ascii=False))
if __name__=='__main__':main()
