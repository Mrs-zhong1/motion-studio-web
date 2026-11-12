"""Stage 9 malformed/offline GLB rejection: existing project must survive every invalid upload."""
import json,struct,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'STAGE9-INVALID-GLB-RESULT.json'
GOOD=ROOT.parent/'Sample-Textured-Animated.glb'
def minimal_glb(doc):
    raw=json.dumps(doc,separators=(',',':')).encode('utf8')
    raw+=b' ' * ((-len(raw))%4)
    return struct.pack('<4sII',b'glTF',2,20+len(raw))+struct.pack('<I4s',len(raw),b'JSON')+raw
cases={
 'empty':b'',
 'bad_header':b'bad-data' * 5,
 'bad_json':struct.pack('<4sII',b'glTF',2,28)+struct.pack('<I4s',8,b'JSON')+b'not-json',
 'external_uri':minimal_glb({'asset':{'version':'2.0'},'meshes':[],'buffers':[{'byteLength':4,'uri':'remote.bin'}]}),
 'oversized':b'!'*(2*1024*1024+20),
}
result={'source':'GitHub Actions Chromium','errorCases':[],'passed':False,'errors':[]}
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':850},accept_downloads=True)
    page.on('pageerror',lambda e:result['errors'].append(str(e)))
    page.set_content((ROOT/'Motion-Studio-Stage9-THREE-OFFLINE.html').read_text(),wait_until='domcontentloaded')
    page.locator('#resumeProject').click()
    page.locator('[data-asset-tier-button="l3"]').click()
    page.locator('.comp[data-id="offline-glb-scene"] button').click()
    page.locator('#stage9GlbInput').set_input_files(str(GOOD))
    page.wait_for_timeout(250)
    original=page.evaluate('project.sections.find(s=>s.id==="offline-glb-scene").glb')
    assert len(original)>1000
    for name,data in cases.items():
        entry={'name':name,'bytes':len(data)}
        result['errorCases'].append(entry)
        try:
            page.locator('#stage9GlbInput').set_input_files({'name':name+'.glb','mimeType':'model/gltf-binary','buffer':data})
            page.wait_for_timeout(120)
            current=page.evaluate('project.sections.find(s=>s.id==="offline-glb-scene").glb')
            entry['modelPreserved']=(current==original)
            entry['passed']=entry['modelPreserved']
        except Exception as exc:
            entry['passed']=False
            entry['error']=str(exc)
    with page.expect_download() as dl:
        page.locator('#exportPage').click()
    path=ROOT/'STAGE9-INVALID-GLB-RECOVERY.html'
    dl.value.save_as(path)
    result['exportAfterRejectionsBytes']=path.stat().st_size
    result['componentCount']=page.evaluate('registry.length')
    result['passed']=all(i['passed'] for i in result['errorCases']) and result['componentCount']==20 and result['exportAfterRejectionsBytes']>30000 and not result['errors']
    browser.close()
except Exception:
 result['exception']=traceback.format_exc()
finally:
 RESULT.write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(result,indent=2))
assert result['passed'],'Invalid GLB must be rejected without corrupting existing project/export'
