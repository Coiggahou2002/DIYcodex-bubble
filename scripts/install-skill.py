#!/usr/bin/env python3
from pathlib import Path
import shutil,os,argparse
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--dest',default=str(Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'skills'));p.add_argument('--replace',action='store_true');args=p.parse_args()
target=Path(args.dest).expanduser()/'douyin-bubble-studio'
if target.exists() and not args.replace:raise SystemExit(f'Skill already exists: {target}. Use --replace to replace this skill only.')
if target.exists():shutil.rmtree(target)
shutil.copytree(ROOT/'skills/douyin-bubble-studio',target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
studio=target/'assets/studio';studio.mkdir(parents=True,exist_ok=True);shutil.copytree(ROOT/'app',studio/'app',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
print(f'Installed: {target}')
print(f'Start companion studio: python3 "{studio}/app/server.py"')
