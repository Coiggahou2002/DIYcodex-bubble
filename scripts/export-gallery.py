#!/usr/bin/env python3
"""Export the PNG gallery and Codex simulation as a static, backend-free site."""
from pathlib import Path
import argparse,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
def export(destination):
 destination=destination.resolve();destination.mkdir(parents=True,exist_ok=True)
 static=ROOT/'app/static'
 for name in ['gallery.html','gallery.css','gallery.js','workshop.html','workshop.css','workshop.js','editor-core.mjs','submission.mjs','submission-config.json','codex-preview.mjs','codex-preview.css','nine-slice.mjs','i18n.mjs']:
  shutil.copy2(static/name,destination/('index.html' if name=='gallery.html' else name))
 for name in ['gallery.css','gallery.js','codex-preview.css']:
  page=destination/'index.html';page.write_text(page.read_text().replace('"/'+name+'"','"./'+name+'"'))
 page=destination/'index.html';page.write_text(page.read_text().replace('<body>','<body data-mode="static">'))
 workshop=destination/'workshop.html';workshop.write_text(workshop.read_text().replace('href="gallery.html"','href="./index.html"'))
 shutil.copytree(ROOT/'presets',destination/'presets',dirs_exist_ok=True)
 shutil.copytree(ROOT/'community/approved',destination/'community-gallery',dirs_exist_ok=True)
 shutil.copy2(ROOT/'LICENSE',destination/'LICENSE')
 (destination/'.nojekyll').touch()
 # Bust Pages CDN caches when stylesheet contents change.
 for name in ['gallery.css','codex-preview.css']:
  digest=hashlib.sha256((destination/name).read_bytes()).hexdigest()[:12]
  page=destination/'index.html';page.write_text(page.read_text().replace('./'+name+'"','./'+name+'?v='+digest+'"'))
 # GitHub Pages caches HTML and JS independently. Version links and scripts so a
 # gallery handoff cannot land in an older workshop after a deployment.
 workshop_version=hashlib.sha256((destination/'workshop.html').read_bytes()).hexdigest()[:12]
 for name in ['index.html','gallery.js']:
  page=destination/name;page.write_text(page.read_text().replace('workshop.html','workshop.html?v='+workshop_version))
 for page_name,names in [('index.html',['gallery.js']),('workshop.html',['workshop.js','workshop.css','codex-preview.css'])]:
  page=destination/page_name
  content=page.read_text()
  for name in names:
   digest=hashlib.sha256((destination/name).read_bytes()).hexdigest()[:12]
   content=content.replace('./'+name+'"','./'+name+'?v='+digest+'"')
  page.write_text(content)
 return destination
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('destination',type=Path);args=parser.parse_args();print(export(args.destination))
