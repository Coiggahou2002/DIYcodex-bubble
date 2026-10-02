import unittest,tempfile,os,sys,json,struct,zlib,threading,urllib.request,urllib.error,base64,shutil
from pathlib import Path
from unittest.mock import patch
TASK_DATA=tempfile.TemporaryDirectory();os.environ['BUBBLE_STUDIO_DATA']=TASK_DATA.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import server

def png(w=198,h=162):
 def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+bytes([253,245,229,255])*w)*h))+chunk(b'IEND',b'')
class StudioTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);server.PORT=cls.http.server_port
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{server.PORT}'
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();TASK_DATA.cleanup()
 def setUp(self):shutil.rmtree(Path(TASK_DATA.name)/'imports',ignore_errors=True);server.save(json.loads(json.dumps(server.DEFAULT)));self.folder=Path(TASK_DATA.name)/'art';shutil.rmtree(self.folder,ignore_errors=True);self.folder.mkdir();(self.folder/'one.png').write_bytes(png());(self.folder/'two.png').write_bytes(png(160,120))
 def request(self,path,body=None,origin=True):
  headers={'Content-Type':'application/json','X-Bubble-Studio':'1'}
  if origin:headers['Origin']=self.base
  r=urllib.request.Request(self.base+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
  with urllib.request.urlopen(r) as response:return json.load(response)
 def connect(self):self.request('/api/folder',{'path':str(self.folder)});return self.request('/api/library')['items']
 def test_real_folder_and_independent_presets(self):
  items=self.connect();self.assertEqual(len(items),2);a,b=items;original=(self.folder/'one.png').read_bytes();c={**a['config'],'left':60,'right':120}
  self.request('/api/save',{'id':a['id'],'config':c});loaded=self.request('/api/library')['items'];self.assertEqual(loaded[0]['config']['left'],60);self.assertEqual(loaded[1]['config'],b['config']);self.assertEqual((self.folder/'one.png').read_bytes(),original)
 def test_apply_restore_and_export_no_private_path(self):
  a=self.connect()[0]
  with patch.object(server,'bridge',return_value={'connected':True,'matched':6}):
   self.assertEqual(self.request('/api/apply',{'id':a['id'],'config':a['config']})['status']['matched'],6)
   exported=self.request('/api/export');self.assertNotIn(TASK_DATA.name,json.dumps(exported));self.assertEqual(exported['active']['filename'],'one.png')
   self.request('/api/restore',{});self.assertIsNone(server.state()['active'])
 def test_import_and_bad_png_rollback(self):
  result=self.request('/api/import',{'name':'import.png','data':base64.b64encode(png()).decode()});self.assertTrue(result['id']);before=len(server.library())
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/import',{'name':'bad.png','data':base64.b64encode(b'bad').decode()})
  self.assertEqual(len(server.library()),before)
 def test_crossed_lines_rejected_and_origin_required(self):
  a=self.connect()[0];c={**a['config'],'left':150,'right':80}
  with self.assertRaises(urllib.error.HTTPError) as err:self.request('/api/apply',{'id':a['id'],'config':c})
  self.assertEqual(err.exception.code,400);self.assertIsNone(server.state()['active'])
  with self.assertRaises(urllib.error.HTTPError) as err:self.request('/api/folder',{'path':str(self.folder)},origin=False)
  self.assertEqual(err.exception.code,403)
 def test_large_png_defaults_fit_and_small_scale_radius_save(self):
  self.assertEqual(server.defaults(198,162)['scale'],.6)
  for w,h in [(420,210),(1000,500),(4096,4096)]:
   c=server.defaults(w,h)
   self.assertLessEqual(w*c['scale'],240.1)
   self.assertLessEqual(h*c['scale'],98.1)
  (self.folder/'large.png').write_bytes(png(1000,500))
  a=next(i for i in self.connect() if i['width']==1000)
  c={**a['config'],'scale':.05,'radius':24,'borderWidth':2.5,'borderColor':'#123456'}
  self.request('/api/save',{'id':a['id'],'config':c})
  saved=next(i for i in self.request('/api/library')['items'] if i['id']==a['id'])
  self.assertEqual(saved['config']['scale'],.05)
  self.assertEqual(saved['config']['radius'],24)
  self.assertEqual(saved['config']['borderWidth'],2.5)
  self.assertEqual(saved['config']['borderColor'],'#123456')
  for bad in ({**c,'scale':.001},{**c,'radius':-1},{**c,'radius':201},{**c,'borderWidth':21},{**c,'borderColor':'invalid'}):
   with self.assertRaises(urllib.error.HTTPError):self.request('/api/save',{'id':a['id'],'config':bad})
 def test_delete_undo_preserves_png_preset_and_active_restore(self):
  a=self.connect()[0];path=self.folder/'one.png';original=path.read_bytes()
  c={**a['config'],'radius':16}
  with patch.object(server,'bridge',return_value={'connected':True,'matched':2}) as bridge:
   self.request('/api/apply',{'id':a['id'],'config':c})
   deleted=self.request('/api/delete',{'id':a['id']})
   self.assertTrue(deleted['activeRemoved']);self.assertFalse(path.exists())
   self.assertIsNone(server.state()['active']);bridge.assert_called_with('restore')
   library=self.request('/api/library');self.assertEqual(len(library['items']),1)
   self.assertEqual(library['trashCount'],1);self.assertNotIn(TASK_DATA.name,json.dumps(library['latestTrashId']))
   restored=self.request('/api/undo-delete',{'token':deleted['token']})
   self.assertEqual(restored['id'],a['id']);self.assertEqual(path.read_bytes(),original)
   self.assertEqual(server.state()['presets'][a['id']]['radius'],16)
   self.assertIsNone(server.state()['active']);self.assertEqual(self.request('/api/library')['trashCount'],0)
 def test_undo_delete_refuses_overwriting_and_unknown_id(self):
  a=self.connect()[0];deleted=self.request('/api/delete',{'id':a['id']})
  path=self.folder/'one.png';path.write_bytes(b'new file')
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/undo-delete',{'token':deleted['token']})
  self.assertEqual(path.read_bytes(),b'new file');self.assertEqual(len(server.state()['trash']),1)
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/delete',{'id':'arbitrary-path'})
 def test_asset_route_cannot_read_arbitrary_path(self):
  with self.assertRaises(urllib.error.HTTPError) as err:self.request('/asset/../../app/server.py')
  self.assertEqual(err.exception.code,404)
if __name__=='__main__':unittest.main()
